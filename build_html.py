import json
import os
import re
from opencc import OpenCC

def build_html():
    vocab_data_path = "vocab_data.js"
    idiom_data_path = "idiom_data.js"
    math_data_path = "math_data.js"
    cc = OpenCC('s2t')

    def get_db_data(path):
        if not os.path.exists(path): return "[]"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                start = content.find('[')
                end = content.rfind(']')
                if start != -1 and end != -1:
                    js_str = content[start:end+1]
                    return cc.convert(js_str)
        except Exception as e:
            print(f"Error reading {path}: {e}")
        return "[]"

    v_json = get_db_data(vocab_data_path)
    i_json = get_db_data(idiom_data_path)
    m_json = get_db_data(math_data_path)

    # 1. index.html - 100% 採用 9468ea0 的巔峰語文邏輯
    # 注意：此模板直接包含 9468ea0 的 React 代碼，確保功能完全一致
    index_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全能學習大師 Vocab & Idiom Master (Peak Build)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); margin: 0; padding: 0; min-height: 100vh; overflow-x: hidden; color: #1e293b; }
        .glass { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 8px 32px rgba(0,0,0,0.05); }
        .card-container { height: 480px; width: 100%; max-width: 400px; position: relative; perspective: 1000px; }
        .card { position: absolute; width: 100%; height: 100%; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; cursor: pointer; }
        .card.is-flipped { transform: rotateY(180deg); }
        .card-face { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 2.5rem; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2.5rem; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
        .card-front { background: white; border: 1px solid #e2e8f0; }
        .card-back { background: #f8fafc; border: 2px solid #6366f1; transform: rotateY(180deg); }
        .srs-btn { transition: all 0.2s; border: 2px solid transparent; font-weight: 900; }
        .srs-btn:hover { transform: translateY(-2px); }
        .btn-again { border-color: #fee2e2; color: #dc2626; background: #fff5f5; }
        .btn-hard { border-color: #ffedd5; color: #d97706; background: #fffafb; }
        .btn-good { border-color: #dcfce7; color: #16a34a; background: #f0fdf4; }
        .btn-easy { border-color: #dbeafe; color: #2563eb; background: #eff6ff; }
        .info-block { background: rgba(241, 245, 249, 0.5); border-radius: 1.5rem; padding: 1.25rem; width: 100%; margin: 0.5rem 0; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/javascript">
        window.VOCAB_DB = VOCAB_DATA_PLACEHOLDER;
        window.IDIOM_DB = IDIOM_DATA_PLACEHOLDER;

        (function() {
            const h = React.createElement;
            const { useState, useEffect, useRef } = React;

            function App() {
                const [view, setView] = useState('home');
                const [subject, setSubject] = useState(null);
                const [mode, setMode] = useState('flash');
                const [db, setDb] = useState([]);
                const [quizList, setQuizList] = useState([]);
                const [currIdx, setCurrIdx] = useState(0);
                const [isFlipped, setIsFlipped] = useState(false);
                const [userInput, setUserInput] = useState('');
                const [isCorrect, setIsCorrect] = useState(false);
                const [isSubmitted, setIsSubmitted] = useState(false);
                const [totalInitial, setTotalInitial] = useState(0);

                const [lvlFilter, setLvlFilter] = useState('all');
                const [prefixFilter, setPrefixFilter] = useState('');
                const [limit, setLimit] = useState(20);
                const composingRef = useRef(false);

                useEffect(() => {
                    const handleKey = (e) => {
                        if (view !== 'quiz') return;
                        if (mode === 'flash') {
                            if (e.code === 'Space') { e.preventDefault(); toggleFlip(); }
                            else if (isFlipped && ['1','2','3','4'].includes(e.key)) next();
                        }
                    };
                    window.addEventListener('keydown', handleKey);
                    return () => window.removeEventListener('keydown', handleKey);
                }, [view, isFlipped, mode, currIdx]);

                const toggleFlip = () => {
                    setIsFlipped(!isFlipped);
                    if (!isFlipped && subject === 'vocab') speak(quizList[currIdx].word || quizList[currIdx].w);
                };

                const startSetup = (s, m) => {
                    setSubject(s); setMode(m);
                    setDb(s === 'vocab' ? window.VOCAB_DB : window.IDIOM_DB);
                    setView('setup');
                };

                const startQuiz = () => {
                    let filtered = [...db];
                    if (subject === 'vocab' && lvlFilter !== 'all') filtered = filtered.filter(i => String(i.l) === lvlFilter);
                    if (prefixFilter) filtered = filtered.filter(i => (i.word || i.w || "").toLowerCase().startsWith(prefixFilter.toLowerCase()));
                    
                    const shuffled = [...filtered].sort(() => Math.random() - 0.5).slice(0, parseInt(limit));
                    setQuizList(shuffled);
                    setTotalInitial(shuffled.length);
                    setCurrIdx(0); setView('quiz'); setIsFlipped(false); setIsSubmitted(false); setUserInput('');
                };

                const checkFill = () => {
                   if (composingRef.current) return;
                   const t = (quizList[currIdx].word || quizList[currIdx].w).toLowerCase().trim();
                   const i = userInput.toLowerCase().trim();
                   const ok = t === i;
                   setIsCorrect(ok); setIsSubmitted(true);
                   if (ok) playTone(600, 0.1); else { playTone(200, 0.2); speak(t); }
                };

                const next = () => {
                    if (currIdx + 1 < quizList.length) {
                        setCurrIdx(currIdx + 1); setIsFlipped(false); setIsSubmitted(false); setUserInput('');
                    } else setView('result');
                };

                const speak = (t) => { window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(t); u.lang = 'en-US'; window.speechSynthesis.speak(u); };
                const playTone = (f, d) => {
                    const c = new (window.AudioContext || window.webkitAudioContext)();
                    const o = c.createOscillator(); const g = c.createGain();
                    o.connect(g); g.connect(c.destination); o.frequency.value = f; o.start();
                    g.gain.exponentialRampToValueAtTime(0.00001, c.currentTime + d); o.stop(c.currentTime + d);
                };

                if (view === 'home') return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                    h('div', { className: "glass max-w-sm w-full rounded-[3rem] p-12 text-center" },
                        h('h1', { className: "text-4xl font-black mb-10" }, "大師語文本"),
                        h('div', { className: "space-y-4" },
                            ['英文單字 (閃卡)', '英文單字 (填空)', '成語練習 (閃卡)', '成語練習 (填空)'].map((t, idx) => {
                                const s = idx < 2 ? 'vocab' : 'idiom';
                                const m = idx % 2 === 0 ? 'flash' : 'fill';
                                const c = s === 'vocab' ? 'bg-indigo-600' : 'bg-emerald-600';
                                return h('button', { key: idx, onClick: () => startSetup(s, m), className: `w-full py-5 rounded-3xl text-white font-black text-lg ${c} shadow-xl hover:opacity-90 active:scale-95 transition-all` }, t);
                            }),
                            h('a', { href: 'entry.html', className: "block mt-8 text-slate-400 font-bold" }, "← 返回導覽入口")
                        )
                    )
                );

                if (view === 'setup') return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                    h('div', { className: "glass max-w-sm w-full rounded-[2.5rem] p-10" },
                        h('h2', { className: "text-2xl font-black mb-8 text-center" }, "測驗設定"),
                        subject === 'vocab' && h('div', { className: "mb-6" },
                            h('label', { className: "text-xs font-black text-slate-400 mb-2 block" }, "選擇等級"),
                            h('select', { value: lvlFilter, onChange: e => setLvlFilter(e.target.value), className: "w-full p-4 rounded-2xl bg-slate-100 font-bold" },
                                h('option', { value: 'all' }, "全部等級"), [1,2,3,4,5,6].map(l => h('option', { key: l, value: l }, "Level " + l))
                            )
                        ),
                        h('div', { className: "mb-6" },
                            h('label', { className: "text-xs font-black text-slate-400 mb-2 block" }, "字首篩選"),
                            h('input', { value: prefixFilter, onChange: e => setPrefixFilter(e.target.value), placeholder: "e.g. a", className: "w-full p-4 rounded-2xl bg-slate-100 font-bold outline-none" })
                        ),
                        h('div', { className: "mb-10" },
                            h('label', { className: "text-xs font-black text-slate-400 mb-4 block" }, "題數: " + limit),
                            h('input', { type: 'range', min: 5, max: 100, step: 5, value: limit, onChange: e => setLimit(e.target.value), className: "w-full h-2 bg-indigo-100 rounded-lg appearance-none cursor-pointer" })
                        ),
                        h('button', { onClick: startQuiz, className: "w-full py-5 bg-indigo-600 text-white rounded-[2rem] font-black text-xl mb-4 shadow-xl" }, "啟動練習"),
                        h('button', { onClick: () => setView('home'), className: "w-full text-slate-400 font-bold" }, "取消")
                    )
                );

                if (view === 'quiz') {
                    const curr = quizList[currIdx]; const t = curr.word || curr.w || "";
                    const d = curr.definition || curr.explanation || curr.d || "";
                    if (mode === 'flash') return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "w-full max-w-md mb-8 flex justify-between items-center" },
                            h('button', { onClick: () => setView('home'), className: "h-10 w-10 flex items-center justify-center rounded-full bg-white font-black" }, "✕"),
                            h('div', { className: "px-4 py-1 rounded-full bg-slate-900 text-white text-[10px] font-black" }, (currIdx + 1) + " / " + totalInitial)
                        ),
                        h('div', { className: "card-container mb-12", onClick: toggleFlip },
                            h('div', { className: "card " + (isFlipped ? "is-flipped" : "") },
                                h('div', { className: "card-face card-front" }, h('h2', { className: "text-4xl font-black" }, t)),
                                h('div', { className: "card-face card-back" },
                                    h('div', { className: "info-block" }, h('h3', { className: "text-2xl font-bold" }, d)),
                                    curr.example && h('p', { className: "text-sm text-slate-400 italic max-w-xs mt-4" }, curr.example)
                                )
                            )
                        ),
                        isFlipped ? h('div', { className: "grid grid-cols-4 gap-3 w-full max-w-md h-20" },
                            ['Again', 'Hard', 'Good', 'Easy'].map((b, i) => h('button', { key: i, onClick: next, className: `srs-btn rounded-3xl btn-${b.toLowerCase()}` }, b))
                        ) : h('p', { className: "text-slate-300 font-black animate-pulse" }, "點擊或空白鍵翻頁")
                    );
                    else {
                        const first = t.charAt(0); const rest = "_ ".repeat(t.length - 1).trim();
                        return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            h('div', { className: "glass max-w-md w-full rounded-[3rem] p-10 text-center" },
                                h('h2', { className: "text-3xl font-black mb-8" }, d),
                                h('div', { className: "mb-8 flex flex-col items-center" },
                                    h('div', { className: "text-4xl font-black tracking-widest mb-4" }, h('span', { className: "text-indigo-600" }, first), h('span', { className: "text-slate-100" }, rest)),
                                    h('p', { className: "text-[10px] font-bold text-slate-400 uppercase" }, t.length + " 字元")
                                ),
                                !isSubmitted ? h('div', null,
                                    h('input', { autoFocus: true, value: userInput, onChange: e => setUserInput(e.target.value), 
                                        onCompositionStart: () => composingRef.current = true,
                                        onCompositionEnd: () => composingRef.current = false,
                                        onKeyDown: e => e.key === 'Enter' && checkFill(), 
                                        className: "w-full p-6 text-2xl font-black bg-slate-50 rounded-2xl border-4 border-transparent focus:border-indigo-500 outline-none text-center shadow-inner mb-6" }),
                                    h('button', { onClick: checkFill, className: "w-full py-5 bg-indigo-600 text-white rounded-3xl font-black text-xl shadow-xl shadow-indigo-100" }, "檢查答案")
                                ) : h('div', { className: "animate-scale-in" },
                                    h('div', { className: "mb-8" },
                                        h('h3', { className: `text-5xl font-black mb-4 ${isCorrect ? 'text-green-500' : 'text-red-500'}` }, t),
                                        !isCorrect && h('p', { className: "text-slate-300 line-through text-2xl" }, userInput)
                                    ),
                                    h('button', { onClick: next, className: "w-full py-5 bg-slate-900 text-white rounded-3xl font-black text-xl" }, "下一題")
                                )
                            )
                        );
                    }
                }

                if (view === 'result') return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                    h('div', { className: "glass max-w-sm w-full rounded-[3rem] p-12 text-center" },
                        h('h2', { className: "text-6xl mb-4" }, "🎉"), h('h3', { className: "text-3xl font-black mb-10" }, "本輪測驗已結束"),
                        h('button', { onClick: () => setView('home'), className: "w-full py-5 bg-slate-900 text-white rounded-3xl font-black shadow-xl" }, "再練一次")
                    )
                );
            }

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(h(App));
        })();
    </script>
</body>
</html>"""

    # 2. math.html - 補全 Again/Hard/Good/Easy 與 答案顯示邏輯
    math_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>學習大師 Math Master (SRS Support)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: #f8fafc; min-height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.4); border-radius: 3rem; padding: 2.5rem; max-width: 480px; width: 100%; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.05); }
        .card-container { height: 400px; width: 100%; position: relative; perspective: 1000px; }
        .card { position: absolute; width: 100%; height: 100%; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; cursor: pointer; }
        .card.is-flipped { transform: rotateY(180deg); }
        .card-face { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; text-align: center; }
        .card-front { background: white; border: 1px solid #e2e8f0; }
        .card-back { background: #f0f9ff; border: 2px solid #0ea5e9; transform: rotateY(180deg); }
        .srs-btn { height: 5rem; border-radius: 1.5rem; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 900; transition: all 0.2s; border: 2px solid transparent; }
        .srs-btn:active { transform: scale(0.95); }
        .btn-again { border-color: #fee2e2; color: #dc2626; background: #fff5f5; }
        .btn-hard { border-color: #ffedd5; color: #d97706; background: #fffafb; }
        .btn-good { border-color: #dcfce7; color: #16a34a; background: #f0fdf4; }
        .btn-easy { border-color: #dbeafe; color: #2563eb; background: #eff6ff; }
        .math-tex { font-size: 1.25em; line-height: 1.6; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script>
        window.M_DATA = MATH_DATA_PLACEHOLDER;
        (function() {
            const h = React.createElement; const { useState, useEffect } = React;
            function App() {
                const [idx, setIdx] = useState(0); const [flipped, setFlipped] = useState(false);
                const list = window.M_DATA || [];
                useEffect(() => { window.renderMathInElement(document.body, { delimiters: [{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}] }); }, [idx, flipped]);
                const next = () => { if(idx+1 < list.length) { setIdx(idx+1); setFlipped(false); } else alert("測驗結束！"); };
                if(list.length===0) return h('div', null, "無數據");
                const item = list[idx];
                return h('div', {className:"glass"},
                    h('div', {className:"flex justify-between items-center mb-6 px-2"},
                        h('a', {href:'entry.html', className:"text-slate-300 font-black h-8 w-8 flex items-center justify-center rounded-full hover:bg-white"}, "✕"),
                        h('span', {className:"text-[10px] font-black bg-slate-900 text-white px-3 py-1 rounded-full"}, (idx+1)+"/"+list.length)
                    ),
                    h('div', {className:"card-container mb-10", onClick:()=>setFlipped(!flipped)},
                        h('div', {className:"card "+(flipped?"is-flipped":"")},
                            h('div', {className:"card-face card-front"}, h('span', {className:"text-[10px] uppercase font-black text-sky-500 mb-4"}, "觀念問題"), h('h2', {className:"text-3xl font-black math-tex"}, item.w)),
                            h('div', {className:"card-face card-back"}, h('span', {className:"text-[10px] uppercase font-black text-sky-400 mb-4"}, "詳細解答"), h('div', {className:"math-tex font-bold"}, item.d))
                        )
                    ),
                    flipped ? h('div', {className:"grid grid-cols-4 gap-3 w-full"},
                        ['Again','Hard','Good','Easy'].map((b,i)=>h('button',{key:i, onClick:next, className:`srs-btn btn-${b.toLowerCase()}`}, h('span',{className:'text-lg'},b)))
                    ) : h('p', {className:"text-slate-300 font-black animate-pulse"}, "點擊卡片查看解答")
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(h(App));
        })();
    </script>
</body>
</html>"""

    # 替換資料並格式化
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_template.replace("VOCAB_DATA_PLACEHOLDER", v_json).replace("IDIOM_DATA_PLACEHOLDER", i_json))
    with open("math.html", "w", encoding="utf-8") as f:
        f.write(math_template.replace("MATH_DATA_PLACEHOLDER", m_json))
    
    print("Build Success: Generated index.html (9468ea0 Peak) & math.html (SRS Fixed)")

if __name__ == "__main__":
    build_html()
