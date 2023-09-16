import os
from dotenv import load_dotenv
import time
import streamlit as st
from modules.chain import load_chain

#company_logo = 'https://www.app.nl/wp-content/uploads/2019/01/Blendle.png'
company_logo = 'https://cdn-icons-png.flaticon.com/128/249/249441.png'

load_dotenv()
app_password = os.environ["APP_PASSWORD"] 

# Configure Streamlit page
st.set_page_config(
    page_title="Raven 0.1",
    page_icon=company_logo
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == app_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

    # Initialize LLM chain
    chain = load_chain()

    # Initialize chat history
    if 'messages' not in st.session_state:
        # Start with first message from assistant
        st.session_state['messages'] = [{"role": "assistant", 
                                    "content": "Hi, I'm Raven, your laboratory regulatory assistant. Ask me about lab regulations."}]

    # Display chat messages from history on app rerun
    # Custom avatar for the assistant, default avatar for user
    for message in st.session_state.messages:
        if message["role"] == 'assistant':
            with st.chat_message(message["role"], avatar=company_logo):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat logic
    if query := st.chat_input("Ask me a question!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant", avatar=company_logo):
            message_placeholder = st.empty()
            # Send user's question to our chain
            result = chain({"question": query})
            response = result['answer']
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