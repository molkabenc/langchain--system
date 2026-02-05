"""
Streamlit translator using Groq with reusable prompt-template functions.

Features:
- Loads templates from prompts/ or falls back to defaults.
- Provides helper functions that generate prompts:
    - translate_from_english_to_spanish(text)
    - translate(from_language, to_language, text)
- Single or batch translation (one input per line).
- Shows the final prompt(s) and the Groq endpoint being called.
- Uses GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL from environment or Streamlit secrets.

Update .env in project root with:
GROQ_API_KEY="sk_..."
GROQ_API_URL="https://api.groq.ai/v1"
GROQ_MODEL="your-real-model-id"
"""
from urllib.parse import urlparse
from string import Template
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Groq Translator — prompt functions", layout="centered")
st.title("Groq Translator — Prompt templates as functions")
st.write("Use reusable prompt functions (see examples below).")

# ---------------- UI: basic inputs ----------------
COMMON_LANGUAGES = [
    "English", "Spanish", "French", "German", "Portuguese", "Italian",
    "Chinese (Simplified)", "Chinese (Traditional)", "Japanese", "Korean",
    "Arabic", "Russian", "Hindi", "Auto-detect"
]

col1, col2 = st.columns([1, 1])
with col1:
    src_lang = st.selectbox("Main language (source)", COMMON_LANGUAGES, index=0)
with col2:
    tgt_lang = st.selectbox("Target language", COMMON_LANGUAGES, index=1)

st.write("Input text. For batch mode, put one item per line.")
text_input = st.text_area("Text to translate", height=200, placeholder="Enter text or multiple lines for batch processing...")

# batch or single
batch_mode = st.checkbox("Batch mode (one input per line)", value=False)

# API config (UI shows defaults from env)
default_api_url = os.environ.get("GROQ_API_URL", "https://api.groq.ai/v1")
default_model = os.environ.get("GROQ_MODEL", "")
api_url = st.text_input("Groq API URL", value=default_api_url)
model_name = st.text_input("Groq Model name", value=default_model)

# Choose which prompt-function to use
prompt_func_choice = st.selectbox(
    "Prompt function",
    ("translate_from_english_to_spanish", "translate(from,to,statement) - generic"),
)

# ---------------- Templates loading ----------------
TEMPLATES_DIR = "prompts"
TRANSLATE_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, "translate_prompt.txt")
DETECT_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, "detect_translate_prompt.txt")
GENERIC_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, "generic_translate_prompt.txt")

DEFAULT_TRANSLATE_TEMPLATE = Template(
    "Translate the following text from $src to $tgt. Return ONLY the translated text and preserve formatting.\n\nText:\n$text"
)
DEFAULT_DETECT_TEMPLATE = Template(
    "Detect the source language of the following text and then translate it to $tgt.\n\n"
    "Output requirements:\n"
    "1) First line must be: Detected language: <language>\n"
    "2) After a blank line, return ONLY the translated text (preserve formatting).\n\n"
    "Text:\n$text\n\nDo not include any additional commentary."
)
DEFAULT_GENERIC_TEMPLATE = Template(
    "Translate the following from {from_lang} to {to_lang}. Provide just the translation and preserve formatting.\n\nText:\n{text}"
)

def load_file_template(path, fallback: Template, use_string_format=False):
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if use_string_format:
                # convert to string.Template placeholders for later safe_substitute
                return Template(content)
            return Template(content)
        except Exception as e:
            st.warning(f"Failed to read template {path}: {e}. Using default.")
    return fallback

