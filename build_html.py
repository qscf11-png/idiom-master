import json
import os
from opencc import OpenCC

def build_html():
    vocab_data_path = "vocab_data.js"
    idiom_data_path = "idiom_data.js"
    output_path = "index.html"
    
    cc = OpenCC('s2t') # 簡體轉繁體

    # 讀取英文資料
    if not os.path.exists(vocab_data_path):
        print(f"Error: {vocab_data_path} not found.")
        return
    with open(vocab_data_path, "r", encoding="utf-8") as f:
        read_v = f.read()
        v_js = read_v.replace("const VOCAB_DB = ", "").strip()
        if v_js.endswith(";"): v_js = v_js[:-1]
    
    # 英文資料繁體化 (針對翻譯部分)
    v_js = cc.convert(v_js)

    # 讀取成語資料
    idiom_js = "[]"
    if os.path.exists(idiom_data_path):
        with open(idiom_data_path, "r", encoding="utf-8") as f:
            read_i = f.read()
            idiom_js = read_i.replace("const IDIOM_DB = ", "").strip()
            if idiom_js.endswith(";"): idiom_js = idiom_js[:-1]
    
    # 成語資料繁體化
    idiom_js = cc.convert(idiom_js)

    content = []
    content.append(r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全能學習大師 Vocab & Idiom Master</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: linear-gradient(135deg, #e0e7ff 0%, #f1f5f9 50%, #dbeafe 100%); margin: 0; padding: 0; min-height: 100vh; }
        .glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.5); }
        .info-block { border-left: 4px solid; padding: 8px 12px; border-radius: 0 8px 8px 0; margin-bottom: 8px; }
        /* SRS 按鈕顏色 */
        .btn-again { border-color: #fee2e2; color: #dc2626; background: #fff5f5; }
        .btn-again:hover { background: #fee2e2; }
        .btn-hard { border-color: #ffedd5; color: #d97706; background: #fffafb; }
        .btn-hard:hover { background: #ffedd5; }
        .btn-good { border-color: #dcfce7; color: #16a34a; background: #f0fdf4; }
        .btn-good:hover { background: #dcfce7; }
        .btn-easy { border-color: #dbeafe; color: #2563eb; background: #eff6ff; }
        .btn-easy:hover { background: #dbeafe; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script id="vocab-data" type="application/json">""")
    content.append(v_js)
    content.append(r"""</script>
    <script id="idiom-data" type="application/json">""")
    content.append(idiom_js)
    content.append(r"""</script>

    <script type="text/javascript">
        // 語音朗讀函式
        function speak(text, rate, lang) {
            if (!text) return;
            window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance(text);
            u.lang = lang || 'en-US'; u.rate = rate || 1.0;
            window.speechSynthesis.speak(u);
        }

        (function() {
            var h = React.createElement;
            var useState = React.useState;
            var useEffect = React.useEffect;
            var useMemo = React.useMemo;
            var useRef = React.useRef;
            var useCallback = React.useCallback;
            
            var VOCAB_DB_RAW = JSON.parse(document.getElementById('vocab-data').textContent);
            var IDIOM_DB_RAW = JSON.parse(document.getElementById('idiom-data').textContent);

            function shuffle(arr) {
                var n = arr.slice();
                for(var i = n.length - 1; i > 0; i--) {
                    var j = Math.floor(Math.random() * (i + 1));
                    var tmp = n[i]; n[i] = n[j]; n[j] = tmp;
                }
                return n;
            }

            // ===== 範本下載功能 =====
            function downloadTemplate(type) {
                var wb = XLSX.utils.book_new();
                if (type === 'vocab') {
                    var data = [
                        { word: 'abandon', definition: '放棄', pronunciation: '/əˈbændən/', related: 'give up, forsake', collocations: 'abandon hope', example: 'He abandoned his plan.', pos: 'verb', level: 3 },
                        { word: 'benefit', definition: '好處；利益', pronunciation: '/ˈbenɪfɪt/', related: 'advantage, profit', collocations: 'benefit from', example: 'Exercise benefits your health.', pos: 'noun', level: 2 }
                    ];
                    var ws = XLSX.utils.json_to_sheet(data);
                    XLSX.utils.book_append_sheet(wb, ws, '英文單字');
                    XLSX.writeFile(wb, 'english_vocab_template.xlsx');
                } else {
                    var data = [
                        { word: '一石二鳥', explanation: '比喻做一件事同時達到兩個目的。', pinyin: 'yī shí èr niǎo', source: '《英語諺語》', example: '這次活動一石二鳥，既宣傳了產品又拉近了客戶關係。' },
                        { word: '畫龍點睛', explanation: '比喻作文或說話時，在關鍵處加上精闢的語句，使內容更加生動。', pinyin: 'huà lóng diǎn jīng', source: '《歷代名畫記》', example: '他的最後一句話真是畫龍點睛。' }
                    ];
                    var ws = XLSX.utils.json_to_sheet(data);
                    XLSX.utils.book_append_sheet(wb, ws, '中文成語');
                    XLSX.writeFile(wb, 'idiom_template.xlsx');
                }
            }

            // ===== 匯入 Excel 功能 =====
            function importExcel(file, callback) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var data = new Uint8Array(e.target.result);
                    var wb = XLSX.read(data, { type: 'array' });
                    var ws = wb.Sheets[wb.SheetNames[0]];
                    var rows = XLSX.utils.sheet_to_json(ws);
                    if (!rows.length) { alert('檔案中沒有資料！'); return; }
                    
                    // 自動偵測科目類型
                    var keys = Object.keys(rows[0]).map(function(k) { return k.toLowerCase(); });
                    var isIdiom = keys.indexOf('explanation') !== -1 || keys.indexOf('pinyin') !== -1;
                    
                    var converted;
                    if (isIdiom) {
                        converted = rows.map(function(r) {
                            return { w: r.word || r.Word || '', d: r.explanation || r.Explanation || '', py: r.pinyin || r.Pinyin || '', o: r.source || r.Source || '', x: r.example || r.Example || '' };
                        });
                        callback({ subject: 'idiom', data: converted });
                    } else {
                        converted = rows.map(function(r) {
                            return { w: r.word || r.Word || '', d: r.definition || r.Definition || '', pr: r.pronunciation || r.Pronunciation || '', re: r.related || r.Related || '', co: r.collocations || r.Collocations || '', x: r.example || r.Example || '', po: r.pos || r.POS || '', l: parseInt(r.level || r.Level) || 1 };
                        });
                        callback({ subject: 'vocab', data: converted });
                    }
                };
                reader.readAsArrayBuffer(file);
            }

            // ===== 成語填空元件（支援注音 IME） =====
            function IdiomFillIn(props) {
                var word = props.word;
                var onComplete = props.onComplete;
                var inputsRef = useRef([]);
                var composingRef = useRef(false);
                var chars = word.split('');
                var [values, setValues] = useState(function() {
                    var arr = new Array(chars.length).fill('');
                    arr[0] = chars[0]; // 預填首字
                    return arr;
                });
                var [submitted, setSubmitted] = useState(false);

                function handleCompositionStart() { composingRef.current = true; }
                function handleCompositionEnd(idx, e) {
                    composingRef.current = false;
                    // 如果 e.data 存在，則取最後一個字元
                    var finalChar = (e.data && e.data.length > 0) ? e.data.slice(-1) : '';
                    if (finalChar && !submitted && idx !== 0) {
                        var nv = values.slice(); nv[idx] = finalChar;
                        setValues(nv);
                        // 自動跳至下一格
                        if (idx < chars.length - 1) {
                            setTimeout(function() { inputsRef.current[idx + 1] && inputsRef.current[idx + 1].focus(); }, 50);
                        }
                    }
                }

                function handleInput(idx, e) {
                    if (submitted || idx === 0) return;
                    // 在非 IME 組合期間才處理輸入 (針對英文或直接貼上)
                    if (!composingRef.current) {
                        var val = e.target.value;
                        if (!val) {
                            var nv = values.slice(); nv[idx] = '';
                            setValues(nv);
                            return;
                        }
                        var nv = values.slice(); nv[idx] = val.slice(-1);
                        setValues(nv);
                        if (idx < chars.length - 1) {
                            setTimeout(function() { inputsRef.current[idx + 1] && inputsRef.current[idx + 1].focus(); }, 10);
                        }
                    } else {
                        // IME 期間暫存顯示數值以防輸入框看起來沒反應
                        var nv = values.slice(); nv[idx] = e.target.value;
                        setValues(nv);
                    }
                }

                function handleKeyDown(idx, e) {
                    if (e.key === 'Backspace' && values[idx] === '' && idx > 1) {
                        setTimeout(function() { inputsRef.current[idx - 1] && inputsRef.current[idx - 1].focus(); }, 10);
                        return;
                    }
                    if (e.key === 'Enter' && !composingRef.current) {
                        setSubmitted(true);
                        // 移除立即觸發 onComplete，讓使用者先看回饋
                    }
                }

                var isWordCorrect = values.join('') === word;

                return h('div', { className: 'flex flex-col items-center gap-6' },
                    h('div', { className: 'flex justify-center gap-2 flex-wrap' }, chars.map(function(ch, i) {
                        var statusClass = '';
                        if (i === 0) statusClass = 'bg-slate-50 border-slate-200 text-slate-400';
                        else if (submitted) {
                            statusClass = (values[i] === chars[i]) ? 
                                'border-green-500 bg-green-50 text-green-700 shadow-[0_0_15px_rgba(16,185,129,0.2)]' : 
                                'border-red-500 bg-red-50 text-red-700 shadow-[0_0_15px_rgba(239,68,68,0.2)]';
                        } else {
                            statusClass = 'border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100';
                        }

                        return h('input', {
                            key: i,
                            ref: function(el) { inputsRef.current[i] = el; },
                            className: 'w-14 h-16 text-center text-2xl font-black rounded-xl border-2 transition-all ' + statusClass,
                            value: values[i],
                            onInput: function(e) { handleInput(i, e); },
                            onCompositionStart: handleCompositionStart,
                            onCompositionEnd: function(e) { handleCompositionEnd(i, e); },
                            onKeyDown: function(e) { handleKeyDown(i, e); },
                            disabled: submitted || i === 0,
                            autoComplete: 'off'
                        });
                    })),
                    !submitted ? h('p', { className: 'text-xs font-black text-slate-300 animate-pulse' }, "輸入完成後按 Enter 檢查") :
                    h('div', { className: 'text-center animate-in fade-in zoom-in duration-300' },
                        h('p', { className: 'text-lg font-black mb-4 ' + (isWordCorrect ? 'text-green-600' : 'text-red-500') },
                            isWordCorrect ? '✨ 太棒了！完美正確' : '📌 應該是：' + word
                        ),
                        h('button', { 
                            onClick: function() { onComplete(isWordCorrect); },
                            className: 'px-8 py-3 bg-indigo-600 text-white rounded-2xl font-black shadow-lg shadow-indigo-100 hover:scale-105 transition-all'
                        }, "查看完整詳細資料")
                    )
                );
            }

            // ===== 英文單字填空元件 =====
            function VocabFillIn(props) {
                var word = props.word;
                var onComplete = props.onComplete;
                var inputsRef = useRef([]);
                var chars = word.toLowerCase().split('');
                var [values, setValues] = useState(function() {
                    var arr = new Array(chars.length).fill('');
                    arr[0] = chars[0]; // 預填首字母
                    return arr;
                });
                var [submitted, setSubmitted] = useState(false);

                function handleChange(idx, e) {
                    if (submitted || idx === 0) return;
                    var val = e.target.value.toLowerCase();
                    var nv = values.slice(); nv[idx] = val.slice(-1);
                    setValues(nv);
                    if (val !== '' && idx < chars.length - 1) {
                        setTimeout(function() { inputsRef.current[idx + 1] && inputsRef.current[idx + 1].focus(); }, 10);
                    }
                }

                function handleKeyDown(idx, e) {
                    if (e.key === 'Backspace' && values[idx] === '' && idx > 1) {
                        setTimeout(function() { inputsRef.current[idx - 1] && inputsRef.current[idx - 1].focus(); }, 10);
                        return;
                    }
                    if (e.key === 'Enter') {
                        setSubmitted(true);
                    }
                }

                var isWordCorrect = values.join('') === word.toLowerCase();

                return h('div', { className: 'flex flex-col items-center gap-6 font-mono' },
                    h('div', { className: 'flex justify-center gap-1.5 flex-wrap' }, chars.map(function(ch, i) {
                        var statusClass = '';
                        if (i === 0) statusClass = 'bg-slate-50 border-slate-200 text-slate-400';
                        else if (submitted) {
                            statusClass = (values[i] === chars[i]) ? 
                                'border-green-500 bg-green-50 text-green-700 shadow-[0_0_15px_rgba(16,185,129,0.2)]' : 
                                'border-red-500 bg-red-50 text-red-700 shadow-[0_0_15px_rgba(239,68,68,0.2)]';
                        } else {
                            statusClass = 'border-slate-200 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100';
                        }

                        return h('input', {
                            key: i,
                            ref: function(el) { inputsRef.current[i] = el; },
                            className: 'w-10 h-12 text-center text-xl font-black rounded-lg border-2 transition-all lowercase ' + statusClass,
                            value: values[i],
                            onInput: function(e) { handleChange(i, e); },
                            onKeyDown: function(e) { handleKeyDown(i, e); },
                            disabled: submitted || i === 0,
                            maxLength: 1,
                            autoComplete: 'off'
                        });
                    })),
                    !submitted ? h('p', { className: 'text-xs font-black text-slate-300 animate-pulse' }, "輸入完成後按 Enter 檢查") :
                    h('div', { className: 'text-center animate-in fade-in zoom-in duration-300' },
                        h('p', { className: 'text-lg font-black mb-4 ' + (isWordCorrect ? 'text-green-600' : 'text-red-500') },
                            isWordCorrect ? '✅ 拼法正確！' : '📌 正確答案：' + word
                        ),
                        h('button', { 
                            onClick: function() { onComplete(isWordCorrect); },
                            className: 'px-8 py-3 bg-indigo-600 text-white rounded-2xl font-black shadow-lg shadow-indigo-100 hover:scale-105 transition-all'
                        }, "查看詳細資訊")
                    )
                );
            }

            function App() {
                var [subject, setSubject] = useState(null);
                var [mode, setMode] = useState('flashcard'); // flashcard or fillin
                var [activeList, setActiveList] = useState([]);
                var [totalInitial, setTotalInitial] = useState(0);
                var [stats, setStats] = useState({ again: 0, hard: 0, good: 0, easy: 0 });
                var [isSettingUp, setIsSettingUp] = useState(false);
                var [isFlipped, setIsFlipped] = useState(false);
                var [speechRate, setSpeechRate] = useState(1.0);
                var [levels, setLevels] = useState([1,2,3,4,5,6]);
                var [count, setCount] = useState(50);
                var [isFinished, setIsFinished] = useState(false);
                var [customDB, setCustomDB] = useState(null);
                var [customSubject, setCustomSubject] = useState(null);
                var fileInputRef = useRef(null);

                var currentDB = useMemo(function() {
                    if (customDB) return customDB;
                    if (!subject) return [];
                    return subject === 'idiom' ? IDIOM_DB_RAW : VOCAB_DB_RAW;
                }, [subject, customDB]);

                var filteredCount = useMemo(function() {
                    if (!subject) return 0;
                    if (customDB) return customDB.length;
                    if (subject === 'idiom') return currentDB.length;
                    return currentDB.filter(function(x) { return levels.indexOf(x.l) !== -1; }).length;
                }, [currentDB, levels, subject, customDB]);

                function startQuiz() {
                    var f;
                    if (customDB) {
                        f = customDB;
                    } else if (subject === 'idiom') {
                        f = currentDB;
                    } else {
                        f = currentDB.filter(function(x) { return levels.indexOf(x.l) !== -1; });
                    }
                    if (f.length === 0) return;
                    var sampled = shuffle(f).slice(0, Math.min(count, f.length));
                    setActiveList(sampled); setTotalInitial(sampled.length);
                    setStats({ again: 0, hard: 0, good: 0, easy: 0 });
                    setIsSettingUp(false); setIsFinished(false); setIsFlipped(false);
                }

                function goHome() {
                    setSubject(null); setCustomDB(null); setCustomSubject(null);
                    setActiveList([]); setIsSettingUp(false); setIsFinished(false); setIsFlipped(false);
                }

                function handleSRS(type) {
                    setStats(function(prev) { var n = Object.assign({}, prev); n[type]++; return n; });
                    var rest = activeList.slice(1); var curr = activeList[0]; var next;
                    if(type === 'again') next = rest.length > 0 ? [rest[0], curr].concat(rest.slice(1)) : [curr];
                    else if(type === 'hard') next = rest.length >= 4 ? rest.slice(0,4).concat([curr]).concat(rest.slice(4)) : rest.concat([curr]);
                    else if(type === 'good') next = rest.concat([curr]);
                    else next = rest;
                    if(next.length === 0) setIsFinished(true);
                    setActiveList(next); setIsFlipped(false);
                }

                function handleFileImport(e) {
                    var file = e.target.files[0];
                    if (!file) return;
                    importExcel(file, function(result) {
                        setCustomDB(result.data);
                        setCustomSubject(result.subject);
                        setSubject(result.subject);
                        setMode('flashcard');
                        setIsSettingUp(true);
                    });
                    e.target.value = '';
                }

                // 自動語音朗讀（正面）
                useEffect(function() {
                    if (activeList.length > 0 && !isFlipped && !isSettingUp && !isFinished) {
                        var item = activeList[0];
                        var l = (subject === 'idiom') ? 'zh-TW' : 'en-US';
                        if (mode === 'flashcard') {
                            setTimeout(function() { speak(item.w, speechRate, l); }, 300);
                        } else if (mode === 'fillin' && subject === 'idiom') {
                            setTimeout(function() { speak(item.d, speechRate, 'zh-TW'); }, 300);
                        }
                    }
                }, [activeList.length, isFlipped, isSettingUp, subject, mode]);

                // 自動語音朗讀（背面）
                useEffect(function() {
                    if (activeList.length > 0 && isFlipped && !isFinished) {
                        var item = activeList[0];
                        var l = (subject === 'idiom') ? 'zh-TW' : 'en-US';
                        var textToSpeak = item.x ? item.x : item.w;
                        setTimeout(function() { speak(textToSpeak, speechRate, l); }, 100);
                    }
                }, [isFlipped]);

                // 快捷鍵
                useEffect(function() {
                    function handleK(e) {
                        if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                        if(activeList.length === 0 || isFinished) return;
                        if (mode === 'flashcard' && (e.key === ' ' || e.code === 'Space')) { 
                            e.preventDefault(); setIsFlipped(true); 
                        }
                        if(isFlipped) {
                            if(e.key === '1') handleSRS('again'); if(e.key === '2') handleSRS('hard');
                            if(e.key === '3') handleSRS('good'); if(e.key === '4') handleSRS('easy');
                        }
                    }
                    window.addEventListener('keydown', handleK);
                    return function() { window.removeEventListener('keydown', handleK); };
                });

                // ===== 首頁 =====
                if (!subject || (!activeList.length && !isSettingUp && !isFinished)) {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-10 text-center" },
                            h('h1', { className: "text-3xl font-black mb-6" }, "全能學習大師"),
                            h('div', { className: "grid grid-cols-1 gap-3 mb-6" },
                                // 英文模式
                                h('button', { onClick: function() { setCustomDB(null); setSubject('vocab'); setMode('flashcard'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-indigo-50 transition-all font-bold" }, "英文單字 (閃卡)"),
                                h('button', { onClick: function() { setCustomDB(null); setSubject('vocab'); setMode('fillin'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-violet-50 transition-all font-bold" }, "英文單字 (填空)"),
                                // 成語模式
                                h('button', { onClick: function() { setCustomDB(null); setSubject('idiom'); setMode('flashcard'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-emerald-50 transition-all font-bold" }, "中文成語 (閃卡)"),
                                h('button', { onClick: function() { setCustomDB(null); setSubject('idiom'); setMode('fillin'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-amber-50 transition-all font-bold" }, "中文成語 (填空)")
                            ),
                            // 匯入自訂字庫
                            h('div', { className: "border-t border-slate-200 pt-6 mt-2 space-y-3" },
                                h('input', { type: 'file', accept: '.xlsx,.xls', ref: fileInputRef, onChange: handleFileImport, className: 'hidden' }),
                                h('button', { onClick: function() { fileInputRef.current && fileInputRef.current.click(); }, className: "w-full py-4 rounded-2xl border-2 border-dashed border-slate-300 hover:bg-slate-50 transition-all font-bold text-slate-500" }, "📂 匯入自訂 Excel 字庫"),
                                h('p', { className: "text-xs text-slate-400" }, "支援英文單字 / 中文成語格式，系統自動偵測"),
                                // 範本下載
                                h('div', { className: "flex gap-2 justify-center" },
                                    h('button', { onClick: function() { downloadTemplate('vocab'); }, className: "text-xs text-indigo-500 hover:text-indigo-700 underline" }, "📥 英文範本"),
                                    h('button', { onClick: function() { downloadTemplate('idiom'); }, className: "text-xs text-emerald-500 hover:text-emerald-700 underline" }, "📥 中文範本")
                                )
                            )
                        )
                    );
                }

                // ===== 設定頁面 =====
                if(isSettingUp) {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-4" },
                        h('div', { className: "glass max-w-md w-full rounded-3xl p-8" },
                            h('div', { className: "flex justify-between items-center mb-6" },
                                h('h2', { className: "text-xl font-black" }, "測驗設定"),
                                h('button', { onClick: goHome, className: "text-sm text-slate-400 hover:text-slate-600" }, "返回首頁")
                            ),
                            customDB && h('div', { className: "mb-4 p-3 bg-indigo-50 rounded-xl" },
                                h('p', { className: 'text-sm font-bold text-indigo-600' }, '📂 自訂字庫：' + customDB.length + ' 筆資料 (' + (customSubject === 'idiom' ? '中文成語' : '英文單字') + ')'),
                                h('div', { className: "flex gap-2 mt-2" },
                                    h('button', { onClick: function() { setMode('flashcard'); }, className: "text-xs px-3 py-1 rounded-lg " + (mode === 'flashcard' ? 'bg-indigo-600 text-white' : 'bg-white border') }, "閃卡模式"),
                                    h('button', { onClick: function() { setMode('fillin'); }, className: "text-xs px-3 py-1 rounded-lg " + (mode === 'fillin' ? 'bg-indigo-600 text-white' : 'bg-white border') }, "填空模式")
                                )
                            ),
                            h('div', { className: "space-y-6" },
                                subject === 'vocab' && !customDB && h('div', null,
                                    h('p', { className: "text-xs font-black text-slate-400 mb-2" }, "選擇等級"),
                                    h('div', { className: "flex flex-wrap gap-2" }, [1,2,3,4,5,6].map(function(l) { return h('button', { key: l, onClick: function() { setLevels(levels.includes(l) ? levels.filter(function(x) { return x !== l; }) : levels.concat(l)); }, className: "px-4 py-2 rounded-lg border-2 " + (levels.includes(l) ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-100') }, "L"+l); }))
                                ),
                                h('div', null,
                                    h('div', { className: "flex justify-between mb-2" }, h('span', { className: "text-sm font-bold" }, "抽樣數量"), h('span', { className: "text-sm font-black text-indigo-600" }, count)),
                                    h('input', { type: 'range', min: 5, max: Math.min(filteredCount || 200, 200), value: count, onChange: function(e) { setCount(parseInt(e.target.value)); }, className: "w-full accent-indigo-600" })
                                ),
                                h('button', { onClick: startQuiz, className: "w-full py-4 bg-slate-900 text-white rounded-2xl font-black shadow-xl shadow-slate-200" }, "開始測驗")
                            )
                        )
                    );
                }

                // ===== 完成頁面 =====
                if(isFinished) {
                    var total = stats.again + stats.hard + stats.good + stats.easy;
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-10 text-center" },
                            h('h2', { className: "text-2xl font-black mb-4" }, "🎉 測驗完成！"),
                            h('div', { className: "grid grid-cols-4 gap-2 mb-6" },
                                h('div', { className: 'p-2 rounded-xl bg-red-50' }, h('p', { className: 'text-lg font-black text-red-500' }, stats.again), h('p', { className: 'text-[10px] text-red-400' }, 'AGAIN')),
                                h('div', { className: 'p-2 rounded-xl bg-orange-50' }, h('p', { className: 'text-lg font-black text-orange-500' }, stats.hard), h('p', { className: 'text-[10px] text-orange-400' }, 'HARD')),
                                h('div', { className: 'p-2 rounded-xl bg-green-50' }, h('p', { className: 'text-lg font-black text-green-500' }, stats.good), h('p', { className: 'text-[10px] text-green-400' }, 'GOOD')),
                                h('div', { className: 'p-2 rounded-xl bg-blue-50' }, h('p', { className: 'text-lg font-black text-blue-500' }, stats.easy), h('p', { className: 'text-[10px] text-blue-400' }, 'EASY'))
                            ),
                            h('button', { onClick: goHome, className: "w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold" }, "返回首頁")
                        )
                    );
                }

                // ===== 測驗主畫面 =====
                var curr = activeList[0];
                var prog = ((totalInitial - activeList.length) / totalInitial) * 100;
                var l_tag = (subject === 'idiom') ? 'zh-TW' : 'en-US';

                return h('div', { className: "flex flex-col items-center min-h-screen p-4" },
                    // 頂部導航列
                    h('div', { className: "w-full max-w-lg flex items-center gap-4 mb-4" }, 
                        h('button', { onClick: goHome, className: "p-2 glass rounded-xl text-slate-400 hover:text-slate-600" }, "🏠"),
                        h('div', { className: "flex-1 h-2 bg-white/50 rounded-full overflow-hidden" }, h('div', { className: "bg-indigo-500 h-full transition-all duration-500", style: { width: prog + "%" } })),
                        h('span', { className: 'text-xs text-slate-400 font-bold' }, activeList.length + ' 剩餘')
                    ),
                    // 正面
                    !isFlipped ? h('div', { className: "glass max-w-lg w-full rounded-3xl p-10 text-center" },
                        mode === 'flashcard' ? h('div', { onClick: function() { setIsFlipped(true); }, className: "cursor-pointer py-10" },
                            h('h2', { className: "text-5xl font-black mb-6 " + (subject==='idiom'?'tracking-widest':'') }, curr.w),
                            curr.py && h('p', { className: "text-lg text-slate-400 font-mono mb-10" }, curr.py),
                            h('p', { className: "text-xs font-black text-slate-300 animate-pulse" }, "點擊查看解答")
                        ) : (subject === 'idiom' ? 
                            // 成語填空
                            h('div', { className: "py-4 text-left" },
                                h('div', { className: "info-block bg-indigo-50 border-indigo-400 mb-10" }, 
                                    h('p', { className: "text-[10px] uppercase font-black text-indigo-400 mb-1" }, "請根據解釋提供成語"),
                                    h('p', { className: "text-lg font-bold" }, curr.d)
                                ),
                                h(IdiomFillIn, { key: curr.w, word: curr.w, onComplete: function() { setIsFlipped(true); } })
                            ) :
                            // 英文填空
                            h('div', { className: "py-4 text-left" },
                                h('div', { className: "info-block bg-violet-50 border-violet-400 mb-10" }, 
                                    h('p', { className: "text-[10px] uppercase font-black text-violet-400 mb-1" }, "請根據定義拼出英文單字"),
                                    h('p', { className: "text-lg font-bold" }, curr.d)
                                ),
                                curr.pr && h('p', { className: "text-sm text-slate-400 mb-4 text-center" }, curr.pr),
                                h(VocabFillIn, { key: curr.w, word: curr.w, onComplete: function() { setIsFlipped(true); } })
                            )
                        )
                    ) : 
                    // 背面
                    h('div', { className: "glass max-w-lg w-full rounded-3xl p-8" },
                        h('div', { className: "flex justify-between items-center mb-4" },
                            h('h2', { className: "text-3xl font-black text-indigo-600" }, curr.w),
                            h('button', { onClick: function() { speak(curr.w, speechRate, l_tag); }, className: "p-3 bg-indigo-50 rounded-2xl text-xl transition-all active:scale-90" }, "\uD83D\uDD0A")
                        ),
                        h('hr', { className: "mb-6 border-slate-100" }),
                        h('div', { className: "space-y-4" },
                            curr.d && h('div', { className: "info-block bg-indigo-50 border-indigo-400" }, h('p', { className: "text-[10px] uppercase font-black text-indigo-400" }, "解釋"), h('p', { className: "text-base font-bold" }, curr.d)),
                            curr.o && h('div', { className: "info-block bg-amber-50 border-amber-400" }, h('p', { className: "text-[10px] uppercase font-black text-amber-400" }, "出處"), h('p', { className: "text-sm" }, curr.o)),
                            curr.x && h('div', { className: "info-block bg-blue-50 border-blue-400" }, h('p', { className: "text-[10px] uppercase font-black text-blue-400" }, "例句"), h('p', { className: "text-sm italic" }, curr.x)),
                            curr.pr && h('div', { className: "info-block bg-purple-50 border-purple-400" }, h('p', { className: "text-[10px] uppercase font-black text-purple-400" }, "發音"), h('p', { className: "text-sm font-mono" }, curr.pr)),
                            curr.re && h('div', { className: "info-block bg-teal-50 border-teal-400" }, h('p', { className: "text-[10px] uppercase font-black text-teal-400" }, "相關"), h('p', { className: "text-sm" }, curr.re)),
                            curr.co && h('div', { className: "info-block bg-cyan-50 border-cyan-400" }, h('p', { className: "text-[10px] uppercase font-black text-cyan-400" }, "搭配詞"), h('p', { className: "text-sm" }, curr.co))
                        ),
                        h('div', { className: "grid grid-cols-4 gap-2 mt-10" }, ['again', 'hard', 'good', 'easy'].map(function(t) { return h('button', { key: t, onClick: function() { handleSRS(t); }, className: "btn-" + t + " py-4 rounded-2xl border-2 text-xs font-black transition-all transform active:scale-95" }, t.toUpperCase()); }))
                    )
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(h(App));
        })();
    </script>
</body>
</html>""")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(content))
    
    print(f"Build Success. Vocab & Idiom converted to Traditional. UI Updated.")

if __name__ == "__main__":
    build_html()
