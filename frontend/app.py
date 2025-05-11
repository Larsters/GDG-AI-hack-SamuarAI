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

# ------------------ NAVIGATION ------------------ #
# Create a sidebar menu for navigation
with st.sidebar:
    st.title("EVA Assistant")
    selected_page = st.radio("Navigation", ["Chat", "Memory"])

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

# Create a global variable to collect agent logs rather than printing them immediately
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

# Add a session state variable to track reasoning logs per step:
if "reasoning_history" not in st.session_state:
    st.session_state.reasoning_history = {}

# Replace the agent_log function with one that collects logs instead of displaying them
def agent_log(agent_name, message, step_id=None):
    """Add an agent interaction log to the collection"""
    log_entry = f"<div class='agent-log'><b>{agent_name}</b>: {message}</div>"
    st.session_state.agent_logs.append(log_entry)
    
    # If step_id is provided, store the log in that step's history
    if step_id:
        if step_id not in st.session_state.reasoning_history:
            st.session_state.reasoning_history[step_id] = []
        st.session_state.reasoning_history[step_id].append(log_entry)

# Update the show_agent_reasoning function to place it at the top with a collapsible style
def show_agent_reasoning():
    """Show the collected agent logs in a collapsible section"""
    if st.session_state.agent_logs:
        logs_html = "".join(st.session_state.agent_logs)
        
        # Create a collapsible section with HTML/JS
        st.markdown(f"""
        <div class="reasoning-container">
            <div class="reasoning-header" id="reasoning-header" onclick="toggleReasoning()">⊕ View agent reasoning</div>
            <div class="reasoning-content" id="reasoning-content">
                {logs_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

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
    
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .message-bot {
        background-color: #ffffff;  /* White background */
        color: #000000;  /* Black text */
        border: 1px solid #e1e1e1;  /* Light gray border for definition */
        border-radius: 15px 15px 15px 0;
        padding: 10px 15px;
        margin-right: 25%;
        margin-left: 0;
        position: relative;
        display: inline-block;
        max-width: 75%;
        align-self: flex-start;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .message-user {
        background-color: #2e6fdb;
        color: white;
        border-radius: 15px 15px 0 15px;
        padding: 10px 15px;
        margin-left: 25%;
        margin-right: 0;
        text-align: right;
        position: relative;
        display: inline-block;
        max-width: 75%;  /* Limit width */
        align-self: flex-end;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .message-wrapper-bot {
        display: flex;
        justify-content: flex-start;
        width: 100%;
    }
    
    .message-wrapper-user {
        display: flex;
        justify-content: flex-end;
        width: 100%;
    }
    
    .eva2-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0.05;
        width: 200px;
        z-index:s 0;
    }
    
    .agent-log {
        font-size: 0.8em;
        color: #555;
        background: #f5f5f5;
        padding: 4px 8px;
        margin: 3px 0;
        border-left: 3px solid #2e6fdb;
        border-radius: 0 4px 4px 0;
    }
    
    /* Image container styles */
    .screenshot-container {
        margin: 8px 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Reasoning section - updated styles */
    .reasoning-container {
        margin: 10px 0 20px 0;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    
    .reasoning-header {
        padding: 8px 15px;
        background-color: #f0f0f0;
        color: #666;
        font-size: 0.9em;
        border-bottom: 1px solid #e0e0e0;
        cursor: pointer;
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
    }
    
    .reasoning-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.2s ease-out;
    }
    
    .reasoning-content-active {
        max-height: 200px;
        padding: 10px;
        overflow-y: auto;
    }
    
    .agent-log {
        font-size: 0.8em;
        color: #777;
        background: #f5f5f5;
        padding: 3px 6px;
        margin: 2px 0;
        border-left: 2px solid #aaa;
        border-radius: 0 2px 2px 0;
    }
    </style>
    
    <script>
    function toggleReasoning() {
        const content = document.getElementById('reasoning-content');
        const header = document.getElementById('reasoning-header');
        
        if (content.className.includes('reasoning-content-active')) {
            content.className = 'reasoning-content';
            header.innerHTML = '⊕ View agent reasoning';
        } else {
            content.className = 'reasoning-content reasoning-content-active';
            header.innerHTML = '⊖ Hide agent reasoning';
        }
    }
    </script>
""", unsafe_allow_html=True)

