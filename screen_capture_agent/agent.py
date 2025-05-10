from google.adk.agents import Agent
import pyautogui
import datetime
import os
import json
import subprocess

def get_active_url_and_app():
    app_name = "Unknown"
    url = ""
    
    # Currently using AppleScript to get the active app name
    try:
        cmd = """
        osascript -e 'tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell'
        """
        app_name = subprocess.check_output(cmd, shell=True).decode().strip()
    except Exception as e:
        print(f"Error getting active app: {e}")
    
    # Now try to get URL from common browsers (mine is Arc)
    if app_name in ["Safari", "Google Chrome", "Firefox", "Arc"]:
        try:
            if app_name == "Safari":
                cmd = """
                osascript -e 'tell application "Safari" to return URL of current tab of front window'
                """
            elif app_name == "Google Chrome":
                cmd = """
                osascript -e 'tell application "Google Chrome" to return URL of active tab of front window'
                """
            elif app_name == "Firefox":
                cmd = """
                osascript -e 'tell application "Firefox" to return URL of active tab of front window'
                """
            elif app_name == "Arc":
                cmd = """
                osascript -e 'tell application "Arc" to return URL of active tab of front window'
                """
            
            url = subprocess.check_output(cmd, shell=True).decode().strip()
        except Exception as e:
            print(f"Error getting URL from {app_name}: {e}")
    
    return app_name, url

app_root = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(app_root, "..", "screenshots")
output_dir = os.path.abspath(output_dir)
os.makedirs(output_dir, exist_ok=True)

def capture_screen():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    app_name, url = get_active_url_and_app()
    filepath = os.path.join(output_dir, f"screenshot_{timestamp}.png")
    
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None 

    source_value = f"{app_name}"
    if url:
        source_value += f" – {url}"
    
    note = {
        "timestamp": timestamp,
        "source": source_value,
        "type": "screenshot",
        "content": filepath,
        "tags": []
    }

    json_path = os.path.join(output_dir, f"meta_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(note, f, indent=2)

    print(f"Captured to {filepath}")
    return note

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant that captures screenshots and saves them as notes',
    instruction='Capture a screenshot and save it as a note',
    tools=[capture_screen],
)