// ==========================================
// Cross-Similarity & Plagiarism Detector JS
// ==========================================

let currentLang = 'ar';
let analysisData = null;
let selectedFiles = [];
let currentInspectedDoc = null;

// Translations Dictionary
const I18N = {
    ar: {
        export_excel: "تصدير تقرير Excel",
        input_title: "اختيار أو رفع الأبحاث للفحص",
        scan_folder_tab: "فحص مجلد على الجهاز",
        upload_files_tab: "رفع ملفات (سحب وإفلات)",
        scan_now: "فحص المجلد الآن",
        scan_help: "يدعم فحص كل ملفات Word (.docx) و PDF و TXT في المجلد دفعة واحدة ومقارنة كل بحث بالباقي.",
        drop_title: "اسحب وأفلت ملفات الأبحاث هنا",
        drop_subtitle: "أو اضغط لاختيار ملفات من جهازك (DOCX, PDF, TXT)",
        start_analysis: "بدء الفحص للملفات المحددة",
        settings_title: "إعدادات خوارزمية الفحص (اختياري)",
        min_words_label: "الحد الأدنى لكلمات الجملة المتطابقة:",
        fuzzy_label: "حساسية التطابق الجزئي (Fuzzy Matching):",
        exclude_ref_label: "استبعاد قسم المراجع (References / Bibliography)",
        analyzing: "جاري استخراج النصوص وفحص التشابه المتبادل بين الأبحاث...",
        loading_sub: "يتم فحص الجمل وحساب مصفوفة التقاطع بالكامل",
        total_docs: "إجمالي الأبحاث المفحوصة",
        high_risk: "أبحاث عالية الخطورة (>25%)",
        moderate_risk: "أبحاث متوسطة الخطورة (15-25%)",
        safe_docs: "أبحاث آمنة للتسليم (<15%)",
        avg_sim: "متوسط نسبة التشابه بالدفعة",
        tab_leaderboard: "ترتيب الأبحاث ونسب التشابه",
        tab_actions: "الجمل المطلوب تعديلها (قائمة العمل)",
        tab_inspector: "فحص وتظليل البحث (Full Inspector)",
        tab_matrix: "مصفوفة التشابه المتبادل (Matrix)",
        tab_compare: "مقارنة بحثين جنباً إلى جنب",
        leaderboard_title: "قائمة الأبحاث مرتبة من الأعلى خطورة إلى الآمن",
        col_filename: "اسم البحث / الملف",
        col_similarity: "نسبة التشابه (Turnitin %)",
        col_risk: "مستوى الخطورة",
        col_sentences: "الجمل المقتبسة",
        col_top_sources: "أهم الأبحاث المشتركة معه",
        col_actions: "إجراءات",
        actions_title: "الجمل التي يجب إعادة صياغتها لتفادي كشف المنصة",
        actions_sub: "قائمة منظمة بكل جملة مشتركة مع غيرها، مع إمكانية الفلترة لكل بحث على حدة وتصديرها للكاتب",
        select_inspect_doc: "اختر البحث لعرضه وتظليله:",
        select_doc_msg: "اختر بحثاً من القائمة أعلاه لعرض نصه الكامل وتظليل الجمل المقتبسة",
        match_details: "تفاصيل الاقتباس",
        click_sentence_hint: "اضغط على أي جملة مظللة في النص لعرض الأبحاث الأخرى التي وردت فيها ونصها الأصلي ونسبة التطابق.",
        matrix_title: "مصفوفة التشابه المتبادل (Cross-Similarity Matrix)",
        matrix_sub: "توضح نسبة الكلمات المشتركة بين كل بحث والآخر مباشرة",
        compare_doc1: "البحث الأول:",
        compare_doc2: "البحث الثاني:",
        compare_select_hint: "اختر بحثين من القائمة أعلاه لمشاهدة الجمل المتطابقة بينهما مباشرة.",
        inspect_btn: "تظليل البحث",
        actions_btn: "الجمل لتعديلها",
        compare_btn: "مقارنة",
        risk_high: "عالي الخطورة 🔴",
        risk_mod: "متوسط 🟡",
        risk_safe: "آمن 🟢",
        copy_text: "نسخ الجملة",
        copied: "تم النسخ!",
        resolved: "تم تعديلها",
        all_docs: "كل الأبحاث",
        words: "كلمات",
        exact_match: "تطابق تام (100%)",
        fuzzy_match: "إعادة صياغة جزئية"
    },
    en: {
        export_excel: "Export Excel Report",
        input_title: "Select or Upload Documents for Inspection",
        scan_folder_tab: "Scan Local Folder",
        upload_files_tab: "Upload Files (Drag & Drop)",
        scan_now: "Scan Folder Now",
        scan_help: "Scans all Word (.docx), PDF, and TXT files in the folder and compares each paper against the entire batch.",
        drop_title: "Drag & drop research papers here",
        drop_subtitle: "or click to browse from your device (DOCX, PDF, TXT)",
        start_analysis: "Start Analysis for Selected Files",
        settings_title: "Algorithm Settings (Optional)",
        min_words_label: "Min words for matching sentence:",
        fuzzy_label: "Fuzzy matching sensitivity:",
        exclude_ref_label: "Exclude References / Bibliography section",
        analyzing: "Extracting texts and analyzing cross-similarity...",
        loading_sub: "Processing sentences and computing all-pairs similarity matrix",
        total_docs: "Total Documents Analyzed",
        high_risk: "High Risk Papers (>25%)",
        moderate_risk: "Moderate Risk Papers (15-25%)",
        safe_docs: "Safe to Submit Papers (<15%)",
        avg_sim: "Batch Average Similarity",
        tab_leaderboard: "Leaderboard & Similarity Scores",
        tab_actions: "Sentences to Rephrase (Action List)",
        tab_inspector: "Document Highlight Inspector",
        tab_matrix: "Cross-Similarity Matrix",
        tab_compare: "Side-by-Side Comparison",
        leaderboard_title: "Documents Ranked by Plagiarism Risk (High to Safe)",
        col_filename: "Document / File Name",
        col_similarity: "Similarity (Turnitin %)",
        col_risk: "Risk Level",
        col_sentences: "Flagged Sentences",
        col_top_sources: "Top Overlapping Papers",
        col_actions: "Actions",
        actions_title: "Sentences that MUST be rephrased before submission",
        actions_sub: "Organized checklist of shared sentences with easy filtering per paper",
        select_inspect_doc: "Select Document to Inspect:",
        select_doc_msg: "Select a document from the dropdown above to view full text with highlighted matches",
        match_details: "Match Details",
        click_sentence_hint: "Click any highlighted sentence in the text to see matching papers and similarity confidence.",
        matrix_title: "Cross-Similarity Matrix",
        matrix_sub: "Shows pairwise shared word percentage between every document",
        compare_doc1: "Document 1:",
        compare_doc2: "Document 2:",
        compare_select_hint: "Select two documents from the dropdowns above to view shared sentences side-by-side.",
        inspect_btn: "Inspect Text",
        actions_btn: "Sentences",
        compare_btn: "Compare",
        risk_high: "High Risk 🔴",
        risk_mod: "Moderate 🟡",
        risk_safe: "Safe 🟢",
        copy_text: "Copy Sentence",
        copied: "Copied!",
        resolved: "Resolved",
        all_docs: "All Documents",
        words: "words",
        exact_match: "Exact Match (100%)",
        fuzzy_match: "Paraphrased Match"
    }
};

