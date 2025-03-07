import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load environment variables (useful during local development)
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    st.error("Missing DeepSeek API Key. Please set DEEPSEEK_API_KEY in your environment.")
    st.stop()

# Configure OpenAI (using DeepSeek endpoint)
openai.api_key = API_KEY
openai.api_base = "https://api.deepseek.com"

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS for styling
st.markdown("""
    <style>
        .chat-container {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user {
            text-align: right;
            background-color: #d1ecf1;
        }
        .assistant {
            text-align: left;
            background-color: #f8d7da;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>DeepSeek Chat</h2>", unsafe_allow_html=True)

# Function to display conversation history
def display_chat():
    chat_html = '<div class="chat-container">'
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            chat_html += f'<div class="message user"><strong>You:</strong> {message["content"]}</div>'
        else:
            chat_html += f'<div class="message assistant"><strong>Bot:</strong> {message["content"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

display_chat()

# User input text area
user_input = st.text_area("Type your message here...", height=100)

if st.button("Send") and user_input.strip() != "":
    # Append the user message to the chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Placeholder to stream the bot response
    response_placeholder = st.empty()
    full_response = ""
    
    try:
        # Call the DeepSeek API with streaming enabled
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            stream=True
        )
        # Stream the response and update the placeholder
        for chunk in response:
            delta = chunk.choices[0].delta
            if "content" in delta:
                full_response += delta["content"]
                response_placeholder.markdown(
                    f'<div class="chat-container">'
                    f'<div class="message assistant"><strong>Bot:</strong> {full_response}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"Error: {e}")
        full_response = "Sorry, an error occurred while generating the response."
    
    # Append the bot response to chat history and rerun to update display
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    st.experimental_rerun()
