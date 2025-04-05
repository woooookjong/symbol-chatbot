import streamlit as st
import openai

# 🔁 너가 만든 한글 ↔ 기호 변환 함수 가져오기
from hangul_converter import hangul_to_symbols, symbols_to_hangul

st.set_page_config(page_title="고대 문자 챗봇", layout="centered")
st.title("🤖 ᚠ𐔀 고대 문자 GPT 챗봇")

# 🔐 GPT API 키 입력 (Streamlit secrets 또는 수동 입력)
openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
if not openai_api_key:
    openai_api_key = st.text_input("🔑 OpenAI API 키를 입력하세요", type="password")

# 💬 채팅 기록 세션 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 👤 사용자 입력 (기호 언어)
user_input_symbol = st.text_area("🗣️ 기호 언어 입력", height=100)

def generate_gpt_reply(prompt_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        api_key=openai_api_key,
        messages=[
            {"role": "system", "content": "친절하고 쉽게 설명해 주세요."},
            {"role": "user", "content": prompt_text}
        ]
    )
    return response.choices[0].message["content"]

# ▶️ 버튼 클릭 시 GPT 호출 및 변환
if st.button("💬 기호로 대화하기") and user_input_symbol and openai_api_key:
    # 1️⃣ 기호 → 한글
    user_input_korean = symbols_to_hangul(user_input_symbol)

    # 2️⃣ GPT 호출 (한글)
    gpt_reply_korean = generate_gpt_reply(user_input_korean)

    # 3️⃣ GPT 응답 → 기호 변환
    gpt_reply_symbol = hangul_to_symbols(gpt_reply_korean)

    # 💾 채팅 기록 저장
    st.session_state.chat_history.append(("👤", user_input_symbol))
    st.session_state.chat_history.append(("🤖", gpt_reply_symbol))

# 🪶 채팅 출력
st.markdown("## 💬 대화 기록")
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}**: {msg}")