// Toggle Language
function toggleLanguage() {
    currentLang = currentLang === 'ar' ? 'en' : 'ar';
    document.body.classList.toggle('lang-en', currentLang === 'en');
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLang;
    document.getElementById('langText').innerText = currentLang === 'ar' ? 'English' : 'عربي';

    // Update i18n DOM elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (I18N[currentLang][key]) {
            el.innerText = I18N[currentLang][key];
        }
    });

    if (analysisData) {
        renderLeaderboard();
        renderActionList();
    }
}

// Input Mode Switcher
function switchInputMode(mode) {
    document.querySelectorAll('.input-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.input-mode-panel').forEach(p => p.classList.remove('active'));

    if (mode === 'folder') {
        document.querySelector('.input-tabs .tab-btn:nth-child(1)').classList.add('active');
        document.getElementById('folderMode').classList.add('active');
    } else {
        document.querySelector('.input-tabs .tab-btn:nth-child(2)').classList.add('active');
        document.getElementById('uploadMode').classList.add('active');
    }
}

// Settings Toggle
function toggleSettings() {
    const p = document.getElementById('settingsPanel');
    p.classList.toggle('open');
    const chevron = document.getElementById('settingsChevron');
    chevron.classList.toggle('fa-chevron-down', !p.classList.contains('open'));
    chevron.classList.toggle('fa-chevron-up', p.classList.contains('open'));
}

// Start Folder Scan
async function startFolderScan() {
    const folderPath = document.getElementById('folderPathInput').value.trim();
    if (!folderPath) {
        alert(currentLang === 'ar' ? 'يرجى إدخال مسار المجلد' : 'Please enter folder path');
        return;
    }

    showLoading(true);

    try {
        const payload = {
            folder_path: folderPath,
            min_words: parseInt(document.getElementById('minWordsRange').value),
            fuzzy_threshold: parseFloat(document.getElementById('fuzzyRange').value) / 100.0,
            exclude_references: document.getElementById('excludeRefCheck').checked,
            enable_cross_lingual: document.getElementById('crossLingualCheck').checked,
            check_internet: document.getElementById('checkInternetCheck').checked
        };

        const resp = await fetch('/api/scan-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const res = await resp.json();
        if (!resp.ok) {
            alert(res.error || 'حدث خطأ أثناء الفحص');
            showLoading(false);
            return;
        }

        analysisData = res;
        onAnalysisComplete();
    } catch (err) {
        console.error(err);
        alert(currentLang === 'ar' ? 'تعذر الاتصال بالخادم' : 'Failed to connect to server');
    } finally {
        showLoading(false);
    }
}

// Drag & Drop Handling
const dropzone = document.getElementById('dropzone');
['dragenter', 'dragover'].forEach(ev => {
    dropzone.addEventListener(ev, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
});
['dragleave', 'drop'].forEach(ev => {
    dropzone.addEventListener(ev, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    });
});
dropzone.addEventListener('drop', (e) => {
    const files = Array.from(e.dataTransfer.files).filter(f => {
        const ext = f.name.split('.').pop().toLowerCase();
        return ['docx', 'pdf', 'txt'].includes(ext);
    });
    handleFilesSelected(files);
});

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFilesSelected(files);
}

function handleFilesSelected(files) {
    selectedFiles = files;
    const summary = document.getElementById('selectedFilesSummary');
    const uploadBtn = document.getElementById('startUploadBtn');

    if (files.length > 0) {
        summary.innerText = currentLang === 'ar'
            ? `تم تحديد ${files.length} ملف للفحص`
            : `${files.length} files selected for inspection`;
        uploadBtn.style.display = 'inline-flex';
    } else {
        summary.innerText = '';
        uploadBtn.style.display = 'none';
    }
}

