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

    def get_db_data(path, var_name):
        if not os.path.exists(path): return "[]"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # 提取 JSON 陣列部分
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                js_str = match.group(0)
                return cc.convert(js_str)
        return "[]"

    v_js = get_db_data(vocab_data_path, "VOCAB_DB")
    idiom_js = get_db_data(idiom_data_path, "IDIOM_DB")
    math_js = get_db_data(math_data_path, "MATH_DB")

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
        .input-underline { border-bottom: 3px solid #cbd5e1; font-family: monospace; }
        .input-underline:focus { border-color: #6366f1; outline: none; }
        @keyframes bounce-subtle { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        .animate-bounce-subtle { animation: bounce-subtle 2s infinite; }
        .math-tex { font-size: 1.2em; line-height: 1.5; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/javascript">
        window.V_DB = V_DATA;
        window.I_DB = I_DATA;
        window.M_DB = M_DATA;

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
                const [view, setView] = useState('home'); // home, setup, quiz, result
                const [subject, setSubject] = useState(null); // vocab, idiom, math
                const [mode, setMode] = useState('flash'); // flash, fill
                const [rawDb, setRawDb] = useState([]);
                const [quizList, setQuizList] = useState([]);
                const [currIdx, setCurrIdx] = useState(0);
                const [isFlipped, setIsFlipped] = useState(false);
                const [userInput, setUserInput] = useState('');
                const [isSubmitted, setIsSubmitted] = useState(false);
                const [isCorrect, setIsCorrect] = useState(false);
                const [totalInitial, setTotalInitial] = useState(0);

                // Filters
                const [lvlFilter, setLvlFilter] = useState('all');
                const [prefixFilter, setPrefixFilter] = useState('');
                const [limit, setLimit] = useState(20);

                useEffect(() => {
                    if (view === 'home') {
                        setSubject(null);
                        setRawDb([]);
                    }
                }, [view]);

                useEffect(() => {
                    const el = document.getElementById('root');
                    if (el && window.renderMathInElement) {
                        window.renderMathInElement(el, {
                            delimiters: [
                                {left: '$$', right: '$$', display: true},
                                {left: '$', right: '$', display: false}
                            ],
                            throwOnError: false
                        });
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
                    setRawDb(sub === 'vocab' ? window.V_DB : (sub === 'idiom' ? window.I_DB : window.M_DB));
                    setView('setup');
                };

                const startQuiz = () => {
                    let filtered = [...rawDb];
                    if (subject === 'vocab' && lvlFilter !== 'all') {
                        filtered = filtered.filter(item => String(item.l) === lvlFilter);
                    }
                    if (prefixFilter) {
                        filtered = filtered.filter(item => item.word?.toLowerCase().startsWith(prefixFilter.toLowerCase()) || item.w?.toLowerCase().startsWith(prefixFilter.toLowerCase()));
                    }
                    const shuffled = shuffle(filtered).slice(0, Math.min(limit, filtered.length));
                    setQuizList(shuffled);
                    setTotalInitial(shuffled.length);
                    setCurrIdx(0);
                    setIsFlipped(false);
                    setUserInput('');
                    setIsSubmitted(false);
                    setView('quiz');
                };

                const toggleFlip = () => {
                    const next = !isFlipped;
                    setIsFlipped(next);
                    if (next && subject === 'vocab' && mode === 'flash') speak(quizList[currIdx].word);
                };

                const checkFill = () => {
                    const target = (quizList[currIdx].word || quizList[currIdx].w).trim().toLowerCase();
                    const input = userInput.trim().toLowerCase();
                    const correct = input === target;
                    setIsCorrect(correct);
                    setIsSubmitted(true);
                    if (correct) {
                        playTone(600, 0.1); 
                    } else {
                        playTone(200, 0.2);
                        speak(quizList[currIdx].word || quizList[currIdx].w);
                    }
                };

                const nextQuestion = () => {
                    if (currIdx + 1 < quizList.length) {
                        setCurrIdx(currIdx + 1);
                        setIsFlipped(false);
                        setIsSubmitted(false);
                        setUserInput('');
                    } else {
                        setView('result');
                    }
                };

                const speak = (text) => {
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance(text);
                    u.lang = 'en-US';
                    window.speechSynthesis.speak(u);
                };

                const playTone = (freq, dur) => {
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    const g = ctx.createGain();
                    osc.connect(g); g.connect(ctx.destination);
                    osc.frequency.value = freq;
                    osc.start();
                    g.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + dur);
                    osc.stop(ctx.currentTime + dur);
                };

                if (view === 'home') {
                    return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        e('div', { className: "glass max-w-sm w-full rounded-[3rem] p-12 text-center animate-bounce-subtle" },
                            e('h1', { className: "text-4xl font-black mb-2" }, "學習大師"),
                            e('p', { className: "text-slate-400 text-sm mb-10 font-bold" }, "Vocab • Idiom • Math"),
                            e('div', { className: "space-y-4" },
                                e('button', { onClick: () => startSetup('vocab', 'flash'), className: "w-full py-5 rounded-3xl bg-indigo-600 text-white font-black text-lg shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all" }, "英文單字 (閃卡)"),
                                e('button', { onClick: () => startSetup('vocab', 'fill'), className: "w-full py-5 rounded-3xl border-4 border-indigo-100 text-indigo-600 font-black text-lg hover:bg-indigo-50 transition-all" }, "英文單字 (填空)"),
                                e('div', { className: "h-2" }),
                                e('button', { onClick: () => startSetup('idiom', 'flash'), className: "w-full py-5 rounded-3xl bg-emerald-600 text-white font-black text-lg shadow-lg shadow-emerald-200 hover:bg-emerald-700 transition-all" }, "中文成語 (閃卡)"),
                                e('button', { onClick: () => startSetup('idiom', 'fill'), className: "w-full py-5 rounded-3xl border-4 border-emerald-100 text-emerald-600 font-black text-lg hover:bg-emerald-50 transition-all" }, "中文成語 (填空)"),
                                e('div', { className: "h-2" }),
                                e('button', { onClick: () => startSetup('math', 'flash'), className: "w-full py-5 rounded-3xl bg-slate-900 text-white font-black text-lg shadow-lg shadow-slate-300 hover:opacity-90 transition-all" }, "國中數學 (觀念)")
                            )
                        )
                    );
                }

                if (view === 'setup') {
                    const lvls = subject === 'vocab' ? [...new Set(rawDb.map(i => i.l))].sort((a,b)=>a-b) : [];
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
                            e('button', { onClick: startQuiz, className: "w-full py-5 bg-indigo-600 text-white rounded-[2rem] font-black text-xl mb-4" }, "開始測驗"),
                            e('button', { onClick: () => setView('home'), className: "w-full text-slate-400 font-bold" }, "返回首頁")
                        )
                    );
                }

                if (view === 'quiz') {
                    const item = quizList[currIdx];
                    const target = item.word || item.w;
                    const displayDef = item.definition || item.explanation || item.d;

                    if (mode === 'flash') {
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            e('div', { className: "w-full max-w-md mb-8 flex justify-between items-center" },
                                e('button', { onClick: () => setView('home'), className: "text-slate-400 font-black" }, "✕ 結束"),
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
                                        item.example && e('p', { className: "text-sm text-slate-500 italic" }, item.example)
                                    )
                                )
                            ),
                            isFlipped ? e('div', { className: "w-full max-w-md grid grid-cols-4 gap-3 h-20" },
                                ['Again', 'Hard', 'Good', 'Easy'].map((t, i) => e('button', { key: t, onClick: nextQuestion, className: `srs-btn rounded-3xl flex flex-col items-center justify-center btn-${t.toLowerCase()}` }, 
                                    e('span', { className: 'text-lg font-black' }, t),
                                    e('span', { className: 'text-[10px] font-bold opacity-50' }, i + 1)
                                ))
                            ) : e('p', { className: "text-slate-300 font-black animate-pulse" }, "點擊卡片或空白鍵翻頁")
                        );
                    } else {
                        // Fill-in mode
                        const firstChar = target.charAt(0);
                        const restLen = target.length - 1;
                        const underscores = "_ ".repeat(restLen).trim();
                        
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            e('div', { className: "glass max-w-md w-full rounded-[3rem] p-10 text-center" },
                                e('h2', { className: "text-3xl font-black mb-8" }, displayDef),
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
                            e('button', { onClick: () => setView('home'), className: "w-full py-5 bg-slate-900 text-white rounded-3xl font-black" }, "回首頁")
                        )
                    );
                }
            }

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(e(App));
        })();
    </script>
    <script type="text/javascript">
        // Embed Data directly as JS objects
        const V_DATA = VOCAB_DATA_PLACEHOLDER;
        const I_DATA = IDIOM_DATA_PLACEHOLDER;
        const M_DATA = MATH_DATA_PLACEHOLDER;
    </script>
</body>
</html>"""

    html_output = html_template.replace("VOCAB_DATA_PLACEHOLDER", v_js).replace("IDIOM_DATA_PLACEHOLDER", idiom_js).replace("MATH_DATA_PLACEHOLDER", math_js)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Build Success. All legacy features restored and Math KaTeX integrated.")

if __name__ == "__main__":
    build_html()
