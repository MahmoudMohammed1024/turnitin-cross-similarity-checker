import os
import difflib
from collections import defaultdict
from typing import List, Dict, Any

try:
    import docx
except ImportError:
    docx = None


class TableAuditDetector:
    """
    Dedicated detector for shared tables, matrices, and frameworks across student assignments.
    Identifies if multiple papers share identical table cells or structures (the #1 cause of the 80% jump!).
    """
    def __init__(self, table_similarity_threshold: float = 0.60):
        self.table_similarity_threshold = table_similarity_threshold

    def extract_tables_from_docx(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Extracts structured tables with cell text and dimensions.
        """
        if not docx or not os.path.exists(filepath):
            return []

        tables = []
        try:
            doc = docx.Document(filepath)
            for t_idx, tbl in enumerate(doc.tables):
                # Safely extract text from all cells
                cells = []
                for tc in tbl._tbl.xpath('.//w:tc'):
                    txt = ''.join(tc.itertext()).strip()
                    if txt:
                        cells.append(txt)

                if len(cells) >= 3:
                    full_text = ' '.join(cells)
                    tables.append({
                        'table_idx': t_idx + 1,
                        'cell_count': len(cells),
                        'cells': cells,
                        'full_text': full_text,
                        'word_count': len(full_text.split()),
                        'snippet': full_text[:120] + ('...' if len(full_text) > 120 else '')
                    })
        except Exception:
            pass

        return tables

    def audit_batch_tables(self, doc_paths: Dict[int, Dict[str, str]]) -> Dict[str, Any]:
        """
        Compares all tables across all documents in the batch.
        doc_paths: {doc_id: {'filename': str, 'filepath': str}}
        Returns table overlap report with flagged shared tables.
        """
        doc_tables: Dict[int, List[Dict[str, Any]]] = {}
        for d_id, info in doc_paths.items():
            if info['filepath'].lower().endswith('.docx'):
                doc_tables[d_id] = self.extract_tables_from_docx(info['filepath'])
            else:
                doc_tables[d_id] = []

        flagged_tables = []
        table_pairs = []

        checked = set()
        doc_ids = list(doc_tables.keys())

        for i, d1_id in enumerate(doc_ids):
            for d2_id in doc_ids[i + 1:]:
                tables1 = doc_tables[d1_id]
                tables2 = doc_tables[d2_id]

                for t1 in tables1:
                    for t2 in tables2:
                        # Quick length ratio check
                        len_ratio = min(len(t1['full_text']), len(t2['full_text'])) / max(1, max(len(t1['full_text']), len(t2['full_text'])))
                        if len_ratio < 0.40:
                            continue

                        # Fast Token Jaccard Filter (0.0001s)
                        words1 = set(t1['full_text'].lower().split())
                        words2 = set(t2['full_text'].lower().split())
                        if not words1 or not words2:
                            continue

                        common = len(words1 & words2)
                        jaccard = common / len(words1 | words2)
                        overlap = common / min(len(words1), len(words2))

                        if overlap < 0.40:
                            continue

                        # Precise sequence similarity for candidates
                        sim = round(0.7 * overlap + 0.3 * jaccard, 2)

                        if sim >= self.table_similarity_threshold:
                            flagged_tables.append({
                                'doc1_id': d1_id,
                                'doc1_filename': doc_paths[d1_id]['filename'],
                                'doc1_table_idx': t1['table_idx'],
                                'doc1_snippet': t1['snippet'],
                                'doc2_id': d2_id,
                                'doc2_filename': doc_paths[d2_id]['filename'],
                                'doc2_table_idx': t2['table_idx'],
                                'doc2_snippet': t2['snippet'],
                                'similarity': sim,
                                'similarity_pct': int(sim * 100),
                                'shared_words': min(t1['word_count'], t2['word_count']),
                                'severity': 'critical' if sim >= 0.75 else 'moderate'
                            })

        # Sort by similarity descending
        flagged_tables.sort(key=lambda x: x['similarity'], reverse=True)

        return {
            'total_flagged_tables': len(flagged_tables),
            'high_risk_tables_count': sum(1 for t in flagged_tables if t['severity'] == 'critical'),
            'flagged_tables': flagged_tables
        }
