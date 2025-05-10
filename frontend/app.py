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
    .input-container {
        max-width: 600px;
        margin: 10px auto 30px;
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
            f'<div class="message message-bot">{msg["text"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="message message-user">{msg["text"]}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# ------------------ INPUT BOX ------------------ #
user_input = st.text_input("Message", key="user_input")
if st.button("Send"):
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "text": user_input})
        
        # Simple response logic
        bot_reply = "I received your message and I'm processing it."
        
        # Add bot response
        st.session_state.messages.append({"role": "bot", "text": bot_reply})
        
        # Clear the input
        st.session_state.user_input = ""
        st.experimental_rerun()