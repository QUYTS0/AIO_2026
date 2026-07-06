import langcodes
import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory, LangDetectException
from nltk.tokenize import TreebankWordDetokenizer, wordpunct_tokenize
from spellchecker import SpellChecker

DetectorFactory.seed = 0    # Đặt hạt giống để đảm bảo kết quả phát hiện ngôn ngữ nhất quán
MIN_INPUT_LENGTH = 3        # Độ dài đầu vào tối thiểu để phát hiện ngôn ngữ


SPELL_LANGS = {
"en", "es", "fr", "pt", "de",
"ru", "ar", "eu", "lv", "nl"
}

TARGET_LANGS = {
"Vietnamese": "vi",
"English": "en",
"French": "fr",
"Japanese": "ja",
"Chinese": "zh-CN",
"Korean": "ko",
"Spanish": "es",
"German": "de",
}

EXAMPLES_T = [
"Every morning, I drink a cup of coffee.",
"Bonjour, comment allez-vous?",
"Xin chao, hom nay troi dep qua.",
]

EXAMPLES_S = [
"Yesturday, I recieveed a mesage from my freind.",
"Definately a great oppurtunity.",
"Je voudraiis allerr au marchee.",
]

# Các hàm bên dưới hỗ trợ giúp khởi tạo SpellChecker, phát hiện ngôn ngữ thành tên dễ đọc, và xử lý trường hợp không phát hiện được ngôn ngữ.
@st.cache_resource(show_spinner=False)
def get_spellchecker(lang_code):
    return SpellChecker(language=lang_code)

def language_name(lang_code):
    try:
        return langcodes.Language.get(lang_code).language_name()
    except Exception:
        return lang_code or "Unknown"
    
def detect_language(raw):
    try:
        return detect(raw)
    except LangDetectException:
        return None
    
# ===== Hàm sửa lỗi chính tả =====
# This function takes a text input and a language code, then uses the SpellChecker library to correct any typos in the text.
# It tokenizes the input text, checks each token for spelling errors, and applies corrections while preserving the original casing of the words. 
# Finally, it returns the corrected text along with a boolean indicating whether any changes were made.

def fix_typos(text, lang_code):
    spell = get_spellchecker(lang_code)
    tokens = wordpunct_tokenize(text)
    fixed = []
    
    for token in tokens:
        if token.isalpha() and len(token) > 1: # Chỉ sửa các từ có độ dài lớn hơn 1
            suggestion = spell.correction(token.lower()) or token
            suggestion = suggestion.title() if token.istitle() else suggestion
            suggestion = suggestion.upper() if token.isupper() else suggestion
            fixed.append(suggestion)
        else:
            fixed.append(token)
        
    return TreebankWordDetokenizer().detokenize(fixed), fixed != tokens

# ===== Pipeline dịch văn bản =====
# This function orchestrates the translation process. It first checks if the input text meets the minimum length requirement.
# Then, it detects the language of the input text. If the detected language matches the target language, it attempts to fix any typos in the text.
# If the detected language is different from the target language, it uses the GoogleTranslator to translate the text into the target language. 
# The function returns a dictionary containing the results of the translation process, including any errors encountered.
# NOTE: GoogleTranslator need internet connection to work properly.

