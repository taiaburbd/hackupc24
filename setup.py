import getpass
import os
from dotenv import load_dotenv

load_dotenv(override=True)


os.environ["OPENAI_API_KEY"] = ""

from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.fastembed import FastEmbedEmbeddings

from langchain_iris import IRISVector

def datagen(query):
    loader = TextLoader("data/pg15069.txt", encoding='utf-8')
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    username = 'demo'
    password = 'demo' 
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972' 
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"


    COLLECTION_NAME = "state_of_the_union_test"

    db = IRISVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
    )

    # query = "Joint patrols to catch traffickers"
    docs_with_score = db.similarity_search_with_score(query)

    return docs_with_score


    # db.add_documents([Document(page_content="foo")])
    # docs_with_score = db.similarity_search_with_score("foo")
    # print(docs_with_score[0])