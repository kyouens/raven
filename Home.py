import os
from dotenv import load_dotenv
import time
import sqlite3
from cryptography.fernet import Fernet
import streamlit as st
from streamlit_option_menu import option_menu
from modules.chain import load_chain
from modules.auth import check_password
from streamlit_extras.app_logo import add_logo


# Load key from environmental variable and initialize Fernet object
load_dotenv()
key = os.getenv('SQLITE_KEY')
if key:
    key_bytes = key[2:-1].encode()
    cipher_suite = Fernet(key_bytes)
else:
    raise ValueError("No encryption key found in environmental variables.")

# Initialize SQLite database connection
with sqlite3.connect("./sources/SQLite/encrypted_checklist_data.db") as conn:
    c = conn.cursor()

# Configure Streamlit page
site_logo = 'static/logo.png'
raven_logo = 'static/raven.png'
user_logo = 'static/user.png' 
st.set_page_config(
    page_title="Raven 0.1",
    page_icon=raven_logo,
    initial_sidebar_state="expanded",
    menu_items=None
)

def main_app():

    # Initialize LLM chain
    chain = load_chain()

    # Initialize chat history
    if 'messages' not in st.session_state:
        # Start with first message from assistant
        st.session_state['messages'] = [
            {"role": "assistant", "content": "Hi, I'm Raven, your laboratory regulatory assistant. Ask me about lab regulations."},
            ]

    # Display chat messages from history on app rerun
    # Custom avatar for the assistant, default avatar for user
    for message in st.session_state.messages:
        if message["role"] == 'assistant':
            with st.chat_message(message["role"], avatar=raven_logo):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar=user_logo):
                st.markdown(message["content"])

    # Chat logic
    if query := st.chat_input("Ask me a question!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant", avatar=raven_logo):
            message_placeholder = st.empty()
            # Send user's question to our chain
            result = chain({"question": query})
            response = result['answer']
            sources = [doc.metadata.get("source") for doc in result["source_documents"]]
            full_response = ""

            # Simulate stream of response with milliseconds delay
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Existing sidebar markdown
        st.sidebar.markdown("### Related Sources")

        # Remove duplicates by converting to a set and then back to a list
        unique_sources = list(set(sources))

        # Display markdown in the sidebar for each source
        for i, source in enumerate(unique_sources):
            # Query database for markdown content based on source
            c.execute("SELECT Content FROM checklist_data WHERE Source = ?", (source,))
            encrypted_md_content = c.fetchone()
            
            # If content exists, decrypt and display it
            if encrypted_md_content:
                encrypted_md_content = encrypted_md_content[0]
                decrypted_md_content = cipher_suite.decrypt(encrypted_md_content).decode()
                with st.sidebar.expander(source):
                    st.markdown(decrypted_md_content)
            else:
                st.sidebar.warning(f"The file for {source} could not be found.")

# Run if authenticated
#if check_password():
main_app()

