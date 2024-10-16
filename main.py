import streamlit as st
import os
import time
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
st.set_page_config(layout="wide")

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'document_text' not in st.session_state:
    st.session_state['document_text'] = ''

# Sidebar components
st.sidebar.title("Settings")

# Model selection
model_options = ['gpt-4o', 'gpt-4', 'gpt-4o-mini', 'o1-preview', 'o1-mini', 'gpt-3.5-turbo']
selected_model = st.sidebar.selectbox("Select OpenAI Model", model_options)

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload a document", type=['pdf', 'docx', 'html', 'txt'])

# Process the uploaded document
def extract_text_from_uploaded_file(file):
    file_type = file.name.split('.')[-1].lower()
    if file_type == 'pdf':
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_type == 'docx':
        doc = Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    elif file_type == 'html':
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text()
    elif file_type == 'txt':
        return file.read().decode('utf-8', errors='ignore')
    else:
        return ''

if uploaded_file is not None:
    st.session_state['document_text'] = extract_text_from_uploaded_file(uploaded_file)
    st.sidebar.success("Document uploaded and processed!")

# Custom prompt
custom_prompt = (
    "Act like an investor that may want to invest in a company. I will share you a detailed document. "
    "Act the context, the data in the file as well as the arguments and statements. You will help me to analyze "
    "whether this is an interesting company to invest in but also you need to help you finding out what kind "
    "remarks or unclarities you see. So questions I can ask to this company to validate if this is a company with "
    "really a promising proposition. In some respect it feels a bit 'too good to be true' so I want to tackle. "
    "You really need me to do due diligence on this. It's essential to identify competitors and analyze their "
    "approaches. Please use also all the information in the doc. Present the results so we can directly use it as "
    "a conversation piece to both this company as the stakeholders."
)

# Main chat interface
st.title("Due Diligence Bot 🤖")

# Clear chat history
if st.sidebar.button("Clear Chat", key='clear'):
    st.session_state['messages'] = []
    st.session_state['document_text'] = ''  # Optionally clear document text
    st.rerun()  # Immediately rerun the script

# User input using st.chat_input
user_input = st.chat_input("Your message")

# Handle user input
if user_input:
    # Append user's message to chat history
    st.session_state['messages'].append({'role': 'user', 'content': user_input})

    # Prepare the context for the LLM
    context = st.session_state['document_text']

    # Build the messages for OpenAI API with custom prompt
    messages = [
        {'role': 'system', 'content': custom_prompt},
        {'role': 'system', 'content': f"Document context:\n{context}\n"},
    ] + st.session_state['messages']

    # Make the API call
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=messages
        )

        assistant_response = response.choices[0].message.content
        st.session_state['messages'].append({'role': 'assistant', 'content': assistant_response})

    except Exception as e:
        st.error(f"Error: {e}")

# Function to simulate streaming text output
def stream_assistant_response(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)  # Simulate delay

# Display chat history with streaming for the latest assistant response
for message in st.session_state['messages']:
    if message['role'] == 'user':
        with st.chat_message("user"):
            st.write(message['content'])
    else:
        with st.chat_message("assistant"):
            if message == st.session_state['messages'][-1]:  # Stream the latest assistant response
                st.write_stream(stream_assistant_response(message['content']))
            else:
                st.write(message['content'])
