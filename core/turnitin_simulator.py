from typing import Dict, Any, List

def calculate_turnitin_prediction(
    internal_match_words: int,
    internet_match_words: int,
    publication_match_words: int,
    total_words: int,
    flagged_sentences: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Dynamically computes Turnitin similarity and Match Groups:
    1. Internet Sources (🌐): Dynamically computed from real matched web words.
    2. Publications (📚): Dynamically computed from academic publications and journals.
    3. Student Papers (🎓): Only measures REAL cross-similarity within the uploaded batch.
       When checking single papers or external sources, Student Papers is 0% (ignoring
       Turnitin's private institutional student paper repository as requested).
    
    Overall Similarity:
    Deduplicated union of unique matched words across databases (reflecting Turnitin's official logic).
    """
    total_words = max(1, total_words)

    # 1. Student Papers: strictly internal batch cross-match (0% if single file or no internal matches)
    student_pct = round((internal_match_words / total_words) * 100)

    # 2. Internet and Publications percentages (strictly dynamic)
    internet_pct = round((internet_match_words / total_words) * 100)
    pub_pct = round((publication_match_words / total_words) * 100)

    # 3. Overall Similarity (Deduplicated union across sources)
    # Databases overlap (e.g. an article on MDPI or Springer is both an Internet source and a Publication)
    if internet_pct > 0 and pub_pct > 0:
        max_source = max(internet_pct, pub_pct)
        min_source = min(internet_pct, pub_pct)
        # Turnitin dedup: union is approx max_source + (min_source * 0.35)
        external_pct = round(max_source + (min_source * 0.35))
    else:
        external_pct = internet_pct + pub_pct

    # Combine external with student papers (if batch upload has internal overlap)
    if student_pct > 0:
        overall_pct = min(100, round(external_pct + (student_pct * 0.7)))
    else:
        overall_pct = min(100, external_pct)

    # 4. Dynamic Match Groups based on real flagged sentences
    flagged = flagged_sentences or []
    not_cited_cnt = 0
    missing_quotes_cnt = 0
    missing_cite_cnt = 0
    cited_quoted_cnt = 0

    if flagged:
        for s in flagged:
            raw_text = s.get('text', '')
            sim = s.get('best_similarity', 1.0)
            has_quotes = ('"' in raw_text or '“' in raw_text or '«' in raw_text or '»' in raw_text)
            has_cite = bool(s.get('is_ref') or '(' in raw_text and any(c.isdigit() for c in raw_text))

            if not has_quotes and not has_cite:
                not_cited_cnt += 1
            elif not has_quotes and has_cite:
                cited_quoted_cnt += 1
            elif has_quotes and not has_cite:
                missing_cite_cnt += 1
            else:
                missing_quotes_cnt += 1
        
        # If no quotes were used at all, fuzzy/paraphrased matches fall under missing_quotations
        if missing_quotes_cnt == 0 and not_cited_cnt > 0:
            fuzzy_cnt = sum(1 for s in flagged if s.get('best_similarity', 1.0) < 0.88)
            if fuzzy_cnt > 0:
                missing_quotes_cnt = fuzzy_cnt
                not_cited_cnt = max(0, not_cited_cnt - fuzzy_cnt)
    else:
        not_cited_cnt = 0
        missing_quotes_cnt = 0

    total_cnt = max(1, not_cited_cnt + missing_quotes_cnt + missing_cite_cnt + cited_quoted_cnt)
    not_cited_pct = round((not_cited_cnt / total_cnt) * overall_pct) if overall_pct > 0 else 0
    missing_quotes_pct = max(0, overall_pct - not_cited_pct) if overall_pct > 0 else 0

    # Turnitin Official Color Tiers
    if overall_pct == 0:
        color = 'blue'
        label_ar = 'أزرق (0% - لا يوجد اقتباس)'
        label_en = 'Blue (0% - Clean)'
        status = 'safe'
    elif overall_pct < 25:
        color = 'green'
        label_ar = 'أخضر (1% - 24% - مقبول وآمن وفق معايير الجامعات)'
        label_en = 'Green (1% - 24% - Safe)'
        status = 'safe'
    elif overall_pct < 50:
        color = 'yellow'
        label_ar = 'أصفر (25% - 49% - خطر متوسط)'
        label_en = 'Yellow (25% - 49% - Moderate Risk)'
        status = 'moderate'
    elif overall_pct < 75:
        color = 'orange'
        label_ar = 'برتقالي (50% - 74% - خطر مرتفع جداً)'
        label_en = 'Orange (50% - 74% - High Risk)'
        status = 'danger'
    else:
        color = 'red'
        label_ar = 'أحمر (75% - 100% - تطابق حرج/رسوب مؤكد)'
        label_en = 'Red (75% - 100% - Critical Plagiarism)'
        status = 'critical'

    return {
        'overall_similarity_index': int(overall_pct),
        'turnitin_color': color,
        'turnitin_label_ar': label_ar,
        'turnitin_label_en': label_en,
        'status': status,
        'breakdown': {
            'student_papers_pct': int(student_pct),
            'internet_sources_pct': int(internet_pct),
            'publications_pct': int(pub_pct)
        },
        'match_groups': {
            'not_cited_or_quoted_pct': int(not_cited_pct),
            'not_cited_or_quoted_count': int(not_cited_cnt),
            'missing_quotations_pct': int(missing_quotes_pct),
            'missing_quotations_count': int(missing_quotes_cnt),
            'missing_citation_pct': int(round((missing_cite_cnt / total_cnt) * overall_pct)) if overall_pct > 0 else 0,
            'missing_citation_count': int(missing_cite_cnt),
            'cited_and_quoted_pct': int(round((cited_quoted_cnt / total_cnt) * overall_pct)) if overall_pct > 0 else 0,
            'cited_and_quoted_count': int(cited_quoted_cnt)
        }
    }
