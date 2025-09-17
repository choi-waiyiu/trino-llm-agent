from zenml import pipeline, step, get_step_context
from typing_extensions import Annotated
from urllib.parse import urlparse
from loguru import logger
from tqdm import tqdm
from trino_llm_agent.applications.crawlers.crawler_dispatcher import CrawlerDispatcher

@pipeline
def raw_document_etl(links: list[str]) -> str:
    crawl_links_step = crawl_links(links)
    return crawl_links_step.invocation_id

@step
def crawl_links(links: list[str]) -> Annotated[list[str], "crawled_links"]:
    dispatcher = CrawlerDispatcher.build().register_trino_blog().register_trino_release_note().register_trino_documentation()
    logger.info(f"Starting to crawl {len(links)} link(s)...")

    metadata = {}

    for link in tqdm(links):
        crawler = dispatcher.get_crawler(link)
        software = crawler.software.name
        document_type = crawler.document_type.value

        if software not in metadata:
            metadata[software] = {}
        if document_type not in metadata[software]:
            metadata[software][document_type] = {}

        metadata[software][document_type]["total"] = metadata[software][document_type].get("total", 0) + 1
        try:
            crawler.crawl_link(link)
            metadata[software][document_type]["successful"] = metadata[software][document_type].get("successful", 0) + 1
        except Exception as e:
            logger.error(f"Failed to crawl {link}: {e!s}")
    
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_links", metadata=metadata)

    return links