def run_translation(text, target_lang_code):
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        return {"ok": False, "error": f"Vui lòng nhập văn bản có độ dài ít nhất {MIN_INPUT_LENGTH} ký tự."}
    
    # Bước 1: Phát hiện ngôn ngữ
    detected_lang_code = detect_language(raw)
    if detected_lang_code is None:
        return {"ok": False, "error": "Không thể phát hiện ngôn ngữ. Vui lòng thử lại với văn bản khác."}

    # Bước 2: Sửa lỗi chính tả nếu ngôn ngữ được hỗ trợ
    if detected_lang_code == target_lang_code:
        fixed_text, changed = fix_typos(raw, detected_lang_code)
        if changed:
            st.info(f"Đã sửa lỗi chính tả: {fixed_text}")
            raw = fixed_text

        return {
            "ok": True,
            "detected_lang_code": detected_lang_code,
            "target_lang_code": target_lang_code,
            "language_name": language_name(detected_lang_code),
            "translated_text": raw,
            "fixed_text": fixed_text if changed else None,
            "message": "Văn bản đã ở ngôn ngữ mục tiêu. Không cần dịch."
        }
    
    # Bước 3: Dịch văn bản sang ngôn ngữ mục tiêu
    try:
        translated_text = GoogleTranslator(source=detected_lang_code, target=target_lang_code).translate(raw)
    except Exception as e:
        st.error(f"Lỗi khi dịch văn bản: {e}")
        return {"ok": False, "error": f"Lỗi khi dịch văn bản: {e}"}

    return {
        "ok": True, 
        "detected_lang": language_name(detected_lang_code), 
        "target_lang": language_name(target_lang_code), 
        "translated_text": translated_text
        }


# ===== Pipeline sửa lỗi chính tả =====
# This pipeline function takes a text input and attempts to correct any spelling errors based on the detected language.
# It first checks if the input text meets the minimum length requirement, then detects the language of the input text.
# If the detected language is supported for spellchecking, it uses the fix_typos function to correct any typos.
# The function returns a dictionary containing the results of the spellchecking process, including any errors encountered and the corrected text if changes were made.
# NOTE: The function only supports spellchecking for specific languages defined in the SPELL_LANGS set.
# NOTE: pyspellchecker does not support Vietnamese, we can use `underthesea` or `pyvi` for Vietnamese spellchecking, but they are not included in this implementation.

def run_spellcheck(text, lang_code):
    raw = text.strip()
    if len(raw) < MIN_INPUT_LENGTH:
        return {"ok": False, "error": f"Vui lòng nhập văn bản có độ dài ít nhất {MIN_INPUT_LENGTH} ký tự."}
    
    detected_lang_code = detect_language(raw)
    if detected_lang_code is None:
        return {"ok": False, "error": "Không thể phát hiện ngôn ngữ. Vui lòng thử lại với văn bản khác."}
    
    if detected_lang_code not in SPELL_LANGS:
        return {"ok": False, "error": f"Ngôn ngữ '{language_name(detected_lang_code)}' không được hỗ trợ để sửa lỗi chính tả."}
    
    fixed_text, changed = fix_typos(raw, detected_lang_code)
    return {
        "ok": True,
        "detected_lang": language_name(detected_lang_code),
        "fixed_text": fixed_text,
        "changed": changed
    }


# ===== Create main UI with Streamlit =====
st.set_page_config(page_title="Text Translator $ Spell Checker", page_icon="🌐", layout="centered")
st.title("🌐 Text Translator & Spell Checker")
st.caption("A simple app to translate text and check spelling errors using Google Translator and pyspellchecker.")

tab_t, tab_s = st.tabs(["Translate Text", "Spell Check"])

with tab_t:
    st.session_state.setdefault("res_t", None)
    with st.expander("Examples for Translation"):
        for ex in EXAMPLES_T:
            st.code(ex, language="text")

    with st.form("form_translate"):
        text_t = st.text_area("Enter text to translate:", height=150, placeholder="Type or paste your text here...")
    
        target_lang = st.selectbox("Select target language:", list(TARGET_LANGS.keys()))
        submitted_t = st.form_submit_button("Translate", type='primary')
    
    if submitted_t:
        target_lang_code = TARGET_LANGS[target_lang]
        st.session_state['res_t'] = run_translation(text_t, target_lang_code)
        
    res = st.session_state.get("res_t")

    if res:
        if res["ok"]:
            st.caption(f"""
                       Detected Language: {res['detected_lang_code']},
                       Target Language: {res['target_lang_code']},
                       """)
            st.caption(f"Translated Text: {res["translated_text"]}")

            if res.get("message"):
                st.info(res['message'])
        
        else:
            st.warning(res['error'])


