from trino_llm_agent.domain.db.mongodb import MongoDBConnector
from trino_llm_agent.domain.documents import *
from dateutil import parser
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import re
from trino_llm_agent.pipelines.raw_document_etl import raw_document_etl
from trino_llm_agent.applications.crawlers.crawler_dispatcher import CrawlerDispatcher

def test_mongodb():
    MongoDBConnector.connect()

    date_string = "2024-12-18T00:00:00+00:00"
    datetime_object = parser.isoparse(date_string)
    date_object = datetime_object.date()

    software = Software(name="trino")

    blog_post = BlogPost(
        software = software,
        link = "test_link",
        content = "asdf, aefef, ehtet",
    )
    blog_post.save()

    release_note = ReleaseNote(
        software = software,
        link = "test_link",
        content = "asdf, aefef, ehtet",
    )
    release_note.save()

    MongoDBConnector.disconnect()

def test_beautiful_soup():
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(
        options=options
    )
    driver.get("https://trino.io/docs/current/release/release-476.html")
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.visibility_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print(f"{e!s}")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.find("h1", class_="post-title")
    release_date = soup.find("time", class_="dt-published")
    # print(title.string.strip())
    # print(release_date.attrs['abbrtime'])
    buttons = soup.find_all("button")
    for button in buttons:
        button.decompose()
    print(soup.find("article", class_="md-content__inner").get_text())

def test_dispatcher():
    sub_domain = "/docs/.*/release"
    url_parsed_result = urlparse("https://trino.io/docs/current/release/release-476.html")
    netloc = url_parsed_result.netloc
    parsed_domain = netloc if not sub_domain else re.escape(netloc) + sub_domain
    parttern = r"https://(www\.)?{}/*".format(parsed_domain)
    print(parsed_domain)
    print(parttern)
    if re.match(parttern, "https://trino.io/docs/current/release/release-476.html"):
        print("match")
    else:
        print("no match")

def test_crawler_dispatcher():
    dispatcher = CrawlerDispatcher.build().register_trino_blog().register_trino_release_note().register_trino_documentation()

def test_pipeline():
    links = [
        "https://trino.io/blog/2019/01/31/presto-software-foundation-launch",
        "https://trino.io/docs/current/installation/kubernetes.html",
        "https://trino.io/docs/current/release/release-440.html"
    ]
    MongoDBConnector.connect()
    raw_document_etl(links)
    MongoDBConnector.disconnect()

if __name__ == "__main__":
    test_pipeline()
