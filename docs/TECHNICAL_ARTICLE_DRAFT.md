# Building VoxAgent: A Local Voice-Controlled AI Agent That Can Actually Do Things

If you ask most AI demos to do something useful, they stop right at the answer.

They will transcribe your speech, summarize your request, maybe even explain what they would do next, but they rarely cross the line into safe, observable action on a real machine.

For my Mem0 AI/ML & Generative AI Developer Intern assignment, I wanted to build something more practical: a local-first voice agent that could listen to spoken commands, understand intent, execute a small set of local tools, and expose the whole pipeline in a UI so nothing felt hidden.

That project became **VoxAgent**.

## What I Wanted the System to Do

The assignment requirements were straightforward on paper:

- accept microphone input or uploaded audio
- convert speech to text
- classify user intent
- execute local tools
- show the transcript, detected intent, action, and final result in a web UI

The interesting part was not checking those boxes individually. The real challenge was making them work together in a way that felt reliable on a normal laptop.

I did not want a system that was technically “local” but unusable in practice. I also did not want a system that could write arbitrary files anywhere on disk just because a language model interpreted a command loosely.

So the project ended up being guided by three principles:

1. Local first
2. Safe by default
3. Transparent at every step

## The Final Architecture

VoxAgent has five layers:

### 1. Audio ingestion

The frontend is built with Streamlit. It accepts input in two ways:

- direct microphone capture
- uploaded audio files such as `.wav`, `.mp3`, `.m4a`, and `.ogg`

This sounds simple, but it matters for usability. Browser microphone APIs are not always consistent across environments, so supporting file uploads gives the system a dependable fallback for demos and testing.

### 2. Local speech-to-text

For transcription, I used **faster-whisper** with a CPU-friendly default configuration:

- model: `base.en`
- device: `cpu`
- compute type: `int8`

I chose `faster-whisper` because it offers a strong balance of accuracy and local performance. Running a large speech model locally can become expensive very quickly, so the goal here was not maximum benchmark accuracy. It was practical responsiveness on typical hardware.

### 3. Intent planning

After transcription, the transcript is sent to a local Ollama model. Instead of asking the model for a plain-text interpretation, I ask it for a strict JSON action plan.

That plan includes:

- the detected intent
- whether confirmation is required
- target file or folder names when relevant
- instructions for code generation or summarization

This structure was important. Free-form model output is easy to read but harder to trust. Structured output makes downstream execution much safer and easier to debug.

### 4. Tool execution

The system supports four core intents:

- create a file or folder
- write code to a file
- summarize text
- general chat

All file system actions are constrained to a dedicated `output/` directory inside the repository. This was a hard requirement from the assignment, and it is also the correct design choice. Once an agent can touch the local file system, scope control stops being optional.

### 5. UI and memory

The UI shows:

- the original transcript
- the detected intent or intents
- the planned actions
- the executed result
- backend and timing information
- session notes

Each interaction is also stored in a lightweight JSON history file so recent actions remain visible during the session.

## Why I Chose This Stack

### Why Streamlit?

Because I needed a clean interface fast, and I needed to spend most of my time on the agent pipeline, not on frontend plumbing. Streamlit made it easy to create a UI that was good enough for a demo while still exposing the internals of the system.

### Why faster-whisper?

Because it keeps speech-to-text local while still being feasible on CPU. That mattered more than chasing a bigger model.

### Why Ollama?

Because local LLM routing was part of the spirit of the assignment. Ollama gave me a practical way to run local intent classification and generation without moving the project into a fully hosted architecture.

## The Most Important Design Decision: Safety

The most important part of the assignment was not speech recognition or even intent classification. It was deciding how much power the agent should be given.

I added three guardrails:

### 1. All writes are restricted to `output/`

The agent cannot write anywhere else.

### 2. Path traversal is rejected

Anything containing traversal or nested path tokens such as `..`, `/`, or `\` is blocked before execution.

### 3. File operations require explicit UI approval

The interface includes a human-in-the-loop confirmation checkbox before file creation or code writing can happen.

This preserved usability while making the agent much harder to misuse accidentally.

## What Broke During Real Verification

The first version worked in architecture terms, but real end-to-end verification exposed two weak points.

### Weak point 1: Partial fallback logic

Initially, I had a fallback planner for cases where Ollama was unavailable, but execution still depended on the model for summarization, chat, and code generation.

That meant the app could recover during planning and still fail a few seconds later during execution.

I fixed that by adding a **local fallback responder**:

- summarization falls back to a lightweight local summarizer
- chat falls back to a transparent rule-based response
- code generation falls back to a safe template

### Weak point 2: Planning timeouts were too expensive

In live runs, intent planning could stall long enough to dominate the user experience. That made the system feel frozen even when later steps could still complete.

The fix was to separate planning timeout from generation timeout:

- planning now times out faster
- long-form generation still has a larger timeout budget
- the fallback reason is surfaced in the UI notes

That one change made the app easier to demo and easier to explain.

## Demo Flows I Verified

I verified the pipeline locally with generated `.wav` commands, not just unit tests.

### Demo 1: Summarization

Input:

> “Summarize this text. Local AI agents combine speech recognition, reasoning, and tool execution to automate tasks.”

Observed behavior:

- transcript was recognized correctly
- intent was classified as `summarize_text`
- planner fell back after timeout
- summarization still completed successfully

### Demo 2: Code generation

Input:

> “Create a Python file named retry helper dot py with a retry function.”

Observed behavior:

- transcript normalized into `retryhelper.py`
- intents resolved to `create_file` and `write_code`
- file was created inside `output/`
- fallback code generation produced a valid retry helper implementation

That verification mattered. It confirmed that the system still behaves sensibly under degraded local-model conditions, which is exactly the kind of thing polished demos usually hide.

## Challenges I Faced

### Running everything locally without making it painful

Local AI stacks sound good in theory, but latency and hardware limits show up quickly. The solution was to be disciplined about defaults:

- smaller Whisper model
- CPU quantization
- short planner timeout
- safe fallback paths

### Converting language into action safely

Natural language is messy. File systems are not. The agent can feel flexible only if the execution layer is strict.

That meant separating “understanding the command” from “being allowed to perform the action.”

### Making the system explain itself

An agent that acts without showing its reasoning is harder to trust. For this reason, the UI was not just a wrapper. It became part of the architecture by showing the transcript, action plan, outputs, backend used, and execution notes.

## What I Would Improve Next

If I keep iterating on VoxAgent, the next steps would be:

- better entity extraction for filenames and structured parameters
- support for compound actions like “summarize this and save it to summary.txt”
- richer local code templates by language
- benchmarking different Whisper and Ollama model combinations
- a more interactive action-review screen before execution

## Final Takeaway

The most useful lesson from building VoxAgent was this:

**a good local agent is not just a model wrapped in a UI.**

It is a pipeline with carefully chosen failure modes, explicit safety boundaries, and enough visibility that a user can understand what happened at each step.

Speech-to-text, intent classification, and code generation are all important. But the thing that makes an agent usable is everything around them: safe execution, graceful fallback behavior, and a UI that turns opaque automation into something inspectable.

That is what I tried to build with VoxAgent.

## Repo

GitHub repository:

[https://github.com/dev-sanidhya/VoxAgent](https://github.com/dev-sanidhya/VoxAgent)
