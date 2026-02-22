# llama.cpp 使用指南 (繁體中文)

## 1. 簡介 (Introduction)

`llama.cpp` 是一個使用純 C/C++ 實現的 LLM (大型語言模型) 推理工具。它的主要目標是在各種硬體上（本地和雲端）以最少的設置和最先進的性能實現 LLM 推理。

**主要特點：**
- 純 C/C++ 實現，無依賴。
- Apple Silicon 是“一等公民” - 經由 ARM NEON, Accelerate 和 Metal 框架優化。
- 支援 x86 架構的 AVX, AVX2, AVX512 和 AMX。
- 支援 NVIDIA GPU (CUDA), AMD GPU (HIP), Moore Threads (MUSA), Vulkan 和 SYCL 後端。
- 支援多種量化精度 (1.5-bit 到 8-bit) 以加快推理速度並減少記憶體使用。

## 2. 安裝與編譯 (Installation & Build)

獲取程式碼：
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

### 2.1 CPU 編譯
使用 CMake 編譯：
```bash
cmake -B build
cmake --build build --config Release
```
*提示：使用 `-j` 參數可以並行編譯加快速度，例如 `cmake --build build --config Release -j 8`。*

### 2.2 macOS (Metal / Apple Silicon)
在 macOS 上，Metal 支援預設是啟用的。直接使用上述 CMake指令即可。
```bash
cmake -B build
cmake --build build --config Release
```
如果需要禁用 Metal，可以使用 `-DGGML_METAL=OFF`。

