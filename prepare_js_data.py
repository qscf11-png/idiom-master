import json
import os

def prepare_js_data():
    input_path = "master_vocab_full.json"
    output_path = "vocab_data.js"
    
    if not os.path.exists(input_path):
        print("Error: master_vocab_full.json not found.")
        return

    print(f"正在讀取 {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    js_list = []
    for word, d in data.items():
        # 標註：這部分將欄位扁平化以節省 JS 空間
        js_list.append({
            "w": word,
            "d": d.get("def", ""),
            "i": d.get("ipa", ""),
            "t": d.get("trans", ""),
            "c": d.get("col", ""),
            "x": d.get("ex", ""),
            "p": d.get("pos", ""),
            "l": d.get("level", 0)
        })

    print(f"總計轉換 {len(js_list)} 個單字。")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("const VOCAB_DB = ")
        json.dump(js_list, f, ensure_ascii=False)
        f.write(";")
        
    print(f"JS 數據已產出: {output_path}")

if __name__ == "__main__":
    prepare_js_data()
