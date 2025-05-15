# EVA – Your Memory Assistant

## Problem Statement & Use Case

Modern PC users are overwhelmed by information scattered across apps, browsers, and documents. Important details are easily forgotten or lost in context switches. Traditional note-taking is manual and disruptive, leading to incomplete knowledge capture and poor recall.

**Who is EVA for?**  
Everyday computer users and knowledge workers who want to revolutionize their memory and recall. EVA optimizes the workflow of capturing, organizing, and retrieving information from anywhere on your desktop, making your digital memory searchable and actionable.

## Solution Approach

EVA is a multi-agent system that automates the capture, extraction, and organization of information from your screen and conversations.

### Main Components

- **ScreenCaptureAgent**: Captures screenshots and context from your desktop.
- **TextExtractionAgent**: Extracts text from images using OCR.
- **SummarizationAgent**: Summarizes and prioritizes extracted content.
- **MemoryStorageAgent**: Stores notes, memos, and tasks with metadata.
- **RecallSummarizationAgent**: Retrieves and summarizes relevant memories on demand.
- **QueryInterfaceAgent**: Handles calendar and email integration.
- **TaskManagerAgent**: Manages TODOs with prioritization.

### Flow Overview

1. **Capture**: User triggers a capture (e.g., "Eva, Snap") or asks a question.
2. **Extraction**: Text and context are extracted from the screenshot or query.
3. **Summarization**: Content is summarized and prioritized.
4. **Storage**: Notes and tasks are stored in a structured memory.
5. **Recall**: User can query EVA in natural language to retrieve or act on memories.
6. **Integration**: EVA can add events to your calendar, forward emails, or create TODOs.

### Frameworks & Models

- **Python** & **Streamlit** for the frontend and UI
- **OpenAI GPT-4o** for language understanding and summarization
- **PIL/PyTesseract** for image and OCR processing
- **BeautifulSoup** for web content parsing
- **Session state** for in-memory data management

### Clever Hacks & Challenges

- Seamless screenshot and context capture on macOS
- Automatic prioritization and categorization of notes
- Conversational recall with context-aware suggestions (e.g., TODOs before meetings)
- Collapsible agent reasoning logs for transparency

## Agent Capabilities & Limitations

**Capabilities:**
- Screenshot capture and text extraction from any app
- Natural language memory search and recall
- Calendar and email integration
- TODO list with prioritization
- Conversational interface with context-aware suggestions

**Limitations:**
- Full functionality currently macOS only
- English language optimized
- Requires OpenAI API key
- Not integrated with all third-party apps (e.g., Outlook, Notion)

## Setup Instructions

**Prerequisites:**
- Python 3.9+
- macOS (for screenshot features)
- OpenAI API key

**Installation:**
1. Clone the repo:
    ```bash
    git clone https://github.com/Larsters/GDG-AI-hack-SamuarAI.git
    cd GDG-AI-hack-SamuarAI
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Add your Model API key to a `.env` file:

4. (macOS) Install Tesseract for OCR:
    ```bash
    brew install tesseract
    ```
5. Run the app:
    ```bash
    cd frontend
    streamlit run app.py
    ```

## Future Improvements

- Windows/Linux support
- Mobile companion apps
- Real-time meeting transcription
- Integration with more productivity tools (Notion, Slack, Jira)
- Local/offline LLM support
- Multi-user collaboration

---

EVA is your next-generation memory assistant, making your digital life searchable, actionable, and truly memorable.