### 2.3 NVIDIA GPU (CUDA)
確保已安裝 [CUDA toolkit](https://developer.nvidia.com/cuda-toolkit)。
```bash
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release
```

### 2.4 Windows
建議使用 Visual Studio 2022 和 CMake。
1. 安裝 Visual Studio 2022 (Desktop development with C++)。
2. 在 Developer Command Prompt 中執行：
```cmd
cmake -B build
cmake --build build --config Release
```
若要支援 CUDA，請添加 `-DGGML_CUDA=ON`。

## 3. 獲取模型 (Obtaining Models)

`llama.cpp` 需要 **GGUF** 格式的模型。

您可以從 [Hugging Face](https://huggingface.co/models?library=gguf&sort=trending) 下載 GGUF 模型。
或是使用 CLI 工具直接下載：
```bash
# 下載 gemma-3-1b-it-GGUF
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF
```

### 3.1 查看下載的模型 (Listing Models)

你可以使用 `-cl` 參數來列出目前緩存中的所有模型：

```bash
llama-cli -cl
```

或者查看你的緩存目錄 (見 6.1 節)。

### 3.2 清除緩存 (Removing Cache)

目前 `llama.cpp` 沒有內建的指令來刪除特定模型。您需要手動刪除緩存檔案。

1. **查看緩存目錄位置**：
   執行 `llama-cli -cl`，輸出中會顯示 `model cache directory`。

   ```bash
   llama-cli -cl
   # Output example:
   # model cache directory: /Users/yourname/Library/Caches/llama.cpp/
   ```

2. **手動刪除檔案**：
   進入該目錄並刪除不需要的模型檔案。

   ```bash
   # 範例：刪除主要緩存目錄下的所有檔案
   rm -rf ~/Library/Caches/llama.cpp/*
   ```

   *注意：請確保您刪除的是正確的檔案。*

## 4. 基本使用 (Basic Usage - `llama-cli`)

編譯完成後，二進制文件位於 `build/bin/` 目錄下。

### 4.1 核心參數一覽 (Overview of Parameters)

以下列出 `llama-cli` 常用的參數，分為模型、性能、採樣與交互四類。

#### 4.1.1 模型與載入 (Model & Loading)
| 縮寫 | 全名 | 說明 |
| :--- | :--- | :--- |
| `-m` | `--model` | 指定模型檔案的路徑 (`path/to/model.gguf`)。 |
| `-hf` | `--hf-repo` | 從 Hugging Face 下載並使用模型 (格式 `user/repo`)。 |
| `-c` | `--ctx-size` | 上下文大小 (Context Size)。預設為 `0` (由模型決定)，可手動設定如 `4096` 或 `8192`。 |
| `-ngl`| `--gpu-layers` | 將多少層模型 offload 到 GPU。設定 `99` 或更大值通常代表全部加載到 GPU。 |
| `-sm` | `--split-mode` | 多 GPU 分割模式：`none` (單卡), `layer` (按層分割, 預設), `row` (按行分割)。 |
| `-ts` | `--tensor-split`| 多 GPU 張量分割比例，例如 `3,1` 代表第一張卡分 3/4，第二張卡分 1/4。 |
| `-mg` | `--main-gpu` | 指定主要 GPU 的索引 (預設 0)。 |

#### 4.1.2 性能與系統 (Performance & System)
| 縮寫 | 全名 | 說明 |
| :--- | :--- | :--- |
| `-t` | `--threads` | 推理時使用的 CPU 線程數。建議設為物理核心數。 |
| `-b` | `--batch-size` | 批次處理大小 (Batch Size)，預設 2048。 |
| `-ub` | `--ubatch-size` | 物理最大批次大小 (Physical Batch Size)，預設 512。 |
| `--mlock` | (無) | 強制將模型鎖定在記憶體中，防止被 swap 到硬碟。 |
| `--no-mmap` | (無) | 禁用 memory-map。讀取模型會變慢，但可能減少記憶體壓力。 |

#### 4.1.3 採樣與生成 (Sampling & Generation)
| 縮寫 | 全名 | 說明 |
| :--- | :--- | :--- |
| `-n` | `--predict` | 最大生成 token 數。`-1` 代表無限 (直到上下文滿或遇到結束符)。 |
| `--temp` | `--temperature` | 溫度 (Temperature)。`0.8` 為預設。數值越高越隨機，越低越確定。 |
| `--top-k` | (無) | Top-K 採樣。限制僅從機率最高的 K 個 token 中採樣。預設 `40`。 |
| `--top-p` | (無) | Top-P (Nucleus) 採樣。預設 `0.95`。 |
| `--min-p` | (無) | Min-P 採樣。預設 `0.05`。 |
| `--repeat-penalty` | (無) | 重複懲罰係數。預設 `1.0` (不懲罰)。通常設 `1.1` 或 `1.2` 避免跳針。 |
| `-s` | `--seed` | 隨機種子 (Seed)。`-1` 為隨機，固定數值可重現結果。 |

#### 4.1.4 交互與輸入 (Interaction & Input)
| 縮寫 | 全名 | 說明 |
| :--- | :--- | :--- |
| `-p` | `--prompt` | 設定初始提示詞 (Prompt)。 |
| `-f` | `--file` | 從檔案讀取提示詞。 |
| `-cnv`| `--conversation` | 啟用對話模式 (Conversation Mode)，會自動套用 chat template。 |
| `-i` | `--interactive` | 啟用交互模式，允許使用者在生成中途介入。 |
| `--chat-template` | (無) | 強制指定模型的 chat template (如 `chatml`, `llama3`, `vicuna`)。 |
| `-r` | `--reverse-prompt`| 設定反向提示詞 (Reverse Prompt)，遇到此詞時暫停生成並等待輸入。 |
| `--color` | (無) | 啟用彩色輸出區分提示詞與生成內容 (`on`, `off`, `auto`)。 |

### 4.2 使用範例

**基本對話：**
```bash
./build/bin/llama-cli -m my_model.gguf -cnv -p "你好，請自我介紹。"
```

**高性能全 GPU 推理 (16k context)：**
```bash
./build/bin/llama-cli -m my_model.gguf -ngl 99 -c 16384 -t 8 -p "詳細分析這份報告..."
```

## 5. 伺服器模式 (Server Usage - `llama-server`)

`llama-server` 是一個輕量級、相容 OpenAI API 的 HTTP 伺服器。

### 5.1 常用參數一覽 (Server Parameters)
除了繼承 `llama-cli` 的模型與性能參數 (如 `-m`, `-ngl`, `-c`, `--temp`) 外，伺服器還有專屬參數：

| 縮寫 | 全名 | 說明 |
| :--- | :--- | :--- |
| `--host` | (無) | 綁定的 IP 地址。預設 `127.0.0.1`。若要允許外部訪問可設 `0.0.0.0`。 |
| `--port` | (無) | 綁定的端口。預設 `8080`。 |
| `-np` | `--parallel` | 並行槽位數 (Parallel Slots)。決定同時能處理多少請求。預設 `1` (或 auto)。 |
| `--api-key` | (無) | 設定 API 金鑰，增加安全性。 |
| `--webui` | `--no-webui` | 啟用或禁用內建的 Web UI 介面。 |
| `-cb` | `--cont-batching` | 啟用 Continuous Batching (動態批處理)，提升高負載下的吞吐量。 |
| `--log-format`| (無) | 日誌格式，可選 `text` 或 `json`。 |

### 5.2 啟動範例

**基本啟動：**
```bash
./build/bin/llama-server -m my_model.gguf --port 8080
```
瀏覽器訪問 `http://localhost:8080` 可使用簡易 Web UI。

**高併發 GPU 伺服器：**
```bash
./build/bin/llama-server -m my_model.gguf -c 32768 -ngl 99 -np 4 --host 0.0.0.0 --port 8080
```
- `-np 4`: 啟用 4 個併發 slots，可同時服務 4 個用戶。
- `-c 32768`: 開大上下文以容納多個併發請求的總 context。

### 5.2 API 使用 (API Usage)

**Chat Completions (OpenAI Compatible):**
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      { "role": "system", "content": "You are a helpful assistant." },
      { "role": "user", "content": "Hello!" }
    ]
  }'
