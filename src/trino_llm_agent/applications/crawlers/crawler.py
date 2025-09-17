from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from tempfile import mkdtemp
from loguru import logger
from trino_llm_agent.domain.documents import *

chromedriver_autoinstaller.install()

class Crawler(ABC):
    software: Software = None
    document = RawDocument
    document_type = DocumentType.WEBPAGE

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        self.driver = webdriver.Chrome(options)

    @abstractmethod
    def _crawl(self, link: str, **kwargs) -> None: ...

    def is_crawled(self, link:str) -> bool:
        return self.document.objects(link=link).count() > 0
    
    def crawl_link(self, link: str, **kwargs) -> None:
        if self.is_crawled(link=link):
            logger.info(f"Document already exists in the database: {link}")
            return
        self._crawl(link=link)
    
    def get_soup(self, link) -> BeautifulSoup:
        self.driver.get(link)
        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.visibility_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            logger.error(f"{e!s}")
            raise
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        buttons = soup.find_all("button")
        for button in buttons:
            button.decompose()
        return soup

class DefaultCrawler(Crawler):
    def crawl(self, link, **kwargs) -> None:
        self.driver.get(link)
        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.visibility_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            logger.error(f"{e!s}")
            raise
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        content = soup.get_text()
        document = RawDocument(
            software=Software(name="unknown"),
            document_type=DocumentType.WEBPAGE.value,
            link=link,
            content=content
        )
        document.save()
