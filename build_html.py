import json
import os
import re
from opencc import OpenCC

def build_html():
    vocab_data_path = "vocab_data.js"
    idiom_data_path = "idiom_data.js"
    math_data_path = "math_data.js"
    output_path = "index.html"
    
    cc = OpenCC('s2t')

    def get_db_data(path):
        if not os.path.exists(path): return "[]"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                # 尋找第一對方括號 [ ... ]
                start = content.find('[')
                end = content.rfind(']')
                if start != -1 and end != -1:
                    js_str = content[start:end+1]
                    # 繁體轉換
                    return cc.convert(js_str)
        except Exception as e:
            print(f"Error reading {path}: {e}")
        return "[]"

    v_json = get_db_data(vocab_data_path)
    i_json = get_db_data(idiom_data_path)
    m_json = get_db_data(math_data_path)

    html_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全能學習大師 Vocab & Idiom & Math Master</title>
    <!-- 核心庫 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- KaTeX 數學渲染 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); margin: 0; padding: 0; min-height: 100vh; overflow-x: hidden; color: #1e293b; }
        .glass { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 8px 32px rgba(0,0,0,0.05); }
        .card-container { height: 480px; width: 100%; max-width: 400px; position: relative; }
        .card { position: absolute; width: 100%; height: 100%; transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); transform-style: preserve-3d; cursor: pointer; }
        .card.is-flipped { transform: rotateY(180deg); }
        .card-face { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2.5rem; text-align: center; }
        .card-front { background: white; border: 1px solid #e2e8f0; }
        .card-back { background: #f8fafc; border: 2px solid #6366f1; transform: rotateY(180deg); }
        .srs-btn { transition: all 0.2s; border: 2px solid transparent; }
        .srs-btn:hover { transform: translateY(-2px); }
        .btn-again { border-color: #fee2e2; color: #dc2626; background: #fff5f5; }
        .btn-hard { border-color: #ffedd5; color: #d97706; background: #fffafb; }
        .btn-good { border-color: #dcfce7; color: #16a34a; background: #f0fdf4; }
        .btn-easy { border-color: #dbeafe; color: #2563eb; background: #eff6ff; }
        @keyframes bounce-subtle { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        .animate-bounce-subtle { animation: bounce-subtle 2s infinite; }
        .math-tex { font-size: 1.2em; line-height: 1.5; }
    </style>
</head>
<body>
    <div id="root"></div>

    <!-- 先注入資料 -->
    <script type="text/javascript">
        window.V_DATA = VOCAB_DATA_PLACEHOLDER;
        window.I_DATA = IDIOM_DATA_PLACEHOLDER;
        window.M_DATA = MATH_DATA_PLACEHOLDER;
    </script>

    <!-- 再執行 React -->
    <script type="text/javascript">
        (function() {
            const e = React.createElement;
            const { useState, useEffect, useMemo, useRef } = React;

            function shuffle(array) {
                const arr = [...array];
                for (let i = arr.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [arr[i], arr[j]] = [arr[j], arr[i]];
                }
                return arr;
            }

            function App() {
                const [view, setView] = useState('home');
                const [subject, setSubject] = useState(null);
                const [mode, setMode] = useState('flash');
                const [rawDb, setRawDb] = useState([]);
                const [quizList, setQuizList] = useState([]);
                const [currIdx, setCurrIdx] = useState(0);
                const [isFlipped, setIsFlipped] = useState(false);
                const [userInput, setUserInput] = useState('');
                const [isSubmitted, setIsSubmitted] = useState(false);
                const [isCorrect, setIsCorrect] = useState(false);
                const [totalInitial, setTotalInitial] = useState(0);

                const [lvlFilter, setLvlFilter] = useState('all');
                const [prefixFilter, setPrefixFilter] = useState('');
                const [limit, setLimit] = useState(20);

                useEffect(() => {
                    const el = document.getElementById('root');
                    if (el && window.renderMathInElement) {
                        try {
                            window.renderMathInElement(el, {
                                delimiters: [
                                    {left: '$$', right: '$$', display: true},
                                    {left: '$', right: '$', display: false}
                                ],
                                throwOnError: false
                            });
                        } catch(err) { console.error("KaTeX Error:", err); }
                    }
                }, [view, currIdx, isFlipped, isSubmitted]);

                useEffect(() => {
                    const handleKey = (ev) => {
                        if (view !== 'quiz') return;
                        if (mode === 'flash') {
                            if (ev.code === 'Space') {
                                ev.preventDefault();
                                toggleFlip();
                            } else if (isFlipped && ['1','2','3','4'].includes(ev.key)) {
                                nextQuestion();
                            }
                        }
                    };
                    window.addEventListener('keydown', handleKey);
                    return () => window.removeEventListener('keydown', handleKey);
                }, [view, mode, isFlipped, currIdx]);

                const startSetup = (sub, m) => {
                    setSubject(sub);
                    setMode(m);
                    const db = sub === 'vocab' ? window.V_DATA : (sub === 'idiom' ? window.I_DATA : window.M_DATA);
                    setRawDb(db || []);
                    setView('setup');
                };

                const startQuiz = () => {
                    let filtered = [...rawDb];
                    if (subject === 'vocab' && lvlFilter !== 'all') {
                        filtered = filtered.filter(item => String(item.l) === lvlFilter);
                    }
                    if (prefixFilter) {
                        const pf = prefixFilter.toLowerCase();
                        filtered = filtered.filter(item => {
                            const w = (item.word || item.w || "").toLowerCase();
                            return w.startsWith(pf);
                        });
                    }
                    const shuffled = shuffle(filtered).slice(0, Math.min(parseInt(limit), filtered.length));
                    if (shuffled.length === 0) {
                        alert("找不到符合條件的題目！");
                        return;
                    }
                    setQuizList(shuffled);
                    setTotalInitial(shuffled.length);
                    setCurrIdx(0);
                    setIsFlipped(false);
                    setUserInput('');
                    setIsSubmitted(false);
                    setView('quiz');
                };

                const toggleFlip = () => {
                    setIsFlipped(prev => !prev);
                    if (!isFlipped && subject === 'vocab') speak((quizList[currIdx].word || quizList[currIdx].w));
                };

                const checkFill = () => {
                    const target = (quizList[currIdx].word || quizList[currIdx].w || "").trim().toLowerCase();
                    const input = userInput.trim().toLowerCase();
                    const correct = input === target;
                    setIsCorrect(correct);
                    setIsSubmitted(true);
                    if (correct) playTone(600, 0.1); else { playTone(200, 0.2); speak(target); }
                };

                const nextQuestion = () => {
                    if (currIdx + 1 < quizList.length) {
                        setCurrIdx(currIdx + 1);
                        setIsFlipped(false);
                        setIsSubmitted(false);
                        setUserInput('');
                    } else setView('result');
                };

                const speak = (text) => {
                    if (!text) return;
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance(text);
                    u.lang = 'en-US';
                    window.speechSynthesis.speak(u);
                };

                const playTone = (freq, dur) => {
                    try {
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        const osc = ctx.createOscillator();
                        const g = ctx.createGain();
                        osc.connect(g); g.connect(ctx.destination);
                        osc.frequency.value = freq;
                        osc.start();
                        g.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + dur);
                        osc.stop(ctx.currentTime + dur);
                    } catch(e) {}
                };

                if (view === 'home') {
                    return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        e('div', { className: "glass max-w-sm w-full rounded-[3rem] p-12 text-center animate-bounce-subtle" },
                            e('h1', { className: "text-4xl font-black mb-2" }, "學習大師"),
                            e('p', { className: "text-slate-400 text-sm mb-10 font-bold" }, "Vocab • Idiom • Math"),
                            e('div', { className: "space-y-4" },
                                [
                                    { s: 'vocab', m: 'flash', t: '英文單字 (閃卡)', c: 'bg-indigo-600' },
                                    { s: 'vocab', m: 'fill', t: '英文單字 (填空)', c: 'border-4 border-indigo-100 text-indigo-600' },
                                    { s: 'idiom', m: 'flash', t: '中文成語 (閃卡)', c: 'bg-emerald-600' },
                                    { s: 'idiom', m: 'fill', t: '中文成語 (填空)', c: 'border-4 border-emerald-100 text-emerald-600' },
                                    { s: 'math', m: 'flash', t: '國中數學 (觀念)', c: 'bg-slate-900' }
                                ].map((b, idx) => e('button', { key: idx, onClick: () => startSetup(b.s, b.m), className: `w-full py-4 rounded-3xl font-black text-lg transition-all ${b.c} ${b.c.includes('bg-') ? 'text-white shadow-lg' : 'hover:bg-slate-50'}` }, b.t))
                            )
                        )
                    );
                }

                if (view === 'setup') {
                    const lvls = subject === 'vocab' ? [...new Set(rawDb.map(i => i.l))].filter(Boolean).sort((a,b)=>a-b) : [];
                    return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        e('div', { className: "glass max-w-sm w-full rounded-[2.5rem] p-10" },
                            e('h2', { className: "text-2xl font-black mb-8 text-center" }, "測驗設定"),
                            subject === 'vocab' && e('div', { className: "mb-6" },
                                e('label', { className: "block text-xs font-black text-slate-400 uppercase mb-2" }, "選擇 Level"),
                                e('select', { value: lvlFilter, onChange: (ev) => setLvlFilter(ev.target.value), className: "w-full p-4 rounded-2xl bg-slate-100 font-bold outline-none" },
                                    e('option', { value: 'all' }, "全部等級"),
                                    lvls.map(l => e('option', { key: l, value: l }, "Level " + l))
                                )
                            ),
                            e('div', { className: "mb-6" },
                                e('label', { className: "block text-xs font-black text-slate-400 uppercase mb-2" }, "關鍵字/字首 篩選"),
                                e('input', { value: prefixFilter, onChange: (ev) => setPrefixFilter(ev.target.value), placeholder: "例如: a", className: "w-full p-4 rounded-2xl bg-slate-100 font-bold outline-none" })
                            ),
                            e('div', { className: "mb-10" },
                                e('label', { className: "block text-xs font-black text-slate-400 uppercase mb-2" }, "題目數量: " + limit),
                                e('input', { type: 'range', min: 5, max: 100, step: 5, value: limit, onChange: (ev) => setLimit(ev.target.value), className: "w-full h-2 bg-indigo-100 rounded-lg appearance-none cursor-pointer" })
                            ),
                            e('button', { onClick: startQuiz, className: "w-full py-5 bg-indigo-600 text-white rounded-[2rem] font-black text-xl mb-4 shadow-xl" }, "開始測驗"),
                            e('button', { onClick: () => setView('home'), className: "w-full text-slate-400 font-bold" }, "返回首頁")
                        )
                    );
                }

                if (view === 'quiz') {
                    const item = quizList[currIdx];
                    const target = item.word || item.w || "";
                    const displayDef = item.definition || item.explanation || item.d || "";

                    if (mode === 'flash') {
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            e('div', { className: "w-full max-w-md mb-8 flex justify-between items-center" },
                                e('button', { onClick: () => setView('home'), className: "text-slate-400 font-black h-10 w-10 flex items-center justify-center rounded-full hover:bg-white transition-all" }, "✕"),
                                e('div', { className: "px-4 py-1 rounded-full bg-slate-900 text-white text-[10px] font-black" }, (currIdx + 1) + " / " + totalInitial)
                            ),
                            e('div', { className: "card-container mb-12", onClick: toggleFlip },
                                e('div', { className: "card " + (isFlipped ? "is-flipped" : "") },
                                    e('div', { className: "card-face card-front" },
                                        e('span', { className: "text-indigo-500 font-black text-[10px] uppercase tracking-widest mb-4" }, "Question"),
                                        e('h2', { className: "text-4xl font-black leading-tight math-tex" }, target)
                                    ),
                                    e('div', { className: "card-face card-back" },
                                        e('span', { className: "text-indigo-400 font-black text-[10px] uppercase tracking-widest mb-4" }, "Answer"),
                                        e('h3', { className: "text-2xl font-bold mb-4 math-tex" }, displayDef),
                                        item.example && e('p', { className: "text-sm text-slate-500 italic max-w-xs math-tex" }, item.example)
                                    )
                                )
                            ),
                            isFlipped ? e('div', { className: "w-full max-w-md grid grid-cols-4 gap-3 h-20" },
                                [
                                    { t: 'Again', c: 'btn-again' }, { t: 'Hard', c: 'btn-hard' }, { t: 'Good', c: 'btn-good' }, { t: 'Easy', c: 'btn-easy' }
                                ].map((b, i) => e('button', { key: i, onClick: nextQuestion, className: `srs-btn rounded-3xl flex flex-col items-center justify-center font-black ${b.c}` }, 
                                    e('span', { className: 'text-lg' }, b.t),
                                    e('span', { className: 'text-[10px] opacity-40' }, i + 1)
                                ))
                            ) : e('p', { className: "text-slate-300 font-black animate-pulse" }, "點擊卡片或空白鍵翻頁")
                        );
                    } else {
                        const firstChar = target.charAt(0);
                        const restLen = Math.max(0, target.length - 1);
                        const underscores = "_ ".repeat(restLen).trim();
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            e('div', { className: "glass max-w-md w-full rounded-[3rem] p-10 text-center" },
                                e('h2', { className: "text-3xl font-black mb-8 math-tex" }, displayDef),
                                e('div', { className: "mb-8 flex flex-col items-center" },
                                    e('div', { className: "text-3xl font-black tracking-widest mb-2" }, 
                                        e('span', { className: "text-indigo-600" }, firstChar),
                                        e('span', { className: "text-slate-300" }, underscores)
                                    ),
                                    e('p', { className: "text-[10px] font-black text-slate-400 uppercase" }, target.length + " 字元")
                                ),
                                !isSubmitted ? e('div', null,
                                    e('input', { autoFocus: true, value: userInput, onChange: (ev) => setUserInput(ev.target.value), onKeyDown: (ev) => ev.key === 'Enter' && checkFill(), placeholder: "輸入完整單字...", className: "w-full p-5 text-xl font-bold bg-slate-50 rounded-2xl border-4 border-transparent focus:border-indigo-500 outline-none text-center transition-all mb-6" }),
                                    e('button', { onClick: checkFill, className: "w-full py-5 bg-indigo-600 text-white rounded-3xl font-black text-lg shadow-lg shadow-indigo-200" }, "檢查答案")
                                ) : e('div', { className: "animate-slide" },
                                    e('div', { className: "mb-8" },
                                        e('h3', { className: `text-5xl font-black mb-2 ${isCorrect ? 'text-green-500' : 'text-red-500'}` }, target),
                                        !isCorrect && e('p', { className: "text-slate-400 line-through" }, userInput)
                                    ),
                                    e('button', { onClick: nextQuestion, className: "w-full py-5 bg-slate-900 text-white rounded-3xl font-black text-lg" }, "下一題")
                                )
                            )
                        );
                    }
                }

                if (view === 'result') {
                    return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        e('div', { className: "glass max-w-sm w-full rounded-[3rem] p-12 text-center" },
                            e('h2', { className: "text-5xl mb-4" }, "🎉"),
                            e('h3', { className: "text-3xl font-black mb-2" }, "太棒了！"),
                            e('p', { className: "text-slate-400 font-bold mb-10" }, "您已完成本次測驗"),
                            e('button', { onClick: () => setView('home'), className: "w-full py-5 bg-slate-900 text-white rounded-3xl font-black shadow-xl" }, "回首頁")
                        )
                    );
                }
            }

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(e(App));
        })();
    </script>
</body>
</html>"""

    # 正確替換資料預留位置
    html_output = html_template.replace("VOCAB_DATA_PLACEHOLDER", v_json)
    html_output = html_output.replace("IDIOM_DATA_PLACEHOLDER", i_json)
    html_output = html_output.replace("MATH_DATA_PLACEHOLDER", m_json)
    
    # 寫入檔案，確保使用 UTF-8 編碼
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Build Success. All features restored and encoding fixed.")

if __name__ == "__main__":
    build_html()