translate_template = load_file_template(TRANSLATE_TEMPLATE_FILE, DEFAULT_TRANSLATE_TEMPLATE)
detect_template = load_file_template(DETECT_TEMPLATE_FILE, DEFAULT_DETECT_TEMPLATE)
generic_template_raw = ""
if os.path.isfile(GENERIC_TEMPLATE_FILE):
    try:
        with open(GENERIC_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            generic_template_raw = f.read()
    except Exception:
        generic_template_raw = ""
if generic_template_raw:
    # support curly-brace placeholders in generic template by formatting first, then wrap in Template
    # but for simplicity we'll use python .format() on generic templates
    generic_template = generic_template_raw
else:
    # fallback generic string with .format placeholders
    generic_template = "Translate the following from {from_lang} to {to_lang}. Provide just the translation and preserve formatting.\n\nText:\n{text}"

with st.expander("View templates (editable in prompts/ folder)"):
    st.subheader("translate_prompt.txt")
    st.code(translate_template.template, language="text")
    st.subheader("detect_translate_prompt.txt")
    st.code(detect_template.template, language="text")
    st.subheader("generic_translate_prompt.txt (uses {from_lang}, {to_lang}, {text})")
    st.code(generic_template, language="text")

# ---------------- Prompt-function wrappers ----------------
def translate_from_english_to_spanish(english_statement: str) -> str:
    # simple wrapper using translate_template (assumes $src and $tgt placeholders)
    return translate_template.safe_substitute({"text": english_statement, "src": "English", "tgt": "Spanish"})

def translate_generic(from_language: str, to_language: str, statement: str) -> str:
    # use generic_template (curly placeholders)
    try:
        return generic_template.format(from_lang=from_language, to_lang=to_language, text=statement)
    except Exception:
        # fallback to translate_template style if formatting fails
        return translate_template.safe_substitute({"text": statement, "src": from_language, "tgt": to_language})

# ---------------- Groq adapter (normalize + better errors) ----------------
DEFAULT_GROQ_API = "https://api.groq.ai/v1"

def normalize_api_url(raw_url: str) -> str:
    if not raw_url:
        return DEFAULT_GROQ_API
    raw_url = raw_url.strip()
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        raw_url = "https://" + raw_url
        parsed = urlparse(raw_url)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(f"Invalid GROQ_API_URL: {raw_url!r}. It must be a full URL, e.g. https://api.groq.ai/v1")
    return raw_url.rstrip('/')

def translate_with_groq(api_key: str, api_url: str, model: str, prompt: str, timeout: int = 30) -> str:
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env or environment.")
    if not model or model.strip() == "" or "your-groq-model-name" in model:
        raise RuntimeError("GROQ_MODEL is not set or looks like a placeholder. Set GROQ_MODEL to the real model id.")
    api_url = normalize_api_url(api_url)
    endpoint = f"{api_url}/models/{model.strip()}/invoke"
    # debug info (safe — does not print key)
    st.text("Calling endpoint: " + endpoint)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"input": prompt}
    try:
        resp = requests.post(endpoint, headers=headers, json=body, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        resp_obj = getattr(e, "response", None)
        status = getattr(resp_obj, "status_code", None) if resp_obj else None
        body_text = resp_obj.text if resp_obj is not None else ""
        msg = f"Request to Groq failed: {e}\nHTTP status: {status}\nEndpoint: {endpoint}\nResponse (truncated): {body_text[:800]}"
        raise RuntimeError(msg)
    try:
        data = resp.json()
    except Exception:
        return resp.text
    # simple parsing (adapt if your Groq response differs)
    if isinstance(data, dict):
        for k in ("output", "result", "translation", "text"):
            if k in data and isinstance(data[k], str):
                return data[k].strip()
        if "results" in data and isinstance(data["results"], list) and data["results"]:
            first = data["results"][0]
            if isinstance(first, dict):
                for k in ("output", "text", "translation", "content"):
                    if k in first and isinstance(first[k], str):
                        return first[k].strip()
    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        return "\n".join(x.strip() for x in data)
    return json.dumps(data, indent=2, ensure_ascii=False)

# ---------------- Run translation on button ----------------
do_translate = st.button("Translate with Groq")

if do_translate:
    # collect API creds
    groq_api_key = os.environ.get("GROQ_API_KEY") or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None)
    groq_api_url = api_url or os.environ.get("GROQ_API_URL", DEFAULT_GROQ_API)
    groq_model = model_name or os.environ.get("GROQ_MODEL", "")

    if not groq_api_key:
        st.error("GROQ_API_KEY environment variable not set. Add it to .env or Streamlit secrets.")
    elif not groq_model or "your-groq-model-name" in groq_model:
        st.error("GROQ_MODEL not set or is placeholder. Put your real model id in the model input or .env.")
    else:
        # Decide prompt-generation function
        if prompt_func_choice == "translate_from_english_to_spanish":
            generator_fn = lambda s: translate_from_english_to_spanish(s)
        else:
            generator_fn = lambda s: translate_generic(src_lang, tgt_lang, s)

        # Build prompts (single or batch)
        if batch_mode:
            lines = [line.strip() for line in text_input.splitlines() if line.strip()]
            if not lines:
                st.warning("Batch mode selected but no non-empty lines found.")
            else:
                st.write(f"Translating {len(lines)} items...")
                results = []
                for i, item in enumerate(lines, start=1):
                    prompt_text = generator_fn(item)
                    with st.expander(f"Prompt #{i} (preview)"):
                        st.code(prompt_text, language="text")
                    try:
                        out = translate_with_groq(groq_api_key, groq_api_url, groq_model, prompt_text)
                    except Exception as e:
                        out = f"Error: {e}"
                    results.append((item, out))
                # display results
                st.subheader("Batch results")
                for idx, (inp, out) in enumerate(results, start=1):
                    st.markdown(f"**#{idx} Input:** {inp}")
                    st.success(out)
        else:
            if not text_input.strip():
                st.warning("Enter text to translate.")
            else:
                prompt_text = generator_fn(text_input.strip())
                with st.expander("Final prompt sent to the model", expanded=True):
                    st.code(prompt_text, language="text")
                try:
                    out = translate_with_groq(groq_api_key, groq_api_url, groq_model, prompt_text)
                    st.subheader("Translation")
                    st.success(out)
                except Exception as e:
                    st.error("Translation failed:")
                    st.code(str(e)[:1000], language="text")