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
# Main chat interface
st.sidebar.title("Due Diligence Bot 🤖")
# SVG image
svg_image = """
<div style="width:1000px; height:auto;">
<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" viewBox="0 0 316 32">
  <defs>
    <style>
      .cls-1 {
        clip-path: url(#clippath);
      }
      .cls-2 {
        fill: none;
      }
      .cls-2, .cls-3, .cls-4, .cls-5 {
        stroke-width: 0px;
      }
      .cls-3 {
        fill: #cf0;
      }
      .cls-4 {
        fill: #00f0ff;
      }
      .cls-5 {
        fill: #001007;
      }
    </style>
    <clipPath id="clippath">
      <rect class="cls-2" x="0" y="0" width="37.5" height="32"/>
    </clipPath>
  </defs>
  <g class="cls-1">
    <g>
      <path class="cls-3" d="M4.5,6l-1.2,1.2,7.9,7.9H0v1.7h11.2l-7.9,7.9,1.2,1.2,10-10L4.5,6Z"/>
      <path class="cls-4" d="M27.5,6l-1.2,1.2,7.9,7.9h-15.6l-.9.9.9.9h15.6l-7.9,7.9,1.2,1.2,10-10-10-10Z"/>
      <path class="cls-3" d="M26.2,4.5l-1.2-1.2-7.9,7.9V0h-1.7v11.2L7.4,3.3l-1.2,1.2,10,10,10-10Z"/>
      <path class="cls-3" d="M6.2,27.5l1.2,1.2,7.9-7.9v11.2h1.7v-11.2l7.9,7.9,1.2-1.2-10-10-10,10Z"/>
    </g>
  </g>
  <path class="cls-5" d="M61.2,24.5v-14.4h-5.2v-2.4h12.9v2.4h-5.2v14.4h-2.6ZM71.4,24.5V7.7h2.5v6.6h.4c.2-.3.4-.6.7-.9.3-.3.7-.5,1.2-.7.5-.2,1.1-.3,1.9-.3s1.7.2,2.4.6c.7.4,1.3,1,1.7,1.7.4.7.6,1.6.6,2.6v7.1h-2.5v-6.9c0-1-.3-1.8-.8-2.3-.5-.5-1.2-.7-2.1-.7s-1.8.3-2.5,1c-.6.7-.9,1.6-.9,2.9v6h-2.5ZM91.6,24.8c-1.2,0-2.2-.2-3.1-.7-.9-.5-1.6-1.2-2.1-2.1-.5-.9-.7-2-.7-3.2v-.3c0-1.2.2-2.3.7-3.2.5-.9,1.2-1.6,2.1-2.1.9-.5,1.9-.8,3.1-.8s2.1.3,3,.8c.9.5,1.5,1.2,2,2.1.5.9.7,1.9.7,3.1v.9h-9.1c0,1,.4,1.9,1,2.5.7.6,1.5.9,2.5.9s1.6-.2,2.1-.6c.5-.4.8-.9,1.1-1.4l2,1.1c-.2.4-.6.9-1,1.4-.4.5-1,.9-1.7,1.2-.7.3-1.6.5-2.6.5ZM88.1,17.4h6.6c0-.9-.4-1.6-1-2.1-.6-.5-1.3-.8-2.3-.8s-1.7.3-2.3.8c-.6.5-.9,1.2-1.1,2.1ZM104.7,24.5l4.8-16.8h4.6l4.8,16.8h-2.7l-1.1-4h-6.6l-1.1,4h-2.7ZM109.1,18.1h5.3l-2.4-8.8h-.4l-2.4,8.8ZM125.7,24.7c-.9,0-1.7-.2-2.4-.6-.7-.4-1.3-1-1.7-1.7-.4-.7-.6-1.6-.6-2.6v-7.1h2.5v6.9c0,1,.3,1.8.8,2.3.5.5,1.2.7,2.1.7s1.8-.3,2.4-1c.6-.7.9-1.7.9-3v-6h2.5v11.8h-2.4v-1.8h-.4c-.2.5-.6.9-1.2,1.4-.6.4-1.4.6-2.5.6ZM140.3,24.5c-.7,0-1.3-.2-1.7-.6-.4-.4-.6-1-.6-1.7v-7.4h-3.3v-2.1h3.3v-3.9h2.5v3.9h3.5v2.1h-3.5v6.9c0,.5.2.7.7.7h2.5v2.1h-3.3ZM152,24.8c-1.2,0-2.2-.2-3.2-.7-.9-.5-1.6-1.2-2.2-2.1s-.8-2-.8-3.2v-.4c0-1.2.3-2.3.8-3.2.5-.9,1.2-1.6,2.2-2.1.9-.5,2-.7,3.2-.7s2.2.2,3.2.7c.9.5,1.7,1.2,2.2,2.1.5.9.8,2,.8,3.2v.4c0,1.2-.3,2.3-.8,3.2s-1.3,1.6-2.2,2.1c-.9.5-2,.7-3.2.7ZM152,22.6c1.1,0,2-.3,2.6-1,.7-.7,1-1.7,1-2.9v-.2c0-1.2-.3-2.2-1-2.9-.7-.7-1.6-1.1-2.7-1.1s-2,.4-2.6,1.1c-.7.7-1,1.6-1,2.9v.2c0,1.2.3,2.2,1,2.9.7.7,1.6,1,2.6,1ZM161.2,24.5v-11.8h2.4v1.4h.4c.2-.4.6-.8,1.1-1.1.5-.3,1.2-.5,2-.5s1.6.2,2.1.6c.5.4,1,.8,1.2,1.4h.4c.3-.5.7-1,1.2-1.4.5-.4,1.3-.6,2.2-.6s1.4.2,2,.5c.6.3,1.1.8,1.4,1.4.4.6.5,1.4.5,2.3v7.9h-2.5v-7.7c0-.7-.2-1.3-.6-1.7-.4-.4-.9-.6-1.7-.6s-1.4.2-1.8.7c-.5.5-.7,1.2-.7,2.1v7.1h-2.5v-7.7c0-.7-.2-1.3-.6-1.7-.4-.4-.9-.6-1.7-.6s-1.4.2-1.8.7c-.5.5-.7,1.2-.7,2.1v7.1h-2.5ZM185.5,24.8c-.8,0-1.6-.1-2.3-.4-.7-.3-1.2-.7-1.6-1.3-.4-.6-.6-1.2-.6-2s.2-1.5.6-2c.4-.5.9-1,1.6-1.2.7-.3,1.5-.4,2.3-.4h3.6v-.8c0-.7-.2-1.2-.6-1.7-.4-.4-1.1-.6-1.9-.6s-1.5.2-1.9.6c-.4.4-.7.9-.9,1.6l-2.3-.7c.2-.6.5-1.2.9-1.7.4-.5,1-1,1.7-1.3.7-.3,1.6-.5,2.5-.5,1.5,0,2.7.4,3.6,1.2.9.8,1.3,1.9,1.3,3.3v4.9c0,.5.2.7.7.7h1v2.1h-1.8c-.6,0-1-.1-1.4-.4s-.5-.7-.5-1.2h0c0,0-.4,0-.4,0-.1.2-.3.5-.6.8s-.6.6-1.1.8c-.5.2-1.2.3-2,.3ZM185.9,22.8c1,0,1.8-.3,2.4-.8.6-.6.9-1.4.9-2.4v-.2h-3.5c-.7,0-1.2.1-1.6.4-.4.3-.6.7-.6,1.2s.2,1,.6,1.3,1,.5,1.7.5ZM199.3,24.5c-.7,0-1.3-.2-1.7-.6-.4-.4-.6-1-.6-1.7v-7.4h-3.3v-2.1h3.3v-3.9h2.5v3.9h3.5v2.1h-3.5v6.9c0,.5.2.7.7.7h2.5v2.1h-3.3ZM205.8,24.5v-11.8h2.5v11.8h-2.5ZM207.1,11.1c-.5,0-.9-.2-1.2-.5-.3-.3-.5-.7-.5-1.2s.2-.9.5-1.2c.3-.3.7-.5,1.2-.5s.9.2,1.2.5c.3.3.5.7.5,1.2s-.2.9-.5,1.2c-.3.3-.7.5-1.2.5ZM217.5,24.8c-1.2,0-2.2-.2-3.2-.7-.9-.5-1.6-1.2-2.2-2.1s-.8-2-.8-3.2v-.4c0-1.2.3-2.3.8-3.2.5-.9,1.2-1.6,2.2-2.1.9-.5,2-.7,3.2-.7s2.2.2,3.2.7c.9.5,1.7,1.2,2.2,2.1.5.9.8,2,.8,3.2v.4c0,1.2-.3,2.3-.8,3.2s-1.3,1.6-2.2,2.1c-.9.5-2,.7-3.2.7ZM217.5,22.6c1.1,0,2-.3,2.6-1,.7-.7,1-1.7,1-2.9v-.2c0-1.2-.3-2.2-1-2.9-.7-.7-1.6-1.1-2.7-1.1s-2,.4-2.6,1.1c-.7.7-1,1.6-1,2.9v.2c0,1.2.3,2.2,1,2.9.7.7,1.6,1,2.6,1ZM226.8,24.5v-11.8h2.4v1.8h.4c.2-.5.6-.9,1.2-1.3.6-.4,1.4-.6,2.6-.6s1.7.2,2.4.6c.7.4,1.3,1,1.7,1.7.4.7.6,1.6.6,2.6v7.1h-2.5v-6.9c0-1-.3-1.8-.8-2.3-.5-.5-1.2-.7-2.1-.7s-1.8.3-2.5,1c-.6.7-.9,1.6-.9,2.9v6h-2.5ZM253.4,24.8c-1.2,0-2.3-.3-3.2-.8-.9-.5-1.7-1.3-2.2-2.3-.5-1-.8-2.2-.8-3.7v-3.9c0-2.2.6-3.9,1.8-5,1.2-1.2,2.8-1.8,4.9-1.8s3.6.6,4.7,1.7c1.1,1.1,1.6,2.6,1.6,4.4h0c0,.1-2.6.1-2.6.1v-.2c0-.7-.1-1.3-.4-1.8-.3-.6-.7-1-1.2-1.3s-1.2-.5-2.1-.5c-1.3,0-2.3.4-3,1.2-.7.8-1.1,1.8-1.1,3.2v4c0,1.4.4,2.4,1.1,3.2.7.8,1.7,1.2,3,1.2s2.2-.4,2.8-1.1.9-1.6.9-2.7v-.3h-4.5v-2.2h7.1v8.3h-2.4v-1.7h-.4c-.1.3-.4.6-.6.9-.3.3-.7.6-1.2.8-.5.2-1.2.3-2.1.3ZM263.5,24.5v-11.8h2.4v1.4h.4c.2-.5.5-.9.9-1.1.4-.2,1-.4,1.6-.4h1.4v2.2h-1.5c-.8,0-1.5.2-2,.7-.5.4-.8,1.1-.8,2v7h-2.5ZM277.9,24.8c-1.2,0-2.2-.2-3.2-.7-.9-.5-1.6-1.2-2.2-2.1-.5-.9-.8-2-.8-3.2v-.4c0-1.2.3-2.3.8-3.2.5-.9,1.2-1.6,2.2-2.1.9-.5,2-.7,3.2-.7s2.2.2,3.2.7c.9.5,1.7,1.2,2.2,2.1.5.9.8,2,.8,3.2v.4c0,1.2-.3,2.3-.8,3.2-.5.9-1.3,1.6-2.2,2.1-.9.5-2,.7-3.2.7ZM277.9,22.6c1.1,0,2-.3,2.6-1,.7-.7,1-1.7,1-2.9v-.2c0-1.2-.3-2.2-1-2.9-.7-.7-1.6-1.1-2.7-1.1s-2,.4-2.6,1.1c-.7.7-1,1.6-1,2.9v.2c0,1.2.3,2.2,1,2.9.7.7,1.6,1,2.6,1ZM291.7,24.7c-.9,0-1.7-.2-2.4-.6-.7-.4-1.3-1-1.7-1.7-.4-.7-.6-1.6-.6-2.6v-7.1h2.5v6.9c0,1,.3,1.8.8,2.3.5.5,1.2.7,2.1.7s1.8-.3,2.4-1c.6-.7.9-1.7.9-3v-6h2.5v11.8h-2.4v-1.8h-.4c-.2.5-.6.9-1.2,1.4-.6.4-1.4.6-2.5.6ZM301.9,29.3V12.7h2.4v1.7h.4c.3-.5.8-1,1.4-1.4.6-.4,1.5-.6,2.7-.6s1.9.2,2.7.7c.8.5,1.5,1.2,2,2.1.5.9.8,2,.8,3.3v.4c0,1.3-.2,2.4-.7,3.3-.5.9-1.2,1.6-2,2.1-.8.5-1.7.7-2.7.7s-1.4,0-1.9-.3c-.5-.2-1-.4-1.3-.7-.3-.3-.6-.6-.8-.9h-.4v6.4h-2.5ZM308,22.7c1.1,0,2-.3,2.7-1,.7-.7,1-1.7,1-3v-.2c0-1.3-.4-2.2-1.1-2.9-.7-.7-1.6-1-2.6-1s-1.9.3-2.6,1c-.7.7-1,1.7-1,2.9v.2c0,1.3.3,2.3,1,3,.7.7,1.6,1,2.6,1Z"/>
</svg>
</div>
"""

# Display SVG image at the top of the page
st.markdown(svg_image, unsafe_allow_html=True)

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