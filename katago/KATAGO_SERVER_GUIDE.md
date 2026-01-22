# KataGo Server 實作與建置指南 (macOS)

這份指南將一步步教您如何在 macOS 環境下編譯 KataGo，並透過 Python 建立一個能夠與其溝通的伺服器介面。

## 第一部分：環境準備與編譯 (Environment Setup & Compilation)

KataGo 的核心引擎是用 C++ 撰寫的，我們需要先將其編譯成執行檔。

### 1. 安裝必要工具
我們使用 macOS 的套件管理工具 Homebrew 來安裝編譯所需的依賴。

開啟終端機 (Terminal)，執行以下指令：

```bash
# 安裝 CMake (編譯設定工具) 和 libzip (壓縮支援)
brew install cmake libzip

# (選用) 如果想要更佳的效能，可以安裝 Google PerfTools
brew install gperftools
```

### 2. 下載 KataGo 原始碼
如果您還沒有下載 KataGo，請執行：

```bash
git clone https://github.com/lightvector/KataGo.git
cd KataGo/cpp
```

### 3. 編譯 KataGo
在 `cpp` 目錄下，我們將使用 CMake 來產生編譯設定檔並進行編譯。針對 macOS，我們通常建議使用 `OPENCL` 或 `EIGEN` (CPU) 後端。若您的 Mac 支援 Metal (Apple Silicon M1/M2/M3)，Metal 後端目前還在實驗階段，OpenCL 通常較為穩定。

**編譯指令 (OpenCL GPU 版本 - 推薦一般 Mac):**
```bash
cmake . -DUSE_BACKEND=OPENCL
make -j$(sysctl -n hw.logicalcpu)
```

**編譯指令 (純 CPU 版本 - 如果沒有獨立顯卡):**
```bash
cmake . -DUSE_BACKEND=EIGEN -DUSE_AVX2=1
make -j$(sysctl -n hw.logicalcpu)
```

編譯完成後，您會在 `cpp` 目錄下看到一個名為 `katago` 的執行檔。

---

## 第二部分：模型與設定 (Model & Configuration)

KataGo 需要由神經網路模型檔案 (`.bin.gz` 或 `.kmodel`) 與設定檔 (`.cfg`) 來運作。

### 1. 下載神經網路模型
請前往 [KataGo Training Site](https://katagotraining.org/networks/) 下載最新的權重檔案。
- 選擇最新的 18b (較快) 或 40b (較強) 網路。
- 下載後將檔案重新命名為 `default_model.bin.gz` (方便後續引用) 並放入 `KataGo/cpp` (或您指定的資源目錄)。

### 2. 準備設定檔
KataGo 提供了範例設定檔。對於伺服器分析用途，我們使用 `analysis_example.cfg` 作為基底。

複製範例設定檔：
```bash
cp ../python/configs/analysis_example.cfg my_server_config.cfg
```

您可以編輯 `my_server_config.cfg` 來調整參數 (例如 `numSearchThreads` 執行緒數量，視您的機器效能而定)。

---

## 第三部分：構建 Python 分析伺服器 (Constructing the Server)

接下來，我們將撰寫一段 Python 程式碼來包裝 KataGo 引擎。這段程式碼會啟動 KataGo 的 `analysis` 模式，並透過標準輸入/輸出 (stdin/stdout) 與其溝通。

### KataGo 引擎包裝器 (KataGo Wrapper)

請建立一個檔案 `katago_server.py`，內容如下：

```python
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
                
                response = json.loads(response_line)
                if response.get("id") == query_id:
                    return response
                # 如果讀到其他 id 的回應 (理論上在這個簡單模型不應發生)，可以忽略或處理

    def close(self):
        self.process.terminate()

# --- 使用範例 ---
if __name__ == "__main__":
    # 請修改為您的實際路徑
    KATAGO_EXEC = "./cpp/katago"
    CONFIG_FILE = "my_server_config.cfg" 
    MODEL_FILE = "default_model.bin.gz"

    print("正在啟動 KataGo...")
    engine = KataGoEngine(KATAGO_EXEC, CONFIG_FILE, MODEL_FILE)
    
    # 測試查詢：19路棋盤，黑棋下在天元
    moves = [["B", "K10"]] 
    print(f"發送查詢: moves={moves}")
    
    result = engine.query(19, moves)
    
    print("\n--- 分析結果 ---")
    print(f"勝率 (Winrate): {result['rootInfo']['winrate']:.2%}")
    print(f"領先目數 (ScoreLead): {result['rootInfo']['scoreLead']:.1f}")
    
    best_move = result['moveInfos'][0]
    print(f"推薦下一手: {best_move['move']} (Visits: {best_move['visits']})")

    engine.close()
```

---

## 第四部分：與網站後端整合 (Integration Context)

若要將此功能整合到您的 **FastAPI** 伺服器 (`gogo01` 專案)，您可以將上述的 `KataGoEngine` 類別實例化為一個全域變數 (Global Singleton)。

範例架構：

1.  **Backend (`backend/main.py`):**
    在伺服器啟動時 (`startup` event) 初始化 `KataGoEngine`。
2.  **API Endpoint (`/api/analyze`):**
    建立一個 API 接收前端傳來的棋譜 (SGF 或 moves 列表)。
3.  **呼叫引擎:**
    API 內部呼叫 `engine.query(...)` 取得分析結果。
4.  **回傳前端:**
    將 KataGo 的 JSON 輸出整理後回傳給前端顯示 (例如勝率折線圖、推薦點)。

這樣您就完成了一個基本的 KataGo AI 圍棋伺服器建置！
