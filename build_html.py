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
                # 尋找第一對方括號 [ ... ]
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

    # 1. 產生 index.html (恢復 5bc2273 的純英文+成語版)
    # 此版本具備最完整的 Level 篩選、字首提示、填空暗示、正確/錯誤音效，且無 Math 干擾
    index_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>學習大師 Vocab & Idiom Master</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); min-height: 100vh; color: #1e293b; }
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
    </style>
</head>
<body>
    <div id="root"></div>
    <script>
        window.V_DATA = VOCAB_DATA_PLACEHOLDER;
        window.I_DATA = IDIOM_DATA_PLACEHOLDER;
        (function() {
            const e = React.createElement;
            const { useState, useEffect } = React;
            function shuffle(array) { const arr = [...array]; for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; } return arr; }
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
                const [lvlFilter, setLvlFilter] = useState('all');
                const [prefixFilter, setPrefixFilter] = useState('');
                const [limit, setLimit] = useState(20);

                const startSetup = (s, m) => { setSubject(s); setMode(m); setRawDb(s==='vocab'?window.V_DATA:window.I_DATA); setView('setup'); };
                const startQuiz = () => {
                    let f = [...rawDb];
                    if(subject==='vocab' && lvlFilter!=='all') f = f.filter(i => String(i.l)===lvlFilter);
                    if(prefixFilter) f = f.filter(i => (i.word||i.w||"").toLowerCase().startsWith(prefixFilter.toLowerCase()));
                    const s = shuffle(f).slice(0, parseInt(limit));
                    setQuizList(s); setCurrIdx(0); setIsFlipped(false); setUserInput(''); setIsSubmitted(false); setView('quiz');
                };
                const toggleFlip = () => { setIsFlipped(!isFlipped); if(!isFlipped && subject==='vocab') speak(quizList[currIdx].word||quizList[currIdx].w); };
                const checkFill = () => {
                    const t = (quizList[currIdx].word||quizList[currIdx].w).toLowerCase().trim();
                    const i = userInput.toLowerCase().trim();
                    const ok = t === i; setIsCorrect(ok); setIsSubmitted(true);
                    if(ok) playTone(600,0.1); else { playTone(200,0.2); speak(t); }
                };
                const next = () => { if(currIdx+1 < quizList.length) { setCurrIdx(currIdx+1); setIsFlipped(false); setIsSubmitted(false); setUserInput(''); } else setView('result'); };
                const speak = (t) => { window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(t); u.lang='en-US'; window.speechSynthesis.speak(u); };
                const playTone = (f,d) => { const c = new (window.AudioContext||window.webkitAudioContext)(); const o=c.createOscillator(); const g=c.createGain(); o.connect(g); g.connect(c.destination); o.frequency.value=f; o.start(); g.gain.exponentialRampToValueAtTime(0.00001, c.currentTime+d); o.stop(c.currentTime+d); };

                if(view==='home') return e('div', {className:"flex flex-col items-center justify-center min-h-screen p-6"},
                    e('div', {className:"glass max-w-sm w-full rounded-[3rem] p-12 text-center"},
                         e('h1', {className:"text-4xl font-black mb-8"}, "大師單字本"),
                         e('div', {className:"space-y-4"},
                            e('button', {onClick:()=>startSetup('vocab','flash'), className:"w-full py-5 bg-indigo-600 text-white rounded-3xl font-black text-lg shadow-lg"}, "英文閃卡"),
                            e('button', {onClick:()=>startSetup('vocab','fill'), className:"w-full py-5 border-4 border-indigo-100 text-indigo-600 rounded-3xl font-black text-lg"}, "英文填空"),
                            e('div', {className:"h-4"}),
                            e('button', {onClick:()=>startSetup('idiom','flash'), className:"w-full py-5 bg-emerald-600 text-white rounded-3xl font-black text-lg shadow-lg"}, "成語閃卡"),
                            e('button', {onClick:()=>startSetup('idiom','fill'), className:"w-full py-5 border-4 border-emerald-100 text-emerald-600 rounded-3xl font-black text-lg"}, "成語填空"),
                            e('a', {href:'entry.html', className:"block mt-8 text-slate-400 font-bold text-sm"}, "← 返回導覽入口")
                         )
                    )
                );
                if(view==='setup') return e('div', {className:"flex flex-col items-center justify-center min-h-screen p-6"},
                    e('div', {className:"glass max-w-sm w-full rounded-[2.5rem] p-10"},
                        e('h2', {className:"text-2xl font-black mb-8 text-center"}, "設定"),
                        subject==='vocab' && e('div', {className:"mb-4"},
                           e('label', {className:"text-xs font-black text-slate-400"}, "Level"),
                           e('select', {value:lvlFilter, onChange:v=>setLvlFilter(v.target.value), className:"w-full p-4 rounded-2xl bg-slate-100 mt-2 font-bold"},
                               e('option',{value:'all'},"全部"), [1,2,3,4,5,6].map(l=>e('option',{key:l,value:l},"Level "+l))
                           )
                        ),
                        e('div', {className:"mb-4"},
                           e('label', {className:"text-xs font-black text-slate-400"}, "字首篩選"),
                           e('input', {value:prefixFilter, onChange:v=>setPrefixFilter(v.target.value), placeholder:"e.g. a", className:"w-full p-4 rounded-2xl bg-slate-100 mt-2 font-bold outline-none"})
                        ),
                        e('div', {className:"mb-8"},
                           e('label', {className:"text-xs font-black text-slate-400"}, "題數: "+limit),
                           e('input', {type:'range', min:5, max:100, step:5, value:limit, onChange:v=>setLimit(v.target.value), className:"w-full h-2 bg-indigo-100 rounded-lg appearance-none cursor-pointer mt-4"})
                        ),
                        e('button', {onClick:startQuiz, className:"w-full py-5 bg-indigo-600 text-white rounded-3xl font-black text-xl mb-4"}, "啟動測驗"),
                        e('button', {onClick:()=>setView('home'), className:"w-full text-slate-400 font-bold"}, "取消")
                    )
                );
                if(view==='quiz') {
                    const item = quizList[currIdx]; const t = item.word||item.w; const d = item.definition||item.explanation||item.d;
                    if(mode==='flash') return e('div', {className:"flex flex-col items-center justify-center min-h-screen p-6"},
                        e('div', {className:"w-full max-w-md mb-8 flex justify-between items-center"},
                             e('button', {onClick:()=>setView('home'), className:"text-slate-400 font-black h-10 w-10 flex items-center justify-center rounded-full bg-white"}, "✕"),
                             e('div', {className:"px-4 py-1 rounded-full bg-slate-900 text-white text-[10px] font-black"}, (currIdx+1)+"/"+quizList.length)
                        ),
                        e('div', {className:"card-container mb-12", onClick:toggleFlip},
                            e('div', {className:"card "+(isFlipped?"is-flipped":"")},
                                e('div', {className:"card-face card-front"}, e('h2', {className:"text-4xl font-black"}, t)),
                                e('div', {className:"card-face card-back"}, e('h3', {className:"text-2xl font-bold mb-4"}, d), item.example && e('p',{className:"text-sm text-slate-400 italic"},item.example))
                            )
                        ),
                        isFlipped ? e('div', {className:"grid grid-cols-4 gap-3 w-full max-w-md h-20"},
                            ['Again','Hard','Good','Easy'].map((b,i)=>e('button',{key:i, onClick:next, className:`srs-btn rounded-3xl font-black text-lg btn-${b.toLowerCase()}`}, b))
                        ) : e('p',{className:"text-slate-300 font-black animate-pulse"},"點擊或空白鍵翻頁")
                    );
                    else {
                        const firstChar = t.charAt(0); const rest = "_ ".repeat(t.length-1).trim();
                        return e('div', {className:"flex flex-col items-center justify-center min-h-screen p-6"},
                            e('div', {className:"glass max-w-md w-full rounded-[3rem] p-10 text-center"},
                                e('h2', {className:"text-3xl font-black mb-8"}, d),
                                e('div', {className:"mb-8"}, 
                                    e('div', {className:"text-3xl font-black tracking-widest mb-2"}, e('span',{className:"text-indigo-600"},firstChar), e('span',{className:"text-slate-200"},rest)),
                                    e('p', {className:"text-[10px] font-black text-slate-400 uppercase"}, t.length+" 字元")
                                ),
                                !isSubmitted ? e('div', null,
                                    e('input', {autoFocus:true, value:userInput, onChange:v=>setUserInput(v.target.value), onKeyDown:v=>v.key==='Enter'&&checkFill(), className:"w-full p-5 text-xl font-bold bg-slate-50 rounded-2xl border-4 border-transparent focus:border-indigo-500 outline-none text-center mb-6"}),
                                    e('button', {onClick:checkFill, className:"w-full py-5 bg-indigo-600 text-white rounded-3xl font-black text-lg shadow-lg"}, "檢查答案")
                                ) : e('div', null,
                                    e('h3', {className:`text-5xl font-black mb-4 ${isCorrect?'text-green-500':'text-red-500'}`}, t),
                                    !isCorrect && e('p', {className:"text-slate-300 line-through mb-4"}, userInput),
                                    e('button', {onClick:next, className:"w-full py-5 bg-slate-900 text-white rounded-3xl font-black text-lg"}, "下一題")
                                )
                            )
                        );
                    }
                }
                if(view==='result') return e('div', {className:"flex flex-col items-center justify-center min-h-screen p-6"},
                    e('div', {className:"glass max-w-sm w-full rounded-[3rem] p-12 text-center"},
                        e('h2', {className:"text-5xl mb-4"}, "🎉"), e('h3', {className:"text-3xl font-black mb-2"}, "完成！"), e('button', {onClick:()=>setView('home'), className:"w-full py-5 bg-slate-900 text-white rounded-3xl font-black mt-8"}, "回首頁")
                    )
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(e(App));
        })();
    </script>
