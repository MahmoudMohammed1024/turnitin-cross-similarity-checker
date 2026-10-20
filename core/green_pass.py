from typing import Dict, Any, List

def evaluate_document_green_pass(
    doc: Dict[str, Any],
    table_audit_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates whether a paper is certified safe for student submission (Green Pass),
    or whether it faces high risk of jumping to 80% upon delivery.
    """
    doc_id = doc['id']
    sim_pct = doc['similarity_percentage']
    flagged_sentences = doc.get('flagged_sentences', [])

    # Check for long identical blocks
    max_words_in_single_match = 0
    for s in flagged_sentences:
        if s.get('best_type') == 'exact':
            max_words_in_single_match = max(max_words_in_single_match, s.get('word_count', 0))

    # Check for table overlap
    has_critical_table_overlap = False
    table_culprits = []
    for t in table_audit_results.get('flagged_tables', []):
        if t['doc1_id'] == doc_id or t['doc2_id'] == doc_id:
            other_file = t['doc2_filename'] if t['doc1_id'] == doc_id else t['doc1_filename']
            table_culprits.append(f"جدول {t['doc1_table_idx']} مطابق بنسبة {t['similarity_pct']}% مع {other_file}")
            if t['severity'] == 'critical':
                has_critical_table_overlap = True

    # Green Pass Rules
    reasons = []
    if sim_pct > 18.0:
        status = 'BLOCKED'
        badge_color = 'danger'
        title_ar = '🛑 ممنوع التسليم (خطر رسوب مؤكد)'
        title_en = '🛑 BLOCKED (Critical Submission Risk)'
        reasons.append(f"نسبة التشابه مع أبحاث الدفعة مرتفعة ({sim_pct}%) وستقفز إلى أكثر من 70-80% عند رفعها لمنصة الجامعة.")
    elif has_critical_table_overlap:
        status = 'BLOCKED'
        badge_color = 'danger'
        title_ar = '🛑 ممنوع التسليم (جداول متطابقة)'
        title_en = '🛑 BLOCKED (Identical Tables Found)'
        reasons.append("تم اكتشاف جداول أو مصفوفات متطابقة مع أبحاث أخرى لنفس الدفعة. هذا الفخ هو السبب الرئيسي لرفع النسبة في Turnitin.")
    elif sim_pct > 10.0 or max_words_in_single_match >= 20:
        status = 'WARNING'
        badge_color = 'warning'
        title_ar = '⚠️ يحتاج مراجعة (تحذير قبل التسليم)'
        title_en = '⚠️ CAUTION (Minor Edits Required)'
        reasons.append(f"يوجد تشابه متوسط ({sim_pct}%). يُنصح بتعديل الجمل المحددة لتنزيل النسبة إلى أقل من 10%.")
    else:
        status = 'PASSED'
        badge_color = 'success'
        title_ar = '✅ تصريح الضوء الأخضر (آمن 100% للتسليم)'
        title_en = '✅ CERTIFIED SAFE TO SUBMIT (Green Pass)'
        reasons.append("البحث فريد بنسبة ممتازة ولا يشترك مع أي بحث آخر في الدفعة. يمكن تسليمه للعميل بأمان تام.")

    return {
        'status': status,
        'badge_color': badge_color,
        'title_ar': title_ar,
        'title_en': title_en,
        'sim_percentage': sim_pct,
        'reasons': reasons,
        'table_culprits': table_culprits,
        'max_identical_sentence_words': max_words_in_single_match
    }


def compute_batch_readiness(doc_passes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes summary KPI for the whole batch readiness before client handover.
    """
    total = len(doc_passes)
    passed = sum(1 for p in doc_passes if p['status'] == 'PASSED')
    warning = sum(1 for p in doc_passes if p['status'] == 'WARNING')
    blocked = sum(1 for p in doc_passes if p['status'] == 'BLOCKED')

    readiness_pct = round((passed / max(1, total)) * 100)

    return {
        'total_documents': total,
        'passed_count': passed,
        'warning_count': warning,
        'blocked_count': blocked,
        'readiness_percentage': readiness_pct,
        'is_safe_to_deliver_all': (blocked == 0 and warning == 0)
    }
