import re
from typing import List, Dict, Any, Optional, Tuple

# Pre-defined cross-lingual semantic anchor concepts (English <-> Arabic academic terms)
ACADEMIC_CROSS_DICT = {
    'airport': 'مطار', 'biometrics': 'بيومتري', 'passenger': 'مسافر', 'passengers': 'ركاب',
    'traffic': 'حركة', 'digital': 'رقمي', 'transformation': 'تحول', 'project': 'مشروع',
    'strategy': 'استراتيجية', 'management': 'ادارة', 'stakeholder': 'اصحاب المصلحة',
    'implementation': 'تنفيذ', 'matrix': 'مصفوفة', 'evaluation': 'تقييم',
    'culture': 'ثقافة', 'organization': 'منظمة', 'leadership': 'قيادة',
    'performance': 'اداء', 'efficiency': 'كفاءة', 'security': 'امان',
    'technology': 'تكنولوجيا', 'sustainable': 'مستدام', 'supply': 'توريد',
    'chain': 'سلسلة', 'analysis': 'تحليل', 'risk': 'مخاطر', 'framework': 'اطار عمل'
}

_MODEL = None
_CHECKED_MODEL = False

def get_multilingual_model():
    """
    Checks for locally cached sentence-transformer model without blocking the network.
    """
    global _MODEL, _CHECKED_MODEL
    if _CHECKED_MODEL:
        return _MODEL

    _CHECKED_MODEL = True
    try:
        from sentence_transformers import SentenceTransformer
        # Try loading only if already downloaded/cached locally
        _MODEL = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            local_files_only=True
        )
        return _MODEL
    except Exception:
        _MODEL = None
        return None


def detect_language(text: str) -> str:
    """
    Detects whether text is primarily Arabic or English.
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    if arabic_chars > english_chars:
        return 'ar'
    return 'en'


class CrossLanguageDetector:
    """
    Detects cross-lingual plagiarism (English <-> Arabic translation)
    and deep semantic paraphrasing.
    """
    def __init__(self, semantic_threshold: float = 0.80):
        self.semantic_threshold = semantic_threshold

    def compute_cross_lingual_similarity(self, text1: str, text2: str) -> Tuple[float, str]:
        """
        Calculates similarity between two sentences, even if one is English and the other is Arabic.
        Returns: (similarity_score, detection_method)
        """
        lang1 = detect_language(text1)
        lang2 = detect_language(text2)
        is_cross = (lang1 != lang2)

        # 1. Try Neural Multilingual Model if locally cached
        model = get_multilingual_model()
        if model is not None:
            try:
                embeddings = model.encode([text1, text2], normalize_embeddings=True)
                cosine = float(embeddings[0] @ embeddings[1])
                method = 'cross_lingual_neural' if is_cross else 'semantic_neural'
                return cosine, method
            except Exception:
                pass

        # 2. Heuristic Cross-Lingual Concept Alignment (Instant & 100% Offline)
        if is_cross:
            en_text = text1.lower() if lang1 == 'en' else text2.lower()
            ar_text = text1 if lang1 == 'ar' else text2

            matches = 0
            total_anchors = 0
            for en_word, ar_word in ACADEMIC_CROSS_DICT.items():
                if en_word in en_text:
                    total_anchors += 1
                    if ar_word in ar_text:
                        matches += 1

            if total_anchors >= 2:
                score = matches / total_anchors
                return score, 'cross_lingual_heuristic'

        return 0.0, 'none'
