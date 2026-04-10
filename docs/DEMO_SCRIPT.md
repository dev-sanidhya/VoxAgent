# Demo Script

This script is designed to help record the required 2 to 3 minute video demo quickly.

## Suggested structure

### 1. Intro

- Open the Streamlit UI.
- State that the app accepts microphone input and uploaded audio files.
- Point out that all file actions are restricted to `output/`.

### 2. Intent demo 1: Write code

Use a voice command like:

> Create a Python file named retry_helper.py with a retry function.

What to show:

- uploaded or recorded audio
- transcribed text
- detected intent
- action plan
- file execution result
- generated file inside `output/`

### 3. Intent demo 2: Summarize text

Use a voice command like:

> Summarize this text: Local AI agents combine speech recognition, reasoning, and tool execution to automate tasks.

What to show:

- transcript
- summarize intent
- final summarized output

### 4. Bonus demo

Use a command like:

> Create a folder named notes.

Then show the approval checkbox and explain the human-in-the-loop safety step.

### 5. Outro

- mention that STT runs locally using `faster-whisper`
- mention that intent routing uses Ollama
- mention fallback behavior when Ollama is unavailable
