import streamlit as st
import pandas as pd

col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')

with col2:
    st.image("static/raven.png")

with col3:
    st.write(' ')

st.markdown("""

# About

## Overview

Raven is a regulatory assistant designed to answer questions about laboratory regulations. Raven employs a [large language model (LLM)](https://en.wikipedia.org/) to provide answers based on guidelines from regulatory authorities. Its goal is to streamline and accelerate the process of ensuring laboratory compliance and safety.

## Features

- Answers complex regulatory questions in plain language
- Supplies links to source documents
- Tuned to minimize [hallucinations](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)) and other undesirable behaviors that may arise with LLMs

## How it Works

Raven uses a technique known as [retrieval-augmented generation (RAG)](https://arxiv.org/abs/2005.11401v4). In this method, an LLM's capabilities are enhanced by an external database of regulatory documents. Raven employs a [vector database](https://learn.microsoft.com/en-us/semantic-kernel/memories/vector-db) to identify the most pertinent regulatory documents based on the user's inquiry. The LLM then synthesizes the question and the retrieved documents to formulate the most accurate answer.

## Technologies

Raven is coded in Python and utilizes open-source or readily available commercial services for its infrastructure and user interface.
- [OpenAI API](https://platform.openai.com): This API offers an interface to access multiple machine learning models developed by OpenAI, including conversational agents based on the GPT architecture. It enables the incorporation of OpenAI's sophisticated natural language processing into applications, products, or services.
- [Streamlit](https://streamlit.io): An open-source Python library designed to ease the creation of web apps and data dashboards.
- [Langchain](https://www.langchain.com): This open-source framework simplifies building applications using LLMs by orchestrating the conversation flow, routing questions to the appropriate natural language processing models, and retrieving answers.
- [Qdrant](https://qdrant.tech): An open-source vector similarity database and search engine that powers the application's query handling and data retrieval capabilities.

## Disclaimer

Raven is a prototype and should not be used in an actual laboratory setting. *Raven makes mistakes, so do not depend on its answers for regulatory compliance.* Raven is not a substitute for laboratory expertise or professional regulatory advice.

## Source

The source code for this application can be obtained upon request and is licensed under a [Creative Commons Attribution-NonCommercial (CC BY-NC)](https://creativecommons.org/licenses/by-nc/3.0/) license. The project is currently being prepared for publication in a peer-reviewed journal, after which the source code will be available on GitHub.

The regulatory documentation used to operate Raven is owned by its respective publishers and is not part of the source code.

## Contact

- [LinkedIn](https://www.linkedin.com/in/kyouens/)
- [Mastodon](https://med-mastodon.com/@kyouens)
- [Email](mailto:ironic0_uplands@icloud.com)

""")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
