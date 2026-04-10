# Setup Notes

## Local prerequisites

- Python 3.10+
- Ollama installed locally
- an Ollama model pulled locally, for example:

```powershell
ollama pull llama3.1:8b
```

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

## Recommended local-first configuration

The default `.env.example` values are tuned for a laptop CPU:

- `WHISPER_MODEL=small.en`
- `WHISPER_DEVICE=cpu`
- `WHISPER_COMPUTE_TYPE=int8`
- `OLLAMA_MODEL=llama3.1:8b`

## Troubleshooting

- If transcription is slow, switch to `base.en`.
- If uploaded compressed audio formats fail, install ffmpeg on the machine and retry.
- If Ollama is not running, the app falls back to rule-based intent parsing.
