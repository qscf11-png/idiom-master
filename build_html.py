import json
import os
import re
from opencc import OpenCC

def build_html():
    vocab_data_path = "vocab_data.js"
    idiom_data_path = "idiom_data.js"
    math_data_path = "math_data.js"
    output_path = "index.html"
    
    cc = OpenCC('s2t') # 簡體轉繁體

    def get_db_data(path, var_prefix):
        if not os.path.exists(path): return "[]"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            start = content.find("[")
            end = content.rfind("]")
            if start != -1 and end != -1:
                js_str = content[start:end+1]
                return cc.convert(js_str)
        return "[]"

    v_js = get_db_data(vocab_data_path, "const VOCAB_DB = ")
    idiom_js = get_db_data(idiom_data_path, "const IDIOM_DB = ")
    math_js = get_db_data(math_data_path, "const MATH_DB = ")

    html_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全能學習大師 Vocab & Idiom & Math Master</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <!-- KaTeX -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: linear-gradient(135deg, #e0e7ff 0%, #f1f5f9 50%, #dbeafe 100%); margin: 0; padding: 0; min-height: 100vh; overflow-x: hidden; }
        .glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.5); }
        .info-block { border-left: 4px solid; padding: 8px 12px; border-radius: 0 8px 8px 0; margin-bottom: 8px; }
        .katex { font-size: 1.1em; }
        /* SRS 按鈕顏色 */
        .btn-again { border-color: #fee2e2; color: #dc2626; background: #fff5f5; }
        .btn-hard { border-color: #ffedd5; color: #d97706; background: #fffafb; }
        .btn-good { border-color: #dcfce7; color: #16a34a; background: #f0fdf4; }
        .btn-easy { border-color: #dbeafe; color: #2563eb; background: #eff6ff; }
        .math-card { font-family: 'Times New Roman', serif; }
        @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .animate-slide { animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
        /* 避免視窗過大 */
        .main-card-container { max-height: 75vh; overflow: visible; }
        .perspective-1000 { perspective: 1000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
    </style>
</head>
<body>
    <div id="root"></div>
    <script>
        window.VOCAB_DB_RAW = V_DATA;
        window.IDIOM_DB_RAW = I_DATA;
        window.MATH_DB_RAW = M_DATA;
    </script>
    <script type="text/javascript">
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
            
            var VOCAB_DB_RAW = window.VOCAB_DB_RAW;
            var IDIOM_DB_RAW = window.IDIOM_DB_RAW;
            var MATH_DB_RAW = window.MATH_DB_RAW;

            function shuffle(arr) {
                var n = arr.slice();
                for(var i = n.length - 1; i > 0; i--) {
                    var j = Math.floor(Math.random() * (i + 1));
                    var tmp = n[i]; n[i] = n[j]; n[j] = tmp;
                }
                return n;
            }

            function downloadTemplate(type) {
                var wb = XLSX.utils.book_new();
                var data = [];
                if (type === 'vocab') {
                    data = [{ word: 'abandon', definition: '放棄', example: 'He decided to abandon the project.' }];
                    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), '英文單字');
                    XLSX.writeFile(wb, 'english_vocab_template.xlsx');
                } else if (type === 'idiom') {
                    data = [{ word: '一石二鳥', explanation: '比喻做一件事同時達到兩個目的。', example: '這個計畫簡直是一石二鳥。' }];
                    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), '中文成語');
                    XLSX.writeFile(wb, 'idiom_template.xlsx');
                } else {
                    data = [{ w: '$a^2+b^2=c^2$', d: '畢氏定理', l: 8 }];
                    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), '數學');
                    XLSX.writeFile(wb, 'math_template.xlsx');
                }
            }

            function App() {
                var [subject, setSubject] = useState(null);
                var [mode, setMode] = useState('flashcard');
                var [isSettingUp, setIsSettingUp] = useState(false);
                var [activeList, setActiveList] = useState([]);
                var [idx, setIdx] = useState(0);
                var [isFlipped, setIsFlipped] = useState(false);
                var [isFinished, setIsFinished] = useState(false);
                var [customDB, setCustomDB] = useState(null);
                var [userInput, setUserInput] = useState('');
                var [showAnswer, setShowAnswer] = useState(false);
                var fileInputRef = useRef(null);

                var DB = useMemo(function() {
                    if (customDB) return customDB;
                    if (subject === 'vocab') return VOCAB_DB_RAW;
                    if (subject === 'idiom') return IDIOM_DB_RAW;
                    if (subject === 'math') return MATH_DB_RAW;
                    return [];
                }, [subject, customDB]);

                useEffect(function() {
                    if (subject === 'math') {
                        var el = document.getElementById('root');
                        if (el && window.renderMathInElement) {
                            window.renderMathInElement(el, { 
                                delimiters: [{left:'$', right:'$', display:false},{left:'$$', right:'$$', display:true}],
                                throwOnError: false
                            });
                        }
                    }
                }, [isFlipped, subject, idx, isSettingUp, showAnswer]);

                useEffect(function() {
                    function handleK(e) {
                        if (isSettingUp || isFinished || !subject) return;
                        if (mode === 'flashcard') {
                            if (e.code === 'Space') { 
                                e.preventDefault(); 
                                setIsFlipped(prev => !prev); 
                                if(subject === 'vocab' && !isFlipped) speak(activeList[idx].word);
                            }
                            if (isFlipped) {
                                if (e.key === '1') handleAction();
                                if (e.key === '2') handleAction();
                                if (e.key === '3') handleAction();
                                if (e.key === '4') handleAction();
                            }
                        }
                    }
                    window.addEventListener('keydown', handleK);
                    return () => window.removeEventListener('keydown', handleK);
                }, [isFlipped, isSettingUp, isFinished, subject, mode, idx, activeList]);

                function handleAction() {
                    if (idx + 1 < activeList.length) {
                        setIdx(idx + 1); setIsFlipped(false); setShowAnswer(false); setUserInput('');
                    } else {
                        setIsFinished(true);
                    }
                }

                function handleFillInSubmit() {
                    setShowAnswer(true);
                }

                function handleFileImport(e) {
                    var file = e.target.files[0];
                    if(!file) return;
                    var reader = new FileReader();
                    reader.onload = function(evt) {
                        var data = XLSX.utils.sheet_to_json(XLSX.read(evt.target.result, {type:'binary'}).Sheets[XLSX.read(evt.target.result, {type:'binary'}).SheetNames[0]]);
                        if (data.length > 0) {
                            setSubject(data[0].w ? 'math' : (data[0].explanation ? 'idiom' : 'vocab'));
                            setCustomDB(data);
                            setIsSettingUp(true);
                        }
                    };
                    reader.readAsBinaryString(file);
                }

                if (!subject || (!activeList.length && !isSettingUp && !isFinished)) {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-10 text-center animate-slide" },
                            h('h1', { className: "text-3xl font-black mb-6" }, "全能學習大師"),
                            h('div', { className: "grid grid-cols-1 gap-3 mb-6" },
                                h('button', { onClick: function() { setSubject('vocab'); setMode('flashcard'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-indigo-50 transition-all font-bold" }, "英文單字 (閃卡)"),
                                h('button', { onClick: function() { setSubject('vocab'); setMode('fillin'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-violet-50 transition-all font-bold" }, "英文單字 (填空)"),
                                h('button', { onClick: function() { setSubject('idiom'); setMode('flashcard'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-emerald-50 transition-all font-bold" }, "中文成語 (閃卡)"),
                                h('button', { onClick: function() { setSubject('idiom'); setMode('fillin'); setIsSettingUp(true); }, className: "py-4 rounded-2xl border-2 hover:bg-amber-50 transition-all font-bold" }, "中文成語 (填空)"),
                                h('button', { onClick: function() { setSubject('math'); setMode('flashcard'); setIsSettingUp(true); }, className: "py-4 rounded-2xl bg-slate-900 text-white hover:opacity-90 transition-all font-black" }, "國中數學 (觀念閃卡)")
                            ),
                            h('button', { onClick: function() { fileInputRef.current.click(); }, className: "w-full py-4 rounded-2xl border-2 border-dashed border-slate-300 text-slate-500 font-bold" }, "📂 匯入 Excel"),
                            h('input', { type: 'file', ref: fileInputRef, onChange: handleFileImport, className: 'hidden' }),
                            h('div', { className: "flex gap-2 justify-center mt-4" },
                                h('button', { onClick: function() { downloadTemplate('vocab'); }, className: "text-xs text-indigo-500 underline" }, "英文範本"),
                                h('button', { onClick: function() { downloadTemplate('idiom'); }, className: "text-xs text-emerald-500 underline" }, "中文範本"),
                                h('button', { onClick: function() { downloadTemplate('math'); }, className: "text-xs text-slate-500 underline" }, "數學範本")
                            )
                        )
                    );
                }

                if (isSettingUp) {
                    return h('div', { className: "flex items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-8 text-center animate-slide" },
                            h('h2', { className: "text-2xl font-black mb-4" }, "設定測驗"),
                            h('input', { type: 'range', min: 1, max: DB.length, value: activeList.length || DB.length, onChange: function(e) { setActiveList(new Array(parseInt(e.target.value))); }, className: "w-full mb-6" }),
                            h('button', { onClick: function() { setActiveList(shuffle(DB).slice(0, activeList.length || DB.length)); setIsSettingUp(false); setIdx(0); }, className: "w-full py-4 bg-indigo-600 text-white rounded-2xl font-black" }, "開始"),
                            h('button', { onClick: function() { setSubject(null); setIsSettingUp(false); }, className: "mt-4 text-slate-400 font-bold" }, "返回")
                        )
                    );
                }

                if (isFinished) {
                    return h('div', { className: "flex items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-10 text-center animate-slide" },
                            h('h2', { className: "text-3xl font-black mb-8" }, "🎉 完成！"),
                            h('button', { onClick: function() { setSubject(null); setIsFinished(false); }, className: "w-full py-4 bg-slate-900 text-white rounded-2xl font-black" }, "回到首頁")
                        )
                    );
                }

                var curr = activeList[idx];
                if (mode === 'flashcard') {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "w-full max-w-md mb-6 flex justify-between items-center" },
                            h('button', { onClick: function() { setSubject(null); }, className: "font-black text-slate-400" }, "✕ 結束"),
                            h('div', { className: "bg-slate-900 text-white px-4 py-1 rounded-full text-xs font-black" }, (idx + 1) + " / " + activeList.length)
                        ),
                        h('div', { 
                            onClick: function() { setIsFlipped(!isFlipped); if(subject === 'vocab' && !isFlipped) speak(curr.word); },
                            className: "w-full max-w-md aspect-[3/4] main-card-container cursor-pointer perspective-1000 mb-8"
                        }, 
                            h('div', { className: "relative w-full h-full transition-all duration-500 preserve-3d " + (isFlipped ? "rotate-y-180" : "") },
                                h('div', { className: "absolute inset-0 backface-hidden glass rounded-[2.5rem] flex flex-col items-center justify-center p-10 text-center" },
                                    h('p', { className: "text-slate-400 font-black text-xs uppercase tracking-widest mb-4" }, "Question"),
                                    h('h2', { className: "text-3xl font-black leading-tight " + (subject === 'math' ? "math-card" : "") }, subject === 'math' ? curr.w : curr.word)
                                ),
                                h('div', { className: "absolute inset-0 backface-hidden rotate-y-180 glass rounded-[2.5rem] flex flex-col items-center justify-center p-8 text-center bg-white/95" },
                                    h('p', { className: "text-indigo-400 font-black text-[10px] mb-4 uppercase" }, "Answer"),
                                    h('div', { className: "text-xl font-medium leading-relaxed " + (subject === 'math' ? "math-card" : "") }, subject === 'math' ? curr.d : curr.definition),
                                    curr.example && h('div', { className: "mt-4 p-3 bg-slate-50 rounded-xl text-sm italic" }, curr.example)
                                )
                            )
                        ),
                        h('div', { className: "w-full max-w-md grid grid-cols-4 gap-3 h-20" },
                            ['Again', 'Hard', 'Good', 'Easy'].map((l, i) => h('button', { onClick: handleAction, className: "border-2 rounded-2xl flex flex-col items-center justify-center btn-" + l.toLowerCase() }, h('span', { className: 'text-lg font-black' }, l), h('span', { className: 'text-[10px]' }, i+1)))
                        ),
                        h('p', { className: "text-xs text-slate-400 mt-4 font-bold" }, "提示：Space 翻牌 | 1-4 評分")
                    );
                } else {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-md w-full rounded-3xl p-10 animate-slide" },
                            h('h2', { className: "text-4xl font-black mb-8 text-center" }, subject === 'vocab' ? curr.definition : curr.explanation),
                            !showAnswer ? h('div', null,
                                h('input', { autoFocus: true, value: userInput, onChange: e => setUserInput(e.target.value), onKeyDown: e => e.key === 'Enter' && handleFillInSubmit(), className: "w-full p-6 text-2xl font-black border-4 border-slate-100 rounded-2xl text-center focus:border-indigo-500 outline-none transition-all mb-4", placeholder: "請輸入答案" }),
                                h('button', { onClick: handleFillInSubmit, className: "w-full py-4 bg-indigo-600 text-white rounded-2xl font-black" }, "提交答案")
                            ) : h('div', { className: "text-center" },
                                h('h3', { className: "text-5xl font-black mb-4 " + (userInput.trim() === (subject === 'vocab' ? curr.word : curr.word) ? "text-green-500" : "text-red-500") }, subject === 'vocab' ? curr.word : curr.word),
                                h('p', { className: "text-xl text-slate-500 mb-8" }, curr.example || ""),
                                h('button', { onClick: handleAction, className: "w-full py-4 bg-slate-900 text-white rounded-2xl font-black" }, "下一題")
                            )
                        )
                    );
                }
            }
            ReactDOM.createRoot(document.getElementById('root')).render(h(App));
        })();
    </script>
</body>
</html>"""
    
    html_output = html_template.replace("V_DATA", v_js).replace("I_DATA", idiom_js).replace("M_DATA", math_js)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Build Success. All features restored and Math fixed.")

if __name__ == "__main__":
    build_html()