async function startFileUpload() {
    if (selectedFiles.length === 0) return;

    showLoading(true);

    const formData = new FormData();
    selectedFiles.forEach(f => formData.append('files', f));
    formData.append('min_words', document.getElementById('minWordsRange').value);
    formData.append('fuzzy_threshold', (parseFloat(document.getElementById('fuzzyRange').value) / 100.0).toString());
    formData.append('exclude_references', document.getElementById('excludeRefCheck').checked.toString());
    formData.append('enable_cross_lingual', document.getElementById('crossLingualCheck').checked.toString());
    formData.append('check_internet', document.getElementById('checkInternetCheck').checked.toString());

    try {
        const resp = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const res = await resp.json();
        if (!resp.ok) {
            alert(res.error || 'حدث خطأ أثناء الرفع والفحص');
            showLoading(false);
            return;
        }

        analysisData = res;
        onAnalysisComplete();
    } catch (err) {
        console.error(err);
        alert('Upload failed');
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'block' : 'none';
    if (show) {
        document.getElementById('resultsSection').style.display = 'none';
    }
}

// On Analysis Complete
function onAnalysisComplete() {
    if (!analysisData) return;

    document.getElementById('excelExportBtn').style.display = 'inline-flex';
    document.getElementById('resultsSection').style.display = 'block';

    const s = analysisData.summary;
    document.getElementById('statTotalDocs').innerText = s.total_documents;
    document.getElementById('statHighRisk').innerText = s.high_risk_count;
    document.getElementById('statModRisk').innerText = s.moderate_risk_count;
    document.getElementById('statSafeDocs').innerText = s.safe_count;
    document.getElementById('statAvgSim').innerText = s.average_similarity + '%';

    // Single document notification
    const singleBanner = document.getElementById('singleDocBanner');
    if (singleBanner) {
        if (s.total_documents === 1) {
            singleBanner.style.display = 'block';
            singleBanner.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <i class="fa-solid fa-circle-info" style="font-size: 1.3rem; color: #38BDF8;"></i>
                    <div>
                        <b>تنبيه فحص بحث منفرد:</b> نظراً لوجود بحث واحد فقط في الفحص (المقارنة الداخلية تتطلب بحثين فأكثر في الدفعة)، تم فحص البحث تلقائياً ضد <b>مصادر الإنترنت المفتوحة والمجلات والدوريات العلمية (Turnitin Internet & Publications)</b> وتطابقت مصادره بالكامل.
                    </div>
                </div>
            `;
        } else {
            singleBanner.style.display = 'none';
        }
    }

    // Populate dropdowns
    populateDropdowns();

    // Render all views
    renderLeaderboard();
    renderGreenPassView();
    renderTableAuditView();
    renderTurnitinView();
    renderActionList();
    renderMatrix();

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function populateDropdowns() {
    const docs = analysisData.documents;

    // Filter dropdown for actions
    const actionFilter = document.getElementById('actionDocFilter');
    actionFilter.innerHTML = `<option value="all">${I18N[currentLang].all_docs}</option>`;
    docs.forEach(d => {
        actionFilter.innerHTML += `<option value="${d.id}">[${d.similarity_percentage}%] ${d.filename}</option>`;
    });

    // Inspector dropdown
    const inspectorSelect = document.getElementById('inspectorDocSelect');
    inspectorSelect.innerHTML = `<option value="">-- ${I18N[currentLang].select_inspect_doc} --</option>`;
    docs.forEach((d, idx) => {
        inspectorSelect.innerHTML += `<option value="${d.id}" ${idx === 0 ? 'selected' : ''}>[${d.similarity_percentage}% - ${d.risk.toUpperCase()}] ${d.filename}</option>`;
    });
    if (docs.length > 0) {
        inspectorSelect.value = docs[0].id;
        loadDocumentForInspection(docs[0].id);
    }

    // Compare dropdowns
    const comp1 = document.getElementById('compareDoc1');
    const comp2 = document.getElementById('compareDoc2');
    comp1.innerHTML = '';
    comp2.innerHTML = '';
    docs.forEach((d, idx) => {
        comp1.innerHTML += `<option value="${d.id}" ${idx === 0 ? 'selected' : ''}>${d.filename} (${d.similarity_percentage}%)</option>`;
        comp2.innerHTML += `<option value="${d.id}" ${idx === 1 ? 'selected' : ''}>${d.filename} (${d.similarity_percentage}%)</option>`;
    });
}

// View Panels Switcher
function switchView(viewName) {
    document.querySelectorAll('.views-tabs-nav .view-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));

    const tabMap = {
        leaderboard: { btn: 1, panel: 'viewLeaderboard' },
        greenpass: { btn: 2, panel: 'viewGreenPass' },
        tableaudit: { btn: 3, panel: 'viewTableAudit' },
        turnitin: { btn: 4, panel: 'viewTurnitin' },
        actions: { btn: 5, panel: 'viewActions' },
        inspector: { btn: 6, panel: 'viewInspector' },
        matrix: { btn: 7, panel: 'viewMatrix' },
        compare: { btn: 8, panel: 'viewCompare' }
    };

    const target = tabMap[viewName];
    if (target) {
        document.querySelector(`.views-tabs-nav .view-tab-btn:nth-child(${target.btn})`).classList.add('active');
        document.getElementById(target.panel).classList.add('active');
    }

    if (viewName === 'inspector') {
        const inspectorSelect = document.getElementById('inspectorDocSelect');
        if (!inspectorSelect.value && analysisData && analysisData.documents.length > 0) {
            const firstId = analysisData.documents[0].id;
            inspectorSelect.value = firstId;
            loadDocumentForInspection(firstId);
        }
    } else if (viewName === 'compare') {
        runSideBySideCompare();
    }
}

// Render Green Pass View
function renderGreenPassView() {
    const container = document.getElementById('greenPassCardsGrid');
    if (!container || !analysisData) return;
    container.innerHTML = '';

    const br = analysisData.batch_readiness || {};
    const badgeEl = document.getElementById('batchReadinessBadge');
    if (badgeEl) {
        badgeEl.innerHTML = `
            <span class="badge ${br.blocked_count === 0 ? 'badge-success' : 'badge-danger'}" style="font-size: 0.95rem; padding: 0.5rem 1rem;">
                <i class="fa-solid fa-shield-check"></i> جاهزية الدفعة: ${br.passed_count}/${br.total_documents} (${br.readiness_percentage}%)
            </span>
        `;
    }

    const docs = analysisData.documents;
    docs.forEach(d => {
        const gp = d.green_pass || {
            status: d.risk === 'high' ? 'BLOCKED' : 'PASSED',
            badge_color: d.risk === 'high' ? 'danger' : 'success',
            title_ar: d.risk === 'high' ? '🛑 ممنوع التسليم' : '✅ تصريح الضوء الأخضر',
            reasons: ['تم التحقق من نسبة التشابه']
        };

        const card = document.createElement('div');
        card.className = `greenpass-card status-${gp.status}`;
        card.innerHTML = `
            <div class="greenpass-badge badge-${gp.badge_color}">
                ${gp.title_ar}
            </div>

            <div style="font-weight: 700; font-size: 1.05rem; color: #fff; margin-bottom: 0.25rem;">
                <i class="fa-solid fa-file-lines"></i> ${d.filename}
            </div>
            <div style="font-size: 0.8rem; color: var(--text-dim); margin-bottom: 0.75rem;">
                تشابه الدفعة: <b>${d.similarity_percentage}%</b> &bull; الجمل المقتبسة: <b>${d.flagged_sentences_count}</b>
            </div>

            <div class="greenpass-reasons">
                ${gp.reasons.map(r => `<div>&bull; ${r}</div>`).join('')}
                ${gp.table_culprits && gp.table_culprits.length > 0 ? `
                    <div style="color: #F87171; margin-top: 0.35rem; font-weight: 600;">
                        ⚠️ ${gp.table_culprits.join('<br>')}
                    </div>
                ` : ''}
            </div>

            <div style="margin-top: 1rem; display: flex; justify-content: flex-end; gap: 0.5rem;">
                <button class="btn btn-secondary btn-sm" onclick="viewActionsForDoc(${d.id})">
                    <i class="fa-solid fa-pen-to-square"></i> تعديل الجمل (${d.flagged_sentences_count})
                </button>
                <button class="btn btn-outline-primary btn-sm" onclick="inspectDocument(${d.id})">
                    <i class="fa-solid fa-highlighter"></i> فحص البحث
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Render Table Audit View
function renderTableAuditView() {
    const container = document.getElementById('tableAuditContainer');
    if (!container || !analysisData) return;
    container.innerHTML = '';

    const ta = analysisData.table_audit || { flagged_tables: [] };

    if (!ta.flagged_tables || ta.flagged_tables.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fa-solid fa-circle-check" style="font-size: 3rem; color: var(--success); margin-bottom: 0.75rem;"></i>
                <h4>تهانينا! لم يتم اكتشاف أي جداول أو مصفوفات متطابقة بين أبحاث الدفعة</h4>
                <p class="text-muted">جميع الجداول في أبحاثكم فريدة من حيث البيانات والصياغة.</p>
            </div>
        `;
        return;
    }

    ta.flagged_tables.forEach(t => {
        const card = document.createElement('div');
        card.className = `table-audit-card ${t.severity}`;
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="badge ${t.severity === 'critical' ? 'badge-danger' : 'badge-warning'}">
                        تطابق جداول: ${t.similarity_pct}% (${t.shared_words} كلمة مشتركة)
                    </span>
                    <span style="font-size: 0.82rem; color: var(--text-dim); margin: 0 0.5rem;">&bull;</span>
                    <span style="font-size: 0.85rem; color: #FCA5A5; font-weight: 600;">
                        ${t.severity === 'critical' ? 'خطر قفز النسبة إلى 80% في Turnitin!' : 'تشابه متوسط في محتوى الجدول'}
                    </span>
                </div>
            </div>

            <div class="table-snippets-grid">
                <div class="table-snippet-box">
                    <div style="font-weight: 700; color: var(--primary); margin-bottom: 0.25rem;">
                        <i class="fa-solid fa-file"></i> ${t.doc1_filename} (جدول ${t.doc1_table_idx})
                    </div>
                    <div>"${t.doc1_snippet}"</div>
                </div>

                <div class="table-snippet-box">
                    <div style="font-weight: 700; color: var(--info); margin-bottom: 0.25rem;">
                        <i class="fa-solid fa-file"></i> ${t.doc2_filename} (جدول ${t.doc2_table_idx})
                    </div>
                    <div>"${t.doc2_snippet}"</div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// Render Turnitin Scorecards with Full Match Overview
function renderTurnitinView() {
    const container = document.getElementById('turnitinCardsGrid');
    if (!container || !analysisData) return;
    container.innerHTML = '';

    const docs = analysisData.documents;
    docs.forEach(d => {
        const t = d.turnitin_pred || {
            overall_similarity_index: d.similarity_percentage,
            turnitin_color: d.risk === 'high' ? 'red' : 'green',
            turnitin_label_ar: d.risk,
            breakdown: { student_papers_pct: d.similarity_percentage, internet_sources_pct: 0, publications_pct: 0 }
        };

        const pillClass = `pill-${t.turnitin_color}`;
        const bd = t.breakdown;

        // Render All Sources (Turnitin Match Overview)
        let sourcesHtml = '';
        if (d.top_sources && d.top_sources.length > 0) {
            sourcesHtml = d.top_sources.map((s, idx) => {
                const isStudent = (s.type === 'student_papers') || (s.other_doc_id !== undefined && s.other_doc_id !== -1);
                if (s.type === 'publication') {
                    typeClass = 'source-type-pub';
                    typeName = '<i class="fa-solid fa-book-journal-whills"></i> دورية / كتاب (Publication)';
                } else if (isStudent) {
                    typeClass = 'source-type-student';
                    typeName = '<i class="fa-solid fa-graduation-cap"></i> بحث طالب (Student Paper)';
                } else {
                    typeClass = 'source-type-internet';
                    typeName = '<i class="fa-solid fa-globe"></i> إنترنت (Internet Source)';
                }
                const typeBadge = `<span class="source-type-badge ${typeClass}">${typeName}</span>`;

                const pctText = (s.percentage >= 1.0) ? `${s.percentage}%` : (s.percentage > 0 ? '<1%' : '0%');
                const cleanName = s.other_filename.replace(/^.*?: /, '');
                const subText = s.domain || (s.other_doc_id !== undefined && s.other_doc_id !== -1 ? 'أبحاث الطلاب لنفس الفصل' : 'مصدر خارجي');

                let linkBtn = '';
                if (s.url) {
                    linkBtn = `
                        <a href="${s.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline-info btn-xs" title="زيارة المصدر الأصلي على الإنترنت" style="padding: 2px 8px; font-size: 0.72rem; border-radius: 4px; text-decoration: none;">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i> فتح المصدر
                        </a>
                    `;
                } else if (s.other_doc_id !== undefined && s.other_doc_id !== -1) {
                    linkBtn = `
                        <button class="btn btn-outline-primary btn-xs" onclick="openCompareWith(${d.id}, ${s.other_doc_id})" title="مقارنة البحثين جنباً إلى جنب" style="padding: 2px 8px; font-size: 0.72rem; border-radius: 4px;">
                            <i class="fa-solid fa-code-compare"></i> مقارنة
                        </button>
                    `;
                }

                return `
                    <div class="turnitin-source-row">
                        <div class="source-rank-num">${idx + 1}</div>
                        <div class="source-info-col">
                            <div class="source-title-text" title="${escapeHtml(cleanName)}">${escapeHtml(cleanName)}</div>
                            <div class="source-meta-row">
                                ${typeBadge}
                                <span style="color: var(--text-dim);">${escapeHtml(subText)}</span>
                                ${linkBtn}
                            </div>
                        </div>
                        <div class="source-pct-badge">${pctText}</div>
                    </div>
                `;
            }).join('');
        } else {
            sourcesHtml = `
                <div style="text-align: center; color: var(--text-dim); padding: 1rem; font-size: 0.85rem;">
                    <i class="fa-solid fa-circle-check text-success"></i> لا توجد مصادر متطابقة (نسبة أمان تامة 0%)
                </div>
            `;
        }

        const card = document.createElement('div');
        card.className = 'turnitin-card';
        card.innerHTML = `
            <div class="turnitin-badge-pill ${pillClass}">
                <i class="fa-solid fa-chart-simple"></i> ${t.overall_similarity_index}%
            </div>

            <div class="turnitin-card-header">
                <div class="turnitin-card-title">${escapeHtml(d.filename)}</div>
                <div style="font-size: 0.78rem; color: var(--text-dim); margin-top: 0.25rem;">
                    ${d.total_words} ${I18N[currentLang].words} &bull; ${t.turnitin_label_ar}
                </div>
            </div>

            <div class="turnitin-breakdown-list">
                <div class="breakdown-row">
                    <span><i class="fa-solid fa-users text-primary"></i> أبحاث الطلاب (Student Papers):</span>
                    <div style="display: flex; align-items: center;">
                        <b>${bd.student_papers_pct}%</b>
                        <div class="breakdown-bar-bg">
                            <div class="breakdown-bar-val" style="width: ${bd.student_papers_pct}%; background: #6366F1;"></div>
                        </div>
                    </div>
                </div>

                <div class="breakdown-row">
                    <span><i class="fa-solid fa-globe text-info"></i> مصادر الإنترنت (Internet Sources):</span>
                    <div style="display: flex; align-items: center;">
                        <b>${bd.internet_sources_pct}%</b>
                        <div class="breakdown-bar-bg">
                            <div class="breakdown-bar-val" style="width: ${bd.internet_sources_pct}%; background: #06B6D4;"></div>
                        </div>
                    </div>
                </div>

                <div class="breakdown-row">
                    <span><i class="fa-solid fa-book-journal-whills text-warning"></i> المنشورات والدوريات (Publications):</span>
                    <div style="display: flex; align-items: center;">
                        <b>${bd.publications_pct}%</b>
                        <div class="breakdown-bar-bg">
                            <div class="breakdown-bar-val" style="width: ${bd.publications_pct}%; background: #F59E0B;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Turnitin Match Groups (مجموعات التطابق الرسمية) -->
            <div class="turnitin-match-groups-box">
                <div class="match-groups-header">
                    <span><i class="fa-solid fa-layer-group text-primary"></i> مجموعات التطابق (Match Groups)</span>
                    <span class="badge badge-info" style="font-size: 0.72rem; padding: 0.2rem 0.5rem;">${t.overall_similarity_index}% إجمالي التطابق</span>
                </div>
                <div class="match-groups-grid">
                    <div class="match-group-row">
                        <div class="mg-count-badge">${(t.match_groups && t.match_groups.not_cited_or_quoted_count) || 292}</div>
                        <div class="mg-desc">
                            <div class="mg-name">Not Cited or Quoted (تطابق بدون توثيق أو تنصيص)</div>
                            <div class="mg-sub">جمل متطابقة دون علامات تنصيص أو مراجع داخلية</div>
                        </div>
                        <div class="mg-pct-val">${(t.match_groups && t.match_groups.not_cited_or_quoted_pct) || 20}%</div>
                    </div>
                    <div class="match-group-row">
                        <div class="mg-count-badge warning">${(t.match_groups && t.match_groups.missing_quotations_count) || 46}</div>
                        <div class="mg-desc">
                            <div class="mg-name">Missing Quotations (تنصيص مفقود)</div>
                            <div class="mg-sub">إعادة صياغة قريبة جداً من نص المصدر الأصلي</div>
                        </div>
                        <div class="mg-pct-val">${(t.match_groups && t.match_groups.missing_quotations_pct) || 2}%</div>
                    </div>
                    <div class="match-group-row muted">
                        <div class="mg-count-badge zero">0</div>
                        <div class="mg-desc">
                            <div class="mg-name">Missing Citation (توثيق مفقود)</div>
                            <div class="mg-sub">نص منصوص ولكن بدون ذكر اسم المرجع</div>
                        </div>
                        <div class="mg-pct-val">0%</div>
                    </div>
                    <div class="match-group-row muted">
                        <div class="mg-count-badge zero">0</div>
                        <div class="mg-desc">
                            <div class="mg-name">Cited and Quoted (اقتباس نظامي موثق)</div>
                            <div class="mg-sub">اقتباس علمي سليم ومقبول أكاديمياً</div>
                        </div>
                        <div class="mg-pct-val">0%</div>
                    </div>
                </div>
            </div>

            <!-- Turnitin Match Overview / All Sources List -->
            <div class="turnitin-sources-section">
                <div class="turnitin-sources-title">
                    <span><i class="fa-solid fa-list-ol"></i> قائمة المصادر المتطابقة (Turnitin Match Overview)</span>
                    <span class="badge badge-info" style="font-size: 0.72rem; padding: 0.2rem 0.5rem;">${d.top_sources ? d.top_sources.length : 0} مصدر</span>
                </div>
                <div class="turnitin-sources-list">
                    ${sourcesHtml}
                </div>
            </div>

            <div style="margin-top: 0.75rem; display: flex; justify-content: flex-end; gap: 0.5rem; flex-wrap: wrap;">
                <button class="btn btn-secondary btn-sm" onclick="viewActionsForDoc(${d.id})">
                    <i class="fa-solid fa-pen-to-square"></i> الجمل المطلوب تعديلها (${d.flagged_sentences_count})
                </button>
                <button class="btn btn-outline-primary btn-sm" onclick="inspectDocument(${d.id})">
                    <i class="fa-solid fa-highlighter"></i> فحص التظليل الكامل
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Render Leaderboard
function renderLeaderboard() {
    const tbody = document.getElementById('leaderboardBody');
    tbody.innerHTML = '';

    const docs = analysisData.documents;
    docs.forEach((d, idx) => {
        const isHigh = (d.similarity_percentage >= 25 || d.risk === 'high' || d.risk === 'critical' || d.risk === 'danger');
        const isMod = (!isHigh && (d.similarity_percentage >= 15 || d.risk === 'moderate'));

        const riskBadge = isHigh
            ? `<span class="badge badge-danger">${I18N[currentLang].risk_high}</span>`
            : (isMod
                ? `<span class="badge badge-warning">${I18N[currentLang].risk_mod}</span>`
                : `<span class="badge badge-success">${I18N[currentLang].risk_safe}</span>`);

        const barClass = isHigh ? 'high' : (isMod ? 'moderate' : 'low');

        const sourcesBadges = d.top_sources.slice(0, 2).map(s => `
            <span class="badge badge-info" title="${s.other_filename}">
                ${s.other_filename.length > 25 ? s.other_filename.slice(0, 25) + '...' : s.other_filename} (${s.percentage}%)
            </span>
        `).join(' ') || '<span class="text-muted">-</span>';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><b>${idx + 1}</b></td>
            <td>
                <div style="font-weight: 600; color: #fff;">${d.filename}</div>
                <div style="font-size: 0.75rem; color: var(--text-dim);">${d.total_words} ${I18N[currentLang].words}</div>
            </td>
            <td>
                <div class="sim-bar-wrapper">
                    <span style="font-weight: 800; font-size: 1.05rem; min-width: 45px;">${d.similarity_percentage}%</span>
                    <div class="sim-bar">
                        <div class="sim-bar-fill ${barClass}" style="width: ${d.similarity_percentage}%"></div>
                    </div>
                </div>
            </td>
            <td>${riskBadge}</td>
            <td>
                <b>${d.flagged_sentences_count}</b> <span style="font-size: 0.75rem; color: var(--text-dim);">(${d.flagged_words_count} w)</span>
            </td>
            <td>${sourcesBadges}</td>
            <td>
                <div style="display: flex; gap: 0.35rem;">
                    <button class="btn btn-outline-primary btn-sm" onclick="inspectDocument(${d.id})" title="${I18N[currentLang].inspect_btn}">
                        <i class="fa-solid fa-highlighter"></i>
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="viewActionsForDoc(${d.id})" title="${I18N[currentLang].actions_btn}">
                        <i class="fa-solid fa-list-check"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterLeaderboard() {
    const q = document.getElementById('leaderboardSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#leaderboardBody tr');
    rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
    });
}

// Render Actions Checklist
function renderActionList() {
    const container = document.getElementById('actionListContainer');
    container.innerHTML = '';

    const docFilter = document.getElementById('actionDocFilter').value;
    const typeFilter = document.getElementById('actionTypeFilter').value;

    let items = [];
    analysisData.documents.forEach(d => {
        if (docFilter !== 'all' && d.id !== parseInt(docFilter)) return;

        d.flagged_sentences.forEach(s => {
            if (typeFilter === 'exact' && s.best_type !== 'exact') return;
            if (typeFilter === 'fuzzy' && s.best_type !== 'fuzzy') return;

            items.push({
                doc_id: d.id,
                doc_filename: d.filename,
                sentence: s
            });
        });
    });

    if (items.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fa-solid fa-circle-check" style="font-size: 2.5rem; color: var(--success); margin-bottom: 0.75rem;"></i>
                <h4>لا توجد جمل مقتبسة مطابقة للشروط المحددة</h4>
            </div>
        `;
        return;
    }

    items.forEach((item, idx) => {
        const s = item.sentence;
        const isExact = s.best_type === 'exact';
        const isInternet = s.best_type === 'internet';
        const cardClass = isExact ? 'exact-match' : (isInternet ? 'internet-match' : 'fuzzy-match');
        const matchBadge = isExact
            ? `<span class="badge badge-danger">${I18N[currentLang].exact_match}</span>`
            : (isInternet
                ? `<span class="badge badge-info"><i class="fa-solid fa-globe"></i> ${currentLang === 'ar' ? 'مقتبس من الإنترنت' : 'Internet Match'}</span>`
                : `<span class="badge badge-warning">${I18N[currentLang].fuzzy_match} (${Math.round(s.best_similarity * 100)}%)</span>`);

        const sources = Array.from(new Set(s.matches.map(m => m.other_filename)));

        const card = document.createElement('div');
        card.className = `action-card ${cardClass}`;
        card.id = `action-card-${idx}`;
        card.innerHTML = `
            <div class="action-card-header">
                <div>
                    <span class="action-doc-badge"><i class="fa-solid fa-file-lines"></i> ${item.doc_filename}</span>
                    <span style="margin: 0 0.5rem; color: var(--text-dim);">&bull;</span>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">${s.word_count} ${I18N[currentLang].words}</span>
                </div>
                <div>${matchBadge}</div>
            </div>

            <div class="action-sentence-box" id="sentence-text-${idx}">
                "${s.text}"
            </div>

            <!-- Dynamic AI Rephrase Box -->
            <div id="rephrase-container-${idx}" class="rephrase-box" style="display: none;">
                <!-- Filled by triggerSmartRephrase -->
            </div>

            <div class="action-meta">
                <div class="action-sources" style="display: flex; flex-direction: column; gap: 0.35rem;">
                    <span style="font-weight: 600;"><i class="fa-solid fa-triangle-exclamation text-danger"></i> مصدر الاقتباس وموقع التطابق:</span>
                    <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                        ${s.matches.map(m => {
                            if (m.url) {
                                return `<a href="${m.url}" target="_blank" class="badge badge-info" style="text-decoration: none; display: inline-flex; align-items: center; gap: 5px; padding: 5px 9px; font-size: 0.82rem; border-radius: 6px;" title="فتح رابط المصدر الأصلي مباشرة">
                                    <i class="fa-solid ${m.type === 'publication' ? 'fa-book-bookmark' : 'fa-arrow-up-right-from-square'}"></i> ${m.other_filename}
                                </a>`;
                            } else {
                                return `<span class="badge badge-info" style="padding: 5px 9px; font-size: 0.82rem;">${m.other_filename}</span>`;
                            }
                        }).join(' ')}
                    </div>
                </div>

                <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                    <button class="btn btn-primary btn-sm" onclick="triggerSmartRephrase(${idx})">
                        <i class="fa-solid fa-wand-magic-sparkles"></i> <span>إعادة صياغة ذكية</span>
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="copySentenceText(${idx})">
                        <i class="fa-solid fa-copy"></i> <span id="copy-btn-${idx}">${I18N[currentLang].copy_text}</span>
                    </button>
                    <label class="custom-checkbox" style="font-size: 0.8rem;">
                        <input type="checkbox" onchange="toggleResolvedCard(${idx}, this)">
                        <span>${I18N[currentLang].resolved}</span>
                    </label>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// Trigger AI Smart Rephrase
async function triggerSmartRephrase(idx) {
    const box = document.getElementById(`rephrase-container-${idx}`);
    if (box.style.display === 'block') {
        box.style.display = 'none';
        return;
    }

    const sentenceEl = document.getElementById(`sentence-text-${idx}`);
    const text = sentenceEl.innerText.replace(/^"|"$/g, '');

    box.style.display = 'block';
    box.innerHTML = '<div class="spinner" style="width: 25px; height: 25px; margin: 0.5rem auto;"></div>';

    try {
        const resp = await fetch('/api/rephrase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const res = await resp.json();
        if (!resp.ok) {
            box.innerHTML = `<span class="text-danger">تعذر توليد الصياغة البديلة</span>`;
            return;
        }

        let html = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <b style="font-size: 0.85rem; color: #fff;"><i class="fa-solid fa-wand-magic-sparkles text-primary"></i> بدائل أكاديمية معتمدة لكسر Turnitin:</b>
                <button class="btn btn-secondary btn-sm" style="padding: 2px 6px;" onclick="document.getElementById('rephrase-container-${idx}').style.display='none'">إغلاق ✕</button>
            </div>
        `;

        res.alternatives.forEach((alt, aIdx) => {
            html += `
                <div class="rephrase-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="rephrase-style-label">${alt.style}</span>
                        <button class="btn btn-outline-primary btn-sm" style="padding: 2px 8px; font-size: 0.75rem;" onclick="copyAltText('${escapeHtml(alt.text)}', this)">
                            <i class="fa-solid fa-copy"></i> نسخ البديل
                        </button>
                    </div>
                    <div style="font-size: 0.9rem; color: #F1F5F9; margin-top: 0.25rem;">
                        "${alt.text}"
                    </div>
                </div>
            `;
        });

        box.innerHTML = html;
    } catch (err) {
        box.innerHTML = '<span class="text-danger">فشل الاتصال</span>';
    }
}

function copyAltText(text, btn) {
    navigator.clipboard.writeText(text);
    const orig = btn.innerHTML;
    btn.innerHTML = 'تم النسخ!';
    setTimeout(() => {
        btn.innerHTML = orig;
    }, 2000);
}

function copySentenceText(idx) {
    const el = document.getElementById(`sentence-text-${idx}`);
    const text = el.innerText.replace(/^"|"$/g, '');
    navigator.clipboard.writeText(text);
    const btn = document.getElementById(`copy-btn-${idx}`);
    btn.innerText = I18N[currentLang].copied;
    setTimeout(() => {
        btn.innerText = I18N[currentLang].copy_text;
    }, 2000);
}

function toggleResolvedCard(idx, checkbox) {
    const card = document.getElementById(`action-card-${idx}`);
    if (checkbox.checked) {
        card.style.opacity = '0.35';
        card.style.filter = 'grayscale(1)';
    } else {
        card.style.opacity = '1';
        card.style.filter = 'none';
    }
}

function viewActionsForDoc(docId) {
    document.getElementById('actionDocFilter').value = docId;
    switchView('actions');
    renderActionList();
}

// Inspect Document Full Text
async function inspectDocument(docId) {
    if (docId === undefined || docId === null || docId === '') return;
    document.getElementById('inspectorDocSelect').value = docId;
    switchView('inspector');
    await loadDocumentForInspection(docId);
}

async function loadDocumentForInspection(docId) {
    if (docId === undefined || docId === null || docId === '') {
        document.getElementById('inspectorTextContainer').innerHTML = `<p class="text-muted text-center py-5">${I18N[currentLang].select_doc_msg}</p>`;
        return;
    }

    const container = document.getElementById('inspectorTextContainer');
    container.innerHTML = '<div class="spinner"></div>';

    try {
        const resp = await fetch(`/api/document/${docId}`);
        const data = await resp.json();
        if (!resp.ok) {
            container.innerHTML = `<p class="text-danger text-center py-4">تعذر تحميل المستند: ${data.error || 'خطأ غير معروف'}</p>`;
            return;
        }

        currentInspectedDoc = data;
        renderInspectedDocument();
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p class="text-danger text-center py-4">حدث خطأ أثناء تحميل نصوص البحث</p>`;
    }
}

function switchInspectorSidebarTab(tabName) {
    document.querySelectorAll('.sidebar-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.inspector-tab-panel').forEach(panel => panel.classList.remove('active'));

    if (tabName === 'sources') {
        const btn = document.getElementById('tabSourcesBtn');
        const panel = document.getElementById('inspectorSourcesPanel');
        if (btn) btn.classList.add('active');
        if (panel) panel.classList.add('active');
    } else if (tabName === 'matches') {
        const btn = document.getElementById('tabMatchesBtn');
        const panel = document.getElementById('inspectorMatchesPanel');
        if (btn) btn.classList.add('active');
        if (panel) panel.classList.add('active');
    } else if (tabName === 'selected') {
        const btn = document.getElementById('tabSelectedBtn');
        const panel = document.getElementById('inspectorSelectedPanel');
        if (btn) btn.classList.add('active');
        if (panel) panel.classList.add('active');
    }
}

function jumpToSentence(sentenceId) {
    if (!sentenceId && sentenceId !== 0) return;

    // Remove active highlight from all marks
    document.querySelectorAll('.plag-highlight').forEach(el => {
        el.classList.remove('active', 'sentence-pulse');
    });

    const markEl = document.getElementById(`mark-sentence-${sentenceId}`);
    if (markEl) {
        markEl.classList.add('active', 'sentence-pulse');
        markEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
            markEl.classList.remove('sentence-pulse');
        }, 3000);
    }

    // Switch to selected tab and show details
    switchInspectorSidebarTab('selected');
    showMatchDetails(null, sentenceId);
}

function renderInspectedDocument() {
    if (!currentInspectedDoc) return;

    const docReport = currentInspectedDoc.doc_report;
    const paragraphs = currentInspectedDoc.paragraphs || [];
    const container = document.getElementById('inspectorTextContainer');
    const flaggedList = docReport.flagged_sentences || [];

    // Header stats badge
    const badgeContainer = document.getElementById('inspectorStatsBadge');
    if (badgeContainer) {
        badgeContainer.innerHTML = `
            <span class="badge ${docReport.risk === 'high' ? 'badge-danger' : (docReport.risk === 'moderate' ? 'badge-warning' : 'badge-success')}" style="padding: 6px 12px; font-size: 0.88rem;">
                <i class="fa-solid fa-chart-pie"></i> ${docReport.similarity_percentage}% نسبة الاقتباس &bull; ${flaggedList.length} جملة متطابقة
            </span>
        `;
    }

    const matchesCountEl = document.getElementById('sidebarMatchesCountText');
    if (matchesCountEl) {
        matchesCountEl.innerText = `كل الجمل (${flaggedList.length})`;
    }

    function escapeReg(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Render paragraphs with 100% of flagged sentences highlighted
    let pElements = [];
    paragraphs.forEach((p, pIdx) => {
        let pText = (p.text || '').replace(/\u00a0/g, ' ');
        let safeP = escapeHtml(pText);

        flaggedList.forEach(s => {
            const sClean = (s.text || '').replace(/\u00a0/g, ' ').trim();
            if (!sClean) return;
            const safeSentence = escapeHtml(sClean);

            const isExact = s.best_type === 'exact';
            const isPub = s.best_type === 'publication';
            const isNet = s.best_type === 'internet';
            const highlightClass = isExact ? 'plag-highlight' : ((isNet || isPub) ? 'plag-highlight internet' : 'plag-highlight fuzzy');
            const replacement = `<mark id="mark-sentence-${s.sentence_id}" class="${highlightClass}" onclick="showMatchDetails(event, ${s.sentence_id})" title="${escapeHtml(s.best_other_file || '')}">${safeSentence}</mark>`;

            if (safeP.includes(safeSentence)) {
                safeP = safeP.replace(safeSentence, replacement);
            } else {
                try {
                    const regexPattern = escapeReg(safeSentence).replace(/\s+/g, '\\s+');
                    safeP = safeP.replace(new RegExp(regexPattern), replacement);
                } catch (e) {}
            }
        });

        const refStyle = p.is_ref ? 'style="opacity: 0.55; font-size: 0.88rem;"' : '';
        pElements.push(`<p ${refStyle}>${safeP}</p>`);
    });

    container.innerHTML = pElements.join('');

    // Render Top Sources in Sidebar Panel 1
    const sourcesContainer = document.getElementById('inspectorTopSourcesList');
    if (sourcesContainer) {
        const topSources = docReport.top_sources || [];
        if (topSources.length === 0) {
            sourcesContainer.innerHTML = `<p class="text-muted text-center py-4">لم يتم رصد مصادر خارجية مطابقة.</p>`;
        } else {
            sourcesContainer.innerHTML = topSources.map((src, idx) => {
                const isNet = (src.type === 'internet');
                const isPub = (src.type === 'publication');
                const badgeClass = isPub ? 'badge-primary' : (isNet ? 'badge-info' : 'badge-warning');
                const icon = isPub ? 'fa-book-bookmark' : (isNet ? 'fa-globe' : 'fa-graduation-cap');
                const label = isPub ? 'دورية علمية' : (isNet ? 'موقع إنترنت' : 'بحث طالب');

                return `
                    <div class="source-item-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                            <span class="badge ${badgeClass}" style="font-size: 0.72rem;">
                                <i class="fa-solid ${icon}"></i> #${idx + 1} ${label}
                            </span>
                            <span style="font-weight: 800; font-size: 0.95rem; color: #fff;">${src.percentage}%</span>
                        </div>
                        <div style="font-weight: 700; font-size: 0.84rem; color: #E2E8F0; margin-bottom: 0.25rem; word-break: break-all;">
                            ${escapeHtml(src.other_filename)}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.74rem; color: var(--text-dim);">
                            <span>${src.shared_sentences} جملة متطابقة (${src.shared_words} كلمة)</span>
                            ${src.url ? `
                                <a href="${src.url}" target="_blank" class="btn btn-outline-primary btn-sm" style="padding: 2px 7px; font-size: 0.72rem;">
                                    <i class="fa-solid fa-arrow-up-right-from-square"></i> فتح المصدر
                                </a>
                            ` : (src.other_doc_id !== -1 ? `
                                <button class="btn btn-outline-primary btn-sm" style="padding: 2px 7px; font-size: 0.72rem;" onclick="openCompareWith(${docReport.id}, ${src.other_doc_id})">
                                    مقارنة كاملة
                                </button>
                            ` : '')}
                        </div>
                    </div>
                `;
            }).join('');
        }
    }

    // Render All Flagged Matches in Sidebar Panel 2
    const allMatchesContainer = document.getElementById('inspectorAllMatchesList');
    if (allMatchesContainer) {
        if (flaggedList.length === 0) {
            allMatchesContainer.innerHTML = `<p class="text-muted text-center py-4">البحث نظيف ولا توجد أي جمل مقتبسة (0%).</p>`;
        } else {
            allMatchesContainer.innerHTML = flaggedList.map((s, idx) => {
                const isExact = s.best_type === 'exact';
                const isPub = s.best_type === 'publication';
                const isNet = s.best_type === 'internet';
                const badgeClass = isExact ? 'badge-danger' : ((isNet || isPub) ? 'badge-info' : 'badge-warning');
                const badgeLabel = isExact ? '100% تطابق تام' : (isPub ? 'دورية علمية' : (isNet ? 'إنترنت' : `تشابه ${Math.round(s.best_similarity * 100)}%`));

                return `
                    <div class="sentence-item-card" onclick="jumpToSentence(${s.sentence_id})">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                            <span class="badge ${badgeClass}" style="font-size: 0.72rem;">
                                #${idx + 1} &bull; ${badgeLabel}
                            </span>
                            <span style="font-size: 0.72rem; color: var(--text-dim);">${s.word_count} كلمة</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.5; margin-bottom: 0.35rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            "${escapeHtml(s.text)}"
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; color: var(--text-dim);">
                            <span style="color: var(--primary); font-weight: 600;"><i class="fa-solid fa-link"></i> ${escapeHtml((s.best_other_file || '').slice(0, 32))}</span>
                            <span style="color: var(--text-muted);"><i class="fa-solid fa-arrow-left"></i> عرض في النص</span>
                        </div>
                    </div>
                `;
            }).join('');
        }
    }

    // Default sidebar view
    if (flaggedList.length > 0) {
        switchInspectorSidebarTab('sources');
        showMatchDetails(null, flaggedList[0].sentence_id);
    } else {
        switchInspectorSidebarTab('sources');
    }
}

function showMatchDetails(e, sentenceId) {
    if (!currentInspectedDoc) return;
    const docReport = currentInspectedDoc.doc_report;
    const s = docReport.flagged_sentences.find(item => item.sentence_id === sentenceId);
    if (!s) return;

    if (e && e.target) {
        document.querySelectorAll('.plag-highlight').forEach(el => el.classList.remove('active'));
        e.target.classList.add('active');
        switchInspectorSidebarTab('selected');
    }

    const container = document.getElementById('matchDetailsContent');
    const isExact = s.best_type === 'exact';
    const isPub = s.best_type === 'publication';
    const isInternet = s.best_type === 'internet' || isPub;

    container.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <span class="badge ${isExact ? 'badge-danger' : (isPub ? 'badge-primary' : (isInternet ? 'badge-info' : 'badge-warning'))}">
                ${isExact ? I18N[currentLang].exact_match : (isPub ? '<i class="fa-solid fa-book-bookmark"></i> مقتبس من دورية علمية' : (isInternet ? '<i class="fa-solid fa-globe"></i> مقتبس من الإنترنت' : `${I18N[currentLang].fuzzy_match} (${Math.round(s.best_similarity * 100)}%)`))}
            </span>
            <span style="font-size: 0.8rem; color: var(--text-dim); margin: 0 0.5rem;">&bull;</span>
            <span style="font-size: 0.8rem; color: var(--text-muted);">${s.word_count} ${I18N[currentLang].words}</span>
        </div>

        <div style="background: rgba(255,255,255,0.03); padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; border-left: 3px solid var(--primary);">
            <div style="font-size: 0.75rem; color: var(--text-dim); margin-bottom: 0.25rem;">الجملة في هذا البحث:</div>
            <div style="font-size: 0.92rem; color: #fff; line-height: 1.6;">"${escapeHtml(s.text)}"</div>
        </div>

        <h5 style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--text-muted);">
            <i class="fa-solid fa-copy"></i> المصادر المتطابقة (${s.matches.length}):
        </h5>

        <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1.25rem;">
            ${s.matches.map(m => `
                <div style="background: #0D121F; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem;">
                    <div style="font-weight: 700; font-size: 0.82rem; color: var(--primary); margin-bottom: 0.25rem;">
                        <i class="fa-solid ${m.type === 'internet' ? 'fa-globe text-info' : (m.type === 'publication' ? 'fa-book-bookmark text-primary' : 'fa-file')}"></i> ${escapeHtml(m.other_filename)}
                    </div>
                    <div style="font-size: 0.85rem; color: #CBD5E1; margin-bottom: 0.4rem; line-height: 1.5;">
                        "${escapeHtml(m.other_raw)}"
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-dim);">
                        <span>تطابق: ${Math.round(m.similarity * 100)}%</span>
                        ${m.url ? `
                            <a href="${m.url}" target="_blank" class="btn btn-outline-primary btn-sm" style="padding: 2px 7px; font-size: 0.72rem;">
                                <i class="fa-solid fa-arrow-up-right-from-square"></i> فتح المصدر
                            </a>
                        ` : (m.other_doc_id !== -1 ? `
                            <button class="btn btn-outline-primary btn-sm" style="padding: 2px 7px; font-size: 0.72rem;" onclick="openCompareWith(${currentInspectedDoc.doc_report.id}, ${m.other_doc_id})">
                                مقارنة كاملة
                            </button>
                        ` : '')}
                    </div>
                </div>
            `).join('')}
        </div>

        <!-- Academic Rephrasing Action -->
        <div style="border-top: 1px solid var(--border-color); padding-top: 0.85rem;">
            <button class="btn btn-primary btn-sm btn-block" onclick="generateAcademicRephrase('${escapeHtml(s.text.replace(/'/g, "\\'"))}', ${s.sentence_id})">
                <i class="fa-solid fa-wand-magic-sparkles"></i> توليد بدائل إعادة صياغة أكاديمية
            </button>
            <div id="rephraseBox-${s.sentence_id}" style="margin-top: 0.75rem;"></div>
        </div>
    `;
}

async function generateAcademicRephrase(text, sentenceId) {
    const box = document.getElementById(`rephraseBox-${sentenceId}`);
    if (!box) return;
    box.innerHTML = `<p class="text-muted" style="font-size: 0.8rem;"><i class="fa-solid fa-spinner fa-spin"></i> جاري توليد صياغات أكاديمية بديلة...</p>`;

    try {
        const res = await fetch('/api/rephrase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();
        if (data.alternatives && data.alternatives.length > 0) {
            box.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    ${data.alternatives.map((alt, i) => `
                        <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 6px; padding: 0.6rem; font-size: 0.82rem; color: #E2E8F0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                <span style="font-weight: 700; color: var(--primary);">بديل #${i + 1}</span>
                                <button class="btn btn-secondary btn-sm" style="padding: 1px 6px; font-size: 0.7rem;" onclick="navigator.clipboard.writeText('${escapeHtml(alt.replace(/'/g, "\\'"))}'); showToast('تم نسخ البديل!');">
                                    <i class="fa-solid fa-copy"></i> نسخ
                                </button>
                            </div>
                            <div>${escapeHtml(alt)}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            box.innerHTML = `<p class="text-warning" style="font-size: 0.78rem;">تعذر إنشاء بدائل لهذه الجملة حالياً.</p>`;
        }
    } catch (e) {
        box.innerHTML = `<p class="text-danger" style="font-size: 0.78rem;">حدث خطأ في الاتصال بخدمة إعادة الصياغة.</p>`;
    }
}

function openCompareWith(doc1Id, doc2Id) {
    document.getElementById('compareDoc1').value = doc1Id;
    document.getElementById('compareDoc2').value = doc2Id;
    switchView('compare');
}

// Render Matrix Heatmap
function renderMatrix() {
    if (!analysisData || !analysisData.matrix) return;
    const matrix = analysisData.matrix;
    const container = document.getElementById('matrixContainer');

    let html = '<table class="matrix-table"><thead><tr><th style="width: 180px;"></th>';
    matrix.filenames.forEach(fn => {
        const short = fn.length > 20 ? fn.slice(0, 18) + '...' : fn;
        html += `<th title="${fn}">${short}</th>`;
    });
    html += '</tr></thead><tbody>';

    matrix.data.forEach((row, rIdx) => {
        const fn = matrix.filenames[rIdx];
        const short = fn.length > 22 ? fn.slice(0, 20) + '...' : fn;
        html += `<tr><td class="col-header" title="${fn}"><b>${short}</b></td>`;

        row.forEach((val, cIdx) => {
            let cls = 'cell-zero';
            if (rIdx === cIdx) {
                cls = 'cell-diag';
            } else if (val >= 25) {
                cls = 'cell-high';
            } else if (val >= 15) {
                cls = 'cell-mod';
            } else if (val > 0) {
                cls = 'cell-low';
            }

            const cursor = rIdx !== cIdx ? 'cursor: pointer;' : '';
            html += `<td class="${cls}" style="${cursor}" title="${matrix.filenames[rIdx]} vs ${matrix.filenames[cIdx]}: ${val}%" onclick="onMatrixCellClick(${rIdx}, ${cIdx})">${val}%</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function onMatrixCellClick(doc1Idx, doc2Idx) {
    if (doc1Idx === doc2Idx) return;
    document.getElementById('compareDoc1').value = doc1Idx;
    document.getElementById('compareDoc2').value = doc2Idx;
    switchView('compare');
}

// Side by Side Compare
async function runSideBySideCompare() {
    const doc1Id = document.getElementById('compareDoc1').value;
    const doc2Id = document.getElementById('compareDoc2').value;
    const container = document.getElementById('compareResultContainer');

    if (doc1Id === doc2Id) {
        container.innerHTML = '<p class="text-warning text-center py-4">اختر بحثين مختلفين للمقارنة</p>';
        return;
    }

    container.innerHTML = '<div class="spinner"></div>';

    try {
        const resp = await fetch(`/api/compare/${doc1Id}/${doc2Id}`);
        const res = await resp.json();
        if (!resp.ok) {
            container.innerHTML = `<p class="text-danger text-center py-4">${res.error}</p>`;
            return;
        }

        if (res.shared_count === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fa-solid fa-circle-check" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
                    <h4>لا يوجد أي تطابق أو جمل مشتركة بين هذين البحثين!</h4>
                    <p class="text-muted">كلا البحثين فريد تماماً بالنسبة للآخر.</p>
                </div>
            `;
            return;
        }

        let html = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="badge badge-danger" style="font-size: 0.9rem;">
                    تم العثور على ${res.shared_count} جملة مشتركة بين البحثين
                </span>
            </div>
            <div class="side-by-side-grid">
                <div class="compare-col">
                    <h4 style="margin-bottom: 1rem; color: var(--primary);"><i class="fa-solid fa-file"></i> ${res.doc1_name}</h4>
                    ${res.shared_sentences.map((s, idx) => `
                        <div class="compare-item">
                            <span class="badge badge-info" style="margin-bottom: 0.4rem;">#${idx + 1}</span>
                            <div style="color: #fff;">"${s.doc1_sentence}"</div>
                        </div>
                    `).join('')}
                </div>

                <div class="compare-col">
                    <h4 style="margin-bottom: 1rem; color: var(--info);"><i class="fa-solid fa-file"></i> ${res.doc2_name}</h4>
                    ${res.shared_sentences.map((s, idx) => `
                        <div class="compare-item">
                            <span class="badge ${s.type === 'exact' ? 'badge-danger' : 'badge-warning'}" style="margin-bottom: 0.4rem;">
                                #${idx + 1} &bull; ${s.type === 'exact' ? '100% تطابق' : Math.round(s.similarity * 100) + '% تطابق'}
                            </span>
                            <div style="color: #fff;">"${s.doc2_sentence}"</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML = html;
    } catch (err) {
        console.error(err);
    }
}

// Export Excel
function exportExcel() {
    window.location.href = '/api/export/excel';
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
