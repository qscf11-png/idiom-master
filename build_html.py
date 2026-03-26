import json
import os

def build_html_ultimate():
    data_path = "vocab_data.js"
    output_path = "index.html"
    
    if not os.path.exists(data_path):
        print("Error: data not found.")
        return

    # 讀取並純化 JSON 數據
    with open(data_path, "r", encoding="utf-8") as f:
        raw_js = f.read()
        json_str = raw_js.replace("const VOCAB_DB = ", "").strip()
        if json_str.endswith(";"):
            json_str = json_str[:-1]

    content = []
    content.append("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>英語詞彙大師 Vocab Master</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lucide/0.263.0/umd/lucide.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background: #f1f5f9; margin: 0; padding: 0; }
        .glass { background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.4); }
        .perspective-1000 { perspective: 1000px; }
        .transform-style-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <!-- 數據隔離：將 1.2MB JSON 放入非執行腳本標籤，防止 JS 解析器崩潰 -->
    <script id="vocab-data" type="application/json">""")
    
    content.append(json_str)
    
    content.append("""</script>

    <script type="text/javascript">
        (function() {
            try {
                const { useState, useEffect, useCallback, useMemo } = React;
                const e = React.createElement;
                const STORAGE_KEY = 'vocab_master_v1';
                
                // 從隱藏標籤中解析數據，這不會產生語法錯誤
                const rawData = document.getElementById('vocab-data').textContent;
                const VOCAB_DB = JSON.parse(rawData);

                const shuffle = (arr) => {
                    const n = [...arr];
                    for(let i = n.length - 1; i > 0; i--) {
                        const j = Math.floor(Math.random() * (i + 1));
                        [n[i], n[j]] = [n[j], n[i]];
                    }
                    return n;
                };

                const App = () => {
                    const [vocabList, setVocabList] = useState(() => {
                        try {
                            const s = localStorage.getItem(STORAGE_KEY);
                            return s ? JSON.parse(s).vocabList : [];
                        } catch(err) { return []; }
                    });
                    const [totalInitial, setTotalInitial] = useState(() => {
                        try {
                            const s = localStorage.getItem(STORAGE_KEY);
                            return s ? JSON.parse(s).totalInitial : 0;
                        } catch(err) { return 0; }
                    });
                    const [stats, setStats] = useState({ again: 0, hard: 0, good: 0, easy: 0 });
                    const [isFinished, setIsFinished] = useState(false);
                    const [isSettingUp, setIsSettingUp] = useState(false);
                    const [isFlipped, setIsFlipped] = useState(false);
                    const [speechRate, setSpeechRate] = useState(1.0);
                    const [levels, setLevels] = useState([1,2,3,4,5,6]);
                    const [letter, setLetter] = useState('All');
                    const [posFilter, setPosFilter] = useState('All');
                    const [count, setCount] = useState(50);
                    const [imgOk, setImgOk] = useState(false);

                    const allPOS = useMemo(() => {
                        const s = new Set(['All']);
                        VOCAB_DB.forEach(x => { if(x.p) s.add(x.p.split('/')[0].trim()); });
                        return Array.from(s).sort();
                    }, []);

                    const filteredCount = useMemo(() => {
                        return VOCAB_DB.filter(x => {
                            const lOk = levels.includes(x.l);
                            const aOk = letter === 'All' || x.w.toLowerCase().startsWith(letter.toLowerCase());
                            const pOk = posFilter === 'All' || (x.p && x.p.includes(posFilter));
                            return lOk && aOk && pOk;
                        }).length;
                    }, [levels, letter, posFilter]);

                    const start = () => {
                        const f = VOCAB_DB.filter(x => {
                            const lOk = levels.includes(x.l);
                            const aOk = letter === 'All' || x.w.toLowerCase().startsWith(letter.toLowerCase());
                            const pOk = posFilter === 'All' || (x.p && x.p.includes(posFilter));
                            return lOk && aOk && pOk;
                        });
                        if(f.length === 0) return alert("沒有符合條件的單字");
                        const sampled = shuffle(f).slice(0, Math.min(count, f.length));
                        setVocabList(sampled);
                        setTotalInitial(sampled.length);
                        setStats({ again: 0, hard: 0, good: 0, easy: 0 });
                        setIsSettingUp(false);
                        setIsFinished(false);
                    };

                    const reset = () => {
                        if(confirm("確定要重新開始嗎？內容進度將被清除。")) {
                            setVocabList([]);
                            localStorage.removeItem(STORAGE_KEY);
                            setIsSettingUp(false);
                            setIsFinished(false);
                        }
                    };

                    const handleSRS = (type) => {
                        setStats(s => ({ ...s, [type]: s[type]+1 }));
                        const rest = vocabList.slice(1);
                        const curr = vocabList[0];
                        let next = [];
                        if(type==='again') next = rest.length > 0 ? [rest[0], curr, ...rest.slice(1)] : [curr];
                        else if(type==='hard') next = rest.length >= 4 ? [...rest.slice(0,4), curr, ...rest.slice(4)] : [...rest, curr];
                        else if(type==='good') next = [...rest, curr];
                        else next = rest;

                        if(next.length === 0) setIsFinished(true);
                        setVocabList(next);
                        setIsFlipped(false);
                        setImgOk(false);
                    };

                    const speak = (t) => {
                        window.speechSynthesis.cancel();
                        const u = new SpeechSynthesisUtterance(t);
                        u.lang = 'en-US';
                        u.rate = speechRate;
                        window.speechSynthesis.speak(u);
                    };

                    useEffect(() => {
                        if(vocabList.length > 0) localStorage.setItem(STORAGE_KEY, JSON.stringify({ vocabList, totalInitial }));
                    }, [vocabList, totalInitial]);

                    useEffect(() => { if(window.lucide) window.lucide.createIcons(); });

                    if(vocabList.length === 0 && !isSettingUp && !isFinished) {
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            e('div', { className: "glass max-w-sm w-full rounded-[40px] shadow-2xl p-10 text-center shadow-indigo-100/50" },
                                e('div', { className: "w-20 h-20 bg-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-xl" },
                                    e('i', { 'data-lucide': 'graduation-cap', className: "text-white w-10 h-10" })
                                ),
                                e('h1', { className: "text-3xl font-black text-slate-800 mb-2" }, "Vocab Master"),
                                e('p', { className: "text-slate-400 mb-10 text-xs font-bold uppercase tracking-widest" }, "7,000+ Database Ready"),
                                e('button', { onClick: () => setIsSettingUp(true), className: "w-full py-5 bg-indigo-600 text-white rounded-3xl font-black shadow-lg" }, "進行設定")
                            )
                        );
                    }

                    if(isSettingUp) {
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-4" },
                            e('div', { className: "glass max-w-md w-full rounded-[32px] shadow-2xl p-8" },
                                e('h2', { className: "text-xl font-black text-slate-800 mb-6 text-center" }, "抽籤篩選器"),
                                e('div', { className: "space-y-6" },
                                    e('div', null,
                                        e('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "Level"),
                                        e('div', { className: "flex flex-wrap gap-2" },
                                            [1,2,3,4,5,6].map(l => e('button', {
                                                key: l,
                                                onClick: () => levels.includes(l) ? setLevels(levels.filter(x=>x!==l)) : setLevels([...levels, l]),
                                                className: `px-3 py-1.5 rounded-lg text-xs font-bold border-2 ${levels.includes(l)?'bg-indigo-600 border-indigo-600 text-white':'border-slate-100 text-slate-400'}`
                                            }, `L${l}`))
                                        )
                                    ),
                                    e('div', { className: "grid grid-cols-2 gap-4" },
                                        e('div', null,
                                            e('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "首字母"),
                                            e('select', { value: letter, onChange: e=>setLetter(e.target.value), className: "w-full bg-slate-50 rounded-xl p-2 text-sm border-none ring-1 ring-slate-200" },
                                                ['All', ...'abcdefghijklmnopqrstuvwxyz'.split('')].map(c => e('option', { key: c, value: c }, c.toUpperCase()))
                                            )
                                        ),
                                        e('div', null,
                                            e('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "詞性"),
                                            e('select', { value: posFilter, onChange: e=>setPosFilter(e.target.value), className: "w-full bg-slate-50 rounded-xl p-2 text-sm border-none ring-1 ring-slate-200" },
                                                allPOS.map(p => e('option', { key: p, value: p }, p))
                                            )
                                        )
                                    ),
                                    e('div', null,
                                        e('div', { className: "flex justify-between mb-2" },
                                            e('label', { className: "text-[10px] font-black text-slate-400 uppercase" }, "抽樣數量"),
                                            e('span', { className: "text-sm font-black text-indigo-600" }, count)
                                        ),
                                        e('input', { type: 'range', min: '5', max: Math.min(filteredCount, 200), value: count, onChange: e=>setCount(parseInt(e.target.value)), className: "w-full h-1 bg-slate-100 rounded-full appearance-none accent-indigo-600" })
                                    ),
                                    e('button', { onClick: start, className: "w-full py-4 bg-slate-800 text-white rounded-2xl font-black shadow-xl" }, "開始學習"),
                                    e('button', { onClick: () => setIsSettingUp(false), className: "w-full text-xs font-bold text-slate-400 py-2" }, "取消")
                                )
                            )
                        );
                    }

                    if(isFinished) {
                        return e('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                            e('div', { className: "glass max-w-sm w-full rounded-[40px] shadow-2xl p-10 text-center" },
                                e('i', { 'data-lucide': 'award', className: "w-16 h-16 text-yellow-500 mx-auto mb-6" }),
                                e('h2', { className: "text-2xl font-black text-slate-800 mb-6" }, "測試完成！"),
                                e('button', { onClick: () => { setVocabList([]); setIsFinished(false); setIsSettingUp(false); }, className: "w-full py-4 bg-indigo-600 text-white rounded-2xl font-black shadow-lg" }, "新學習")
                            )
                        );
                    }

                    const current = vocabList[0];
                    const progress = ((totalInitial - vocabList.length) / totalInitial) * 100;

                    return e('div', { className: "flex flex-col items-center min-h-screen p-4 overflow-hidden" },
                        e('div', { className: "w-full max-w-md glass rounded-2xl shadow-lg p-4 mb-4 flex flex-col gap-3" },
                            e('div', { className: "flex justify-between items-center text-[10px] font-black text-slate-400" },
                                e('div', { className: "flex gap-1" },
                                    e('span', { className: "text-red-500 bg-red-50 px-1.5 rounded" }, stats.again),
                                    e('span', { className: "text-orange-500 bg-orange-50 px-1.5 rounded" }, stats.hard),
                                    e('span', { className: "text-blue-500 bg-blue-50 px-1.5 rounded" }, stats.good),
                                    e('span', { className: "text-green-500 bg-green-50 px-1.5 rounded" }, stats.easy)
                                ),
                                e('span', null, `${vocabList.length} / ${totalInitial}`),
                                e('button', { onClick: reset }, e('i', { 'data-lucide': 'rotate-ccw', className: "w-3.5 h-3.5" }))
                            ),
                            e('div', { className: "w-full h-1.5 bg-slate-100 rounded-full overflow-hidden" },
                                e('div', { className: "bg-indigo-500 h-full transition-all", style: { width: `${progress}%` } })
                            )
                        ),
                        e('div', { className: "w-full max-w-md flex-grow relative perspective-1000 mb-6" },
                            e('div', { 
                                onClick: () => setIsFlipped(!isFlipped),
                                className: `relative w-full h-full transition-all duration-700 transform-style-3d cursor-pointer ${isFlipped?'rotate-y-180':''}`
                            },
                                e('div', { className: "absolute inset-0 backface-hidden bg-white rounded-[40px] shadow-2xl p-8 flex flex-col items-center justify-center border-8 border-white" },
                                    e('button', { onClick: es => { es.stopPropagation(); speak(current.w); }, className: "absolute top-6 right-6 p-2 bg-indigo-50 text-indigo-600 rounded-full" }, e('i', { 'data-lucide': 'volume-2', className: "w-5 h-5" })),
                                    e('div', { className: "w-full h-40 bg-slate-50 rounded-3xl mb-8 overflow-hidden relative flex items-center justify-center border border-slate-100" },
                                        !imgOk && e('i', { 'data-lucide': 'image', className: "w-8 h-8 text-slate-200" }),
                                        e('img', { 
                                            src: `https://loremflickr.com/400/300/${current.w.split(' ')[0]},nature?lock=${current.w.length}`,
                                            onLoad: () => setImgOk(true),
                                            className: `w-full h-full object-cover transition-opacity ${imgOk?'opacity-100':'opacity-0'}`
                                        })
                                    ),
                                    e('h2', { className: "text-4xl font-black text-slate-800 text-center" }, current.w)
                                ),
                                e('div', { className: "absolute inset-0 backface-hidden bg-white rounded-[40px] shadow-2xl p-8 flex flex-col rotate-y-180 border-8 border-white" },
                                    e('div', { className: "flex justify-between items-center mb-4" },
                                        e('div', { className: "flex gap-2" },
                                            e('span', { className: "px-2 py-0.5 bg-indigo-600 text-white text-[9px] font-black rounded" }, `L${current.l}`),
                                            e('span', { className: "px-2 py-0.5 bg-slate-100 text-slate-500 text-[9px] font-black rounded" }, current.p)
                                        ),
                                        e('button', { onClick: es => { es.stopPropagation(); speak(current.w); }, className: "p-2 bg-indigo-50 text-indigo-600 rounded-full" }, e('i', { 'data-lucide': 'volume-2', className: "w-4 h-4" }))
                                    ),
                                    e('h2', { className: "text-2xl font-black text-indigo-600 mb-4" }, current.w),
                                    e('div', { className: "flex-grow overflow-y-auto custom-scrollbar pr-2 space-y-3" },
                                        e('div', { className: "text-[15px] font-bold text-slate-700 border-l-4 border-indigo-200 pl-3" }, current.d),
                                        current.i && e('div', { className: "text-[13px] text-slate-500 pl-3" }, current.i),
                                        current.t && e('div', { className: "text-[12px] text-slate-400 italic" }, current.t),
                                        current.x && e('div', { className: "text-[13px] text-slate-700 bg-indigo-50/20 p-3 rounded-xl" }, current.x)
                                    ),
                                    e('div', { className: "grid grid-cols-4 gap-2 mt-4" },
                                        ['again', 'hard', 'good', 'easy'].map(t => e('button', { 
                                            key: t, 
                                            onClick: es => { es.stopPropagation(); handleSRS(t); },
                                            className: `py-3 rounded-2xl text-[9px] font-black ${t==='again'?'bg-red-50 text-red-600':t==='hard'?'bg-orange-50 text-orange-600':t==='good'?'bg-blue-50 text-blue-600':'bg-green-50 text-green-600'}`
                                        }, t.toUpperCase()))
                                    )
                                )
                            )
                        )
                    );
                };
                
                const root = ReactDOM.createRoot(document.getElementById('root'));
                root.render(e(App));
            } catch(e) { console.error("Mount Error:", e); }
        })();
    </script>
</body>
</html>""")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(content))
    
    print(f"Vocab Master Tool Build (Physical Isolation) Success.")

if __name__ == "__main__":
    build_html_ultimate()
