import json
import os

def build_html_v3():
    data_path = "vocab_data.js"
    output_path = "Vocab_Master_Tool.html"
    
    if not os.path.exists(data_path):
        print("Error: data not found.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        js_data = f.read()

    # 使用普通字串拼接，避開 f-string 的大括號轉義陷阱
    content = []
    content.append("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vocab Master - 英語詞彙大師</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background: #f1f5f9; }
        .glass { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); }
        .perspective-1000 { perspective: 1000px; }
        .transform-style-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
    <script>""")
    
    content.append(js_data)
    
    content.append("""</script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect, useCallback, useMemo } = React;
        const STORAGE_KEY = 'vocab_master_v1';
        
        const shuffle = (arr) => {
            const n = [...arr];
            for(let i=n.length-1; i>0; i--) {
                const j = Math.floor(Math.random()*(i+1));
                [n[i], n[j]] = [n[j], n[i]];
            }
            return n;
        };

        const App = () => {
            const [vocabList, setVocabList] = useState(() => {
                const s = localStorage.getItem(STORAGE_KEY);
                return s ? JSON.parse(s).vocabList : [];
            });
            const [totalInitial, setTotalInitial] = useState(() => {
                const s = localStorage.getItem(STORAGE_KEY);
                return s ? JSON.parse(s).totalInitial : 0;
            });
            const [stats, setStats] = useState({ again: 0, hard: 0, good: 0, easy: 0 });
            const [isFinished, setIsFinished] = useState(false);
            const [isSettingUp, setIsSettingUp] = useState(false);
            const [isFlipped, setIsFlipped] = useState(false);
            const [speechRate, setSpeechRate] = useState(1.0);
            
            // 篩選器
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
                setVocabList([]);
                setIsSettingUp(false);
                setIsFinished(false);
                localStorage.removeItem(STORAGE_KEY);
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
                if(vocabList.length > 0) {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify({ vocabList, totalInitial }));
                }
            }, [vocabList, totalInitial]);

            useEffect(() => {
                if(typeof lucide !== 'undefined') lucide.createIcons();
            });

            if(vocabList.length === 0 && !isSettingUp && !isFinished) {
                return (
                    <div className="flex flex-col items-center justify-center min-h-screen p-6">
                        <div className="glass max-w-sm w-full rounded-[40px] shadow-2xl p-10 text-center">
                            <div className="w-20 h-20 bg-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-xl shadow-indigo-100">
                                <i data-lucide="graduation-cap" className="text-white w-10 h-10"></i>
                            </div>
                            <h1 className="text-3xl font-black text-slate-800 mb-2">Vocab Master</h1>
                            <p className="text-slate-400 mb-10 text-xs font-bold uppercase tracking-widest">7,000+ Words Database</p>
                            <button onClick={() => setIsSettingUp(true)} className="w-full py-5 bg-indigo-600 text-white rounded-3xl font-black transition-all hover:bg-indigo-700 active:scale-95 shadow-lg">進入設定</button>
                        </div>
                    </div>
                );
            }

            if(isSettingUp) {
                return (
                    <div className="flex flex-col items-center justify-center min-h-screen p-4">
                        <div className="glass max-w-md w-full rounded-[32px] shadow-2xl p-8">
                            <h2 className="text-xl font-black text-slate-800 mb-6 text-center">抽籤篩選器</h2>
                            <div className="space-y-6">
                                <div>
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">Level 範圍</label>
                                    <div className="flex flex-wrap gap-2">
                                        {[1,2,3,4,5,6].map(l => (
                                            <button key={l} onClick={() => levels.includes(l) ? setLevels(levels.filter(x=>x!==l)) : setLevels([...levels, l])}
                                                className={`px-3 py-1.5 rounded-lg text-xs font-bold border-2 transition-all ${levels.includes(l)?'bg-indigo-600 border-indigo-600 text-white':'border-slate-100 text-slate-400'}`}>L{l}</button>
                                        ))}
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">首字母 (A-Z)</label>
                                        <select value={letter} onChange={e=>setLetter(e.target.value)} className="w-full bg-slate-50 rounded-xl p-2 text-sm font-bold border-none ring-1 ring-slate-200 focus:ring-indigo-500">
                                            {['All', ...'abcdefghijklmnopqrstuvwxyz'.split('')].map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-2">詞性篩選</label>
                                        <select value={posFilter} onChange={e=>setPosFilter(e.target.value)} className="w-full bg-slate-50 rounded-xl p-2 text-sm font-bold border-none ring-1 ring-slate-200 focus:ring-indigo-500">
                                            {allPOS.map(p => <option key={p} value={p}>{p}</option>)}
                                        </select>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between mb-2">
                                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">抽樣數量</label>
                                        <span className="text-sm font-black text-indigo-600">{count}</span>
                                    </div>
                                    <input type="range" min="5" max={Math.min(filteredCount, 200)} value={count} onChange={e=>setCount(parseInt(e.target.value))} className="w-full h-2 bg-slate-100 rounded-lg appearance-none accent-indigo-600" />
                                </div>
                                <div className="p-4 bg-indigo-50 rounded-2xl border border-indigo-100 flex justify-between items-center">
                                    <span className="text-xs font-bold text-indigo-400">符合條件總筆數</span>
                                    <span className="text-xl font-black text-indigo-600">{filteredCount}</span>
                                </div>
                                <button onClick={start} className="w-full py-4 bg-slate-800 text-white rounded-2xl font-black shadow-xl hover:bg-slate-900 transition-all">開始測試</button>
                                <button onClick={()=>setIsSettingUp(false)} className="w-full text-xs font-bold text-slate-400">取消</button>
                            </div>
                        </div>
                    </div>
                );
            }

            if(isFinished) {
                return (
                    <div className="flex flex-col items-center justify-center min-h-screen p-6">
                        <div className="glass max-w-sm w-full rounded-[40px] shadow-2xl p-10 text-center">
                            <i data-lucide="award" className="w-16 h-16 text-yellow-500 mx-auto mb-6"></i>
                            <h2 className="text-2xl font-black text-slate-800 mb-2">測試完成！</h2>
                            <div className="grid grid-cols-2 gap-2 my-8">
                                <div className="bg-red-50 p-3 rounded-2xl text-red-600"><p className="text-[8px] font-black uppercase">Again</p><p className="text-xl font-black">{stats.again}</p></div>
                                <div className="bg-orange-50 p-3 rounded-2xl text-orange-600"><p className="text-[8px] font-black uppercase">Hard</p><p className="text-xl font-black">{stats.hard}</p></div>
                                <div className="bg-blue-50 p-3 rounded-2xl text-blue-600"><p className="text-[8px] font-black uppercase">Good</p><p className="text-xl font-black">{stats.good}</p></div>
                                <div className="bg-green-50 p-3 rounded-2xl text-green-600"><p className="text-[8px] font-black uppercase">Easy</p><p className="text-xl font-black">{stats.easy}</p></div>
                            </div>
                            <button onClick={reset} className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-black shadow-lg">新測試</button>
                        </div>
                    </div>
                );
            }

            const current = vocabList[0];
            return (
                <div className="flex flex-col items-center min-h-screen p-4 overflow-hidden relative">
                    <div className="w-full max-w-md glass rounded-2xl shadow-lg p-4 mb-4 flex flex-col gap-3">
                        <div className="flex justify-between items-center text-[10px] font-black text-slate-400">
                            <div className="flex gap-1">
                                <span className="text-red-500 bg-red-50 px-1.5 rounded">{stats.again}</span>
                                <span className="text-orange-500 bg-orange-50 px-1.5 rounded">{stats.hard}</span>
                                <span className="text-blue-500 bg-blue-50 px-1.5 rounded">{stats.good}</span>
                                <span className="text-green-500 bg-green-50 px-1.5 rounded">{stats.easy}</span>
                            </div>
                            <span>{vocabList.length} / {totalInitial}</span>
                            <button onClick={reset} className="hover:text-red-500"><i data-lucide="rotate-ccw" className="w-3.5 h-3.5"></i></button>
                        </div>
                        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div className="bg-indigo-500 h-full transition-all" style={{width:`${((totalInitial-vocabList.length)/totalInitial)*100}%`}}></div>
                        </div>
                    </div>

                    <div className="w-full max-w-md flex-grow relative perspective-1000 mb-6">
                        <div onClick={()=>setIsFlipped(!isFlipped)} className={`relative w-full h-full transition-all duration-700 transform-style-3d cursor-pointer ${isFlipped?'rotate-y-180':''}`}>
                            {/* 正面 */}
                            <div className="absolute inset-0 backface-hidden bg-white rounded-[40px] shadow-2xl p-8 flex flex-col items-center justify-center border-8 border-white">
                                <div className="absolute top-6 right-6 flex gap-2">
                                    <button onClick={e=>{e.stopPropagation(); speak(current.w)}} className="p-2 bg-indigo-50 text-indigo-600 rounded-full"><i data-lucide="volume-2" className="w-5 h-5"></i></button>
                                </div>
                                <div className="w-full h-40 bg-slate-50 rounded-3xl mb-8 overflow-hidden relative flex items-center justify-center border border-slate-100">
                                    {!imgOk && <i data-lucide="image" className="w-8 h-8 text-slate-200"></i>}
                                    <img src={`https://loremflickr.com/400/300/${current.w.split(' ')[0]},nature?lock=${current.w.length}`} onLoad={()=>setImgOk(true)} className={`w-full h-full object-cover transition-opacity ${imgOk?'opacity-100':'opacity-0'}`} />
                                </div>
                                <h2 className="text-4xl font-black text-slate-800 text-center">{current.w}</h2>
                                <p className="mt-8 text-[10px] font-black text-slate-300 uppercase tracking-[0.4em] animate-pulse">Tap to Reveal</p>
                            </div>
                            {/* 背面 */}
                            <div className="absolute inset-0 backface-hidden bg-white rounded-[40px] shadow-2xl p-8 flex flex-col rotate-y-180 border-8 border-white">
                                <div className="flex justify-between items-center mb-4">
                                    <div className="flex gap-2">
                                        <span className="px-2 py-0.5 bg-indigo-600 text-white text-[9px] font-black rounded uppercase">L{current.l}</span>
                                        <span className="px-2 py-0.5 bg-slate-100 text-slate-500 text-[9px] font-black rounded uppercase">{current.p}</span>
                                    </div>
                                    <button onClick={e=>{e.stopPropagation(); speak(current.w)}} className="p-2 bg-indigo-50 text-indigo-600 rounded-full"><i data-lucide="volume-2" className="w-4 h-4"></i></button>
                                </div>
                                <h2 className="text-2xl font-black text-indigo-600 mb-6">{current.w}</h2>
                                <div className="flex-grow overflow-y-auto custom-scrollbar pr-2 space-y-3">
                                    <div className="text-[15px] font-bold text-slate-700 leading-relaxed border-l-4 border-indigo-200 pl-3">{current.d}</div>
                                    {current.i && <div className="text-[13px] text-slate-500 font-mono pl-3">{current.i}</div>}
                                    {current.t && <div className="text-[13px] text-slate-600 bg-slate-50 p-2 rounded-lg italic">{current.t}</div>}
                                    {current.c && <div className="text-[13px] text-indigo-500 font-bold border-t border-slate-50 pt-2">{current.c}</div>}
                                    {current.x && <div className="text-[13px] text-slate-700 bg-indigo-50/30 p-3 rounded-xl border border-indigo-50">{current.x}</div>}
                                </div>
                                <div className="grid grid-cols-4 gap-2 mt-6">
                                    <button onClick={e=>{e.stopPropagation(); handleSRS('again')}} className="py-3 bg-red-50 text-red-600 rounded-2xl text-[9px] font-black hover:bg-red-100">AGAIN</button>
                                    <button onClick={e=>{e.stopPropagation(); handleSRS('hard')}} className="py-3 bg-orange-50 text-orange-600 rounded-2xl text-[9px] font-black hover:bg-orange-100">HARD</button>
                                    <button onClick={e=>{e.stopPropagation(); handleSRS('good')}} className="py-3 bg-blue-50 text-blue-600 rounded-2xl text-[9px] font-black hover:bg-blue-100">GOOD</button>
                                    <button onClick={e=>{e.stopPropagation(); handleSRS('easy')}} className="py-3 bg-green-50 text-green-600 rounded-2xl text-[9px] font-black hover:bg-green-100">EASY</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="w-full max-w-md flex items-center gap-4 py-2 shrink-0">
                        <i data-lucide="volume-1" className="w-4 h-4 text-indigo-400"></i>
                        <input type="range" min="0.5" max="2.0" step="0.1" value={speechRate} onChange={e=>setSpeechRate(parseFloat(e.target.value))} className="flex-grow h-1 bg-white rounded-full appearance-none accent-indigo-600" />
                        <span className="text-[10px] font-black text-indigo-600">{speechRate.toFixed(1)}x</span>
                    </div>
                </div>
            );
        };
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>""")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(content))
    
    print(f"Vocab Master Tool is ready: {output_path}")

if __name__ == "__main__":
    build_html_v3()
