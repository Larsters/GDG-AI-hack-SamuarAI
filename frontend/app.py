import streamlit as st
from datetime import datetime
import os
import base64
import glob
from PIL import Image
import io
import time
from model_interact import analyze_screenshot

st.set_page_config(page_title="EVA – Your Memory Assistant", layout="centered")

# ------------------ HELPER FUNCTIONS ------------------ #
def get_image_as_base64(file_path):
    """Convert an image file to base64 encoding for embedding in HTML"""
    if not os.path.isfile(file_path):
        return ""
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def get_latest_screenshot():
    """Find the most recent screenshot on the Desktop"""
    # Get user's desktop path
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # Look for common screenshot file patterns
    screenshot_patterns = [
        os.path.join(desktop_path, 'Screenshot*.png'),  # macOS format
        os.path.join(desktop_path, 'Screen Shot*.png'),
        os.path.join(desktop_path, 'screen*.png')
    ]
    
    all_screenshots = []
    for pattern in screenshot_patterns:
        all_screenshots.extend(glob.glob(pattern))
    
    if not all_screenshots:
        return None, 0
    
    # Find the most recent file
    latest_screenshot = max(all_screenshots, key=os.path.getmtime)
    mod_time = os.path.getmtime(latest_screenshot)
    
    return latest_screenshot, mod_time

# Get path to SVG files
src_dir = os.path.join(os.path.dirname(__file__), "src")
eva_logo_path = os.path.join(src_dir, "eva_logo.svg")
eva1_path = os.path.join(src_dir, "eva1.svg")
eva2_path = os.path.join(src_dir, "eva2.svg")

