import streamlit as st
import streamlit.components.v1 as components

# ===== 한글 자모 및 기호 매핑 =====

CHOSUNG_LIST = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
                "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
JUNGSUNG_LIST = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
                 "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
JONGSUNG_LIST = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ",
                 "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ",
                 "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

initial_map = {
    'ㄱ': '𐎀', 'ㄴ': '𐎐', 'ㄷ': '𐎂', 'ㄹ': '𐎑', 'ㅁ': '𐎄',
    'ㅂ': '𐎅', 'ㅅ': '𐎃', 'ㅇ': '𐎊', 'ㅈ': '𐎆', 'ㅊ': '𐎇',
    'ㅋ': '𐎚', 'ㅌ': '𐎛', 'ㅍ': '𐎜', 'ㅎ': '𐎟'
}
final_map = {
    'ㄱ': '𐎰', 'ㄴ': '𐎱', 'ㄷ': '𐎲', 'ㄹ': '𐎳', 'ㅁ': '𐎴',
    'ㅂ': '𐎵', 'ㅅ': '𐎶', 'ㅇ': '𐎷', 'ㅈ': '𐎸', 'ㅊ': '𐎹',
    'ㅋ': '𐎺', 'ㅌ': '𐎻', 'ㅍ': '𐎼', 'ㅎ': '𐎽'
}
vowel_map = {
    'ㅏ': '𐎠', 'ㅑ': '𐎢', 'ㅓ': '𐎤', 'ㅕ': '𐎦', 'ㅗ': '𐎨',
    'ㅛ': '𐎩', 'ㅜ': '𐎪', 'ㅠ': '𐎫', 'ㅡ': '𐎬', 'ㅣ': '𐎭',
    'ㅐ': '𐎡', 'ㅒ': '𐎣', 'ㅔ': '𐎥', 'ㅖ': '𐎧'
}
rev_initial = {v: k for k, v in initial_map.items()}
rev_final = {v: k for k, v in final_map.items()}
rev_vowel = {v: k for k, v in vowel_map.items()}

# 자모 → 완성형 한글
def combine_jamos(cho, jung, jong):
    cho_i = CHOSUNG_LIST.index(cho)
    jung_i = JUNGSUNG_LIST.index(jung)
    jong_i = JONGSUNG_LIST.index(jong) if jong else 0
    return chr(0xAC00 + (cho_i * 21 * 28) + (jung_i * 28) + jong_i)

# 기호 → 한글 해석
def decode_symbols(symbol_text):
    jamos = []
    for ch in symbol_text:
        if ch in rev_initial:
            jamos.append(("초", rev_initial[ch]))
        elif ch in rev_vowel:
            jamos.append(("중", rev_vowel[ch]))
        elif ch in rev_final:
            jamos.append(("종", rev_final[ch]))
        else:
            jamos.append(("기타", ch))

    result = ""
    i = 0
    while i < len(jamos):
        if i + 1 < len(jamos) and jamos[i][0] == "초" and jamos[i+1][0] == "중":
            cho = jamos[i][1]
            jung = jamos[i+1][1]
            jong = ""
            if i + 2 < len(jamos) and jamos[i+2][0] == "종":
                jong = jamos[i+2][1]
                i += 3
            else:
                i += 2
            result += combine_jamos(cho, jung, jong)
        else:
            result += jamos[i][1]
            i += 1
    return result

# 한글 → 기호 변환
def encode_hangul(text):
    result = ""
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            base = code - 0xAC00
            cho = CHOSUNG_LIST[base // 588]
            jung = JUNGSUNG_LIST[(base % 588) // 28]
            jong = JONGSUNG_LIST[base % 28]
            result += initial_map.get(cho, cho)
            result += vowel_map.get(jung, jung)
            if jong:
                result += final_map.get(jong, jong)
        else:
            result += ch
    return result

# ========== Streamlit 챗봇 UI ==========

st.title("💬 기호 언어 챗봇")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("기호로 메시지를 입력해보세요:")

if st.button("보내기"):
    if user_input.strip():
        decoded = decode_symbols(user_input)
        st.session_state.messages.append(("🧑", user_input, decoded))

        # GPT 대신 간단한 로컬 응답
        if "날씨" in decoded:
            reply = "오늘 날씨는 맑고 따뜻해요!"
        else:
            reply = f"'{decoded}'라는 말, 정말 멋지네요!"

        encoded = encode_hangul(reply)
        st.session_state.messages.append(("🤖", encoded, reply))

# 대화 출력
for speaker, symbol_msg, decoded_msg in st.session_state.messages:
    st.markdown(f"**{speaker}**: {symbol_msg}")
    st.caption(f"({decoded_msg})")
