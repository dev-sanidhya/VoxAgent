# Title

Building VoxAgent: A Local Voice-Controlled AI Agent with Whisper, Ollama, and Safe File Actions

# Suggested Tags

`ai`, `machinelearning`, `python`, `streamlit`

# Body

If you ask most AI demos to do something useful, they usually stop right before the interesting part.

They can transcribe your speech, explain what they think you meant, and generate a polished response. But they often do not cross the line into safe, visible action on a real machine.

For my Mem0 AI/ML & Generative AI Developer Intern assignment, I wanted to build something more practical: a local-first voice-controlled AI agent that could listen to spoken commands, understand user intent, execute local tools, and expose the whole pipeline in a simple UI.

That project became **VoxAgent**.

## What VoxAgent Does

VoxAgent is a local-first AI agent that supports:

- microphone input
- uploaded audio files
- local speech-to-text
- local intent understanding
- safe file and folder creation
- code generation into files
- text summarization
- general chat
- a UI that shows the full pipeline from audio to action

The key requirement was not just to generate responses, but to actually perform useful tasks while staying within safe local boundaries.

## The Core Idea

The architecture is simple:

1. Accept voice input
2. Convert speech to text
3. Classify the user’s intent
4. Route the request to a local tool
5. Show the transcript, decision, and final output in the UI

That sounds straightforward, but the interesting engineering work was in making the system:

- local-first
- safe by default
- resilient when local models are slow or unavailable

## Tech Stack

I used the following stack:

- **Streamlit** for the frontend
- **faster-whisper** for local speech-to-text
- **Ollama** for local intent routing and generation
- **Python** for orchestration and tool execution

This gave me a stack that was practical to run on a normal laptop without turning the project into a hosted API workflow.

## System Architecture

VoxAgent is split into five layers.

### 1. Audio ingestion

The Streamlit UI accepts audio in two ways:

- direct microphone recording
- uploaded `.wav`, `.mp3`, `.m4a`, or `.ogg` files

This made the app easier to demo and easier to test. If browser microphone behavior is inconsistent, uploaded audio still works.

### 2. Local speech-to-text

For transcription, I used **faster-whisper** with CPU-friendly defaults:

- model: `base.en`
- device: `cpu`
- compute type: `int8`

I initially considered using a larger Whisper setup, but in practice local responsiveness matters more than chasing the largest possible model.

### 3. Intent planning with Ollama

Once the transcript is available, it is sent to a local Ollama model. Instead of asking for a free-form answer, I ask the model for a **strict JSON action plan**.

That plan includes:

- intent
- file or folder target if needed
- code generation instruction if needed
- text to summarize if needed
- whether confirmation should be required

This structure makes the agent much easier to reason about than a plain-text routing step.

### 4. Tool execution

The agent supports four main intents:

- `create_file`
- `write_code`
- `summarize_text`
- `general_chat`

These actions are executed through a local tool layer, not directly through the UI.

### 5. UI and memory

The interface shows:

- transcribed text
- detected intents
- planned actions
- final results
- execution notes
- backend information
- timing information

The app also stores lightweight session history in JSON so recent interactions remain visible.

## Safety Constraints

This part mattered a lot.

Once an AI agent can write files locally, the execution boundary has to be extremely clear. I added three explicit safeguards:

### 1. All writes are restricted to `output/`

The agent cannot create files outside the repository’s `output/` folder.

### 2. Path traversal is blocked

Any path containing `..`, `/`, or `\` is rejected before execution.

### 3. File actions require confirmation

The UI includes a human-in-the-loop approval checkbox before file creation or code writing happens.

That kept the project aligned with the assignment and prevented the most obvious local-risk failure modes.

## What Broke During Real Testing

The first version worked in structure, but real end-to-end testing exposed some weaknesses.

### Problem 1: Fallback logic was incomplete

At first, I had a rule-based fallback for intent planning if Ollama was unavailable. But some execution paths still depended on the local LLM later in the pipeline.

That meant the app could recover during planning and still fail during summarization or code generation.

I fixed this by adding a **local fallback responder**:

- summarization can fall back locally
- chat can fall back locally
- code generation can fall back to a safe template

This made degraded execution much more predictable.

### Problem 2: Planning latency was too high

In local testing, planning timeouts could make the app feel frozen even when a fallback path was available.

I improved this by separating:

- planner timeout
- generation timeout

The shorter planning timeout lets the UI fall back faster if the local model stalls, while generation still gets its own bounded budget.

## Demo Flows I Verified

I verified the app with actual local audio runs, not just unit tests.

### Demo 1: Summarization

Voice input:

> Summarize this text. Local AI agents combine speech recognition, reasoning, and tool execution to automate tasks.

Observed behavior:

- transcript recognized correctly
- intent detected as `summarize_text`
- planner fell back after timeout
- summarization still completed successfully

Final summary:

> Local AI agents use speech recognition, reasoning, and tool execution to automate tasks.

### Demo 2: Code generation

Voice input:

> Create a Python file named retry helper dot py with a retry function.

Observed behavior:

- transcript normalized to `retryhelper.py`
- intents detected as `create_file` and `write_code`
- file created safely inside `output/`
- fallback code generation completed successfully

Generated output:

```python
"""Generated in fallback mode because the local LLM was unavailable."""

import time


def retry(operation, attempts=3, delay_seconds=1):
    last_error = None
    for _ in range(attempts):
        try:
            return operation()
        except Exception as error:
            last_error = error
            time.sleep(delay_seconds)
    raise last_error
```

## Challenges I Faced

### Running everything locally without making it painful

Local AI systems sound attractive, but latency and hardware limits show up immediately. The practical solution was to tune for reliability:

- smaller Whisper model
- CPU-friendly quantization
- bounded timeouts
- local fallback behavior

### Keeping flexibility without sacrificing safety

Natural language is flexible. File system actions are not.

So the architecture separates:

- transcript and interpretation
- validated action planning
- constrained execution

That separation kept the agent much easier to trust.

### Making the system observable

I did not want the UI to behave like a black box. Showing the transcript, action plan, notes, backend used, and timing information made debugging much easier and also made the demo much stronger.

## What I Would Improve Next

If I continue iterating on VoxAgent, the next improvements would be:

- richer extraction of filenames and structured parameters
- compound actions like “summarize this and save it to summary.txt”
- stronger local templates for multiple programming languages
- benchmarking different Whisper and Ollama combinations
- better multi-step approval flows before execution

## Final Takeaway

The most useful lesson from this project was that a strong local AI agent is not just a model wrapped in a UI.

It is a pipeline with:

- explicit safety boundaries
- predictable fallbacks
- observable execution
- practical local defaults

That is what I tried to build with VoxAgent.

If you want to check out the code, the repository is here:

[https://github.com/dev-sanidhya/VoxAgent](https://github.com/dev-sanidhya/VoxAgent)