```

**Completions (Legacy):**
```bash
curl http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Building a website can be done in 10 simple steps:",
    "n_predict": 128
  }'
```

## 6. 其他工具 (Other Tools)

- **llama-quantize**: 用於將 FP16/FP32 模型量化為 GGUF 格式 (如 Q4_K_M)。
- **llama-perplexity**: 計算模型在給定文本上的困惑度 (Perplexity)，用於評估模型質量。
- **llama-bench**: 基準測試工具，用於測試推理速度 (tokens/sec)。

### 6.1 更改主要模型緩存目錄 (Change Default Cache Folder)

`llama.cpp` 預設會將下載的模型 (使用 `-hf` 或 `llama-server` 時) 儲存在系統的預設緩存目錄下 (例如 macOS 的 `~/Library/Caches/llama.cpp/` 或 Linux 的 `~/.cache/llama.cpp/`)。

若要更改此目錄，請設定 `LLAMA_CACHE` 環境變量：

**Linux / macOS:**
```bash
export LLAMA_CACHE="/path/to/your/cache"
```

**Windows (PowerShell):**
```powershell
$env:LLAMA_CACHE = "C:\path\to\your\cache"
```

設定後，所有下載的模型、manifest 和其他暫存檔都會存放在該目錄下的 `llama.cpp` 子目錄中。

---

## 7. 進階用法：多模型服務 (Advanced: Multi-Model Serving)

`llama-server` 支援 **Router Mode**，允許同時管理多個模型，並根據請求動態加載/卸載模型。

### 7.1 啟動 Router Mode

不指定 `-m` 參數直接啟動 server，即進入 Router Mode：

```bash
./build/bin/llama-server --port 8080
```

此時 server 會等待請求，並根據請求中的 `model` 參數來決定載入哪個模型。

### 7.2 指定模型來源

你可以透過以下方式告訴 server 模型在哪裡：

1.  **使用模型目錄 (`--models-dir`)**:
    
    將所有 GGUF 模型放在一個資料夾中，例如 `models/`：
    ```bash
    ./build/bin/llama-server --port 8080 --models-dir ./models
    ```
    
    支援的資料夾結構：
    ```text
    models/
     ├── llama-3-8b.gguf          # 單檔模型
     ├── gemma-2-9b/              # 多檔模型 (或是為了整潔)
     │    ├── gemma-2-9b.gguf
     │    └── mmproj.gguf         # 多模態投影檔
    ```

2.  **使用設定檔 (`--models-preset`)**:
    
    建立一個 `.ini` 檔案 (例如 `models.ini`) 來定義模型及其特定參數：
    
    ```bash
    ./build/bin/llama-server --port 8080 --models-preset models.ini
    ```
    
    **models.ini 範例：**
    ```ini
    version = 1
    
    ; 全域設定 (所有模型預設套用)
    [*]
    n-gpu-layers = 99
    ctx-size = 4096
    
    ; 定義別名與特定參數
    [llama3]
    model = models/Meta-Llama-3-8B-Instruct.gguf
    temperature = 0.7
    
    [gemma2]
    model = models/gemma-2-9b-it.gguf
    cache-type-k = f16
    
    ; 下載 Hugging Face 模型
    [phi3]
    hf-repo = microsoft/Phi-3-mini-4k-instruct-gguf
    hf-file = Phi-3-mini-4k-instruct-q4.gguf
    ```

### 7.3 調用特定模型

在 API 請求中指定 `model` 欄位 (對應檔案名稱或 `.ini` 中的 section 名稱)：

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [
      { "role": "user", "content": "Hello!" }
    ]
  }'
```

