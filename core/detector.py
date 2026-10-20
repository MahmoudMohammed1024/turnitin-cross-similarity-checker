import os
import difflib
from collections import defaultdict
from typing import List, Dict, Any, Set, Tuple

from .normalizer import normalize_text, split_into_sentences, get_ngrams
from .arabic_nlp import clean_arabic_text, calculate_arabic_similarity
from .cross_lingual import CrossLanguageDetector
from .turnitin_simulator import calculate_turnitin_prediction
from .web_checker import InternetPlagiarismChecker


class PlagiarismDetector:
    def __init__(
        self,
        min_words: int = 5,
        fuzzy_threshold: float = 0.75,
        exclude_references: bool = True,
        enable_cross_lingual: bool = True,
        check_internet: bool = False
    ):
        self.min_words = min_words
        self.fuzzy_threshold = fuzzy_threshold
        self.exclude_references = exclude_references
        self.enable_cross_lingual = enable_cross_lingual
        self.check_internet = check_internet

        self.cross_detector = CrossLanguageDetector(semantic_threshold=0.80) if enable_cross_lingual else None
        self.web_checker = InternetPlagiarismChecker(max_queries=10) if check_internet else None

    def analyze_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs comprehensive multi-engine plagiarism detection:
        1. Exact Inverted Index
        2. N-gram Shingling + Arabic NLP Stemming Fuzzy Matching
        3. Cross-Lingual & Semantic Embedding Matching (English <-> Arabic)
        4. Internet Sources Checking (Optional)
        5. Turnitin Scoring Simulation & Breakdown
        """
        doc_count = len(documents)
        if doc_count == 0:
            return {"error": "No documents provided"}

        doc_meta = {}
        for idx, doc in enumerate(documents):
            doc['id'] = idx
            doc_meta[idx] = {
                'id': idx,
                'filename': doc['filename'],
                'filepath': doc.get('filepath', ''),
                'total_words': max(1, doc['total_words']),
            }

        # 1. Segment sentences and index
        doc_sentences: Dict[int, List[Dict[str, Any]]] = {}
        exact_index = defaultdict(list)
        shingle_index = defaultdict(list)

        for doc in documents:
            d_id = doc['id']
            doc_sentences[d_id] = []
            s_counter = 0

            for p_idx, block in enumerate(doc['blocks']):
                if self.exclude_references and block.get('is_ref', False):
                    continue

                raw_text = block['text']
                sentences = split_into_sentences(raw_text)

                for raw_s in sentences:
                    norm_s = normalize_text(raw_s)
                    words = norm_s.split()
                    w_count = len(words)

                    if w_count < self.min_words:
                        continue

                    # Arabic cleaned version for NLP comparison
                    arabic_clean = clean_arabic_text(raw_s)

                    s_obj = {
                        'id': s_counter,
                        'doc_id': d_id,
                        'p_idx': p_idx,
                        'raw': raw_s,
                        'norm': norm_s,
                        'arabic_clean': arabic_clean,
                        'words': words,
                        'word_count': w_count,
                        'is_ref': block.get('is_ref', False),
                        'matches': []
                    }
                    doc_sentences[d_id].append(s_obj)

                    # Exact normalized index
                    exact_index[norm_s].append((d_id, s_counter))

                    # 4-gram shingles
                    ngrams = get_ngrams(words, n=4)
                    for ng in ngrams:
                        shingle_index[ng].append((d_id, s_counter))

                    s_counter += 1

        # 2. Exact Matches
        for norm_s, occurrences in exact_index.items():
            if len(occurrences) > 1:
                docs_involved = set(d_id for d_id, _ in occurrences)
                if len(docs_involved) > 1:
                    for d_id, s_idx in occurrences:
                        s_obj = doc_sentences[d_id][s_idx]
                        for other_d_id, other_s_idx in occurrences:
                            if other_d_id != d_id:
                                other_s = doc_sentences[other_d_id][other_s_idx]
                                s_obj['matches'].append({
                                    'other_doc_id': other_d_id,
                                    'other_filename': doc_meta[other_d_id]['filename'],
                                    'other_s_id': other_s_idx,
                                    'other_raw': other_s['raw'],
                                    'similarity': 1.0,
                                    'type': 'exact'
                                })

        # 3. Fuzzy & Arabic NLP Paraphrasing Matches
        checked_pairs = set()

        for d_id, s_list in doc_sentences.items():
            for s_obj in s_list:
                if s_obj['matches']:
                    continue

                candidates = defaultdict(int)
                ngrams = get_ngrams(s_obj['words'], n=4)
                if not ngrams:
                    continue

                for ng in ngrams:
                    for other_d_id, other_s_idx in shingle_index.get(ng, []):
                        if other_d_id != d_id:
                            candidates[(other_d_id, other_s_idx)] += 1

                min_shared_ngrams = max(1, len(ngrams) // 3)

                for (other_d_id, other_s_idx), count in candidates.items():
                    if count < min_shared_ngrams:
                        continue

                    pair_key = (min(d_id, other_d_id), max(d_id, other_d_id), s_obj['id'], other_s_idx)
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)

                    other_s = doc_sentences[other_d_id][other_s_idx]

                    # 3.1 Standard Sequence Matcher
                    seq_sim = difflib.SequenceMatcher(None, s_obj['norm'], other_s['norm']).ratio()

                    # 3.2 Arabic NLP Stemmed Similarity
                    ar_sim = 0.0
                    if s_obj['arabic_clean'] and other_s['arabic_clean']:
                        ar_sim = calculate_arabic_similarity(s_obj['arabic_clean'], other_s['arabic_clean'])

                    best_sim = max(seq_sim, ar_sim)

                    if best_sim >= self.fuzzy_threshold:
                        match_type = 'arabic_paraphrased' if ar_sim > seq_sim else 'fuzzy'
                        s_obj['matches'].append({
                            'other_doc_id': other_d_id,
                            'other_filename': doc_meta[other_d_id]['filename'],
                            'other_s_id': other_s_idx,
                            'other_raw': other_s['raw'],
                            'similarity': round(best_sim, 2),
                            'type': match_type
                        })
                        other_s['matches'].append({
                            'other_doc_id': d_id,
                            'other_filename': doc_meta[d_id]['filename'],
                            'other_s_id': s_obj['id'],
                            'other_raw': s_obj['raw'],
                            'similarity': round(best_sim, 2),
                            'type': match_type
                        })

        # 4. Optional Cross-Lingual Plagiarism Check (English <-> Arabic Translation)
        if self.enable_cross_lingual and self.cross_detector:
            # Check long unflagged sentences across different languages
            for d_id, s_list in doc_sentences.items():
                for s_obj in s_list:
                    if s_obj['matches'] or s_obj['word_count'] < 8:
                        continue
                    # sample check
                    for other_d_id, other_s_list in doc_sentences.items():
                        if other_d_id <= d_id:
                            continue
                        for other_s in other_s_list[::4]:
                            if other_s['matches'] or other_s['word_count'] < 8:
                                continue
                            c_score, method = self.cross_detector.compute_cross_lingual_similarity(
                                s_obj['raw'], other_s['raw']
                            )
                            if c_score >= 0.80:
                                s_obj['matches'].append({
                                    'other_doc_id': other_d_id,
                                    'other_filename': doc_meta[other_d_id]['filename'],
                                    'other_s_id': other_s['id'],
                                    'other_raw': other_s['raw'],
                                    'similarity': round(c_score, 2),
                                    'type': 'cross_lingual'
                                })
                                other_s['matches'].append({
                                    'other_doc_id': d_id,
                                    'other_filename': doc_meta[d_id]['filename'],
                                    'other_s_id': s_obj['id'],
                                    'other_raw': s_obj['raw'],
                                    'similarity': round(c_score, 2),
                                    'type': 'cross_lingual'
                                })

        # 5. Live Internet & Publications Search
        doc_internet_results = {}
        should_check_web = self.check_internet or (doc_count == 1)
        if should_check_web:
            if not self.web_checker:
                self.web_checker = InternetPlagiarismChecker(max_queries=45)

            for d_id, s_list in doc_sentences.items():
                net_res = self.web_checker.check_document_internet(s_list)
                doc_internet_results[d_id] = net_res

                # Attach internet and publication matches directly to matching sentences
                s_map = {s['id']: s for s in s_list}
                for m in net_res.get('internet_matches', []):
                    s_id = m.get('sentence_id')
                    target_s = s_map.get(s_id)
                    if target_s:
                        is_pub = (m.get('type') == 'publication')
                        prefix = "📚 دورية علمية" if is_pub else "🌐 إنترنت"
                        target_s['matches'].append({
                            'other_doc_id': -1,
                            'other_filename': f"{prefix} ({m['domain']})",
                            'other_s_id': -1,
                            'other_raw': m.get('snippet', m['text']),
                            'similarity': round(m.get('overlap', 0.8), 2),
                            'type': 'publication' if is_pub else 'internet',
                            'url': m.get('url', ''),
                            'domain': m.get('domain', '')
                        })

        # 6. Turnitin Simulation & Pairwise Stats
        pairwise_shared_words = defaultdict(lambda: defaultdict(int))
        doc_stats = []
        total_flagged_sentences_all = 0

        for d_id, s_list in doc_sentences.items():
            flagged_sentences = []
            matched_words_set = 0
            sources_summary = defaultdict(lambda: {
                'count': 0, 'words': 0, 'url': '', 'domain': '', 'other_doc_id': -1, 'type': 'internet'
            })

            for s in s_list:
                if s['matches']:
                    total_flagged_sentences_all += 1
                    matched_words_set += s['word_count']
                    best_match = max(s['matches'], key=lambda m: m['similarity'])
                    flagged_sentences.append({
                        'sentence_id': s['id'],
                        'paragraph_idx': s['p_idx'],
                        'text': s['raw'],
                        'word_count': s['word_count'],
                        'best_similarity': best_match['similarity'],
                        'best_type': best_match['type'],
                        'best_other_file': best_match['other_filename'],
                        'matches': s['matches']
                    })

                    seen_docs_for_sentence = set()
                    for m in s['matches']:
                        o_id = m['other_doc_id']
                        if o_id not in seen_docs_for_sentence:
                            seen_docs_for_sentence.add(o_id)
                            if o_id != -1:
                                pairwise_shared_words[d_id][o_id] += s['word_count']

                            src_name = m['other_filename']
                            sources_summary[src_name]['count'] += 1
                            sources_summary[src_name]['words'] += s['word_count']
                            sources_summary[src_name]['other_doc_id'] = o_id
                            if m.get('url'):
                                sources_summary[src_name]['url'] = m['url']
                            if m.get('domain'):
                                sources_summary[src_name]['domain'] = m['domain']

                            if o_id != -1:
                                sources_summary[src_name]['type'] = 'student_papers'
                            else:
                                sources_summary[src_name]['type'] = m.get('type', 'publication' if 'دورية' in src_name else 'internet')

            total_words = doc_meta[d_id]['total_words']
            net_info = doc_internet_results.get(d_id, {
                'internet_matches': [], 'internet_percentage': 0.0, 'matched_domains': []
            })

            # Calculate actual matched words per category directly from flagged sentences
            pub_words = sum(s['word_count'] for s in flagged_sentences if s.get('best_type') == 'publication')
            net_words = sum(s['word_count'] for s in flagged_sentences if s.get('best_type') == 'internet')
            internal_words = sum(s['word_count'] for s in flagged_sentences if any(m.get('other_doc_id', -1) != -1 for m in s['matches']))

            # Flagged sentences count is strictly the actual number of flagged sentences
            effective_flagged_sentences = len(flagged_sentences)
            effective_matched_words = matched_words_set

            turnitin_pred = calculate_turnitin_prediction(
                internal_match_words=internal_words,
                internet_match_words=net_words,
                publication_match_words=pub_words,
                total_words=total_words,
                flagged_sentences=flagged_sentences
            )

            sim_percentage = float(turnitin_pred['overall_similarity_index'])

            top_sources = []
            for src_name, data in sorted(sources_summary.items(), key=lambda x: x[1]['words'], reverse=True):
                if doc_count == 1 and matched_words_set > 0:
                    src_share = data['words'] / matched_words_set
                    src_pct = round(src_share * sim_percentage, 1)
                    src_words = int(total_words * (src_pct / 100.0))
                else:
                    src_pct = round((data['words'] / total_words) * 100, 1)
                    src_words = data['words']

                s_type = data.get('type')
                if data.get('other_doc_id', -1) != -1:
                    s_type = 'student_papers'
                elif not s_type or s_type not in ('publication', 'internet'):
                    s_type = 'publication' if 'دورية' in src_name else 'internet'

                top_sources.append({
                    'other_doc_id': data.get('other_doc_id', -1),
                    'other_filename': src_name,
                    'shared_words': src_words,
                    'shared_sentences': data['count'],
                    'percentage': src_pct,
                    'url': data.get('url', ''),
                    'domain': data.get('domain', ''),
                    'type': s_type
                })

            if sim_percentage >= 25.0:
                doc_risk = 'high'
            elif sim_percentage >= 15.0:
                doc_risk = 'moderate'
            else:
                doc_risk = 'low'

            doc_stats.append({
                'id': d_id,
                'filename': doc_meta[d_id]['filename'],
                'filepath': doc_meta[d_id]['filepath'],
                'total_words': total_words,
                'total_sentences': len(s_list),
                'flagged_sentences_count': effective_flagged_sentences,
                'flagged_words_count': effective_matched_words,
                'similarity_percentage': sim_percentage,
                'risk': doc_risk,
                'turnitin_pred': turnitin_pred,
                'internet_info': net_info,
                'top_sources': top_sources,
                'flagged_sentences': flagged_sentences
            })

        doc_stats.sort(key=lambda x: x['turnitin_pred']['overall_similarity_index'], reverse=True)

        # Pairwise matrix
        matrix = []
        matrix_header = [doc_meta[i]['filename'] for i in range(doc_count)]
        for i in range(doc_count):
            row = []
            for j in range(doc_count):
                if i == j:
                    row.append(100.0)
                else:
                    shared_w = pairwise_shared_words[i][j]
                    pct = round((shared_w / doc_meta[i]['total_words']) * 100, 1)
                    row.append(min(100.0, pct))
            matrix.append(row)

        high_risk_count = sum(1 for d in doc_stats if d['turnitin_pred']['overall_similarity_index'] >= 50)
        moderate_risk_count = sum(1 for d in doc_stats if 25 <= d['turnitin_pred']['overall_similarity_index'] < 50)
        safe_count = sum(1 for d in doc_stats if d['turnitin_pred']['overall_similarity_index'] < 25)
        avg_turnitin = round(sum(d['turnitin_pred']['overall_similarity_index'] for d in doc_stats) / max(1, doc_count), 1)

        return {
            'summary': {
                'total_documents': doc_count,
                'high_risk_count': high_risk_count,
                'moderate_risk_count': moderate_risk_count,
                'safe_count': safe_count,
                'average_similarity': avg_turnitin,
                'total_flagged_sentences': total_flagged_sentences_all,
            },
            'documents': doc_stats,
            'matrix': {
                'filenames': matrix_header,
                'data': matrix
            }
        }
