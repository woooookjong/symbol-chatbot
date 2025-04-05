import streamlit as st
import unicodedata
from jamo import h2j, j2hcj
from openai import OpenAI

# 🔐 비밀번호 설정
PASSWORD = "tnguswhddnr123"

# ✅ 인증
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if password == PASSWORD:
        st.session_state.authenticated = True
        st.experimental_rerun()
    else:
        st.stop()

# ✅ OpenAI 클라이언트 객체 생성
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 문자 구성 리스트
CHOSUNG_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JUNGSUNG_LIST = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONGSUNG_LIST = ['', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

# 기호 매핑
decompose_chosung = {'ㄱ': 'ᚠ', 'ㄲ': 'ᚡ', 'ㄴ': 'ᚢ', 'ㄷ': 'ᚣ', 'ㄸ': 'ᚤ','ㄹ': 'ᚥ', 'ㅁ': 'ᚦ', 'ㅂ': 'ᚧ', 'ㅃ': 'ᚨ', 'ㅅ': 'ᚩ','ㅆ': 'ᚪ', 'ㅇ': 'ᚫ', 'ㅈ': 'ᚬ', 'ㅉ': 'ᚭ', 'ㅊ': 'ᚮ','ㅋ': 'ᚯ', 'ㅌ': 'ᚰ', 'ㅍ': 'ᚱ', 'ㅎ': 'ᚲ'}
decompose_jungsung = {'ㅏ': '𐔀', 'ㅐ': '𐔁', 'ㅑ': '𐔂', 'ㅒ': '𐔃', 'ㅓ': '𐔄','ㅔ': '𐔅', 'ㅕ': '𐔆', 'ㅖ': '𐔇', 'ㅗ': '𐔈', 'ㅘ': '𐔉','ㅙ': '𐔊', 'ㅚ': '𐔋', 'ㅛ': '𐔌', 'ㅜ': '𐔍', 'ㅝ': '𐔎','ㅞ': '𐔏', 'ㅟ': '𐔐', 'ㅠ': '𐔑', 'ㅡ': '𐔒', 'ㅢ': '𐔓', 'ㅣ': '𐔔'}
decompose_jongsung = {'': '', 'ㄱ': 'ᚳ', 'ㄲ': 'ᚴ', 'ㄳ': 'ᚵ', 'ㄴ': 'ᚶ','ㄵ': 'ᚷ', 'ㄶ': 'ᚸ', 'ㄷ': 'ᚹ', 'ㄹ': 'ᚺ', 'ㄺ': 'ᚻ','ㄻ': 'ᚼ', 'ㄼ': 'ᚽ', 'ㄽ': 'ᚾ', 'ㄾ': 'ᚿ', 'ㄿ': 'ᛀ','ㅀ': 'ᛁ', 'ㅁ': 'ᛂ', 'ㅂ': 'ᛃ', 'ㅄ': 'ᛄ', 'ㅅ': 'ᛅ','ㅆ': 'ᛆ', 'ㅇ': 'ᛇ', 'ㅈ': 'ᛈ', 'ㅊ': 'ᛉ', 'ㅋ': 'ᛊ','ㅌ': 'ᛋ', 'ㅍ': 'ᛌ', 'ㅎ': 'ᛍ'}

special_symbols = {'?': 'ꡞ', '!': '႟', '.': '꘏', ',': '᛬'}
reverse_special = {v: k for k, v in special_symbols.items()}
reverse_chosung = {v: k for k, v in decompose_chosung.items()}
reverse_jungsung = {v: k for k, v in decompose_jungsung.items()}
reverse_jongsung = {v: k for k, v in decompose_jongsung.items()}

def is_hangul_char(char):
    return 'HANGUL' in unicodedata.name(char, '')

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
                    next_j = jamos[i+3] if i+3 < len(jamos) else ''
                    if next_j in CHOSUNG_LIST or next_j in reverse_special or next_j == '' or next_j == ' ':
                        jong = JONGSUNG_LIST.index(jamos[i+2])
                        i += 1
                result += chr(0xAC00 + cho * 588 + jung * 28 + jong)
                i += 2
            else:
                result += jamos[i]
                i += 1
        else:
            result += jamos[i]
            i += 1
    return result

# 변환: 기호 → 한글
def symbols_to_korean(symbol_input):
    jamo_result = []
    i = 0
    while i < len(symbol_input):
        ch = symbol_input[i]
        next_ch = symbol_input[i+1] if i+1 < len(symbol_input) else ''
        next_next_ch = symbol_input[i+2] if i+2 < len(symbol_input) else ''
        next_3 = symbol_input[i+3] if i+3 < len(symbol_input) else ''

        if ch == ' ':
            jamo_result.append(' ')
            i += 1
        elif ch in reverse_special:
            jamo_result.append(reverse_special[ch])
            i += 1
        elif ch in reverse_chosung and ch not in reverse_jongsung:
            if next_ch in reverse_jungsung:
                cho = reverse_chosung[ch]
                jung = reverse_jungsung[next_ch]
                jong = ''
                if next_next_ch in reverse_jongsung:
                    if next_3 in reverse_chosung or next_3 in reverse_special or next_3 == '' or next_3 == ' ':
                        jong = reverse_jongsung[next_next_ch]
                        jamo_result.extend([cho, jung, jong])
                        i += 3
                    else:
                        jamo_result.extend([cho, jung])
                        i += 2
                else:
                    jamo_result.extend([cho, jung])
                    i += 2
            else:
                jamo_result.append(reverse_chosung[ch])
                i += 1
        elif ch in reverse_jongsung:
            jamo_result.append(reverse_jongsung[ch])
            i += 1
        else:
            jamo_result.append(ch)
            i += 1
    return join_jamos_manual(jamo_result)

# 변환: 한글 → 기호
def korean_to_symbols(text):
    result = ""
    for char in text:
        if char == " ":
            result += " "
        elif char in special_symbols:
            result += special_symbols[char]
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

# 🔁 세션 히스토리 초기화
if "history" not in st.session_state:
    st.session_state.history = []

st.title("📜 고대 문자 GPT 챗봇")

# 💬 유저 입력
user_input = st.text_input("💬 기호 언어 입력")

if user_input:
    # 1️⃣ 기호 → 한글
    korean_input = symbols_to_korean(user_input)
    st.session_state.history.append(("🙋‍♂️", user_input))

    # 2️⃣ GPT 응답
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": korean_input}],
        temperature=0.7
    )
    reply_korean = response.choices[0].message.content

    # 3️⃣ 다시 기호 변환
    reply_symbol = korean_to_symbols(reply_korean)
    st.session_state.history.append(("🤖", reply_symbol))

# 📝 대화 기록 출력
for speaker, message in st.session_state.history:
    st.markdown(f"**{speaker}**: {message}")
