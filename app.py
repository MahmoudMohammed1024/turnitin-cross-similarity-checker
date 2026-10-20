import os
import sys
import tempfile
import glob
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Reconfigure stdout for utf-8
sys.stdout.reconfigure(encoding='utf-8')

from core.extractor import extract_document
from core.detector import PlagiarismDetector
from core.reporter import generate_excel_report
from core.table_detector import TableAuditDetector
from core.paraphraser import SmartParaphraser
from core.green_pass import evaluate_document_green_pass, compute_batch_readiness

paraphraser = SmartParaphraser()
table_detector = TableAuditDetector()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max upload
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'similarity_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global store for current session's analysis
CURRENT_DATA = {
    'documents': [],
    'analysis': None,
    'settings': {
        'min_words': 8,
        'fuzzy_threshold': 0.75,
        'exclude_references': True,
        'enable_cross_lingual': True,
        'check_internet': True
    }
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scan-folder', methods=['POST'])
def scan_folder():
    """
    Scans a local directory on disk for .docx, .pdf, .txt files and analyzes them.
    """
    data = request.json or {}
    folder_path = data.get('folder_path', '').strip()
    if not folder_path or not os.path.exists(folder_path):
        return jsonify({'error': f'المجلد غير موجود: {folder_path}'}), 400

    min_words = int(data.get('min_words', CURRENT_DATA['settings']['min_words']))
    fuzzy_threshold = float(data.get('fuzzy_threshold', CURRENT_DATA['settings']['fuzzy_threshold']))
    exclude_references = bool(data.get('exclude_references', CURRENT_DATA['settings']['exclude_references']))
    enable_cross_lingual = bool(data.get('enable_cross_lingual', CURRENT_DATA['settings']['enable_cross_lingual']))
    check_internet = bool(data.get('check_internet', CURRENT_DATA['settings']['check_internet']))

    CURRENT_DATA['settings'].update({
        'min_words': min_words,
        'fuzzy_threshold': fuzzy_threshold,
        'exclude_references': exclude_references,
        'enable_cross_lingual': enable_cross_lingual,
        'check_internet': check_internet
    })

    patterns = ['*.docx', '*.pdf', '*.txt']
    found_files = []
    for pat in patterns:
        found_files.extend(glob.glob(os.path.join(folder_path, pat)))

    if not found_files:
        return jsonify({'error': 'لم يتم العثور على ملفات Word (.docx) أو PDF أو TXT في هذا المجلد.'}), 400

    # Extract all
    extracted_docs = []
    errors = []
    for f in found_files:
        try:
            doc_obj = extract_document(f)
            extracted_docs.append(doc_obj)
        except Exception as e:
            errors.append(f"{os.path.basename(f)}: {str(e)}")

    if not extracted_docs:
        return jsonify({'error': 'تعذر استخراج النصوص من الملفات.', 'details': errors}), 500

    CURRENT_DATA['documents'] = extracted_docs

    # If analyzing a single document, automatically force live internet check
    if len(extracted_docs) == 1:
        check_internet = True

    detector = PlagiarismDetector(
        min_words=min_words,
        fuzzy_threshold=fuzzy_threshold,
        exclude_references=exclude_references,
        enable_cross_lingual=enable_cross_lingual,
        check_internet=check_internet
    )
    result = detector.analyze_documents(extracted_docs)

    # Run Table Audit
    doc_paths = {d['id']: {'filename': d['filename'], 'filepath': d.get('filepath', '')} for d in extracted_docs}
    table_audit = table_detector.audit_batch_tables(doc_paths)
    result['table_audit'] = table_audit

    # Run Pre-Submission Green Pass Evaluation
    green_passes = []
    for doc in result['documents']:
        gp = evaluate_document_green_pass(doc, table_audit)
        doc['green_pass'] = gp
        green_passes.append(gp)

    result['batch_readiness'] = compute_batch_readiness(green_passes)
    CURRENT_DATA['analysis'] = result

    return jsonify({
        'success': True,
        'summary': result['summary'],
        'documents': result['documents'],
        'matrix': result['matrix'],
        'table_audit': table_audit,
        'batch_readiness': result['batch_readiness'],
        'errors': errors
    })


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """
    Handles multi-file drag-and-drop upload from browser.
    """
    if 'files' not in request.files:
        return jsonify({'error': 'لم يتم إرسال أي ملفات'}), 400

    uploaded_files = request.files.getlist('files')
    if not uploaded_files or uploaded_files[0].filename == '':
        return jsonify({'error': 'لم يتم اختيار ملفات'}), 400

    min_words = int(request.form.get('min_words', CURRENT_DATA['settings']['min_words']))
    fuzzy_threshold = float(request.form.get('fuzzy_threshold', CURRENT_DATA['settings']['fuzzy_threshold']))
    exclude_references = request.form.get('exclude_references', 'true').lower() == 'true'
    enable_cross_lingual = request.form.get('enable_cross_lingual', 'true').lower() == 'true'
    check_internet = request.form.get('check_internet', 'false').lower() == 'true'

    CURRENT_DATA['settings'].update({
        'min_words': min_words,
        'fuzzy_threshold': fuzzy_threshold,
        'exclude_references': exclude_references,
        'enable_cross_lingual': enable_cross_lingual,
        'check_internet': check_internet
    })

    extracted_docs = []
    errors = []

    for file in uploaded_files:
        fname = secure_filename(file.filename)
        if not fname:
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ['.docx', '.pdf', '.txt']:
            continue

        temp_path = os.path.join(UPLOAD_FOLDER, fname)
        file.save(temp_path)

        try:
            doc_obj = extract_document(temp_path)
            extracted_docs.append(doc_obj)
        except Exception as e:
            errors.append(f"{fname}: {str(e)}")

    if not extracted_docs:
        return jsonify({'error': 'تعذر معالجة الملفات المرفوعة', 'details': errors}), 400

    CURRENT_DATA['documents'] = extracted_docs

    if len(extracted_docs) == 1:
        check_internet = True

    detector = PlagiarismDetector(
        min_words=min_words,
        fuzzy_threshold=fuzzy_threshold,
        exclude_references=exclude_references,
        enable_cross_lingual=enable_cross_lingual,
        check_internet=check_internet
    )
    result = detector.analyze_documents(extracted_docs)

    # Run Table Audit
    doc_paths = {d['id']: {'filename': d['filename'], 'filepath': d.get('filepath', '')} for d in extracted_docs}
    table_audit = table_detector.audit_batch_tables(doc_paths)
    result['table_audit'] = table_audit

    # Run Pre-Submission Green Pass Evaluation
    green_passes = []
    for doc in result['documents']:
        gp = evaluate_document_green_pass(doc, table_audit)
        doc['green_pass'] = gp
        green_passes.append(gp)

    result['batch_readiness'] = compute_batch_readiness(green_passes)
    CURRENT_DATA['analysis'] = result

    return jsonify({
        'success': True,
        'summary': result['summary'],
        'documents': result['documents'],
        'matrix': result['matrix'],
        'table_audit': table_audit,
        'batch_readiness': result['batch_readiness'],
        'errors': errors
    })


@app.route('/api/rephrase', methods=['POST'])
def api_rephrase():
    """
    Generates 3 academic alternatives for a given sentence.
    """
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'النص فارغ'}), 400

    alternatives = paraphraser.rephrase(text)
    return jsonify({
        'original': text,
        'alternatives': alternatives
    })


