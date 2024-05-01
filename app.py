import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

st.set_page_config(page_title="Sherlock Holmes Geek", 
                   page_icon=":male-detective:", 
                   layout="centered", 
                   initial_sidebar_state="auto", 
                   menu_items=None)

openai.api_key = st.secrets.openai_key
st.header("Chat with the Sherlock Holmes Nerd 💬 📚")

if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Sherlock Holmes!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Sherlock Holmes novels – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", 
                                                                  temperature=0.5, 
                                                                  system_prompt="""You are an expert on Sir Arthur Conan Doyles Sherlock Holmes. 
                                                                  Assume that all questions are related to Sherlock Holmes. 
                                                                  Use your knowledge from the Novels. 
                                                                  If you are referencing something specific, say 'I got this information from Chapter X Book Y' 
                                                                  and fill in X and Y with where you got it from. 
                                                                  Do not hallucinate."""))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

# Initialize the chat engine
if "chat_engine" not in st.session_state.keys(): 
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="openai", verbose=True)

# Prompt for user input and save to chat history
if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display the prior chat messages
for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Reading..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            # Add response to message history
            st.session_state.messages.append(message) 