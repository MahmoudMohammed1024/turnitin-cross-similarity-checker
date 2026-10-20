import re
from typing import List, Set

# Comprehensive Arabic Diacritics and Marks
ARABIC_DIACRITICS = re.compile(r"""
    [\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]
""", re.VERBOSE)

# Tatweel / Kashida
TATWEEL = '\u0640'

# Common Arabic Stop Words (can be used for keyword filtering)
ARABIC_STOPWORDS = {
    'في', 'من', 'على', 'إلى', 'الي', 'عن', 'مع', 'هذا', 'هذه', 'هؤلاء', 'ذلك', 'تلك',
    'التي', 'الذي', 'الذين', 'اللاتي', 'اللواتي', 'هو', 'هي', 'هم', 'هن', 'نحن', 'أنا',
    'أنت', 'أنتم', 'كان', 'كانت', 'يكون', 'تكون', 'أن', 'إن', 'ما', 'لا', 'لم', 'لن',
    'قد', 'ثم', 'أو', 'أم', 'بل', 'لكن', 'كل', 'بعض', 'غير', 'سوى', 'بين', 'حيث',
    'كلما', 'عندما', 'حين', 'إذا', 'لو', 'لولا', 'كيف', 'ماذا', 'لماذا', 'متى', 'أين'
}

# Arabic Prefixes and Suffixes for Light Stemming (inspired by Khoja / Larkey light stemmer)
ARABIC_PREFIXES = ['كال', 'فال', 'بال', 'ولل', 'فلل', 'وال', 'ال', 'لل', 'فب', 'وب']
ARABIC_SUFFIXES = ['كما', 'هما', 'تان', 'تين', 'وان', 'وين', 'ون', 'ين', 'ات', 'ان', 'هم', 'هن', 'كم', 'نا', 'ها', 'ية', 'يه', 'ه', 'ي']


def clean_arabic_text(text: str) -> str:
    """
    Cleans and standardizes Arabic text:
    - Removes Tashkeel (harakat), Tanween, Shadda, Sukun
    - Removes Tatweel / Kashida
    - Normalizes Alef forms (أ, إ, آ, ٱ -> ا)
    - Normalizes Taa Marbuta (ة -> ه)
    - Normalizes Yaa (ى -> ي)
    - Cleans punctuation and excess spacing
    """
    if not text:
        return ""

    # 1. Remove diacritics
    text = ARABIC_DIACRITICS.sub('', text)

    # 2. Remove Tatweel
    text = text.replace(TATWEEL, '')

    # 3. Normalize Alef
    text = re.sub(r'[إأآٱ]', 'ا', text)

    # 4. Normalize Taa Marbuta
    text = re.sub(r'ة', 'ه', text)

    # 5. Normalize Yaa / Alef Maqsura
    text = re.sub(r'ى', 'ي', text)

    # 6. Normalize Arabic punctuation to spaces or standard
    text = re.sub(r'[،؛؟«»""\'\(\)\[\]\{\}\.:\-–—]', ' ', text)

    # 7. Collapse spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def arabic_light_stem(word: str) -> str:
    """
    Performs light stemming on Arabic words by stripping common affixes (prefixes/suffixes)
    without corrupting short root words (length >= 3).
    """
    if len(word) <= 3:
        return word

    # Strip prefixes
    for pre in ARABIC_PREFIXES:
        if word.startswith(pre) and len(word) - len(pre) >= 3:
            word = word[len(pre):]
            break

    # Strip suffixes
    for suf in ARABIC_SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            word = word[:-len(suf)]
            break

    return word


def get_arabic_stemmed_tokens(text: str, remove_stopwords: bool = False) -> List[str]:
    """
    Tokenizes and light-stems Arabic text for deep linguistic similarity checking.
    """
    clean = clean_arabic_text(text)
    words = clean.split()
    tokens = []
    for w in words:
        if remove_stopwords and w in ARABIC_STOPWORDS:
            continue
        stemmed = arabic_light_stem(w)
        tokens.append(stemmed)
    return tokens


def calculate_arabic_similarity(s1: str, s2: str) -> float:
    """
    Computes a hybrid Jaccard + Overlap similarity using Arabic light stemmed tokens.
    Catches Arabic paraphrased sentences where words have different prefixes/suffixes/conjugations!
    """
    tokens1 = set(get_arabic_stemmed_tokens(s1))
    tokens2 = set(get_arabic_stemmed_tokens(s2))

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    overlap = intersection / min(len(tokens1), len(tokens2))
    jaccard = intersection / union

    # Weighted combination
    return 0.6 * overlap + 0.4 * jaccard
