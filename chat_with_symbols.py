import streamlit as st
import openai
from jamo import h2j, j2hcj
import unicodedata

# GPT API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 기호 언어 변환 설정
decompose_chosung = {'ㄱ': 'ᚠ', 'ㄲ': 'ᚡ', 'ㄴ': 'ᚢ', 'ㄷ': 'ᚣ', 'ㄸ': 'ᚤ',
                     'ㄹ': 'ᚥ', 'ㅁ': 'ᚦ', 'ㅂ': 'ᚧ', 'ㅃ': 'ᚨ', 'ㅅ': 'ᚩ',
                     'ㅆ': 'ᚪ', 'ㅇ': 'ᚫ', 'ㅈ': 'ᚬ', 'ㅉ': 'ᚭ', 'ㅊ': 'ᚮ',
                     'ㅋ': 'ᚯ', 'ㅌ': 'ᚰ', 'ㅍ': 'ᚱ', 'ㅎ': 'ᚲ'}

decompose_jungsung = {'ㅏ': '𐔀', 'ㅐ': '𐔁', 'ㅑ': '𐔂', 'ㅒ': '𐔃', 'ㅓ': '𐔄',
                      'ㅔ': '𐔅', 'ㅕ': '𐔆', 'ㅖ': '𐔇', 'ㅗ': '𐔈', 'ㅘ': '𐔉',
                      'ㅙ': '𐔊', 'ㅚ': '𐔋', 'ㅛ': '𐔌', 'ㅜ': '𐔍', 'ㅝ': '𐔎',
                      'ㅞ': '𐔏', 'ㅟ': '𐔐', 'ㅠ': '𐔑', 'ㅡ': '𐔒', 'ㅢ': '𐔓', 'ㅣ': '𐔔'}

decompose_jongsung = {'': '', 'ㄱ': 'ᚳ', 'ㄲ': 'ᚴ', 'ㄳ': 'ᚵ', 'ㄴ': 'ᚶ',
                      'ㄵ': 'ᚷ', 'ㄶ': 'ᚸ', 'ㄷ': 'ᚹ', 'ㄹ': 'ᚺ', 'ㄺ': 'ᚻ',
                      'ㄻ': 'ᚼ', 'ㄼ': 'ᚽ', 'ㄽ': 'ᚾ', 'ㄾ': 'ᚿ', 'ㄿ': 'ᛀ',
                      'ㅀ': 'ᛁ', 'ㅁ': 'ᛂ', 'ㅂ': 'ᛃ', 'ㅄ': 'ᛄ', 'ㅅ': 'ᛅ',
                      'ㅆ': 'ᛆ', 'ㅇ': 'ᛇ', 'ㅈ': 'ᛈ', 'ㅊ': 'ᛉ', 'ㅋ': 'ᛊ',
                      'ㅌ': 'ᛋ', 'ㅍ': 'ᛌ', 'ㅎ': 'ᛍ'}

SPACE_SYMBOL = '𐤟'

def is_hangul_char(char):
    return 'HANGUL' in unicodedata.name(char, '')

def hangul_to_symbols(text):
    result = ""
    for char in text:
        if char == " ":
            result += SPACE_SYMBOL
        elif is_hangul_char(char):
            decomposed = list(j2hcj(h2j(char)))
            cho = decomposed[0]
            jung = decomposed[1]
            jong = decomposed[2] if len(decomposed) == 3 else ''
            result += decompose_chosung.get(cho, cho)
            result += decompose_jungsung.get(jung, jung)
            result += decompose_jongsung.get(jong, jong)
        else:
            result += char
    return result

# Streamlit UI
st.set_page_config(page_title="기호 챗봇", layout="centered")
st.title("🔮 기호 언어 GPT 챗봇")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("기호 언어로 메시지를 입력하세요:", key="symbol_input")

if st.button("보내기") and user_input:
    # 메시지 저장
    st.session_state.chat_history.append(("user", user_input))

    # GPT API 호출
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 기호 언어만 사용하는 챗봇입니다. 한글은 절대 사용하지 마세요."},
            *[{"role": role, "content": msg} for role, msg in st.session_state.chat_history]
        ]
    )

    bot_reply = response['choices'][0]['message']['content']
    st.session_state.chat_history.append(("assistant", bot_reply))

# 채팅 출력
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"🧑‍💻 **나:** {message}")
    else:
        st.markdown(f"🤖 **기호봇:** {message}")
