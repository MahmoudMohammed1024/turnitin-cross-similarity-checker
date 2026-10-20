# فاحص الاقتباس والتشابه الداخلي للأبحاث (Turnitin Academic Cross-Similarity Checker)

نظام متقدم وشامل لفحص ومحاكاة نسب الاقتباس الأكاديمي وكشف التشابه بين أبحاث الطلاب ومصادر الإنترنت والدوريات العلمية العالمية وفق معايير Turnitin الرسمية.

---

## 🌟 الميزات الرئيسية (Core Features)

1. **محاكاة دقيقة لتقرير Turnitin الرسمي (Similarity Index)**:
   - تقسيم دقيق لمصادر الاقتباس:
     - 🌐 **مصادر الإنترنت (Internet Sources)**: فحص حي عبر فهارس الإنترنت وموسوعات المعرفة.
     - 📚 **المنشورات والدوريات (Publications)**: فحص مباشر عبر فهارس المعرفات الرقمية العالمية (CrossRef DOI Index).
     - 🎓 **أبحاث الطلاب (Student Papers)**: قياس التشابه الفعلي المتبادل بين الأبحاث المرفوعة في نفس الدفعة بدون فرض نسب افتراضية.
   - احتساب المجموعات المتطابقة (Match Groups):
     - `Not Cited or Quoted` (تطابق تام غير موثق).
     - `Missing Quotations` (تشابه أو إعادة صياغة بدون علامات تنصيص).

2. **كاشف فخ الجداول والمصفوفات (Tables & Matrix Trap Detector)**:
   - فحص وتدقيق الجداول المشتركة بين الطلاب التي تتسبب في رفع النسبة للـ 80% في Turnitin.

3. **تصاريح الضوء الأخضر للتسليم (Pre-Submission Green Pass)**:
   - تقييم جاهزية البحث للتسليم للجامعات والعملاء وضمان عدم تجاوزه النسبة المسموحة (Safe Tier < 20%).

4. **المفتش الكامل وتظليل النصوص (Full Inspector)**:
   - تظليل كافة الجمل المقتبسة في البحث بنسبة 100%.
   - شريط جانبي تفاعلي يتيح:
     - عرض أهم المصادر ورابطها الخارجي المباشر.
     - تصفح جميع الجمل المقتبسة مع خاصية الانتقال الفوري بالنقرة (Jump & Highlight).
     - بطاقة تفاصيل الاقتباس وأداة الذكاء الاصطناعي لإعادة الصياغة الأكاديمية الفورية (AI Academic Rephraser).

5. **مصفوفة التشابه المتبادل (Cross-Similarity Matrix)**:
   - خريطة حرارية تفاعلية تقارن كل بحث بجميع أبحاث المجموعة في المجلد.

6. **مقارنة بحثين جنباً إلى جنب (Side-by-Side Comparison)**:
   - فحص تفصيلي للفقرات والجمل المتطابقة بين أي طالبين مع إبراز الفروق.

7. **تصدير تقارير Excel الاحترافية**:
   - تقرير شامل يحتوي على ملخص الدفعة، تفاصيل كل بحث، تصاريح Green Pass، ومصفوفة التشابه.

---

## 🚀 التثبيت والتشغيل (Getting Started)

### 1. المتطلبات الأساسية
* Python 3.10 أو أحدث.

### 2. تثبيت الحزم المطلوبة
```bash
pip install flask python-docx pymupdf pypdf requests beautifulsoup4 openpyxl
```

### 3. تشغيل التطبيق
```bash
python app.py
```
أو عبر الضغط مرتين على ملف `run.bat`.

ثم افتح المتصفح على الرابط:
👉 `http://localhost:5000`

---

## 🛠 التقنيات المستخدمة
* **Backend**: Python (Flask)
* **NLP & Processing**: Exact Inverted Index, N-Gram Shingling, Arabic NLP Stemming, CrossRef REST API
* **Frontend**: Modern Vanilla JS, CSS3 Design System, Cairo & Outfit Typography, FontAwesome Icons

---
*Built for High-Volume Academic Accuracy & Student Paper Integrity.*
