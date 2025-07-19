import streamlit as st
import random
from gtts import gTTS
import base64
import os
import uuid

# --- 問題リスト ---
one_letter_words = [c.upper() for c in list("abcdefghijklmnopqrstuvwxyz")]
two_letter_words = [w.upper() for w in ["ka", "sa", "mi", "ne", "ta", "yu", "ki"]]
three_letter_words = [w.upper() for w in ["tyo", "kyo", "nya", "cha", "shu", "shi"]]

# --- 問題生成 ---
def get_new_target():
    level = st.session_state["level"]
    if level == "1もじ":
        return random.choice(one_letter_words)
    elif level == "2もじ":
        return random.choice(two_letter_words)
    else:
        return random.choice(three_letter_words)

# --- 音声再生 ---
def generate_speech(text, filename="temp.mp3"):
    tts = gTTS(text=text, lang='ja')
    tts.save(filename)
    with open(filename, "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    audio_id = str(uuid.uuid4())  # ユニークIDで強制再描画

    audio_html = f"""
        <audio id="audio-{audio_id}" controls style="display:none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("audio-{audio_id}");
            if (audio) {{
                audio.play().catch(e => {{
                    console.log("Audio play failed:", e);
                }});
            }}
        </script>
    """
    st.components.v1.html(audio_html, height=0)
    os.remove(filename)


# --- セッション初期化 ---
def init_session():
    defaults = {
        "level": "1もじ",
        "target": None,
        "user_input": "",
        "show_result": False,
        "correct": False,
        "play_audio_text": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if st.session_state["target"] is None:
        st.session_state["target"] = get_new_target()

# --- 次の問題へ ---
def next_question():
    st.session_state["target"] = get_new_target()
    st.session_state["show_result"] = False
    st.session_state["correct"] = False
    st.session_state["user_input"] = ""
    st.session_state["play_audio_text"] = None

# --- アプリ本体 ---
init_session()

# スタイル
st.markdown("""
    <style>
    input[type="text"] {
        font-size: 1.5em;
    }
    div.row-widget.stButton > button {
        font-size: 1.5em;
        padding: 0.75em 1.5em;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# UI
st.title("🐱 ネコちゃん アルファベット ゲーム")
st.session_state["level"] = st.selectbox("れべるをえらんでにゃー", ["1もじ", "2もじ", "3もじ"], index=["1もじ", "2もじ", "3もじ"].index(st.session_state["level"]))
st.markdown(f"### 『「{st.session_state['target']}」っていれてみてにゃー』")

# 入力長さをターゲット文字数に合わせる
max_len = len(st.session_state["target"])

# フォーム（入力 + 送信）
with st.form("answer_form", clear_on_submit=False):
    st.text_input("ここにいれてにゃー", max_chars=max_len, key="user_input")
    submitted = st.form_submit_button("えんたーにゃ！")

# 回答処理
if submitted:
    user_input = st.session_state["user_input"].upper()
    is_correct = user_input == st.session_state["target"]
    st.session_state["correct"] = is_correct
    st.session_state["show_result"] = True
    st.session_state["play_audio_text"] = "せいかいだにゃー" if is_correct else "もういっかいやってみるにゃー"

# 音声再生（毎回）
if st.session_state["play_audio_text"]:
    generate_speech(st.session_state["play_audio_text"])
    st.session_state["play_audio_text"] = None

# 結果表示
if st.session_state["show_result"]:
    if st.session_state["correct"]:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>◯</h1>", unsafe_allow_html=True)
        st.button("つぎのもんだい", on_click=next_question)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>😿</h1>", unsafe_allow_html=True)
