import re
from typing import List, Tuple

# Common abbreviations in English to avoid splitting sentences improperly
ABBREVIATIONS = {
    'e.g', 'i.e', 'etc', 'et al', 'dr', 'mr', 'mrs', 'ms', 'prof', 'fig', 'no', 'vol', 'vs', 'dept', 'inc', 'corp', 'co', 'ltd'
}

def normalize_text(text: str) -> str:
    """
    Normalizes both Arabic and English text:
    - Removes Arabic diacritics (tashkeel), tatweel (kashida).
    - Normalizes Arabic letters (alef, yaa, taa marbuta).
    - Converts English to lowercase.
    - Removes punctuation and standardizes whitespace.
    """
    if not text:
        return ""

    # 1. Arabic diacritics (tashkeel) and tatweel
    text = re.sub(r'[\u064B-\u0652\u0640\u0670]', '', text)

    # 2. Arabic letter unification
    text = re.sub(r'[إأآٱ]', 'ا', text)
    text = re.sub(r'[ة]', 'ه', text)
    text = re.sub(r'[ى]', 'ي', text)

    # 3. Lowercase English
    text = text.lower()

    # 4. Remove punctuation & special characters
    text = re.sub(r'[^\w\s]', ' ', text)

    # 5. Collapse spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into meaningful sentences preserving both Arabic and English boundaries.
    Handles common abbreviations gracefully.
    """
    if not text or not text.strip():
        return []

    # Protect common abbreviations by temporarily substituting dots
    temp_text = text
    for abbr in ABBREVIATIONS:
        # e.g. "et al." -> "et al<DOT>"
        pattern = re.compile(rf'\b({re.escape(abbr)})\.', re.IGNORECASE)
        temp_text = pattern.sub(r'\1<DOT>', temp_text)

    # Also protect decimal numbers like 95.2 or 3.14
    temp_text = re.sub(r'(\d+)\.(\d+)', r'\1<DOT>\2', temp_text)

    # Split on sentence terminators: . ! ? ؟ \n
    # Note: semicolon (;) and arabic semicolon (؛) can also separate clauses
    raw_sentences = re.split(r'[\.\!\?\u061f\n\r]+', temp_text)

    cleaned_sentences = []
    for s in raw_sentences:
        # Restore dot
        s = s.replace('<DOT>', '.')
        s_clean = s.strip()
        if s_clean:
            cleaned_sentences.append(s_clean)

    return cleaned_sentences

def get_ngrams(words: List[str], n: int = 5) -> List[Tuple[str, ...]]:
    """
    Returns n-grams of words for shingling.
    """
    if len(words) < n:
        return [tuple(words)] if words else []
    return [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