</body>
</html>"""

    # 2. 產生 math.html (獨立數學版，含 KaTeX)
    math_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>學習大師 Math Master</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', 'Noto Sans TC', sans-serif; background: #f1f5f9; min-height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .glass { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.3); border-radius: 3rem; padding: 3rem; max-width: 450px; width: 100%; text-align: center; }
        .math-card { min-height: 400px; display: flex; flex-direction: column; justify-content: center; }
        .math-tex { font-size: 1.3em; margin: 1rem 0; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script>
        window.M_DATA = MATH_DATA_PLACEHOLDER;
        (function() {
            const e = React.createElement;
            const { useState, useEffect } = React;
            function App() {
                const [idx, setIdx] = useState(0);
                const [flip, setFlip] = useState(false);
                const list = window.M_DATA || [];
                useEffect(() => { window.renderMathInElement(document.body, { delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}] }); }, [idx, flip]);
                const next = () => { setIdx((idx + 1) % list.length); setFlip(false); };
                if (list.length === 0) return e('div', null, "無數據");
                const item = list[idx];
                return e('div', {className:"glass"},
                    e('h1', {className:"text-xs font-black text-slate-400 uppercase mb-8"}, "國中數學觀念測驗 ("+(idx+1)+"/"+list.length+")"),
                    e('div', {className:"math-card", onClick:()=>setFlip(!flip)},
                        !flip ? e('h2', {className:"text-3xl font-black math-tex"}, item.w) : e('div', null, e('p', {className:"text-xl font-bold bg-white p-6 rounded-2xl shadow-sm math-tex"}, item.d))
                    ),
                    e('div', {className:"flex gap-4 mt-8"},
                        e('button', {onClick:next, className:"flex-grow py-4 bg-slate-900 text-white rounded-2xl font-black"}, "下一題"),
                        e('a', {href:'entry.html', className:"px-6 py-4 bg-white text-slate-400 rounded-2xl font-black border border-slate-200"}, "✕")
                    )
                );
            }
            ReactDOM.createRoot(document.getElementById('root')).render(e(App));
        })();
    </script>
</body>
</html>"""

    # 替換並寫入
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_template.replace("VOCAB_DATA_PLACEHOLDER", v_json).replace("IDIOM_DATA_PLACEHOLDER", i_json))
    
    with open("math.html", "w", encoding="utf-8") as f:
        f.write(math_template.replace("MATH_DATA_PLACEHOLDER", m_json))
    
    print("Build Success: Generated index.html (Pure) & math.html (Independent)")

if __name__ == "__main__":
    build_html()
