import json
import os

def build_html():
    data_path = "vocab_data.js"
    output_path = "index.html"
    
    if not os.path.exists(data_path):
        print("Error: data not found.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        raw_js = f.read()
        json_str = raw_js.replace("const VOCAB_DB = ", "").strip()
        if json_str.endswith(";"):
            json_str = json_str[:-1]

    content = []
    content.append(r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>英語詞彙大師 Vocab Master</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background: linear-gradient(135deg, #e0e7ff 0%, #f1f5f9 50%, #dbeafe 100%); margin: 0; padding: 0; min-height: 100vh; }
        .glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.5); }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        .info-block { border-left: 4px solid; padding: 8px 12px; border-radius: 0 8px 8px 0; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script id="vocab-data" type="application/json">""")
    
    content.append(json_str)
    
    content.append(r"""</script>

    <script type="text/javascript">
        (function() {
            var h = React.createElement;
            var useState = React.useState;
            var useEffect = React.useEffect;
            var useMemo = React.useMemo;
            
            var rawData = document.getElementById('vocab-data').textContent;
            var VOCAB_DB = JSON.parse(rawData);

            function shuffle(arr) {
                var n = arr.slice();
                for(var i = n.length - 1; i > 0; i--) {
                    var j = Math.floor(Math.random() * (i + 1));
                    var tmp = n[i]; n[i] = n[j]; n[j] = tmp;
                }
                return n;
            }

            function speak(text, rate) {
                window.speechSynthesis.cancel();
                var u = new SpeechSynthesisUtterance(text);
                u.lang = 'en-US';
                u.rate = rate || 1.0;
                window.speechSynthesis.speak(u);
            }

            function App() {
                var _vl = useState([]);
                var vocabList = _vl[0], setVocabList = _vl[1];
                var _ti = useState(0);
                var totalInitial = _ti[0], setTotalInitial = _ti[1];
                var _st = useState({ again: 0, hard: 0, good: 0, easy: 0 });
                var stats = _st[0], setStats = _st[1];
                var _fin = useState(false);
                var isFinished = _fin[0], setIsFinished = _fin[1];
                var _setup = useState(false);
                var isSettingUp = _setup[0], setIsSettingUp = _setup[1];
                var _flip = useState(false);
                var isFlipped = _flip[0], setIsFlipped = _flip[1];
                var _rate = useState(1.0);
                var speechRate = _rate[0], setSpeechRate = _rate[1];
                var _lev = useState([1,2,3,4,5,6]);
                var levels = _lev[0], setLevels = _lev[1];
                var _let = useState('All');
                var letter = _let[0], setLetter = _let[1];
                var _pos = useState('All');
                var posFilter = _pos[0], setPosFilter = _pos[1];
                var _cnt = useState(50);
                var count = _cnt[0], setCount = _cnt[1];
                var _mode = useState('en2zh');
                var quizMode = _mode[0], setQuizMode = _mode[1];

                var allPOS = useMemo(function() {
                    var s = new Set(['All']);
                    VOCAB_DB.forEach(function(x) { if(x.p) s.add(x.p.split('/')[0].trim()); });
                    return Array.from(s).sort();
                }, []);

                var filteredCount = useMemo(function() {
                    return VOCAB_DB.filter(function(x) {
                        return (levels.indexOf(x.l) !== -1) &&
                               (letter === 'All' || x.w.toLowerCase().charAt(0) === letter.toLowerCase()) &&
                               (posFilter === 'All' || (x.p && x.p.indexOf(posFilter) !== -1));
                    }).length;
                }, [levels, letter, posFilter]);

                function startQuiz() {
                    var f = VOCAB_DB.filter(function(x) {
                        return (levels.indexOf(x.l) !== -1) &&
                               (letter === 'All' || x.w.toLowerCase().charAt(0) === letter.toLowerCase()) &&
                               (posFilter === 'All' || (x.p && x.p.indexOf(posFilter) !== -1));
                    });
                    if(f.length === 0) { alert("沒有符合條件的單字"); return; }
                    var sampled = shuffle(f).slice(0, Math.min(count, f.length));
                    setVocabList(sampled);
                    setTotalInitial(sampled.length);
                    setStats({ again: 0, hard: 0, good: 0, easy: 0 });
                    setIsSettingUp(false);
                    setIsFinished(false);
                    setIsFlipped(false);
                }

                function resetAll() {
                    if(confirm("確定要重新開始嗎？")) {
                        setVocabList([]);
                        setIsSettingUp(false);
                        setIsFinished(false);
                        setIsFlipped(false);
                    }
                }

                function handleSRS(type) {
                    setStats(function(s) {
                        var n = {}; for(var k in s) n[k] = s[k];
                        n[type] = n[type] + 1;
                        return n;
                    });
                    var rest = vocabList.slice(1);
                    var curr = vocabList[0];
                    var next;
                    if(type === 'again') next = rest.length > 0 ? [rest[0], curr].concat(rest.slice(1)) : [curr];
                    else if(type === 'hard') next = rest.length >= 4 ? rest.slice(0,4).concat([curr]).concat(rest.slice(4)) : rest.concat([curr]);
                    else if(type === 'good') next = rest.concat([curr]);
                    else next = rest;
                    if(next.length === 0) setIsFinished(true);
                    setVocabList(next);
                    setIsFlipped(false);
                }

                // ==================== 首頁 ====================
                if(vocabList.length === 0 && !isSettingUp && !isFinished) {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl shadow-2xl p-10 text-center" },
                            h('div', { className: "w-20 h-20 bg-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-xl text-white text-3xl font-black" }, "V"),
                            h('h1', { className: "text-3xl font-black text-slate-800 mb-2" }, "Vocab Master"),
                            h('p', { className: "text-slate-400 mb-10 text-xs font-bold uppercase tracking-widest" }, VOCAB_DB.length + " Words"),
                            h('button', { onClick: function() { setIsSettingUp(true); }, className: "w-full py-5 bg-indigo-600 text-white rounded-2xl font-black text-lg shadow-lg hover:bg-indigo-700 transition-all" }, "進入設定")
                        )
                    );
                }

                // ==================== 設定頁面 ====================
                if(isSettingUp) {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-4" },
                        h('div', { className: "glass max-w-md w-full rounded-3xl shadow-2xl p-8" },
                            h('h2', { className: "text-xl font-black text-slate-800 mb-6 text-center" }, "抽籤篩選器"),
                            h('div', { className: "space-y-5" },
                                // 測驗模式
                                h('div', null,
                                    h('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "測驗模式"),
                                    h('div', { className: "flex gap-2" },
                                        h('button', { onClick: function() { setQuizMode('en2zh'); }, className: "flex-1 py-2.5 rounded-xl text-sm font-bold border-2 transition-all " + (quizMode === 'en2zh' ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-200 text-slate-400') }, "英翻中"),
                                        h('button', { onClick: function() { setQuizMode('zh2en'); }, className: "flex-1 py-2.5 rounded-xl text-sm font-bold border-2 transition-all " + (quizMode === 'zh2en' ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-200 text-slate-400') }, "中翻英")
                                    )
                                ),
                                // Level
                                h('div', null,
                                    h('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "Level 範圍"),
                                    h('div', { className: "flex flex-wrap gap-2" },
                                        [1,2,3,4,5,6].map(function(l) { return h('button', {
                                            key: l,
                                            onClick: function() { levels.indexOf(l) !== -1 ? setLevels(levels.filter(function(x){return x!==l;})) : setLevels(levels.concat([l])); },
                                            className: "px-4 py-2 rounded-lg text-sm font-bold border-2 transition-all " + (levels.indexOf(l) !== -1 ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-200 text-slate-400')
                                        }, "L" + l); })
                                    )
                                ),
                                h('div', { className: "grid grid-cols-2 gap-4" },
                                    h('div', null,
                                        h('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "首字母"),
                                        h('select', { value: letter, onChange: function(ev) { setLetter(ev.target.value); }, className: "w-full bg-white rounded-xl p-2.5 text-sm border ring-0 border-slate-200" },
                                            ['All'].concat('abcdefghijklmnopqrstuvwxyz'.split('')).map(function(c) { return h('option', { key: c, value: c }, c.toUpperCase()); })
                                        )
                                    ),
                                    h('div', null,
                                        h('label', { className: "text-[10px] font-black text-slate-400 uppercase block mb-2" }, "詞性篩選"),
                                        h('select', { value: posFilter, onChange: function(ev) { setPosFilter(ev.target.value); }, className: "w-full bg-white rounded-xl p-2.5 text-sm border ring-0 border-slate-200" },
                                            allPOS.map(function(p) { return h('option', { key: p, value: p }, p); })
                                        )
                                    )
                                ),
                                h('div', null,
                                    h('div', { className: "flex justify-between mb-2" },
                                        h('label', { className: "text-[10px] font-black text-slate-400 uppercase" }, "抽樣數量"),
                                        h('span', { className: "text-lg font-black text-indigo-600" }, count)
                                    ),
                                    h('input', { type: 'range', min: '5', max: Math.min(filteredCount, 200), value: count, onChange: function(ev) { setCount(parseInt(ev.target.value)); }, className: "w-full h-2 bg-slate-200 rounded-lg appearance-none accent-indigo-600" })
                                ),
                                h('div', { className: "p-4 bg-indigo-50 rounded-2xl border border-indigo-100 flex justify-between items-center" },
                                    h('span', { className: "text-sm font-bold text-indigo-400" }, "符合條件的單字"),
                                    h('span', { className: "text-2xl font-black text-indigo-600" }, filteredCount)
                                ),
                                h('button', { onClick: startQuiz, className: "w-full py-4 bg-slate-800 text-white rounded-2xl font-black text-lg shadow-xl hover:bg-slate-900 transition-all" }, "開始學習"),
                                h('button', { onClick: function() { setIsSettingUp(false); }, className: "w-full text-sm font-bold text-slate-400 py-2" }, "取消")
                            )
                        )
                    );
                }

                // ==================== 完成頁 ====================
                if(isFinished) {
                    return h('div', { className: "flex flex-col items-center justify-center min-h-screen p-6" },
                        h('div', { className: "glass max-w-sm w-full rounded-3xl shadow-2xl p-10 text-center" },
                            h('div', { className: "text-6xl mb-4" }, "\uD83C\uDFC6"),
                            h('h2', { className: "text-2xl font-black text-slate-800 mb-4" }, "測試完成！"),
                            h('div', { className: "grid grid-cols-2 gap-3 my-6" },
                                h('div', { className: "bg-red-50 p-4 rounded-2xl" }, h('p', { className: "text-[9px] font-black text-red-400 uppercase" }, "Again"), h('p', { className: "text-2xl font-black text-red-600" }, stats.again)),
                                h('div', { className: "bg-orange-50 p-4 rounded-2xl" }, h('p', { className: "text-[9px] font-black text-orange-400 uppercase" }, "Hard"), h('p', { className: "text-2xl font-black text-orange-600" }, stats.hard)),
                                h('div', { className: "bg-blue-50 p-4 rounded-2xl" }, h('p', { className: "text-[9px] font-black text-blue-400 uppercase" }, "Good"), h('p', { className: "text-2xl font-black text-blue-600" }, stats.good)),
                                h('div', { className: "bg-green-50 p-4 rounded-2xl" }, h('p', { className: "text-[9px] font-black text-green-400 uppercase" }, "Easy"), h('p', { className: "text-2xl font-black text-green-600" }, stats.easy))
                            ),
                            h('button', { onClick: function() { setVocabList([]); setIsFinished(false); setIsSettingUp(false); }, className: "w-full py-4 bg-indigo-600 text-white rounded-2xl font-black text-lg shadow-lg" }, "新學習")
                        )
                    );
                }

                // ==================== 學習卡片頁（不使用 3D 翻轉，改用簡單切換） ====================
                var current = vocabList[0];
                var progress = ((totalInitial - vocabList.length) / totalInitial) * 100;
                var isCn2En = quizMode === 'zh2en';

                // 進度條
                var progressBar = h('div', { className: "w-full max-w-lg glass rounded-2xl shadow-lg p-4 mb-4" },
                    h('div', { className: "flex justify-between items-center text-xs font-black text-slate-500 mb-2" },
                        h('div', { className: "flex gap-2" },
                            h('span', { className: "text-red-500 bg-red-50 px-2 py-0.5 rounded-md" }, "A:" + stats.again),
                            h('span', { className: "text-orange-500 bg-orange-50 px-2 py-0.5 rounded-md" }, "H:" + stats.hard),
                            h('span', { className: "text-blue-500 bg-blue-50 px-2 py-0.5 rounded-md" }, "G:" + stats.good),
                            h('span', { className: "text-green-500 bg-green-50 px-2 py-0.5 rounded-md" }, "E:" + stats.easy)
                        ),
                        h('span', { className: "text-sm font-black text-indigo-600" }, vocabList.length + " / " + totalInitial),
                        h('button', { onClick: resetAll, className: "text-slate-400 hover:text-red-500 text-lg ml-2" }, "\u21BA")
                    ),
                    h('div', { className: "w-full h-2 bg-slate-100 rounded-full overflow-hidden" },
                        h('div', { className: "bg-indigo-500 h-full rounded-full transition-all duration-500", style: { width: progress + "%" } })
                    )
                );

                if(!isFlipped) {
                    // ===== 正面（題目面） =====
                    var questionContent;
                    if(isCn2En) {
                        questionContent = h('div', { className: "glass max-w-lg w-full rounded-3xl shadow-2xl p-8 text-center cursor-pointer hover:shadow-indigo-200/50 transition-all", onClick: function() { setIsFlipped(true); } },
                            h('div', { className: "flex justify-between items-center mb-6" },
                                h('span', { className: "px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-black rounded-lg" }, "中翻英"),
                                h('div', { className: "flex gap-2" },
                                    h('span', { className: "px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-black rounded-lg" }, "L" + current.l),
                                    current.p && h('span', { className: "px-3 py-1 bg-slate-100 text-slate-600 text-xs font-black rounded-lg" }, current.p)
                                )
                            ),
                            h('p', { className: "text-sm font-bold text-slate-400 mb-4 uppercase tracking-widest" }, "這個英文單字是？"),
                            h('h2', { className: "text-3xl font-black text-slate-800 mb-6 leading-relaxed" }, current.d),
                            current.c && h('p', { className: "text-base text-indigo-500 font-bold mb-4" }, "搭配提示：" + current.c),
                            h('p', { className: "text-xs font-black text-slate-300 uppercase tracking-[0.3em] mt-8 animate-pulse" }, "👆 點擊查看答案")
                        );
                    } else {
                        questionContent = h('div', { className: "glass max-w-lg w-full rounded-3xl shadow-2xl p-8 text-center cursor-pointer hover:shadow-indigo-200/50 transition-all", onClick: function() { setIsFlipped(true); } },
                            h('div', { className: "flex justify-between items-center mb-6" },
                                h('span', { className: "px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-black rounded-lg" }, "英翻中"),
                                h('div', { className: "flex gap-2" },
                                    h('span', { className: "px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-black rounded-lg" }, "L" + current.l),
                                    current.p && h('span', { className: "px-3 py-1 bg-slate-100 text-slate-600 text-xs font-black rounded-lg" }, current.p)
                                )
                            ),
                            h('button', { onClick: function(ev) { ev.stopPropagation(); speak(current.w, speechRate); }, className: "mx-auto mb-6 p-3 bg-indigo-50 text-indigo-600 rounded-full hover:bg-indigo-100 transition-all text-xl block" }, "\uD83D\uDD0A"),
                            h('h2', { className: "text-5xl font-black text-slate-800 mb-3" }, current.w),
                            current.i && h('p', { className: "text-lg text-slate-400 font-mono mb-4" }, current.i),
                            h('p', { className: "text-xs font-black text-slate-300 uppercase tracking-[0.3em] mt-8 animate-pulse" }, "👆 點擊查看釋義")
                        );
                    }
                    return h('div', { className: "flex flex-col items-center min-h-screen p-4" },
                        progressBar,
                        questionContent,
                        h('div', { className: "w-full max-w-lg flex items-center gap-3 mt-4 py-2" },
                            h('span', { className: "text-sm" }, "\uD83D\uDD08"),
                            h('input', { type: 'range', min: '0.5', max: '2.0', step: '0.1', value: speechRate, onChange: function(ev) { setSpeechRate(parseFloat(ev.target.value)); }, className: "flex-grow h-1 bg-white rounded-full appearance-none accent-indigo-600" }),
                            h('span', { className: "text-xs font-black text-indigo-600 w-8" }, speechRate.toFixed(1) + "x")
                        )
                    );
                } else {
                    // ===== 背面（答案面 + 完整資訊） =====
                    return h('div', { className: "flex flex-col items-center min-h-screen p-4" },
                        progressBar,
                        h('div', { className: "glass max-w-lg w-full rounded-3xl shadow-2xl p-6" },
                            // 標題區
                            h('div', { className: "flex justify-between items-center mb-4" },
                                h('div', { className: "flex gap-2 items-center" },
                                    h('span', { className: "px-3 py-1 bg-indigo-600 text-white text-xs font-black rounded-lg" }, "L" + current.l),
                                    current.p && h('span', { className: "px-3 py-1 bg-slate-200 text-slate-700 text-xs font-black rounded-lg" }, current.p)
                                ),
                                h('button', { onClick: function() { speak(current.w, speechRate); }, className: "p-2 bg-indigo-50 text-indigo-600 rounded-full hover:bg-indigo-100 text-xl" }, "\uD83D\uDD0A")
                            ),
                            // 單字與音標
                            h('h2', { className: "text-3xl font-black text-indigo-600 mb-1" }, current.w),
                            current.i && h('p', { className: "text-sm text-slate-500 font-mono mb-4" }, current.i),
                            // 分隔線
                            h('hr', { className: "border-slate-100 mb-4" }),
                            // 解釋
                            h('div', { className: "info-block bg-indigo-50", style: { borderColor: '#6366f1' } },
                                h('p', { className: "text-[10px] font-black text-indigo-500 uppercase mb-1" }, "解釋 Definition"),
                                h('p', { className: "text-base font-bold text-slate-800" }, current.d)
                            ),
                            // 搭配字
                            current.c && h('div', { className: "info-block bg-amber-50", style: { borderColor: '#f59e0b' } },
                                h('p', { className: "text-[10px] font-black text-amber-600 uppercase mb-1" }, "搭配字 Collocations"),
                                h('p', { className: "text-sm font-bold text-slate-700" }, current.c)
                            ),
                            // 例句
                            current.x && h('div', { className: "info-block bg-blue-50", style: { borderColor: '#3b82f6' } },
                                h('p', { className: "text-[10px] font-black text-blue-500 uppercase mb-1" }, "例句 Example"),
                                h('p', { className: "text-sm text-slate-700 italic" }, current.x)
                            ),
                            // 衍生詞
                            current.t && h('div', { className: "info-block bg-emerald-50", style: { borderColor: '#10b981' } },
                                h('p', { className: "text-[10px] font-black text-emerald-600 uppercase mb-1" }, "衍生詞 Related"),
                                h('p', { className: "text-sm text-slate-700" }, current.t)
                            ),
                            // SRS 按鈕
                            h('div', { className: "grid grid-cols-4 gap-2 mt-6" },
                                h('button', { onClick: function() { handleSRS('again'); }, className: "py-3 bg-red-100 text-red-700 rounded-2xl text-xs font-black hover:bg-red-200 transition-all" }, "AGAIN"),
                                h('button', { onClick: function() { handleSRS('hard'); }, className: "py-3 bg-orange-100 text-orange-700 rounded-2xl text-xs font-black hover:bg-orange-200 transition-all" }, "HARD"),
                                h('button', { onClick: function() { handleSRS('good'); }, className: "py-3 bg-blue-100 text-blue-700 rounded-2xl text-xs font-black hover:bg-blue-200 transition-all" }, "GOOD"),
                                h('button', { onClick: function() { handleSRS('easy'); }, className: "py-3 bg-green-100 text-green-700 rounded-2xl text-xs font-black hover:bg-green-200 transition-all" }, "EASY")
                            )
                        )
                    );
                }
            }
            
            var root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(h(App));
        })();
    </script>
</body>
</html>""")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(content))
    
    print("Vocab Master Tool Build (No-3D, Full-Info) Success. Words: " + str(len(json.loads(json_str))))

if __name__ == "__main__":
    build_html()
