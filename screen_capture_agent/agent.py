import re
from google.adk.agents import Agent
import pyautogui
import datetime
import os
import json
import subprocess
from bs4 import BeautifulSoup
import requests
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None

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
        # Remove the incorrect "extracted_text": extract_text line
    }

    # First save the metadata without extracted text
    json_path = os.path.join(output_dir, f"meta_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(note, f, indent=2)
    
    # Now extract text and update the JSON
    try:
        extracted_text = extract_text(note)  # Pass the note directly
        # Update the note with extracted text
        note["extracted_text"] = extracted_text
        
        # Update the JSON file with extracted text
        with open(json_path, "w") as f:
            json.dump(note, f, indent=2)
    except Exception as e:
        print(f"Error extracting text: {e}")

    print(f"Captured to {filepath}")
    return note

def extract_text(note_json: str) -> str:
    """
    Extract meaningful context and text from a screenshot or webpage.
    - For screenshots: Uses OCR to extract text and then summarizes the content
    - For webpages: Extracts main content, title, and other relevant information
    Returns a structured description of the content.
    """
    # Parse the JSON string into a dictionary
    note = json.loads(note_json) if isinstance(note_json, str) else note_json
    
    extracted_content = {
        "raw_text": "",
        "title": "",
        "main_content": "",
        "context": "",
        "type": note.get("type", "")
    }
    
    # Get URL if available
    url = ""
    parts = note.get("source", "").split("–", 1)
    if len(parts) == 2:
        url = parts[1].strip()
    
    # Try to get context from URL first (usually cleaner than OCR)
    if url.startswith("http"):
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Get title
            title_tag = soup.find("title")
            if title_tag:
                extracted_content["title"] = title_tag.get_text().strip()
            
            # Get main content - paragraphs
            main_content = []
            paragraphs = soup.find_all("p")
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 40:  # Only include substantial paragraphs
                    main_content.append(text)
            
            if main_content:
                extracted_content["main_content"] = "\n\n".join(main_content[:5])  # First 5 paragraphs
            
            # Get meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                extracted_content["context"] = meta_desc.get("content", "")
            
            # Raw text is everything combined
            extracted_content["raw_text"] = "\n".join(p.get_text().strip() for p in paragraphs)
            
        except Exception as e:
            print(f"Error fetching URL content: {e}")
    
    # If no good context from URL or no URL, use OCR
    if not extracted_content["main_content"] and note.get("type") == "screenshot" and pytesseract:
        try:
            img = Image.open(note["content"])
            raw_text = pytesseract.image_to_string(img)
            extracted_content["raw_text"] = raw_text
            
            # Try to identify content elements from OCR text
            lines = raw_text.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            # Heuristic: First long line might be a title
            for line in non_empty_lines:
                if len(line) > 20 and len(line) < 100:
                    extracted_content["title"] = line
                    break
            
            # Look for specific patterns like code, file paths, etc.
            code_pattern = re.compile(r'(def |class |import |from .+ import)')
            filepath_pattern = re.compile(r'(/[a-zA-Z0-9_.-]+)+\.[a-z]+')
            
            code_lines = []
            for line in non_empty_lines:
                if code_pattern.search(line):
                    code_lines.append(line)
                
                filepath_match = filepath_pattern.search(line)
                if filepath_match and "filepath" not in extracted_content:
                    extracted_content["filepath"] = filepath_match.group(0)
            
            if code_lines:
                extracted_content["code_snippets"] = "\n".join(code_lines)
            
            # Try to create a summary context about what's in the image
            content_types = []
            if "code_snippets" in extracted_content:
                content_types.append("code")
            if "filepath" in extracted_content:
                content_types.append("file paths")
            if len(non_empty_lines) > 20:
                content_types.append("text content")
            
            context = f"Screenshot contains {', '.join(content_types)}"
            if app_name := note.get("source", "").split("–")[0].strip():
                context = f"Screenshot of {app_name} showing {context}"
                
            extracted_content["context"] = context
                
        except Exception as e:
            print(f"OCR error: {e}")
    
    # Create a formatted summary
    summary = ""
    if extracted_content["title"]:
        summary += f"Title: {extracted_content['title']}\n\n"
    
    if extracted_content["context"]:
        summary += f"Context: {extracted_content['context']}\n\n"
        
    if "filepath" in extracted_content:
        summary += f"File: {extracted_content['filepath']}\n\n"
        
    if extracted_content["main_content"]:
        summary += "Content Summary:\n" + extracted_content["main_content"][:500] + "...\n"
    elif "code_snippets" in extracted_content:
        summary += "Code Snippets:\n" + extracted_content["code_snippets"] + "\n"
    
    # If we couldn't generate a good summary, use the raw text
    if not summary:
        # Take the first 500 chars of raw text as fallback
        summary = extracted_content["raw_text"][:500] + "..."
    
    # Save all extracted content back to the JSON file
    if "content" in note and os.path.exists(note["content"]):
        # Construct the JSON file path from the screenshot path
        json_path = os.path.splitext(note["content"])[0] + ".json"
        if os.path.exists(json_path):
            try:
                # Read the existing JSON
                with open(json_path, "r") as f:
                    json_data = json.load(f)
                
                # Update with extracted text and context
                json_data["extracted_text"] = extracted_content["raw_text"]
                json_data["context"] = summary
                json_data["extracted_content"] = extracted_content
                
                # Write back to file
                with open(json_path, "w") as f:
                    json.dump(json_data, f, indent=2)
                
                print(f"Updated {json_path} with extracted context")
            except Exception as e:
                print(f"Error updating JSON with extracted text: {e}")
    
    return summary

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant that captures screenshots and saves them as notes and extracts text from them',
    instruction="""I can help you capture screenshots and extract information from them.
        When asked to capture a screenshot, I'll save it and extract any text or context automatically.
        Use 'capture_screen' to take a screenshot.
        Use 'extract_text' to extract text from an existing screenshot.""",    
    tools=[capture_screen, extract_text],
)