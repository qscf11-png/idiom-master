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
        if not os.path.exists(path): return []
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: #f8fafc; margin: 0; padding: 0; height: 100vh; overflow: hidden; }
        .app-container { height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1rem; }
        .glass { background: white; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
        .info-block { border-left: 4px solid; padding: 8px 12px; border-radius: 0 8px 8px 0; margin-bottom: 8px; }
        .btn-again { border-color: #fee2e2; color: #dc2626; background: #fff5f5; }
        .btn-hard { border-color: #ffedd5; color: #d97706; background: #fffafb; }
        .btn-good { border-color: #dcfce7; color: #16a34a; background: #f0fdf4; }
        .btn-easy { border-color: #dbeafe; color: #2563eb; background: #eff6ff; }
        .math-card { font-family: 'Times New Roman', serif; }
        @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .animate-slide { animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
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

            function App() {
                var [subject, setSubject] = useState(null);
                var [mode, setMode] = useState('flashcard');
                var [isSettingUp, setIsSettingUp] = useState(false);
                var [activeList, setActiveList] = useState([]);
                var [idx, setIdx] = useState(0);
                var [isFlipped, setIsFlipped] = useState(false);
                var [isFinished, setIsFinished] = useState(false);
                var [customDB, setCustomDB] = useState(null);
                var fileInputRef = useRef(null);

                var DB = useMemo(function() {
                    if (customDB) return customDB;
                    if (subject === 'vocab') return VOCAB_DB_RAW;
                    if (subject === 'idiom') return IDIOM_DB_RAW;
                    if (subject === 'math') return MATH_DB_RAW;
                    return [];
                }, [subject, customDB]);

                // 統一數學渲染：無論哪一面，只要有內容就渲染
                useEffect(function() {
                    if (subject === 'math') {
                        var el = document.getElementById('root');
                        if (el && window.renderMathInElement) {
                            window.renderMathInElement(el, { 
                                delimiters: [
                                    {left:'$', right:'$', display:false},
                                    {left:'$$', right:'$$', display:true}
                                ],
                                throwOnError: false
                            });
                        }
                    }
                }, [isFlipped, subject, idx, isSettingUp]);

                // 熱鍵處理
                useEffect(function() {
                    function handleK(e) {
                        if (isSettingUp || isFinished || !subject) return;
                        if (e.code === 'Space') {
                            e.preventDefault();
                            setIsFlipped(prev => !prev);
                        }
                        if (isFlipped) {
                            if (e.key === '1') handleAction('again');
                            if (e.key === '2') handleAction('hard');
                            if (e.key === '3') handleAction('good');
                            if (e.key === '4') handleAction('easy');
                        }
                    }
                    window.addEventListener('keydown', handleK);
                    return () => window.removeEventListener('keydown', handleK);
                }, [isFlipped, isSettingUp, isFinished, subject]);

                function handleAction(type) {
                    if (idx + 1 < activeList.length) {
                        setIdx(idx + 1);
                        setIsFlipped(false);
                    } else {
                        setIsFinished(true);
                    }
                }

                function handleFileImport(e) {
                    var file = e.target.files[0];
                    if(!file) return;
                    var reader = new FileReader();
                    reader.onload = function(evt) {
                        var data = XLSX.utils.sheet_to_json(XLSX.read(evt.target.result, {type:'binary'}).Sheets[XLSX.read(evt.target.result, {type:'binary'}).SheetNames[0]]);
                        if (data.length > 0) {
                            setSubject(data[0].w && data[0].d ? 'math' : (data[0].explanation ? 'idiom' : 'vocab'));
                            setCustomDB(data);
                            setIsSettingUp(true);
                        }
                    };
                    reader.readAsBinaryString(file);
                }

                if (!subject || (!activeList.length && !isSettingUp && !isFinished)) {
                    return h('div', { className: "app-container" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-8 text-center animate-slide" },
                            h('h1', { className: "text-2xl font-black mb-6" }, "全能學習大師"),
                            h('div', { className: "grid grid-cols-1 gap-3 mb-6" },
                                h('button', { onClick: function() { setSubject('vocab'); setIsSettingUp(true); }, className: "py-3 rounded-2xl border-2 font-bold" }, "英文單字 (閃卡)"),
                                h('button', { onClick: function() { setSubject('idiom'); setIsSettingUp(true); }, className: "py-3 rounded-2xl border-2 font-bold" }, "中文成語 (閃卡)"),
                                h('button', { onClick: function() { setSubject('math'); setIsSettingUp(true); }, className: "py-3 rounded-2xl bg-slate-900 text-white font-black" }, "國中數學 (觀念閃卡)")
                            ),
                            h('button', { onClick: function() { fileInputRef.current.click(); }, className: "w-full py-3 rounded-2xl border-2 border-dashed text-slate-400 text-sm" }, "📂 匯入 Excel"),
                            h('input', { type: 'file', ref: fileInputRef, onChange: handleFileImport, className: 'hidden' })
                        )
                    );
                }

                if (isSettingUp) {
                    return h('div', { className: "app-container" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-8 text-center animate-slide" },
                            h('h2', { className: "text-xl font-black mb-4" }, "設定測驗"),
                            h('input', { type: 'range', min: 1, max: DB.length, value: activeList.length || DB.length, onChange: function(e) { setActiveList(new Array(parseInt(e.target.value))); }, className: "w-full mb-4" }),
                            h('button', { onClick: function() { 
                                var count = activeList.length || DB.length;
                                setActiveList(shuffle(DB).slice(0, count));
                                setIsSettingUp(false); setIdx(0); setIsFlipped(false);
                            }, className: "w-full py-3 bg-indigo-600 text-white rounded-2xl font-black" }, "開始測驗")
                        )
                    );
                }

                if (isFinished) {
                    return h('div', { className: "app-container" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl p-10 text-center animate-slide" },
                            h('h2', { className: "text-2xl font-black mb-2" }, "🎉 完成學習！"),
                            h('button', { onClick: function() { setSubject(null); setIsFinished(false); }, className: "w-full py-3 bg-slate-900 text-white rounded-2xl font-black mt-4" }, "回到首頁")
                        )
                    );
                }

                var curr = activeList[idx];
                return h('div', { className: "app-container overflow-hidden" },
                    h('div', { className: "w-full max-w-sm mb-4 flex justify-between items-center" },
                         h('button', { onClick: function() { setSubject(null); }, className: "text-slate-400 font-bold" }, "✕ 離開"),
                         h('div', { className: "text-xs font-black bg-slate-100 px-3 py-1 rounded-full" }, (idx + 1) + " / " + activeList.length)
                    ),
                    h('div', { 
                        onClick: function() { setIsFlipped(!isFlipped); },
                        className: "w-full max-w-sm aspect-[4/5] cursor-pointer perspective-1000 mb-6"
                    }, 
                        h('div', { className: "relative w-full h-full transition-all duration-500 preserve-3d " + (isFlipped ? "rotate-y-180" : "") },
                            h('div', { className: "absolute inset-0 backface-hidden glass rounded-3xl flex flex-col items-center justify-center p-8 text-center" },
                                h('p', { className: "text-[10px] text-slate-400 font-black mb-4 uppercase tracking-widest" }, "Question"),
                                h('h2', { className: "text-2xl font-bold leading-tight " + (subject === 'math' ? "math-card" : "") }, subject === 'math' ? curr.w : curr.word)
                            ),
                            h('div', { className: "absolute inset-0 backface-hidden rotate-y-180 glass rounded-3xl flex flex-col items-center justify-center p-8 text-center bg-indigo-50/30" },
                                h('p', { className: "text-[10px] text-indigo-400 font-black mb-4 uppercase tracking-widest" }, "Answer"),
                                h('div', { className: "text-xl font-medium leading-relaxed " + (subject === 'math' ? "math-card" : "") }, subject === 'math' ? curr.d : curr.definition)
                            )
                        )
                    ),
                    h('div', { className: "w-full max-w-sm grid grid-cols-4 gap-2 h-16" },
                        ['Again', 'Hard', 'Good', 'Easy'].map((label, i) => 
                            h('button', { 
                                onClick: (e) => { e.stopPropagation(); handleAction(label.toLowerCase()); },
                                className: "border-2 rounded-xl flex flex-col items-center justify-center " + (label === 'Good' ? "bg-green-500 text-white border-green-500" : "bg-white text-slate-700")
                            }, h('span', { className: "text-sm font-black" }, label), h('span', { className: "text-[8px] opacity-50" }, i+1))
                        )
                    ),
                    h('p', { className: "text-[10px] text-slate-400 mt-4 font-bold" }, "提示：Space 翻牌 | 1-4 選項")
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(h(App));
        })();
    </script>
</body>
</html>"""
    
    html_output = html_template.replace("V_DATA", v_js).replace("I_DATA", idiom_js).replace("M_DATA", math_js)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Build Success. UI/UX & Math Refined.")

if __name__ == "__main__":
    build_html()
