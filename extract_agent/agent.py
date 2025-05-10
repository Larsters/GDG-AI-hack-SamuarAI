from google.adk.agents import Agent
import requests
import json
import os
from bs4 import BeautifulSoup
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None

def extract_text(note_json: str) -> str:
    """
    TextExtractionAgent: Extract text from a JSON note string.
    Returns the extracted text and updates the original JSON with the result.
    """
    # Parse the JSON string into a dictionary
    note = json.loads(note_json) if isinstance(note_json, str) else note_json
    
    text = ""
    url = ""
    parts = note.get("source", "").split("–", 1)
    if len(parts) == 2:
        url = parts[1].strip()
    
    if url.startswith("http"):
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text().strip() for p in paragraphs)
        except Exception as e:
            print(f"Error fetching URL content: {e}")
    
    if not text and note.get("type") == "screenshot" and pytesseract:
        try:
            img = Image.open(note["content"])
            text = pytesseract.image_to_string(img)
        except Exception as e:
            print(f"OCR error: {e}")
    
    # Save the extracted text back to the JSON file
    if "content" in note and os.path.exists(note["content"]):
        # Construct the JSON file path from the screenshot path
        json_path = os.path.splitext(note["content"])[0] + ".json"
        if os.path.exists(json_path):
            try:
                # Read the existing JSON
                with open(json_path, "r") as f:
                    json_data = json.load(f)
                
                # Update with extracted text
                json_data["extracted_text"] = text
                
                # Write back to file
                with open(json_path, "w") as f:
                    json.dump(json_data, f, indent=2)
                
                print(f"Updated {json_path} with extracted text")
            except Exception as e:
                print(f"Error updating JSON with extracted text: {e}")
    
    return text

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant that extracts text from screenshots and URLs',
    instruction='Extract relevant text from the given note',
    tools=[extract_text],
)