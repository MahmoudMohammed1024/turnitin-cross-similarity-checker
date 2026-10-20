import re
import random
from typing import List, Dict, Any

# Academic Synonym Replacements for English
EN_ACADEMIC_SYNONYMS = {
    'handled': ['processed', 'accommodated', 'managed the volume of', 'facilitated the transit of'],
    'important': ['paramount', 'pivotal', 'crucial', 'imperative', 'of vital significance'],
    'shows': ['illustrates', 'demonstrates', 'exemplifies', 'indicates', 'reveals'],
    'due to': ['attributed to', 'as a consequence of', 'owing to', 'stemming from'],
    'mainly': ['principally', 'predominantly', 'primarily', 'chiefly'],
    'leads to': ['precipitates', 'engenders', 'culminates in', 'results in'],
    'improves': ['enhances', 'optimizes', 'elevates', 'advances'],
    'strategy': ['strategic blueprint', 'tactical framework', 'overarching roadmap'],
    'project': ['initiative', 'undertaking', 'venture', 'endeavor'],
    'significant': ['substantial', 'consequential', 'noteworthy', 'marked'],
    'objective': ['target milestone', 'strategic aim', 'intended outcome'],
    'in order to': ['so as to', 'with the objective of', 'aiming to'],
    'furthermore': ['moreover', 'in addition', 'additionally', 'concomitantly'],
    'however': ['nevertheless', 'nonetheless', 'conversely', 'on the other hand'],
    'implemented': ['deployed', 'executed', 'instituted', 'operationalized'],
    'challenges': ['impediments', 'bottlenecks', 'constraints', 'hurdles'],
}

# Academic Synonym Replacements for Arabic
AR_ACADEMIC_SYNONYMS = {
    'نظرا لان': 'بالنظر الى حقيقه ان',
    'بسبب': 'جراء ذلك ونتيجة لـ',
    'يهدف المشروع الى': 'يتمحور المقصد الجوهري لهذه المبادرة حول',
    'مما يؤدي الى': 'وهو ما يسهم بصورة مباشرة في',
    'من الجدير بالذكر': 'وتجدر الاشارة في هذا الصدد الى',
    'يلعب دورا': 'يضطلع بدور محوري وفعال في',
    'تطوير': 'تعزيز والارتقاء بمستوى',
    'تنفيذ': 'حيز التطبيق العملي لـ',
    'استراتيجية': 'خارطة طريق استراتيجية',
    'تحديات': 'عقبات ومعوقات تشغيلية',
    'تحسين': 'تعظيم الكفاءة والارتقاء بـ',
    'بالاضافة الى': 'علاوة على ما تقدم وفضلاً عن',
    'اهمية': 'أهمية بالغة ومكانة جوهرية',
}


def detect_language(text: str) -> str:
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return 'ar' if arabic_chars > english_chars else 'en'


class SmartParaphraser:
    """
    Generates 3 distinct academic alternative rephrasings for flagged sentences
    specifically engineered to break Turnitin's n-gram matching patterns.
    """
    def rephrase(self, sentence: str) -> List[Dict[str, str]]:
        sentence = sentence.strip()
        if not sentence:
            return []

        lang = detect_language(sentence)

        if lang == 'en':
            return self._rephrase_english(sentence)
        else:
            return self._rephrase_arabic(sentence)

    def _rephrase_english(self, sentence: str) -> List[Dict[str, str]]:
        variations = []

        # Option 1: Academic Lexical Shift
        v1 = sentence
        replaced_count = 0
        for word, syns in EN_ACADEMIC_SYNONYMS.items():
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            if pattern.search(v1):
                choice = random.choice(syns)
                v1 = pattern.sub(choice, v1, count=1)
                replaced_count += 1
        
        if replaced_count == 0:
            v1 = f"It is noteworthy that {v1[0].lower() + v1[1:] if len(v1) > 1 else v1}"
        
        variations.append({
            'style': 'أكاديمي رصين (Scholarly Academic)',
            'style_en': 'Formal Scholarly',
            'text': v1
        })

        # Option 2: Syntactic Clause Shift / Inversion
        # Split on commas or connectors
        if ',' in sentence:
            parts = [p.strip() for p in sentence.split(',', 1)]
            v2 = f"{parts[1].capitalize()}, {parts[0].lower()}."
        else:
            words = sentence.split()
            if len(words) > 7:
                v2 = f"From an operational perspective, {' '.join(words[2:])} in relation to {words[0].lower()} {words[1].lower()}."
            else:
                v2 = f"Evidence suggests that {sentence[0].lower() + sentence[1:]}"

        variations.append({
            'style': 'إعادة هيكلة الجملة (Structural Inversion)',
            'style_en': 'Structural Inversion',
            'text': v2
        })

        # Option 3: Analytical & Direct
        v3 = sentence
        # add prefix framing
        framing = ["Specifically, ", "Crucially, ", "In practical terms, ", "Contextually, "]
        v3 = random.choice(framing) + v3[0].lower() + v3[1:]
        # apply a synonym
        for word, syns in list(EN_ACADEMIC_SYNONYMS.items())[:6]:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            if pattern.search(v3):
                v3 = pattern.sub(syns[0], v3, count=1)

        variations.append({
            'style': 'صياغة تحليلية مباشرة (Analytical Direct)',
            'style_en': 'Analytical Direct',
            'text': v3
        })

        return variations

    def _rephrase_arabic(self, sentence: str) -> List[Dict[str, str]]:
        variations = []

        # Option 1: Academic Lexical
        v1 = sentence
        for word, syn in AR_ACADEMIC_SYNONYMS.items():
            if word in v1:
                v1 = v1.replace(word, syn, 1)

        if v1 == sentence:
            v1 = f"وتجدر الإشارة في هذا السياق إلى أن {v1}"

        variations.append({
            'style': 'أكاديمي رصين (Scholarly Arabic)',
            'style_en': 'Formal Scholarly',
            'text': v1
        })

        # Option 2: Structural Inversion
        if '،' in sentence:
            parts = sentence.split('،', 1)
            v2 = f"{parts[1].strip()}؛ حيث إن {parts[0].strip()}."
        else:
            v2 = f"من المنظور الأكاديمي والعملي، نجد أن {sentence}."

        variations.append({
            'style': 'إعادة هيكلة وتقديم الفكرة (Syntactic Shift)',
            'style_en': 'Syntactic Shift',
            'text': v2
        })

        # Option 3: Concise Executive
        v3 = f"بشكل محدد، {sentence}"
        variations.append({
            'style': 'صياغة تنفيذية مباشرة (Executive Direct)',
            'style_en': 'Executive Direct',
            'text': v3
        })

        return variations
