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
from trino_llm_agent.preprocessing.data_cleaning_dispatcher import DataCleaningHnadlerDispatcher
from nltk import sent_tokenize
import nltk
from trino_llm_agent.applications.embedding.embedding_model import EmbeddingModel
from sentence_transformers.SentenceTransformer import SentenceTransformer
from trino_llm_agent.settings import settings
from trino_llm_agent.domain.embedded_chuck import EmbeddedChunk
from trino_llm_agent.pipelines.rag_feature_etl import rag_feature_etl
from trino_llm_agent.domain.db.qdrant import qdrant_client

def test_mongodb():
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
        "https://trino.io/blog/2023/09/28/trino-gateway",
        "https://trino.io/docs/current/functions/geospatial.html",
        "https://trino.io/docs/current/release/release-321.html"
    ]
    raw_document_etl(links)

def test_get_raw_data():
    software_names = ["trino"]
    raw_documents = []
    for software_name in software_names:
        documents = list(RawDocument.objects(software__name__iregex=software_name))
        raw_documents.extend(documents)
    for document in raw_documents:
        print(document.content)

def test_cleaning_handlers():
    software_names = ["trino"]
    raw_documents = []
    for software_name in software_names:
        documents = list(RawDocument.objects(software__name__iregex=software_name))
        raw_documents.extend(documents)
    for document in raw_documents:
        cleaned_document = DataCleaningHnadlerDispatcher.dispatch(document)
        print(cleaned_document.to_point().payload)

def test_chunking():
    nltk.download('punkt_tab')
    software_names = ["trino"]
    raw_documents = []
    for software_name in software_names:
        documents = list(RawDocument.objects(software__name__iregex=software_name))
        raw_documents.extend(documents)
    for document in raw_documents:
        cleaned_document = DataCleaningHnadlerDispatcher.dispatch(document)
        sentences = sent_tokenize(cleaned_document.to_point().payload["content"])
        for sentence in sentences:
            print(sentence)

def test_embedding():
    nltk.download('punkt_tab')
    software_names = ["trino"]
    raw_documents = []
    embedding_model = EmbeddingModel.get_instance()
    for software_name in software_names:
        documents = list(RawDocument.objects(software__name__iregex=software_name))
        raw_documents.extend(documents)
    for document in raw_documents:
        cleaned_document = DataCleaningHnadlerDispatcher.dispatch(document)
        sentences = sent_tokenize(cleaned_document.to_point().payload["content"])
        for i in range(0, len(sentences), 10):
            sentences_batch = sentences[i:i + 10]
            embedding_batch = embedding_model.embed(sentences_batch)
            embedded_chunks = []
            for i in range(len(sentences_batch)):
                embedded_chunk = EmbeddedChunk(
                    chunk_content=sentences_batch[i],
                    embedding=embedding_batch[i],
                    document_id=document.id,
                    software="Trino"
                )
                embedded_chunks.append(embedded_chunk)
            print(embedded_chunks)

def test_find_from_vector_db():
    while True:
        points, next_offset = EmbeddedChunk.batch_find()
        # points, next_offset = qdrant_client.scroll(collection_name="embedded_chunk")
        for point in points:
            print(point)
        if next_offset is None:
            break

def test_search_from_vector_db():
    embedding_model = EmbeddingModel.get_instance()
    query = "Tell me about Trion Geospatial"
    query_vector = embedding_model.embed(query)
    search_results = qdrant_client.search(
        collection_name="embedded_chunk",
        query_vector=query_vector,
        limit=5
        )
    for point in search_results:
        print(f"Score: {point.score}")
        print(f"Payload: {point.payload}")
        print("-"*20)

if __name__ == "__main__":
    MongoDBConnector.connect()
    # test_pipeline()
    # softwares = ["Trino"]
    # rag_feature_etl(softwares)
    # test_find_from_vector_db()
    test_search_from_vector_db()
    MongoDBConnector.disconnect()
