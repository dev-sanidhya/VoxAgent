# Demo Verification

Verified locally on April 10, 2026 in `C:\Users\shish\Desktop\Internship`.

## Verification Method

- generated two local `.wav` demo clips with Windows speech synthesis
- ran the real `VoiceAgent.process_audio(...)` pipeline against both clips
- kept the default repository configuration with:
  - `WHISPER_MODEL=base.en`
  - `WHISPER_DEVICE=cpu`
  - `OLLAMA_MODEL=llama3.1:8b`
  - `PLANNER_TIMEOUT_SECONDS=20`

## Verified Demo Command 1

Audio prompt:

> Summarize this text. Local AI agents combine speech recognition, reasoning, and tool execution to automate tasks.

Observed result:

- transcript recognized correctly
- detected intent: `summarize_text`
- planner fell back after an Ollama timeout
- summarization still completed successfully
- output summary:

> Local AI agents use speech recognition, reasoning, and tool execution to automate tasks.

## Verified Demo Command 2

Audio prompt:

> Create a Python file named retry helper dot py with a retry function.

Observed result:

- transcript recognized as `Create a Python file named retryhelper.py with a retry function`
- detected intents: `create_file`, `write_code`
- file created successfully inside `output/`
- fallback code generation completed successfully
- after timeout tuning, the execution fallback completed in under a minute on the local machine
- generated file:
  - `output/retryhelper.py`

## Notes

- On a CPU-only machine, first-run STT can still take noticeable time because the local Whisper model has to load.
- The execution path is now resilient even if Ollama planning or generation times out:
  - planning falls back to rule-based intent detection
  - summarization and chat can fall back locally
  - code generation can fall back to a safe template
