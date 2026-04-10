# VoxAgent

VoxAgent is a local-first voice-controlled AI agent built for the Mem0 AI/ML & Generative AI Developer Intern assignment. It accepts spoken instructions, transcribes them locally, classifies intent, executes safe local tools, and shows the full pipeline in a Streamlit UI.

## Assignment Coverage

This project satisfies the requested system requirements:

- direct microphone input
- uploaded audio file input
- local speech-to-text with Hugging Face compatible Whisper-family inference through `faster-whisper`
- LLM-driven intent understanding through a local Ollama model
- local tool execution for:
  - file creation
  - code writing
  - text summarization
  - general chat
- a UI that shows:
  - transcribed text
  - detected intent
  - system action
  - final output

It also includes several bonus-oriented behaviors:

- compound command planning
- human-in-the-loop confirmation before file operations
- graceful degradation when Ollama is unavailable
- lightweight session memory
- lightweight model benchmarking

## Tech Stack

- Streamlit for the UI
- `faster-whisper` for local speech-to-text
- Ollama for local intent routing and generation
- Python for orchestration and tool execution

## Repository Structure

```text
.
|-- app.py
|-- voxagent/
|   |-- agent.py
|   |-- config.py
|   |-- fallback.py
|   |-- llm.py
|   |-- memory.py
|   |-- models.py
|   |-- stt.py
|   |-- tools.py
|   `-- ui.py
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- DEMO_VERIFICATION.md
|   |-- DEMO_SCRIPT.md
|   |-- MODEL_BENCHMARKS.md
|   |-- SETUP.md
|   `-- TECHNICAL_ARTICLE_DRAFT.md
|-- history/
|-- output/
`-- tests/
```

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install and start Ollama

Pull a local model:

```powershell
ollama pull llama3.1:8b
```

Make sure Ollama is running locally on `http://localhost:11434`.

### 4. Configure environment variables

Copy `.env.example` into `.env` and adjust values if needed.

### 5. Run the app

```powershell
streamlit run app.py
```

## How It Works

1. The user records audio or uploads a file.
2. The app stores the audio temporarily and transcribes it using `faster-whisper`.
3. The transcript is sent to a local Ollama model to produce a structured action plan.
4. The agent executes the actions safely inside `output/`.
5. The UI displays the transcript, intents, actions, outputs, and notes.
6. The interaction is saved into `history/session_history.json`.

## Safety Design

- All file and folder writes are restricted to `output/`.
- Any path containing traversal or nested path tokens is rejected.
- File operations require an explicit confirmation checkbox in the UI.

## Supported Voice Commands

- "Create a Python file named retry_helper.py with a retry decorator."
- "Summarize this text: Transformers are useful for speech and language tasks."
- "Create a folder named meeting_notes."
- "What can this app do?"

## Tests

Run the regression suite with:

```powershell
pytest -q
```

## Documentation

- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Setup notes: [docs/SETUP.md](docs/SETUP.md)
- Demo script: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
- Demo verification: [docs/DEMO_VERIFICATION.md](docs/DEMO_VERIFICATION.md)
- Model benchmarks: [docs/MODEL_BENCHMARKS.md](docs/MODEL_BENCHMARKS.md)
- Technical article draft: [docs/TECHNICAL_ARTICLE_DRAFT.md](docs/TECHNICAL_ARTICLE_DRAFT.md)

## Hardware and Runtime Notes

- The default STT configuration is optimized for CPU usage.
- If the Whisper model is too slow on your hardware, switch to a smaller model such as `base.en`.
- If compressed uploaded audio formats fail on your machine, install ffmpeg locally.
- Intent planning uses a shorter timeout than long-form generation so the UI can fall back faster if Ollama stalls.
- Long-form generation also uses a bounded timeout so code or summary requests do not block the UI indefinitely.
- This implementation stays local-first. No API-based STT workaround was required in the repository version.

## Deliverables Status

- Public GitHub repository: covered by this repo
- Video demo: use `docs/DEMO_SCRIPT.md` as a recording guide
- Technical article: use `docs/TECHNICAL_ARTICLE_DRAFT.md` as the publish-ready base

## Submission Link

Official submission form:

[https://forms.gle/5x32P7zr4NvyRgK6A](https://forms.gle/5x32P7zr4NvyRgK6A)