# ------------------ MEMORY PAGE ------------------ #
if selected_page == "Memory":
    st.header("Memory Storage")
    
    # Create a predefined note about Eva startup
    if "notes" not in st.session_state:
        st.session_state.notes = [{
            "title": "Eva Startup",
            "date": "May 11, 2025",
            "type": "Hackathon",
            "priority": "High",
            "source": "Common Knowledge",
            "summary": "Startup information related to Eva assistant development",
            "details": "A startup where Asylbek asylbekbug@gmail.com works with Vasiliy klyosovv@gmail.com on a project to make a new OS-native approach to use notes."
        }]
    
    # Add a visual indicator if we have just one note - MOVED TO TOP
    if len(st.session_state.notes) == 1:
        st.info("1 memory found. Capture more screenshots in Chat to create additional notes.")
    
    # Display the notes
    for note in st.session_state.notes:
        with st.expander(f"{note['title']} ({note.get('priority', 'Medium')})"):
            st.markdown(f"""
            ### {note['title']}
            **Date Added:** {note['date']}  
            **Type:** {note.get('type', 'Note')}  
            **Source:** {note.get('source', 'Screenshot')}
            **Priority:** {note.get('priority', 'Medium')}
            
            **Summary:** {note.get('summary', '')}
            
            **Details:**
            {note.get('details', '')}
            """)

