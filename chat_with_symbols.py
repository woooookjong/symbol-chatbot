import streamlit as st
from jamo import h2j, j2hcj
import unicodedata
import openai

# ✅ 최신 방식: 클라이언트 생성
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 기호 매핑 테이블 (초성/중성/종성)
decompose_chosung = {'ㄱ': 'ᚠ', 'ㄴ': 'ᚢ', 'ㄷ': 'ᚣ', 'ㄹ': 'ᚥ', 'ㅁ': 'ᚦ', 'ㅂ': 'ᚧ', 'ㅅ': 'ᚩ', 'ㅇ': 'ᚫ', 'ㅈ': 'ᚬ', 'ㅊ': 'ᚮ', 'ㅋ': 'ᚯ', 'ㅌ': 'ᚰ', 'ㅍ': 'ᚱ', 'ㅎ': 'ᚲ'}
decompose_jungsung = {'ㅏ': '𐔀', 'ㅓ': '𐔄', 'ㅗ': '𐔈', 'ㅜ': '𐔍', 'ㅡ': '𐔒', 'ㅣ': '𐔔', 'ㅐ': '𐔁', 'ㅔ': '𐔅'}
decompose_jongsung = {'': '', 'ㄱ': 'ᚳ', 'ㄴ': 'ᚶ', 'ㄷ': 'ᚹ', 'ㄹ': 'ᚺ', 'ㅁ': 'ᛂ', 'ㅂ': 'ᛃ', 'ㅅ': 'ᛅ', 'ㅇ': 'ᛇ', 'ㅈ': 'ᛈ', 'ㅊ': 'ᛉ', 'ㅋ': 'ᛊ', 'ㅌ': 'ᛋ', 'ㅍ': 'ᛌ', 'ㅎ': 'ᛍ'}

# 역변환
reverse_chosung = {v: k for k, v in decompose_chosung.items()}
reverse_jungsung = {v: k for k, v in decompose_jungsung.items()}
reverse_jongsung = {v: k for k, v in decompose_jongsung.items()}

CHOSUNG_LIST = list(decompose_chosung.keys())
JUNGSUNG_LIST = list(decompose_jungsung.keys())
JONGSUNG_LIST = list(decompose_jongsung.keys())

SPACE_SYMBOL = '𐤟'

# 한글 여부
def is_hangul_char(char):
    return 'HANGUL' in unicodedata.name(char, '')

# 자모 조합
def join_jamos_manual(jamos):
    result = ""
    i = 0
    while i < len(jamos):
        if jamos[i] in CHOSUNG_LIST:
            cho = CHOSUNG_LIST.index(jamos[i])
            if i+1 < len(jamos) and jamos[i+1] in JUNGSUNG_LIST:
                jung = JUNGSUNG_LIST.index(jamos[i+1])
                jong = 0
                if i+2 < len(jamos) and jamos[i+2] in JONGSUNG_LIST:
                    jong = JONGSUNG_LIST.index(jamos[i+2])
                    i += 1
                result += chr(0xAC00 + cho * 21 * 28 + jung * 28 + jong)
                i += 2
            else:
                result += jamos[i]
                i += 1
        else:
            result += jamos[i]
            i += 1
    return result

# 🧙 Streamlit 앱 시작
st.set_page_config(page_title="ᚠ𐔀 기호 챗봇", layout="centered")
st.title("ᚠ𐔀 기호 언어 챗봇 💬")

# 채팅 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 입력
user_input = st.text_input("기호 언어 입력 👇")

# 전처리: 기호 → 한글
def convert_symbols_to_hangul(symbol_input):
    jamo_result = []
    i = 0
    while i < len(symbol_input):
        ch = symbol_input[i]
        next_ch = symbol_input[i+1] if i+1 < len(symbol_input) else ''
        next_next_ch = symbol_input[i+2] if i+2 < len(symbol_input) else ''
        if ch == SPACE_SYMBOL:
            jamo_result.append(' ')
            i += 1
        elif ch in reverse_chosung:
            if next_ch in reverse_jungsung:
                cho = reverse_chosung[ch]
                jung = reverse_jungsung[next_ch]
                jong = ''
                if next_next_ch in reverse_jongsung:
                    jong = reverse_jongsung[next_next_ch]
                    jamo_result.extend([cho, jung, jong])
                    i += 3
                else:
                    jamo_result.extend([cho, jung])
                    i += 2
            else:
                jamo_result.append(reverse_chosung[ch])
                i += 1
        else:
            jamo_result.append(ch)
            i += 1
    return join_jamos_manual(jamo_result)

# 후처리: 한글 → 기호
def convert_hangul_to_symbols(text):
    result = ""
    for char in text:
        if char == ' ':
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

# 메시지 전송
if user_input:
    # 1️⃣ 기호 → 한글
    user_hangul = convert_symbols_to_hangul(user_input)
    st.session_state.chat_history.append(("🧑", user_input))

    # 2️⃣ GPT 호출
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "모든 대답은 기호 언어로 해줘."},
            {"role": "user", "content": user_hangul}
        ]
    )
    assistant_reply = response.choices[0].message.content.strip()

    # 3️⃣ 한글 → 기호
    assistant_symbols = convert_hangul_to_symbols(assistant_reply)
    st.session_state.chat_history.append(("🤖", assistant_symbols))

# 채팅 출력
st.markdown("---")
for role, msg in st.session_state.chat_history:
    st.markdown(f"**{role}**: {msg}")
