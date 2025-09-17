import re
from urllib.parse import urlparse
from trino_llm_agent.applications.crawlers.crawler import Crawler, DefaultCrawler
from trino_llm_agent.applications.crawlers.trino_crawlers import TrinoBlogPostCrawler, TrinoReleaseNoteCrawler, TrinoDocumentationCrawler
from loguru import logger

class CrawlerDispatcher:
    def __init__(self) -> None:
        self._crawlers = {}
    
    @classmethod
    def build(cls) -> "CrawlerDispatcher":
        return cls()
    
    def register(self, domain: str, sub_domain: str, crawler: type[Crawler]) -> None:
        url_parsed_result = urlparse(domain)
        netloc = url_parsed_result.netloc
        parsed_domain = netloc if not sub_domain else netloc + sub_domain
        self._crawlers[r"https://(www\.)?{}/*".format(re.escape(parsed_domain))] = crawler
    
    def register_trino_blog(self) -> "CrawlerDispatcher":
        self.register("https://trino.io", "/blog", TrinoBlogPostCrawler)
        return self
    
    def register_trino_release_note(self) -> "CrawlerDispatcher":
        self.register("https://trino.io", "/docs/current/release", TrinoReleaseNoteCrawler)
        return self
    
    def register_trino_documentation(self) -> "CrawlerDispatcher":
        self.register("https://trino.io", "/docs", TrinoDocumentationCrawler)
        return self
    
    '''
    Trino documentation parttern: "https://trino.io/docs"
    Trino release note parttern: "https://trino.io/docs/current/release"
    To avoid matching documentation link to release note crawler, sort the items by parttern lengths
    TODO: find a way to solve the above problem without this hack
    '''
    def get_crawler(self, url: str) -> Crawler:
        for pattern, crawler in sorted(self._crawlers.items(), key=lambda item: len(item[0]), reverse=True):
            if re.match(pattern, url):
                logger.info(f"Matched crawler, {pattern}, {url}")
                return crawler()
        else:
            return DefaultCrawler()
