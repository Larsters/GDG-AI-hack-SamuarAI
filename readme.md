### GDG AI Hackathon 2025

SmartNotes

### Demo of the Project
[![Watch the demo on YouTube](https://img.youtube.com/vi/Up4IqVnsPQA/0.jpg)](https://youtu.be/Up4IqVnsPQA)

1. Listener
- Hotkey -> bg service listens for the vc 
2. Context capture 
- Grabbing active window (url, text buffer, screenshot)
- Browser reads DOM + address bar; OCR + window title; meeting- hook into zoom/teams api for a 5 min transcript grab
3. Memory dump 
- Packages captured content into a memory record

```json{
  "timestamp": "...",
  "source": "Chrome – https://…",
  "type": "webpage",
  "content": "<article text or screenshot>",
  "tags": []
}
```
- Appends to local notes DB (sqlite + embeddings)
4. On-demand recall
- On the hotkey, what was the approach I saw on website X?
    - Search note embeddings for website X + approach
    - Pull matching records
    - Summarize via LLM
    - Display the summary
