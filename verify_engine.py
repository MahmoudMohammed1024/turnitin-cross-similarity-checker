import sys
import glob
import time
sys.stdout.reconfigure(encoding='utf-8')

from core.extractor import extract_document
from core.detector import PlagiarismDetector
from core.reporter import generate_excel_report

files = glob.glob(r'd:\similarity\test\*.docx')
print(f"Loading {len(files)} test documents...")

t0 = time.time()
docs = []
for f in files:
    docs.append(extract_document(f))
t_extract = time.time() - t0
print(f"Extracted {len(docs)} documents in {t_extract:.2f}s")

detector = PlagiarismDetector(min_words=5, fuzzy_threshold=0.75, exclude_references=True)
t1 = time.time()
res = detector.analyze_documents(docs)
t_detect = time.time() - t1
print(f"Analyzed cross-similarity in {t_detect:.2f}s")

summary = res['summary']
print("\n--- Summary ---")
print(f"Total Docs: {summary['total_documents']}")
print(f"High Risk (>25%): {summary['high_risk_count']}")
print(f"Moderate Risk (15-25%): {summary['moderate_risk_count']}")
print(f"Safe (<15%): {summary['safe_count']}")
print(f"Average Similarity: {summary['average_similarity']}%")
print(f"Total Flagged Sentences: {summary['total_flagged_sentences']}")

print("\n--- Top 5 Most Similar Documents ---")
for d in res['documents'][:5]:
    print(f"[{d['similarity_percentage']}% - {d['risk'].upper()}] {d['filename'][:40]} (Flagged sentences: {d['flagged_sentences_count']})")
    for s in d['flagged_sentences'][:2]:
        print(f"   -> Match ({s['best_type']} {int(s['best_similarity']*100)}%): \"{s['text'][:70]}...\"")

# Test Excel generation
excel_io = generate_excel_report(res)
with open(r'd:\similarity\test_report.xlsx', 'wb') as f:
    f.write(excel_io.getvalue())
print("\nExcel report successfully generated at d:\\similarity\\test_report.xlsx")
