# Vercel 部署指南 (Vite + React)

本指南將帶您一步步將基於 Vite 和 React 的前端專案部署到 Vercel 上。

## 步驟一：安裝 Vercel CLI 並登入

我們將使用 Vercel 命令列工具 (CLI) 來進行無縫部署，不需手動上傳檔案。

1. 打開終端機 (Terminal)。
2. 確保您目前位於專案的前端資料夾 (例如：`frontend`)。
   ```bash
   cd path/to/your/frontend
   ```
3. 執行 Vercel 登入指令：
   ```bash
   npx vercel login
   ```
4. 終端機會提示您安裝 `vercel` 套件（若是首次使用）。輸入 `y` 並按下 Enter 繼續。
5. 接著，終端機會顯示一個驗證網址和一組設備代碼 (Device Code)。瀏覽器通常會自動開啟至 `https://vercel.com/device`。如果沒有自動開啟，請手動複製網址前往。
6. 在網頁中輸入終端機上顯示的設備代碼，並授權 Vercel CLI 存取您的 GitHub/Email 帳號。
7. 授權完成後返回終端機，您應該會看到 `Congratulations! You are now signed in.` 的成功訊息。

## 步驟二：解決專案名稱的大寫問題 (可選/排錯)

Vercel 的專案名稱**不允許包含大寫字母**。如果您的專案資料夾名稱包含大寫字母（例如 `SlideForge`），Vercel 在自動偵測專案名稱時可能會報錯：
`Error: Project names can be up to 100 characters long and must be lowercase...`

為了確保部署順利，我們可以手動建立一個設定檔來強制指定符合規則的名稱：
1. 在 `frontend` 資料夾的根目錄下，建立一個名為 `vercel.json` 的檔案。
2. 在檔案中填入以下內容（請確保名稱全為小寫，並使用連字號分隔）：
   ```json
   {
     "name": "slideforge-frontend"
   }
   ```
*(註：這是在終端機快速設定專案名稱的便捷方法，能避免後續問答被中斷。)*

## 步驟三：執行第一次部署

在確認您已登入，且位於 `frontend` 目錄下後，開始部署流程：

1. 在終端機輸入：
   ```bash
   npx vercel
   ```
2. Vercel 會以互動式問答確認您的專案設定（大部分可以直接按 Enter 使用預設值）：
   - **Set up and deploy "~/path/to/frontend"?** 
     回答：輸入 `y` 或是直接按 `Enter`。
   - **Which scope should contain your project?** 
     回答：直接按 `Enter` 選擇您的個人帳號。
   - **Link to existing project?** 
     回答：輸入 `n` (因為這是一個全新的專案)。
   - **What’s your project’s name?** 
     回答：如果剛才有設定 `vercel.json`，直接按 `Enter` 即可；或是手動輸入小寫名稱如 `slideforge-frontend`。
   - **In which directory is your code located? ./** 
     回答：直接按 `Enter` (表示程式碼就在當前資料夾)。
   - **Want to modify these settings?** 
     (Vercel 會自動偵測到這是 Vite 專案，並套用正確的 Build 指令與資料夾設定)
     回答：輸入 `n` 或 `N` (不需要手動修改設)。

完成上述問答後，Vercel CLI 就會開始將您的程式碼上傳並在雲端自動建置 (Build)。

## 步驟四：檢查部署結果與取得網址

等待建置進度條跑完後，終端機會顯示幾個重要的狀態與網址：
- **Inspect**: 這是 Vercel 控制台的連結，可以查看這次部署的詳細日誌 (Logs) 與狀態。
- **Production**: 這正是您網站的正式對外網址 (例如 `https://slideforge-frontend-xxxxxx.vercel.app`)。
- **Aliased**: 這是您專案更簡短、固定不變的別名網址 (例如 `https://slideforge-frontend.vercel.app`)。

此時點擊 Terminal 裡的 Production 或 Aliased 網址，就可以在線上看到網站成功運作了！

## 日後更新部署 (Production Deploy)

當您在本地端修改了程式碼，且需要再次將最新版本發佈到正式環境時，不需要再重新回答設定問題，只需要回到 `frontend` 資料夾中執行：

```bash
npx vercel --prod
```

加上 `--prod` 參數代表這是要直接發布、覆蓋到正式環境 (Production)。
> *提示：如果只輸入 `npx vercel`，Vercel 會生成一個開發預覽版 (Preview Deployment) 網址，讓您可以在不影響正式上線網站的情況下，先讓團隊測試新功能。*

---

# 後端 (Backend) 部署指南 (FastAPI)

如果您專案中有包含後端 API (例如 FastAPI)，且需要連帶部署並與前端串接，請參考以下步驟進行 Vercel 部署。

## 步驟一：設定後端的 CORS

為了讓部署後的前端可以跨網域呼叫後端 API，必須先在後端程式碼中設定正確的 CORS Origin。

1. 打開 `backend/main.py`
2. 找到 `CORSMiddleware` 的設定區塊，並將您剛剛**前端部署成功的正式網址**加入到 `allow_origins` 中。例如：
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:5173",
           "http://127.0.0.1:5173",
           "https://slideforge-frontend.vercel.app" # 您的前端 Vercel 網址
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## 步驟二：建立後端的 vercel.json 設定檔

因為後端是 Python/FastAPI，Vercel 預設不會自動知道該如何啟動它，所以我們要建立一個設定檔。

1. 在 `backend` 目錄下新增 `vercel.json` 檔案。
2. 填寫以下內容（這會告訴 Vercel 使用 `@vercel/python` 這個執行環境，並將所有路由導向 `main.py`）：
   ```json
   {
     "name": "slideforge-backend",
     "version": 2,
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

## 步驟三：部署後端

1. 打開終端機，切換到 `backend` 目錄：
   ```bash
   cd path/to/your/backend
   ```
2. 執行部署指令：
   ```bash
   npx vercel --prod
   ```
3. 回答初始化問題（同前端的流程）：
   - `Set up and deploy "~/path/to/backend"?` [Y]
   - `Which scope do you want to deploy to?` [輸入 Enter 選預設帳號]
   - `Link to existing project?` [N]
   - `What's your project's name?` [直接 Enter 套用設定的 slideforge-backend]
   - `In which directory is your code located?` [Enter 代表 ./]

部署完成後，Vercel 會產生另一個網址給後端，例如 `https://slideforge-backend.vercel.app`。

## 步驟四：更新前端的 API 網址並重新部署

現在後端也上線了，我們必須讓前端知道**去哪裡打 API**。

1. 回到前端專案修改 API 網址設定。(例如 `frontend/src/api.js`)：
   ```javascript
   // 將原本的 localhost 改成後端部署在 Vercel 上的網址
   const API = import.meta.env.VITE_API_URL || 'https://slideforge-backend.vercel.app/api';
   ```
2. 切換終端機目錄回到 `frontend`：
   ```bash
   cd ../frontend
   ```
3. 用正式環境指令**重新部署前端**：
   ```bash
   npx vercel --prod
   ```

完成以上步驟後，您的前端與後端就都成功部署於 Vercel 並可以互相溝通了！
