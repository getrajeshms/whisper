import streamlit as st
import whisper
import tempfile
import os
import time
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Whisper Transcriber",
    page_icon="🎙️",
    layout="centered",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark industrial background */
.stApp {
    background-color: #0e0e10;
    color: #e8e8e0;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    letter-spacing: -0.5px;
}

/* Header strip */
.header-strip {
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-left: 4px solid #e94560;
    padding: 1.5rem 2rem;
    border-radius: 4px;
    margin-bottom: 2rem;
}

.header-strip h1 {
    margin: 0;
    font-size: 1.8rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.header-strip p {
    margin: 0.3rem 0 0;
    color: #a8a8b3;
    font-size: 0.85rem;
    font-weight: 300;
}

/* Upload zone */
.upload-zone {
    border: 2px dashed #2a2a3e;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
    background: #131320;
    transition: border-color 0.3s;
}

/* Model selector card */
.model-card {
    background: #131320;
    border: 1px solid #1e1e30;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
}

/* Transcript box */
.transcript-box {
    background: #0a0a12;
    border: 1px solid #1e1e30;
    border-left: 3px solid #e94560;
    border-radius: 4px;
    padding: 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    line-height: 1.8;
    color: #d4d4c8;
    white-space: pre-wrap;
    max-height: 450px;
    overflow-y: auto;
}

/* Accent pill badges */
.badge {
    display: inline-block;
    background: #e94560;
    color: white;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin-right: 6px;
    vertical-align: middle;
}

.badge-green {
    background: #00b894;
}

.badge-blue {
    background: #0984e3;
}

/* Status bar */
.status-bar {
    background: #131320;
    border: 1px solid #1e1e30;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #a8a8b3;
}

/* Streamlit button override */
.stButton > button {
    background: #e94560 !important;
    color: white !important;
    border: none !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 0.6rem 2rem !important;
    border-radius: 4px !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Select box */
.stSelectbox label {
    color: #a8a8b3 !important;
    font-size: 0.82rem !important;
    font-family: 'Space Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #e94560 !important;
    color: #e94560 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
}

/* Info/warning boxes */
.stInfo {
    background: #131320 !important;
    border-left: 3px solid #0984e3 !important;
    color: #a8a8b3 !important;
}

/* Divider */
hr {
    border-color: #1e1e30 !important;
    margin: 1.5rem 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e0e10; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-strip">
  <h1>🎙️ Whisper Transcriber</h1>
  <p>Local audio transcription · Powered by OpenAI Whisper · No data leaves your machine</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — Model Info ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    model_options = {
        "tiny   (~75MB)  — Fastest, lower accuracy":   "tiny",
        "base   (~145MB) — Good balance":               "base",
        "small  (~465MB) — Better accuracy":            "small",
        "medium (~1.5GB) — High accuracy ✓ Recommended":"medium",
        "large  (~3GB)   — Best accuracy, slow":        "large",
    }

    selected_label = st.selectbox(
        "Whisper Model",
        list(model_options.keys()),
        index=3,
        help="Larger models are more accurate but slower to load and run."
    )
    model_name = model_options[selected_label]

    st.markdown("---")

    lang_options = {
        "Auto-detect": None,
        "English":     "en",
        "Hindi":       "hi",
        "Tamil":       "ta",
        "Kannada":     "kn",
        "Telugu":      "te",
        "French":      "fr",
        "Spanish":     "es",
        "German":      "de",
        "Japanese":    "ja",
        "Chinese":     "zh",
    }
    selected_lang_label = st.selectbox("Language", list(lang_options.keys()), index=0)
    language = lang_options[selected_lang_label]

    st.markdown("---")
    task = st.radio(
        "Task",
        ["transcribe", "translate"],
        help="'translate' converts speech to English regardless of source language."
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-family: Space Mono, monospace; font-size: 0.72rem; color: #555570; line-height: 1.6;'>
    INSTALL REQUIREMENTS<br><br>
    <code style='color:#e94560'>pip install streamlit openai-whisper</code><br><br>
    RUN APP<br><br>
    <code style='color:#e94560'>streamlit run transcriber_app.py</code>
    </div>
    """, unsafe_allow_html=True)

# ── File Upload ────────────────────────────────────────────────────────────────
st.markdown("#### Upload Audio File")

SUPPORTED = ["mp3", "mp4", "wav", "m4a", "ogg", "flac", "webm", "mpeg"]
uploaded_file = st.file_uploader(
    "Drop your audio file here",
    type=SUPPORTED,
    label_visibility="collapsed",
)

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.markdown(f"""
    <div class="status-bar">
      <span class="badge">FILE</span> {uploaded_file.name} &nbsp;|&nbsp;
      <span class="badge badge-blue">SIZE</span> {file_size_mb:.1f} MB &nbsp;|&nbsp;
      <span class="badge badge-green">MODEL</span> {model_name} &nbsp;|&nbsp;
      <span class="badge">TASK</span> {task.upper()}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    col1, col2 = st.columns([1, 3])
    with col1:
        run = st.button("▶ TRANSCRIBE")

    if run:
        with st.spinner("Loading Whisper model…"):
            model = whisper.load_model(model_name)

        # Save upload to temp file
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner(f"Transcribing `{uploaded_file.name}` — this may take a minute…"):
            t0 = time.time()
            options = {"task": task}
            if language:
                options["language"] = language
            result = model.transcribe(tmp_path, **options)
            elapsed = time.time() - t0

        os.unlink(tmp_path)

        transcript = result["text"].strip()
        detected_lang = result.get("language", "unknown")

        st.markdown("---")
        st.markdown(f"""
        <div class="status-bar">
          ✅ &nbsp; Done in <strong>{elapsed:.1f}s</strong> &nbsp;|&nbsp;
          Detected language: <strong>{detected_lang.upper()}</strong> &nbsp;|&nbsp;
          ~{len(transcript.split())} words
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Transcript")
        st.markdown(f'<div class="transcript-box">{transcript}</div>', unsafe_allow_html=True)

        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "⬇ Download .txt",
                data=transcript,
                file_name=Path(uploaded_file.name).stem + "_transcript.txt",
                mime="text/plain",
            )
        with col_b:
            # SRT export
            segments = result.get("segments", [])
            if segments:
                srt_lines = []
                for i, seg in enumerate(segments, 1):
                    def fmt_time(t):
                        h = int(t // 3600)
                        m = int((t % 3600) // 60)
                        s = int(t % 60)
                        ms = int((t % 1) * 1000)
                        return f"{h:02}:{m:02}:{s:02},{ms:03}"
                    srt_lines.append(str(i))
                    srt_lines.append(f"{fmt_time(seg['start'])} --> {fmt_time(seg['end'])}")
                    srt_lines.append(seg["text"].strip())
                    srt_lines.append("")
                srt_content = "\n".join(srt_lines)
                st.download_button(
                    "⬇ Download .srt",
                    data=srt_content,
                    file_name=Path(uploaded_file.name).stem + "_transcript.srt",
                    mime="text/plain",
                )

else:
    st.markdown("""
    <div class="upload-zone">
      <p style='color:#555570; font-family: Space Mono, monospace; font-size:0.8rem;'>
        Supported formats: MP3 · MP4 · WAV · M4A · OGG · FLAC · WEBM
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.info("👈  Choose a Whisper model and language in the sidebar, then upload your audio file above.")
