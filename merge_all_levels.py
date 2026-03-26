import json
import glob
import os
import re

def merge_all_levels():
    merged_data = {}
    total_files_processed = 0
    error_files = []
    
    print("--- 開始全量整合 (Level 1-6) ---")
    
    # 遍歷 Level 1 到 6
    for lvl in range(1, 7):
        pattern = f"batch_l{lvl}_p*.json"
        batch_files = glob.glob(pattern)
        
        # 排序以便追蹤進度
        def sort_key(x):
            match = re.search(r'_p(\d+)\.json', x)
            return int(match.group(1)) if match else 0
        
        batch_files.sort(key=sort_key)
        print(f"\n[Level {lvl}] 找到 {len(batch_files)} 個批次檔案。")
        
        lvl_count = 0
        for file_path in batch_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 處理 dict 格式 (預期格式 {"word": {...}})
                    if isinstance(data, dict):
                        for word, details in data.items():
                            if not isinstance(details, dict):
                                continue
                            
                            # 如果單字已存在，進行合併（保留最豐富資訊）
                            if word in merged_data:
                                current = merged_data[word]
                                for k, v in details.items():
                                    if v and not current.get(k):
                                        current[k] = v
                                # 記錄較小的 level (如果有的話)
                                if "level" in current:
                                    current["level"] = min(current["level"], lvl)
                                else:
                                    current["level"] = lvl
                            else:
                                details["level"] = lvl
                                merged_data[word] = details
                            lvl_count += 1
                        
                total_files_processed += 1
                if total_files_processed % 100 == 0:
                    print(f"已處理 {total_files_processed} 個檔案...")
                    
            except Exception as e:
                error_files.append((file_path, str(e)))
                
        print(f"Level {lvl} 完成，新增/更新了 {lvl_count} 筆記錄。")

    # 儲存結果
    output_path = "master_vocab_full.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
    print("\n--- 整合完成 ---")
    print(f"總計處理檔案: {total_files_processed}")
    print(f"最終單字總數: {len(merged_data)}")
    print(f"結果已儲存至: {output_path}")
    
    if error_files:
        print(f"\n[警告] 發現 {len(error_files)} 個損毀檔案:")
        for f, err in error_files[:10]: # 僅列出前 10 個
            print(f" - {f}: {err}")
        if len(error_files) > 10:
            print(f" ... 還有 {len(error_files)-10} 個錯誤。")

if __name__ == "__main__":
    merge_all_levels()
