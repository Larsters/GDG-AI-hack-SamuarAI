from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import InMemoryRunner as Runner

from screen_capture_agent.agent import capture_screen  # returns a note dict
from extract_agent.agent import extract_text       # consumes a note dict

capture_agent = Agent(
    model='gemini-2.0-flash-001',
    name="screen_capture_agent",
    description="Takes a screenshot and returns a note dict",
    instruction="Take a screenshot and save it as a note",
    tools=[capture_screen]
)

extract_agent = Agent(
    model='gemini-2.0-flash-001',
    name="text_extraction_agent",
    description="Receives a note dict and returns its extracted text",
    instruction="Extract text from the given note",
    tools=[extract_text]
)

# Create a sequential agent to run capture then extract
master_agent = SequentialAgent(
    name="master_agent",
    description="Orchestrates screen capture then text extraction",
    sub_agents=[capture_agent, extract_agent]
)

# Set up runtime
runtime = Runner(master_agent)

def run_master_pipeline():
    """
    Uses the sequential agent to chain:
      1) capture_screen → note
      2) extract_text(note) → text
    Returns the fully enriched note.
    """
    from google.genai import types
    user_message = types.Content(
        parts=[types.Part(text="Please capture the screen and extract the text")]
    )
    
    # Run using the InMemoryRunner
    response = None
    for event in runtime.run(
        user_id="user", 
        session_id="default_session", 
        new_message=user_message
    ):
        response = event
    
    if response and hasattr(response, "content"):
        return response.content
    return response

root_agent = master_agent