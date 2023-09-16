import os
from dotenv import load_dotenv
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant

load_dotenv()
openAI_key = os.environ["OPENAI_API_KEY"]
qdrant_key = os.environ["QDRANT_API_KEY"]
qdrant_host = os.environ["QDRANT_HOST"]

# Load data
loader = CSVLoader(
    file_path="./sources/temp/temporary_checklist_data_ready.csv",
    source_column="Source",
)
data = loader.load()

# Run text splitter to break contents into manageable chunks
# Adjust chunk size and overlap for best results
documents = loader.load()
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1500, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# Run embeddings
# Creates a vector representation of each chunk using the OpenAI API
embeddings = OpenAIEmbeddings()

url = qdrant_host
api_key = qdrant_key
qdrant = Qdrant.from_documents(
    docs,
    embeddings,
    url=url,
    prefer_grpc=True,
    api_key=api_key,
    collection_name="raven",
)
