from google.adk.agents import Agent
import pyautogui
import datetime
import os
import json

app_root = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(app_root, "..", "screenshots")
output_dir = os.path.abspath(output_dir)
os.makedirs(output_dir, exist_ok=True)

def capture_screen():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(output_dir, f"screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

    note = {
        "timestamp": timestamp,
        "source": "Unknown", 
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