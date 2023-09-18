import os
from dotenv import load_dotenv
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

print("Loading environment variables...")
load_dotenv()
openAI_key = os.environ["OPENAI_API_KEY"]
qdrant_key = os.environ["QDRANT_API_KEY"]
qdrant_host = os.environ["QDRANT_HOST"]
print("Environment variables loaded.")

print("Loading CSV data...")
loader = CSVLoader(
    file_path="./sources/temp/temporary_checklist_data_ready.csv",
    source_column="Source",
)
data = loader.load()
print("CSV data loaded.")

print("Running text splitter...")
documents = loader.load()
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1500, chunk_overlap=200)
docs = text_splitter.split_documents(documents)
print("Text splitting complete.")

print("Running embeddings...")
embeddings = OpenAIEmbeddings()
print("Embeddings complete.")

print("Initializing Qdrant client...")
url = qdrant_host
api_key = qdrant_key
qdrant_collection = "raven"
qdrant_client = QdrantClient(url=url, api_key=api_key)
print("Qdrant client initialized.")

print("Deleting existing Qdrant collection if it exists...")
qdrant_client.delete_collection(collection_name=qdrant_collection)
print("Collection deleted.")

print("Creating new Qdrant collection...")
qdrant_client.create_collection(
    collection_name=qdrant_collection,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)
print("New collection created.")

print("Populating Qdrant collection...")
qdrant = Qdrant.from_documents(
    docs,
    embeddings,
    url=url,
    prefer_grpc=True,
    api_key=api_key,
    collection_name=qdrant_collection,
)
print("Qdrant collection populated.")

print("Script execution completed.")
