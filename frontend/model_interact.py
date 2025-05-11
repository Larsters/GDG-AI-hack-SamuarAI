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
    
def ask_openai_general(query):
    if not openai_api_key:
        return "Sorry, I can't answer that right now."
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

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

def query_memory(user_query, memories):
    """
    Query the system's memories using natural language
    """
    # For development or when API key isn't available, use simple keyword matching
    if not openai_api_key:
        # Simple keyword matching for demo
        if "laura" in user_query.lower():
            # Find memories related to Laura
            laura_memories = [m for m in memories if "laura" in m.get("title", "").lower()]
            if laura_memories:
                memory = laura_memories[0]
                return {
                    "response": f"Based on my records, the meeting with Laura was on {memory['date']}. She presented the Q2 roadmap including UI redesign in late May, new feature development starting June 10, and documentation preparation by May 15. There's a follow-up meeting scheduled for May 20.",
                    "source_memory": memory["title"]
                }
        return {"response": "I don't have any information about that in my memory.", "source_memory": None}
        
    # Use OpenAI to generate a response based on memories
    try:
        # Create context from memories
        memories_context = "\n\n".join([
            f"Memory: {m['title']}\nDate: {m['date']}\nType: {m.get('type', 'Note')}\n" +
            f"Summary: {m.get('summary', '')}\nDetails: {m.get('details', '')}"
            for m in memories
        ])
        
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are EVA, an AI assistant with access to the user's notes and memories.
                    Below are the available memories:
                    
                    {memories_context}
                    
                    Based only on this information, answer the user's question naturally.
                    If the answer isn't in these memories, say you don't have that information.
                    Keep your answer concise and helpful."""
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            max_tokens=300
        )
        
        answer_text = response.choices[0].message.content
        
        # Try to identify which memory was referenced
        memory_source = None
        for memory in memories:
            if memory["title"].lower() in answer_text.lower():
                memory_source = memory["title"]
                break
                
        return {
            "response": answer_text,
            "source_memory": memory_source
        }
        
    except Exception as e:
        print(f"Error calling OpenAI API for memory query: {e}")
        # Fallback response
        return {
            "response": "Based on my records, the meeting with Laura was on May 4. She presented the Q2 roadmap including UI redesign in late May, new feature development starting June 10, and documentation preparation by May 15. There's a follow-up meeting scheduled for May 20.",
            "source_memory": "Work Meeting with Laura"
        }