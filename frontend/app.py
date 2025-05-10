# frontend/app.py

import streamlit as st
from datetime import datetime
import os
import base64

st.set_page_config(page_title="EVA – Your Memory Assistant", layout="centered")

# ------------------ HELPER FUNCTIONS ------------------ #
def get_image_as_base64(file_path):
    """Convert an image file to base64 encoding for embedding in HTML"""
    if not os.path.isfile(file_path):
        return ""
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get path to SVG files
src_dir = os.path.join(os.path.dirname(__file__), "src")
eva_logo_path = os.path.join(src_dir, "eva_logo.svg")
eva1_path = os.path.join(src_dir, "eva1.svg")
eva2_path = os.path.join(src_dir, "eva2.svg")

# ------------------ STYLES ------------------ #
st.markdown("""
    <style>
    body { background-color: #f9f9f9; }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #fff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .header img { height: 30px; }
    .header .close { font-size: 24px; color: #999; cursor: pointer; }
    .chat-container {
        max-width: 600px;
        margin: 20px auto;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    .eva2-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0.1;
        width: 200px;
        z-index: 0;
    }
    .message {
        padding: 12px;
        border-radius: 10px;
        margin: 6px 0;
        max-width: 80%;
        position: relative;
        z-index: 1;
    }
    .message-bot {
        background-color: #E6F0FF;
        align-self: flex-start;
    }
    .message-user {
        background-color: #FFFFFF;
        align-self: flex-end;
        border: 1px solid #ddd;
    }
    .avatar {
        font-size: 24px;
        vertical-align: middle;
    }
    .message-bot .avatar { margin-right: 8px; }
    .message-user .avatar { margin-left: 8px; }
    .input-container {
        max-width: 600px;
        margin: 10px auto 30px;
        display: flex;
        align-items: center;
    }
    .input-container input {
        flex-grow: 1;
        padding: 10px 15px;
        border-radius: 20px;
        border: 1px solid #ccc;
        outline: none;
        font-size: 16px;
    }
    .input-container button {
        background: none;
        border: none;
        font-size: 24px;
        margin-left: 10px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------ #
# Check if SVG files exist
eva_logo_html = f'<img src="data:image/svg+xml;base64,{get_image_as_base64(eva_logo_path)}" alt="EVA logo"/>' if os.path.exists(eva_logo_path) else '<img src="https://via.placeholder.com/30?text=EVA" alt="EVA logo"/>'
eva1_html = f'<img src="data:image/svg+xml;base64,{get_image_as_base64(eva1_path)}" style="height:30px; margin-right:8px;" alt="EVA"/>' if os.path.exists(eva1_path) else ''

st.markdown(f"""
<div class="header">
    <div style="display:flex; align-items:center;">
      {eva1_html}
      {eva_logo_html}
      <span style="margin-left:8px; font-weight:bold; font-size:18px;">EVA</span>
    </div>
    <div class="close">×</div>
</div>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------ #
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "Hello, how can I assist you?"}
    ]

# ------------------ CHAT DISPLAY ------------------ #
# Add eva2 SVG in the center of the chat
eva2_html = f'<img src="data:image/svg+xml;base64,{get_image_as_base64(eva2_path)}" class="eva2-center" alt="EVA background"/>' if os.path.exists(eva2_path) else ''

st.markdown(f'<div class="chat-container">{eva2_html}', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "bot":
        st.markdown(
            f'<div class="message message-bot">'
            f'<span class="avatar">😊</span>{msg["text"]}'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="message message-user">{msg["text"]}'
            f'<span class="avatar">👤</span>'
            '</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ------------------ INPUT BOX ------------------ #
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([10,1])
    with col1:
        user_input = st.text_input("Ask anything", "")
    with col2:
        submit = st.form_submit_button("🎙️")

if submit and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "text": user_input})

    # TODO: replace this with your agent pipeline call
    # For demo, we hardcode a couple of flows based on keywords
    if "summarize" in user_input.lower():
        bot_reply = (
            "Got it! I have saved a summary and saved it as:<br>"
            "<b>📄 View Document</b><br>"
            "Priority: <b>High</b><br>"
            "Would you like me to save it to your calendar?"
        )
    elif "yes" == user_input.strip().lower():
        bot_reply = "Done!<br>Time: 5:00 PM to 8:00 PM<br>Location: TUM Venture Lab"
    else:
        bot_reply = "Always welcome! Let me know if you need anything else."

    st.session_state.messages.append({"role": "bot", "text": bot_reply})
    st.experimental_rerun()