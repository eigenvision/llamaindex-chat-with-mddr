import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

st.set_page_config(page_title="Chat with the 2023 Microsoft Digital Defense Report", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with the 2023 Microsoft Digital Defense Report")
st.info("""As the digital domain continues to evolve, defenders around the world are innovating 
        and collaborating more closely than ever. In this report Microsoft shares its latest findings 
        about the state of cybersecurity threats in the world and provides actionable advice on 
        how organizations can protect themselves.""")
st.write("[Download the full report](https://www.microsoft.com/en-us/security/security-insider/microsoft-digital-defense-report-2023)")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Chat with the report by asking questions about criminal or nation state cyber threat actors and how to defend against them."}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the report. This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./MDDR_streamlit", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4", temperature=0.5, system_prompt="You are an expert on cybersecurity, cyber threat actors, and cyber defense measures. Your job is to provide clear, accurate, and detailed answers based on the Microsoft Digital Defense Report available to you. Keep your answers precise and based on facts – do not hallucinate events or statements."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
