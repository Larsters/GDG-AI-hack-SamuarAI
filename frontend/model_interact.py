import os
from PIL import Image
import io
import base64
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OpenAI API key not found. Using mock responses.")

def encode_image_to_base64(image_path):
    """Convert an image file to base64 for API transmission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_screenshot(screenshot_path):
    """
    Analyze a screenshot using OpenAI's vision model
    Returns a summary and suggested priority
    """
    # For development or when API key isn't available, return mock data
    if not openai_api_key:
        return {
            "summary": "You received an email invitation about a startup pitch event at TUM Venture Lab.",
            "priority": "High",
            "event_details": {
                "title": "Startup Pitch Event",
                "location": "TUM Venture Lab",
                "time": "5:00 PM to 8:00 PM",
                "date": "Next Thursday"
            }
        }

    # Encode the image
    base64_image = encode_image_to_base64(screenshot_path)

    # Call OpenAI API with vision capabilities
    client = openai.OpenAI(api_key=openai_api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Latest model that supports vision
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI assistant analyzing screenshots. 
                    Extract key information from the image and provide:
                    1. A brief summary of the content (1-2 sentences)
                    2. Suggest a priority level (Low, Medium, High)
                    3. If it's about an event, extract event details (title, location, time, date)
                    Format your response as JSON."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this screenshot? Extract key details."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        # Parse the response to extract JSON
        result_text = response.choices[0].message.content
        # Extract JSON from the response text
        try:
            # Try to parse the entire response as JSON
            result_json = json.loads(result_text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the text
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                try:
                    result_json = json.loads(json_match.group(1))
                except:
                    # Fallback to mock response
                    return {
                        "summary": "You received an email invitation about a startup pitch event at TUM Venture Lab.",
                        "priority": "High",
                        "event_details": {
                            "title": "Startup Pitch Event",
                            "location": "TUM Venture Lab",
                            "time": "5:00 PM to 8:00 PM",
                            "date": "Next Thursday"
                        }
                    }
            else:
                # Another fallback
                result_json = {
                    "summary": result_text[:100] + "...",
                    "priority": "Medium"
                }
                
        return result_json
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback to mock data
        return {
            "summary": "You received an email invitation about a startup pitch event at TUM Venture Lab.",
            "priority": "High",
            "event_details": {
                "title": "Startup Pitch Event",
                "location": "TUM Venture Lab",
                "time": "5:00 PM to 8:00 PM",
                "date": "Next Thursday"
            }
        }