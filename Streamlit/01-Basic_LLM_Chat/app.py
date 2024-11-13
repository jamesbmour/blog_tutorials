# Streamlit app to interact with the Ollama language model
# File Name: app.py
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit as st
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

# Load environment variables from a .env file
load_dotenv()


# Function to configure the Streamlit page layout and settings
def configure_page():
    st.set_page_config(
        page_title="Ollama Chat App",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.title("💬 Ollama with Streamlit Chat App")
    with st.expander("Check State"):
        st.write(st.session_state)


# Function to display and handle sidebar interactions
def handle_sidebar():
    selected_model = st.sidebar.selectbox(
        "Select Model", ("llama3.2", "llama3.2:1b", "qwen2.5:0.5b", "gpt-3.5-turbo")
    )
    st.session_state.model = selected_model
    st.sidebar.divider()
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = [
            SystemMessage(content="You are a helpful AI assistant.")
        ]
        st.rerun()

    if st.sidebar.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Model Information")
    st.sidebar.write(f"Current Model: {selected_model}")
    return selected_model


@st.cache_resource
def get_chat_model(model_name):
    if model_name == "gpt-3.5-turbo":
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=model_name,
            streaming=True,
        )
    return ChatOllama(model=model_name, streaming=True)


# Function to display the chat messages on the screen
def display_chat_messages():
    for message in st.session_state.messages[1:]:
        if isinstance(message, HumanMessage):  # Display user messages
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):  # Display AI responses
            with st.chat_message("assistant"):
                st.write(message.content)


# Function to handle user input and update the chat conversation
def handle_user_input(chat_model):
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in chat_model.stream(st.session_state.messages):
                if chunk.content:  # Update the response content
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append(AIMessage(content=full_response))


###########################################################################
#########################  Main execution flow  ###########################
###########################################################################

configure_page()

selected_model = handle_sidebar()

chat_model = get_chat_model(selected_model)

# Initialize the chat history in the session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful AI assistant.")
    ]

display_chat_messages()

handle_user_input(chat_model)