# ------------------ HEADER ------------------ #
if selected_page == "Chat":
    # Check ifs SVG files exist
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

    # Show agent reasoning logs at the top of the chat
    show_agent_reasoning()

    # ------------------ SESSION STATE ------------------ #
    if "messages" not in st.session_state:
        st.session_state.messages = []  # Start with empty messages instead of welcome message

    if "waiting_for_screenshot" not in st.session_state:
        st.session_state.waiting_for_screenshot = False

    if "last_screenshot_time" not in st.session_state:
        st.session_state.last_screenshot_time = 0

    if "analyzing_screenshot" not in st.session_state:
        st.session_state.analyzing_screenshot = False

    if "screenshot_to_analyze" not in st.session_state:
        st.session_state.screenshot_to_analyze = None

    # ------------------ WAIT FOR SCREENSHOTs ------------------ #
    # If we're in screenshot waiting mode, check for new screenshots
    if st.session_state.waiting_for_screenshot:
        # Create a progress indicator
        with st.spinner("Waiting for new screenshot..."):
            agent_log("ScreenCaptureAgent", "Monitoring desktop for new screenshots...")
            
            # Get the current latest screenshot and its time
            current_screenshot, current_time = get_latest_screenshot()
            
            # Hide debugging info - add to logs but don't display
            agent_log("ScreenCaptureAgent", f"Last known screenshot time: {st.session_state.last_screenshot_time}")
            agent_log("ScreenCaptureAgent", f"Current screenshot time: {current_time}")
            agent_log("ScreenCaptureAgent", f"Current screenshot path: {current_screenshot}")
            
            # Force a check for completely new screenshots
            all_screenshots = []
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            for pattern in [
                os.path.join(desktop_path, 'Screenshot*.png'),
                os.path.join(desktop_path, 'Screen Shot*.png'),
                os.path.join(desktop_path, 'screen*.png')
            ]:
                all_screenshots.extend(glob.glob(pattern))
            
            # If there are new screenshots taken after we started listening
            new_screenshots = [s for s in all_screenshots if os.path.getmtime(s) > st.session_state.last_screenshot_time + 1]
            
            if new_screenshots:
                # Get the newest one
                newest_screenshot = max(new_screenshots, key=os.path.getmtime)
                new_time = os.path.getmtime(newest_screenshot)
                
                # We found a newer screenshot!
                agent_log("ScreenCaptureAgent", f"New screenshot detected: {newest_screenshot}")
                st.session_state.waiting_for_screenshot = False
                
                # Set up for analysis
                st.session_state.analyzing_screenshot = True
                st.session_state.screenshot_to_analyze = newest_screenshot
                
                # Show loading message
                st.session_state.messages.append({
                    "role": "bot", 
                    "text": "I found your screenshot! Analyzing...",
                    "has_image": True,
                    "image_path": newest_screenshot,
                    "is_analyzing_message": True
                })
                
                # Update the last known time
                st.session_state.last_screenshot_time = new_time
                
                st.rerun()
            
            # Manually check again in a few seconds
            time.sleep(3)
            st.rerun()

    # If we're in analysis mode, perform the analysis
    elif st.session_state.analyzing_screenshot and st.session_state.screenshot_to_analyze:
        current_screenshot = st.session_state.screenshot_to_analyze
        
        # Analyze the screenshot
        with st.spinner("TextExtractionAgent processing image content..."):
            agent_log("TextExtractionAgent", "Extracting text from screenshot...")
            time.sleep(3.5)  # Increased from 2 to 3.5
            agent_log("TextExtractionAgent", "Text extraction complete")
            
            time.sleep(1)  # Add pause between agents
            
            agent_log("SummarizationAgent", "Generating content summary...")
            time.sleep(4)  # Increased from 2 to 4
            analysis = analyze_screenshot(current_screenshot)
            agent_log("SummarizationAgent", "Summary generation complete")
        
        # Create response message
        bot_reply = f"""I've analyzed your screenshot!<br><br>
        {analysis['summary']}<br><br>
        <b>📄 Summary saved to notes</b><br>
        Priority: <b>{analysis['priority']}</b>"""
        
        with st.spinner("NotePromptAgent saving extracted information..."):
            agent_log("NotePromptAgent", "Creating note from extracted content...")
            time.sleep(2.5)  # Increased from 1.5 to 2.5
            
            time.sleep(0.8)  # Add pause between agents
            
            agent_log("MemoryStorageAgent", "Storing note in long-term memory...")
            time.sleep(2)  # Increased from 1 to 2
            agent_log("MemoryStorageAgent", "Note stored successfully")
        
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
        agent_log("UIAgent", "Displaying calendar integration prompt...")
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

    # Start the chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Display messages using styled divs
    for msg in st.session_state.messages:
        if msg["role"] == "bot":
            st.markdown(f'<div class="message-wrapper-bot"><div class="message-bot">{msg["text"]}</div></div>', unsafe_allow_html=True)
            if msg.get("has_image") and "image_path" in msg:
                st.markdown('<div class="screenshot-container">', unsafe_allow_html=True)
                st.image(msg["image_path"], caption="Screenshot", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-wrapper-user"><div class="message-user">{msg["text"]}</div></div>', unsafe_allow_html=True)

    # Close the chat container
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------ FOLLOW UP QUESTIONS ------------------ #
    # Check if we need to automatically add a follow-up question
    for i, msg in enumerate(st.session_state.messages):
        # If calendar was just added in the previous message, ask about forwarding
        if msg.get("calendar_added") and i == len(st.session_state.messages) - 1:
            # Wait a little before asking follow-up
            time.sleep(4.5)  # Increased from 3 to 4.5
            
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
                            with st.spinner("QueryInterfaceAgent processing calendar request..."):
                                agent_log("QueryInterfaceAgent", "Processing calendar integration request...")
                                time.sleep(3)  # Increased from 2 to 3
                                
                                time.sleep(0.8)  # Add pause between agents
                                
                                agent_log("MemoryStorageAgent", "Retrieving event details from memory...")
                                time.sleep(2.5)  # Increased from 1.5 to 2.5
                                
                                time.sleep(0.8)  # Add pause between agents
                                
                                agent_log("QueryInterfaceAgent", "Creating calendar event...")
                                time.sleep(2.5)  # Increased from 1.5 to 2.5
                                
                                # Add a new memory about this event being connected to Eva startup
                                agent_log("MemoryStorageAgent", "Creating connection between event and Eva startup...")
                                time.sleep(1.5)
                                
                                # Add the new note to memory
                                new_startup_event = {
                                    "title": "Startup Pitch Event - Eva Team Attending",
                                    "date": "May 11, 2025",
                                    "type": "Event",
                                    "priority": "High",
                                    "source": "Calendar Integration",
                                    "summary": "Asylbek and Vasiliy are planning to attend the startup pitch event at TUM Venture Lab",
                                    "details": "Both Eva startup co-founders will be attending the pitch event at TUM Venture Lab on Thursday from 5:00 PM to 8:00 PM. This event is related to their work on developing an OS-native note-taking application."
                                }
                                
                                if "notes" not in st.session_state:
                                    st.session_state.notes = []
                                    
                                st.session_state.notes.append(new_startup_event)
                                agent_log("MemoryStorageAgent", "Successfully added event to long-term memory and connected to Eva startup context")
                            
                            event_details = "Time: 5:00 PM to 8:00 PM<br>Location: TUM Venture Lab"
                            bot_reply = f"Done!<br>{event_details}"
                            
                            st.session_state.messages.append({
                                "role": "bot", 
                                "text": bot_reply,
                                "has_image": False,
                                "calendar_added": True  # Mark that calendar was added
                            })
                            
                            st.rerun()
                            
                        # Handle forwarding email question
                        elif any("forward the email to anyone" in msg.get("text", "") for msg in st.session_state.messages[-3:]):
                            with st.spinner("SemanticRetrievalAgent searching contacts..."):
                                agent_log("SemanticRetrievalAgent", "Searching for relevant contacts...")
                                time.sleep(3.5)  # Increased from 2 to 3.5
                                agent_log("SemanticRetrievalAgent", "Found teammate: Vasiliy (klyosovv@gmail.com)")
                            
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
                                agent_log("RecallSummarizationAgent", "Retrieving email content from memory...")
                                time.sleep(2.5)  # Increased from 1.5 to 2.5
                                
                                time.sleep(0.8)  # Add pause between agents
                                
                                agent_log("QueryInterfaceAgent", "Preparing email draft...")
                                time.sleep(2)  # Increased from 1 to 2
                                
                                time.sleep(0.8)  # Add pause between agents
                                
                                agent_log("QueryInterfaceAgent", "Sending email to klyosovv@gmail.com...")
                                time.sleep(2.5)  # Increased from 1.5 to 2.5
                                
                                time.sleep(0.8)  # Add pause between agent completions
                                
                                agent_log("QueryInterfaceAgent", "Email sent successfully")
                            
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