from __future__ import annotations

from pathlib import Path

import streamlit as st

from voxagent.agent import VoiceAgent
from voxagent.config import get_settings
from voxagent.utils import write_temp_audio

try:
    from audio_recorder_streamlit import audio_recorder
except ImportError:  # pragma: no cover - optional UI fallback
    audio_recorder = None


def _render_history(history: list[dict]) -> None:
    st.sidebar.header("Session Memory")
    if not history:
        st.sidebar.caption("No interactions stored yet.")
        return

    for item in reversed(history[-8:]):
        intents = ", ".join(item.get("intents", [])) or "no intents"
        with st.sidebar.expander(f"{item.get('timestamp', 'unknown')} | {intents}", expanded=False):
            st.write(item.get("transcript", ""))
            st.caption(item.get("summary", ""))


def _audio_from_input() -> tuple[bytes | None, str | None]:
    uploaded = st.file_uploader(
        "Upload an audio file",
        type=["wav", "mp3", "m4a", "ogg"],
        help="Supported formats depend on your local ffmpeg/audio stack.",
    )
    if uploaded is not None:
        return uploaded.getvalue(), Path(uploaded.name).suffix or ".wav"

    if hasattr(st, "audio_input"):
        clip = st.audio_input("Record from your microphone")
        if clip is not None:
            return clip.read(), ".wav"

    if audio_recorder is not None:
        st.caption("Browser microphone fallback")
        clip_bytes = audio_recorder(text="Record audio", pause_threshold=2.5, sample_rate=41_000)
        if clip_bytes:
            return clip_bytes, ".wav"

    return None, None


def _render_plan(response) -> None:
    st.subheader("Detected Intent")
    if response.intents:
        st.write(", ".join(response.intents))
    else:
        st.write("No intent detected")

    st.subheader("Planned Actions")
    if not response.action_plan:
        st.info("No executable actions were planned.")
        return

    for index, action in enumerate(response.action_plan, start=1):
        with st.container(border=True):
            st.markdown(f"**Step {index}:** `{action.intent}`")
            if action.target_file:
                st.write(f"Target file: `{action.target_file}`")
            if action.language:
                st.write(f"Language: `{action.language}`")
            if action.instruction:
                st.write(action.instruction)


def _render_results(response) -> None:
    st.subheader("System Action")
    if not response.action_results:
        st.warning("Actions were not executed yet.")
        return

    for result in response.action_results:
        with st.container(border=True):
            st.markdown(f"**{result.intent}**")
            st.write(result.message)
            if result.path:
                st.caption(result.path)
            if result.output:
                st.code(result.output)


def run_app() -> None:
    settings = get_settings()
    agent = VoiceAgent(settings)
    history = agent.history_store.load()

    st.set_page_config(page_title="VoxAgent", page_icon="🎙️", layout="wide")
    st.title("VoxAgent")
    st.caption("Voice-controlled local AI agent with speech-to-text, intent routing, and safe local tools.")

    _render_history(history)

    with st.expander("Configuration", expanded=False):
        st.write(f"STT model: `{settings.whisper_model}`")
        st.write(f"LLM backend: `{settings.ollama_model}` via `{settings.ollama_base_url}`")
        st.write(f"Safe output directory: `{settings.output_dir}`")

    approve = st.checkbox(
        "Approve file creation and code writing inside output/",
        value=False,
        help="Required for create-file and write-code actions.",
    )
    audio_bytes, suffix = _audio_from_input()

    if audio_bytes:
        st.audio(audio_bytes)

    process = st.button("Run Agent", type="primary", disabled=audio_bytes is None)
    if not process:
        st.info("Provide microphone input or upload an audio file, then run the agent.")
        return

    if audio_bytes is None:
        st.error("No audio input was provided.")
        return

    audio_path = write_temp_audio(audio_bytes, suffix or ".wav")
    with st.spinner("Transcribing audio and planning actions..."):
        response = agent.process_audio(audio_path=audio_path, approve_file_actions=approve)

    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.subheader("Transcribed Text")
        st.write(response.transcript or "No text extracted.")
        st.caption(f"STT backend: {response.stt_backend}")
        st.caption(f"Planner backend: {response.llm_backend}")
        _render_plan(response)

    with right:
        _render_results(response)
        if response.notes:
            st.subheader("Notes")
            for note in response.notes:
                st.write(f"- {note}")
