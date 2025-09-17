from trino_llm_agent.domain.documents import *
from trino_llm_agent.applications.crawlers.crawler import Crawler

class TrinoCrawler(Crawler):
    software = Software(name="Trino")

class TrinoBlogPostCrawler(TrinoCrawler):
    document = BlogPost
    document_type = DocumentType.BLOG_POST

    def _crawl(self, link, **kwargs) -> None:
        soup = self.get_soup(link)
        article = soup.find("article", class_="post")
        if article is None:
            raise TargetCrawlingContentNotFound("Target crawling content not found in link {link}")
        content = "Trino blog\n" + article.get_text()
        blog_post = BlogPost(
            software=self.software,
            link=link,
            content=content
        )
        blog_post.save()

class TrinoReleaseNoteCrawler(TrinoCrawler):
    document = ReleaseNote
    document_type = DocumentType.RELEASE_NOTE

    def _crawl(self, link, **kwargs):
        soup = self.get_soup(link)
        article = soup.find("article", class_="md-content__inner")
        if article is None:
            raise TargetCrawlingContentNotFound("Target crawling content not found in link {link}")
        content = "Trino release note\n" + article.get_text()
        release_note = ReleaseNote(
            software=self.software,
            link=link,
            content=content
        )
        release_note.save()

class TrinoDocumentationCrawler(TrinoCrawler):
    document = Documentation
    document_type = DocumentType.DOCUMENTATION

    def _crawl(self, link, **kwargs):
        soup = self.get_soup(link)
        article = soup.find("article", class_="md-content__inner")
        if article is None:
            raise TargetCrawlingContentNotFound("Target crawling content not found in link {link}")
        content = "Trino documentation\n" + article.get_text()
        documentation = Documentation(
            software=self.software,
            link=link,
            content=content
        )
        documentation.save()

class TargetCrawlingContentNotFound(Exception):
    pass
