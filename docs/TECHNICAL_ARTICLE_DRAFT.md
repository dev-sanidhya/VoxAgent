# Building VoxAgent: A Local Voice-Controlled AI Agent

## Problem

I wanted to build a local-first AI agent that could listen to speech, understand user intent, execute local tools safely, and make the whole process visible through a simple interface.

## System Design

The system has five layers:

1. Audio ingestion through Streamlit
2. Local transcription using `faster-whisper`
3. Intent planning using a local Ollama-hosted LLM
4. Safe tool execution in a sandboxed repository folder
5. A UI that exposes the transcript, decisions, and outputs

## Why I Chose These Models and Tools

### Speech-to-text

I used `faster-whisper` because it offers practical local inference with good accuracy and CPU-friendly quantized execution. For an assignment project, this keeps setup realistic while still staying local-first.

### Intent understanding

I used Ollama with `llama3.1:8b` as the default reasoning backend. The model receives the transcript and returns a strict JSON action plan. This makes downstream execution predictable and easier to render in the UI.

### UI

Streamlit made it easy to build a compact interface that exposes the entire agent pipeline, not just the final answer.

## Safety Constraints

One important requirement was preventing accidental writes to the host machine. To handle that cleanly:

- every generated file is restricted to `output/`
- path traversal and nested paths are rejected
- file operations require explicit approval in the UI

## Bonus Features

I also implemented a few bonus-oriented behaviors:

- compound command planning
- graceful degradation when Ollama is unavailable
- lightweight session memory stored in JSON
- a human-in-the-loop approval step before file creation

## Challenges

### 1. Keeping the local stack practical

Running STT and an LLM locally can be heavy on some laptops. I handled this by defaulting to CPU-friendly settings for Whisper and separating the planning layer cleanly so fallbacks were possible.

### 2. Balancing flexibility with safety

Voice commands are naturally ambiguous, but file operations need strict boundaries. The solution was to allow free-form transcription and planning, then force execution through constrained local tools.

### 3. Demo reliability

Live demos fail when backend services are unavailable. To make the app resilient, I added a rule-based fallback planner so the interface remains usable even if Ollama is down.

## What I Would Improve Next

- add richer structured extraction for filenames and code targets
- support saving summaries directly into files as compound actions
- benchmark different Whisper and Ollama model sizes
- add more granular action previews before execution

## Conclusion

VoxAgent shows that a useful local AI agent can be built with a relatively small stack when the pipeline is explicit: speech in, transcript, intent plan, safe execution, visible output.
