# VoxAgent Architecture

## Goals

VoxAgent is a local-first voice agent that turns spoken instructions into safe local actions. The assignment required:

- microphone and audio-file input
- speech-to-text
- intent understanding through an LLM
- tool execution on the local machine
- a clean web UI
- strict safety around file writes

## Pipeline

1. Audio capture
   The Streamlit app accepts either:
   - direct microphone input via `st.audio_input`
   - uploaded audio files such as `.wav`, `.mp3`, `.m4a`, and `.ogg`

2. Temporary audio staging
   Incoming audio bytes are written to a temporary file before transcription. This keeps the STT layer model-agnostic and avoids coupling the UI to the transcriber.

3. Speech-to-text
   `voxagent/stt.py` uses `faster-whisper` locally. The default configuration is optimized for CPU usage:
   - model: `small.en`
   - device: `cpu`
   - compute type: `int8`

4. Intent planning
   `voxagent/llm.py` calls a local Ollama model and requests a strict JSON action plan. The planner can emit one or more actions, which allows compound command support.

5. Safe execution
   `voxagent/tools.py` handles:
   - file creation
   - folder creation
   - code generation into a file
   - summarization
   - general chat

   All file and folder operations are restricted to the repository's `output/` directory. Any path containing `..`, `/`, or `\` is rejected before execution.

6. UI rendering
   `voxagent/ui.py` displays:
   - transcribed text
   - detected intent(s)
   - planned actions
   - executed actions
   - final output
   - session notes
   - persistent history

## Fallback Strategy

If the local Ollama server is unavailable, VoxAgent falls back to a rule-based planner. This keeps the UI usable and demonstrates graceful degradation, one of the assignment bonus items.

The fallback planner covers:

- create file
- create folder
- write Python code
- summarize text
- general chat

## Memory

Each interaction is appended to `history/session_history.json`. The Streamlit sidebar reads and displays recent items, which provides lightweight session memory and makes the workflow easier to demo.

## Why This Structure

The project is split into small modules so each concern can evolve independently:

- `config.py`: environment-driven configuration
- `stt.py`: transcription
- `llm.py`: planner and language generation
- `fallback.py`: non-LLM routing fallback
- `tools.py`: local action execution
- `memory.py`: session persistence
- `ui.py`: presentation layer
- `agent.py`: orchestration