@app.route('/api/results', methods=['GET'])
def get_results():
    if not CURRENT_DATA['analysis']:
        return jsonify({'error': 'لا توجد نتائج تحليل حالية'}), 404
    return jsonify(CURRENT_DATA['analysis'])


@app.route('/api/document/<int:doc_id>', methods=['GET'])
def get_document_details(doc_id):
    """
    Returns full text of document broken down by paragraph,
    with matching sentence highlights and metadata.
    """
    if not CURRENT_DATA['documents'] or not CURRENT_DATA['analysis']:
        return jsonify({'error': 'لم يتم إجراء الفحص بعد'}), 404

    # Find the document in analysis
    doc_report = next((d for d in CURRENT_DATA['analysis']['documents'] if d['id'] == doc_id), None)
    if not doc_report:
        return jsonify({'error': 'البحث غير موجود'}), 404

    raw_doc = next((d for d in CURRENT_DATA['documents'] if d.get('id') == doc_id), None)
    if not raw_doc:
        return jsonify({'error': 'نص البحث غير متوفر'}), 404

    # Map of flagged sentence texts to match details
    flagged_map = {s['sentence_id']: s for s in doc_report['flagged_sentences']}

    # Return structured paragraphs
    paragraphs = []
    for idx, block in enumerate(raw_doc['blocks']):
        paragraphs.append({
            'idx': idx,
            'text': block['text'],
            'type': block['type'],
            'is_ref': block.get('is_ref', False)
        })

    return jsonify({
        'doc_report': doc_report,
        'paragraphs': paragraphs
    })


@app.route('/api/compare/<int:doc1_id>/<int:doc2_id>', methods=['GET'])
def compare_two_docs(doc1_id, doc2_id):
    """
    Returns side-by-side comparison data between two documents.
    """
    if not CURRENT_DATA['analysis']:
        return jsonify({'error': 'لا توجد بيانات'}), 404

    doc1_report = next((d for d in CURRENT_DATA['analysis']['documents'] if d['id'] == doc1_id), None)
    doc2_report = next((d for d in CURRENT_DATA['analysis']['documents'] if d['id'] == doc2_id), None)

    if not doc1_report or not doc2_report:
        return jsonify({'error': 'أحد البحثين غير موجود'}), 404

    # Shared sentences directly between these two
    shared = []
    for s in doc1_report['flagged_sentences']:
        for m in s['matches']:
            if m['other_doc_id'] == doc2_id:
                shared.append({
                    'doc1_sentence': s['text'],
                    'doc2_sentence': m['other_raw'],
                    'similarity': m['similarity'],
                    'type': m['type']
                })
                break

    return jsonify({
        'doc1_name': doc1_report['filename'],
        'doc2_name': doc2_report['filename'],
        'shared_count': len(shared),
        'shared_sentences': shared
    })


@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    if not CURRENT_DATA['analysis']:
        return jsonify({'error': 'لا يوجد تحليل لتصديره'}), 404

    excel_stream = generate_excel_report(CURRENT_DATA['analysis'])
    return send_file(
        excel_stream,
        as_attachment=True,
        download_name="Cross_Similarity_Plagiarism_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == '__main__':
    print("=" * 60)
    print("  Turnitin Internal Cross-Similarity Checker is running!")
    print("  Open your browser at: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
