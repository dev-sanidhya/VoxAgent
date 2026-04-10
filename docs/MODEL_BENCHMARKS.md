# Model Benchmarks

Lightweight benchmarks were run locally on April 10, 2026 using the demo audio and a fixed summarization prompt.

## Test Setup

### STT benchmark

- audio file: `demo_audio/summary_command.wav`
- device: CPU
- compute type: `int8`
- library: `faster-whisper`

### LLM benchmark

- backend: Ollama
- task: one-sentence summary generation
- endpoint: `http://localhost:11434/api/chat`

## STT Results

| Model | Load Time (s) | Transcription Time (s) | Notes |
| --- | ---: | ---: | --- |
| `base.en` | 1.494 | 1.523 | Fastest practical default |
| `small.en` | 1.877 | 3.338 | Slightly slower with no transcript gain on the sample |

### STT conclusion

For this project, `base.en` was the better default on the local CPU machine because it was materially faster while producing the same transcript on the sample audio.

## Ollama Results

| Model | Response Time (s) | Output Snapshot |
| --- | ---: | --- |
| `llama3.1:8b` | 41.447 | "AI agents can now perform various everyday tasks through integration of voice recognition, task planning, and device control capabilities." |
| `llama3.2:latest` | 61.164 | "Local AI agents use speech recognition, intent planning, and tool execution to autonomously complete everyday tasks." |

### Ollama conclusion

`llama3.1:8b` was faster in this local setup, so it remains the default model in the repository. `llama3.2:latest` also worked, but it was noticeably slower on the same prompt.

## Practical Takeaway

These benchmarks are intentionally lightweight, but they were enough to guide the default configuration:

- `base.en` for local STT
- `llama3.1:8b` for local Ollama routing and generation

That combination gave the best tradeoff between responsiveness and output quality during local testing.
