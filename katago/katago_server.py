import subprocess
import json
import time
import threading
from typing import Dict, Any

class KataGoEngine:
    def __init__(self, katago_path: str, config_path: str, model_path: str):
        """
        初始化 KataGo 引擎子進程
        """
        self.process = subprocess.Popen(
            [katago_path, "analysis", "-config", config_path, "-model", model_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0  # Unbuffered
        )
        self.query_counter = 0
        self.lock = threading.Lock()
        
        # 啟動一個執行緒來讀取並印出 KataGo 的 debug 訊息 (stderr)
        self.stderr_thread = threading.Thread(target=self._log_stderr, daemon=True)
        self.stderr_thread.start()

    def _log_stderr(self):
        """讀取 KataGo 的標準錯誤輸出並印出"""
        while True:
            line = self.process.stderr.readline()
            if not line:
                break
            # 這裡可以改成寫入 log 檔案
            print(f"[KataGo Log] {line.decode().strip()}")

    def query(self, board_size: int, moves: list, komi: float = 6.5) -> Dict[str, Any]:
        """
        發送查詢給 KataGo 引擎
        
        :param board_size: 棋盤大小 (例如 19)
        :param moves: 棋步列表，格式為 [["B", "Q4"], ["W", "D16"], ...]
        :param komi: 貼目
        """
        query_id = f"query_{self.query_counter}"
        self.query_counter += 1

        # 建構 KataGo 分析模式所需的 JSON 格式
        # 參考: https://github.com/lightvector/KataGo/blob/master/docs/Analysis_Engine.md
        query_data = {
            "id": query_id,
            "moves": moves, 
            "rules": "Chinese", # 或 "Japanese", "Tromp-Taylor" 等
            "komi": komi,
            "boardXSize": board_size,
            "boardYSize": board_size,
            "includePolicy": True, # 是否包含落子機率圖
            "includeOwnership": True, # 是否包含地盤預測
            # "maxVisits": 500 # 可選：限制思考次數
        }

        with self.lock: # 確保線程安全
            # 發送 JSON 查詢
            json_str = json.dumps(query_data)
            self.process.stdin.write((json_str + "\n").encode('utf-8'))
            self.process.stdin.flush()

            # 讀取回應
            # 注意：這裡是一個簡單的同步實作。
            # 在發送請求後，我們立即等待同一行的回應。
            # 若有多個並發請求，建議使用異步 (AsyncIO) 或 callback 機制。
            while True:
                response_line = self.process.stdout.readline()
                if not response_line:
                    raise Exception("KataGo process ended unexpectedly")
                
                response_line_str = response_line.decode().strip()
                if not response_line_str:
                    continue

                # print(f"DEBUG: Response content: {response_line_str}")
                response = json.loads(response_line_str)
                if response.get("id") == query_id:
                    return response
                # 如果讀到其他 id 的回應 (理論上在這個簡單模型不應發生)，可以忽略或處理

    def close(self):
        self.process.terminate()

# --- 使用範例 ---
if __name__ == "__main__":
    # 請修改為您的實際路徑
    KATAGO_EXEC = "./cpp/katago"
    CONFIG_FILE = "./cpp/my_server_config.cfg" 
    MODEL_FILE = "./cpp/default_model.bin.gz"

    print("正在啟動 KataGo...")
    try:
        engine = KataGoEngine(KATAGO_EXEC, CONFIG_FILE, MODEL_FILE)
        
        # 測試查詢：19路棋盤，黑棋下在天元
        moves = [["B", "K10"]] 
        print(f"發送查詢: moves={moves}")
        
        result = engine.query(19, moves)
        
        print("\n--- 分析結果 ---")
        if 'rootInfo' in result:
            print(f"勝率 (Winrate): {result['rootInfo']['winrate']:.2%}")
            print(f"領先目數 (ScoreLead): {result['rootInfo']['scoreLead']:.1f}")
            
            if result['moveInfos']:
                best_move = result['moveInfos'][0]
                print(f"推薦下一手: {best_move['move']} (Visits: {best_move['visits']})")
        else:
            print("Error or incomplete result:", result)

        engine.close()
    except Exception as e:
        print(f"Error: {e}")