# ------------------ STYLES ------------------ #
st.markdown("""
    <style>
    .header {
        display: flex;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    .header img { height: 30px; }
    .eva2-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0.05;
        width: 200px;
        z-index: 0;
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
      {eva1_html if os.path.exists(eva1_path) else ''}
      {eva_logo_html if os.path.exists(eva_logo_path) else ''}
      <span style="margin-left:8px; font-weight:bold; font-size:18px;">EVA</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------ #
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "text": "Hello, how can I assist you?", "has_image": False}
    ]

if "waiting_for_screenshot" not in st.session_state:
    st.session_state.waiting_for_screenshot = False

if "last_screenshot_time" not in st.session_state:
    st.session_state.last_screenshot_time = 0

if "analyzing_screenshot" not in st.session_state:
    st.session_state.analyzing_screenshot = False

if "screenshot_to_analyze" not in st.session_state:
    st.session_state.screenshot_to_analyze = None

# ------------------ WAIT FOR SCREENSHOT ------------------ #
# If we're in screenshot waiting mode, check for new screenshots
if st.session_state.waiting_for_screenshot:
    # Create a progress indicator
    with st.spinner("Waiting for screenshot..."):
        # Get the current latest screenshot and its time
        current_screenshot, current_time = get_latest_screenshot()
        
        # Add debugging info
        st.text(f"Last known screenshot time: {st.session_state.last_screenshot_time}")
        st.text(f"Current screenshot time: {current_time}")
        st.text(f"Current screenshot path: {current_screenshot}")
        
        # Check if we have a screenshot newer than our last recorded one
        if current_time > st.session_state.last_screenshot_time + 1:  # Adding 1 second threshold
            # We found a newer screenshot!
            st.session_state.waiting_for_screenshot = False
            
            # Set up for analysis
            st.session_state.analyzing_screenshot = True
            st.session_state.screenshot_to_analyze = current_screenshot
            
            # Show loading message
            st.session_state.messages.append({
                "role": "bot", 
                "text": "I found your screenshot! Analyzing...",
                "has_image": True,
                "image_path": current_screenshot,
                "is_analyzing_message": True
            })
            
            st.rerun()
        
        # Manually poll for changes by forcing a rerun every few seconds
        time.sleep(2)  # Wait 2 seconds before checking again
        st.rerun()  # Force streamlit to rerun and check again
        
        # Use a placeholder to show we're waiting
        st.text("Take a screenshot now, and I'll capture it.")
        
        # Add a cancel button
        if st.button("Cancel screenshot capture"):
            st.session_state.waiting_for_screenshot = False
            st.session_state.messages.append({
                "role": "bot", 
                "text": "Screenshot capture cancelled.",
                "has_image": False
            })
            st.rerun()

# If we're in analysis mode, perform the analysis
elif st.session_state.analyzing_screenshot and st.session_state.screenshot_to_analyze:
    current_screenshot = st.session_state.screenshot_to_analyze
    
    # Analyze the screenshot
    with st.spinner("Analyzing screenshot..."):
        analysis = analyze_screenshot(current_screenshot)
    
    # Create response message
    bot_reply = f"""I've analyzed your screenshot!<br><br>
    {analysis['summary']}<br><br>
    <b>📄 Summary saved to notes</b><br>
    Priority: <b>{analysis['priority']}</b>"""
    
    # Update the last message or add a new one
    for i, msg in enumerate(st.session_state.messages):
        if msg.get("is_analyzing_message", False):
            # Replace the placeholder message
            st.session_state.messages[i] = {
                "role": "bot", 
                "text": bot_reply,
                "has_image": True,
                "image_path": current_screenshot
            }
            break
    
    # Reset analysis state
    st.session_state.analyzing_screenshot = False
    st.session_state.screenshot_to_analyze = None
    
    # Add follow-up question about calendar
    st.session_state.messages.append({
        "role": "bot", 
        "text": "Would you like me to save this to your calendar?",
        "has_image": False
    })
    
    st.rerun()

# ------------------ CHAT DISPLAY ------------------ #
# Add eva2 SVG in the center of the chat area if it exists
if os.path.exists(eva2_path):
    st.markdown(f'<div style="position:relative;"><img src="data:image/svg+xml;base64,{get_image_as_base64(eva2_path)}" class="eva2-center" alt="EVA background"/></div>', unsafe_allow_html=True)

# Display messages using standard Streamlit components
for msg in st.session_state.messages:
    if msg["role"] == "bot":
        with st.container():
            st.write(msg["text"], unsafe_allow_html=True)
            if msg.get("has_image") and "image_path" in msg:
                st.image(msg["image_path"], caption="Screenshot", use_container_width=True)
    else:
        with st.container():
            st.write(f"<div style='text-align: right;'>{msg['text']}</div>", unsafe_allow_html=True)

# ------------------ FOLLOW UP QUESTIONS ------------------ #
# Check if we need to automatically add a follow-up question
for i, msg in enumerate(st.session_state.messages):
    # If calendar was just added in the previous message, ask about forwarding
    if msg.get("calendar_added") and i == len(st.session_state.messages) - 1:
        # Wait a little before asking follow-up
        time.sleep(3)
        
        # Add follow-up question about forwarding
        follow_up = "Is this related to the Eva startup you're working at? Would you like me to forward the email to anyone?"
        
        st.session_state.messages.append({
            "role": "bot", 
            "text": follow_up,
            "has_image": False
        })
        
        # Remove the flag so we don't keep adding this message
        st.session_state.messages[i].pop("calendar_added", None)
        
        st.rerun()
        break

# ------------------ INPUT BOX ------------------ #
# Only show input if not waiting for screenshot
if not st.session_state.waiting_for_screenshot:
    user_input = st.text_input("Message", key="user_input")
    if st.button("Send"):
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "text": user_input})
            
            # Handle Eva Snap command
            if user_input.lower() == "eva, snap":
                # Get current latest screenshot time to compare later
                _, current_time = get_latest_screenshot()
                st.session_state.last_screenshot_time = current_time
                
                # Enter screenshot waiting mode
                st.session_state.waiting_for_screenshot = True
                
                # Add a message that we're waiting
                st.session_state.messages.append({
                    "role": "bot", 
                    "text": "I'm ready! Take a screenshot now, and I'll capture it.",
                    "has_image": False
                })
                st.rerun()
            else:
                # Default response based on conversation flow
                if user_input.lower() in ["yes", "yeah", "sure", "ok", "y"]:
                    # Handle calendar confirmation
                    if any(("calendar" in msg.get("text", "").lower() and "save" in msg.get("text", "").lower()) 
                           for msg in st.session_state.messages[-3:]):
                        # Show processing message and sleep
                        with st.spinner("Adding to calendar..."):
                            time.sleep(5)  # Simulate processing delay
                        
                        event_details = "Time: 5:00 PM to 8:00 PM<br>Location: TUM Venture Lab"
                        bot_reply = f"Done!<br>{event_details}"
                        
                        st.session_state.messages.append({
                            "role": "bot", 
                            "text": bot_reply,
                            "has_image": False,
                            "calendar_added": True  # Mark that calendar was added
                        })
                        
                        # Rerun to show the calendar confirmation
                        st.rerun()
                        
                    # Handle forwarding email question
                    elif any("forward the email to anyone" in msg.get("text", "") for msg in st.session_state.messages[-3:]):
                        # Add message about specific forwarding
                        bot_reply = "Would you like me to send this email to your teammate Vasiliy at klyosovv@gmail.com?"
                        
                        st.session_state.messages.append({
                            "role": "bot", 
                            "text": bot_reply,
                            "has_image": False,
                            "forwarding_specific": True  # Mark that we're asking about specific forwarding
                        })
                        
                        st.rerun()
                        
                    # Handle specific forwarding confirmation  
                    elif any("send this email to your teammate Vasiliy" in msg.get("text", "") for msg in st.session_state.messages[-3:]):
                        # Show processing message and sleep
                        with st.spinner("Forwarding email..."):
                            time.sleep(3)  # Simulate processing delay
                            
                        bot_reply = "Email forwarded to Vasiliy at klyosovv@gmail.com"
                        
                        st.session_state.messages.append({
                            "role": "bot", 
                            "text": bot_reply,
                            "has_image": False
                        })
                        
                        st.rerun()
                        
                    else:
                        bot_reply = "I received your message. To test the screenshot feature, type 'Eva, Snap'."
                        
                        st.session_state.messages.append({
                            "role": "bot", 
                            "text": bot_reply,
                            "has_image": False
                        })
                        
                        st.rerun()
                else:
                    bot_reply = "I received your message. To test the screenshot feature, type 'Eva, Snap'."
                    
                    st.session_state.messages.append({
                        "role": "bot", 
                        "text": bot_reply,
                        "has_image": False
                    })
                    
                    st.rerun()