---

## 8. Web UI 開發 (Web UI Development)

`llama.cpp` 的 server 包含了一個基於 SvelteKit 的現代化 Web UI。如果您想修改或自定義 Web 介面，可以參考以下步驟。

### 8.1 原始碼位置
Web UI 的原始碼位於 `tools/server/webui` 目錄下。

此專案使用以下技術棧：
- **SvelteKit**: 前端框架
- **TailwindCSS**: CSS 框架
- **Vite**: 建置工具

### 8.2 開發環境設置

1.  **先決條件**: 確保您已安裝 [Node.js](https://nodejs.org/)。

2.  **啟動後端 Server**:
    在開發 Web UI 時，需要有一個運行中的 `llama-server` 作為後端 API。
    ```bash
    ./build/bin/llama-server -m your_model.gguf --port 8080
    ```

3.  **啟動前端開發伺服器**:
    打開一個新的終端視窗，進入 webui 目錄並啟動開發模式：
    ```bash
    cd tools/server/webui
    npm install
    npm run dev
    ```
    
    預設情況下，前端開發伺服器會由 Vite 啟動 (通常在 http://localhost:5173)，它會自動代理請求到 `http://localhost:8080` 的後端。

### 8.3 建置與發布

如果您修改了 Web UI 並希望將其整合回 `llama-server` 二進制檔案中：

1.  **編譯前端**:
    ```bash
    cd tools/server/webui
    npm run build
    ```
    此命令會生成靜態文件並壓縮為 `public/index.html.gz`。

2.  **重新編譯 llama-server**:
    回到專案根目錄，重新編譯 server 以包含新的 UI：
    ```bash
    cd ../../.. # 回到 llama.cpp 根目錄
    cmake --build build --config Release -t llama-server
    ```

---

## 9. Python 使用 (Python Usage)

在 Python 中使用 `llama.cpp` 主要有兩種方式：

### 9.1 方式一：使用 Python Bindings (llama-cpp-python)

這是最直接的方式，將 `llama.cpp` 作為 Python 函式庫使用。最受歡迎的綁定是 `llama-cpp-python`。

1.  **安裝**:
    ```bash
    pip install llama-cpp-python
    ```
    *(支援硬體加速安裝請參考該專案文檔，例如 `CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python`)*

2.  **基本使用**:
    ```python
    from llama_cpp import Llama

    # 載入模型
    llm = Llama(
        model_path="path/to/model.gguf",
        n_gpu_layers=-1, # 全部 offload 到 GPU
        verbose=True
    )

    # 生成文字
    output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=True)
    print(output)
    ```

### 9.2 方式二：使用 OpenAI Python Client (配合 llama-server)

如果您的 `llama-server` 已經在運行 (特別是 Router Mode 支援多模型時)，這是最推薦的方式。

1.  **安裝 OpenAI SDK**:
    ```bash
    pip install openai
    ```

2.  **查詢可用模型 (Query Available Models)**:
    
    ```python
    from openai import OpenAI

    client = OpenAI(
        base_url="http://localhost:8080/v1",
        api_key="sk-no-key-required"
    )

    # 列出所有可用模型 (對應 Server 載入的模型或 Router Mode 的設定)
    models = client.models.list()
    
    print("Available Models:")
    for model in models.data:
        print(f"- {model.id}")
    ```

3.  **進行對話 (Chat Completion)**:
    
    ```python
    response = client.chat.completions.create(
        model="llama3", # 指定剛才查詢到的模型 ID
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
    )
    
    print(response.choices[0].message.content)
    ```

---

更多詳細資訊請參考 `tools/server/README-dev.md` 以及官方文檔：[llama.cpp Documentation](https://github.com/ggml-org/llama.cpp)
