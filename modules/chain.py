import os
import streamlit as st
import openai
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from qdrant_client import qdrant_client


load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]
qdrant_key = os.environ["QDRANT_API_KEY"]
qdrant_host = os.environ["QDRANT_HOST"]


@st.cache_resource
def load_chain():

    # Load OpenAI embedding model
    embeddings = OpenAIEmbeddings()
    
    # Load OpenAI chat model
    llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            )
    
    # Prepare vector store
    client = qdrant_client.QdrantClient(
        qdrant_host,
        api_key=qdrant_key,
        )

    vector_store = Qdrant(
        client=client, 
        collection_name="raven", 
        embeddings=embeddings,
        )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Create memory 'chat_history' 
    memory = ConversationBufferWindowMemory(k=3,memory_key="chat_history", output_key="answer")
        
    # Create system prompt
    template = """
    You are an AI assistant for answering questions about laboratory regulatory matters.
    You are given the following extracted text from a list of regulations and a question. 
    Provide a professional and copmlete answer.
    Provide a reference for each assertion you make.
    If someone thanks you, say 'You are welcome.'.
    If you don't know the answer, just say 'Sorry, I am not sure.'. 
    Don't try to make up an answer.
    If the question is not about laboratory policies or regulations, politely inform them that you are tuned to only answer questions about laboratory regulations.
    
    {context}
    Question: {question}
    Helpful Answer:"""
        
    # Create the Conversational Chain
    chain = ConversationalRetrievalChain.from_llm(  llm=llm, 
                                                    retriever=retriever, 
                                                    memory=memory, 
                                                    get_chat_history=lambda h : h,
                                                    verbose=True,
                                                    return_source_documents=True,
                                                    )
    
    # Add system prompt to chain
    chain_prompt = PromptTemplate(input_variables=["context", "question"],template=template)
    chain.combine_docs_chain.llm_chain.prompt.messages[0] = SystemMessagePromptTemplate(prompt=chain_prompt)
    
    return chain









