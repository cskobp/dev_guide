# Node.js 安裝與使用完全指南 (繁體中文版)

本文檔介紹如何安裝 Node.js 環境，並詳細說明 npm 與 npx 等核心工具的使用方法。

---

## 1. 安裝 Node.js (Windows)

### 1.1 推薦方式：使用 nvm-windows (版本管理器)
強烈建議使用版本管理器，以便隨時切換不同版本的 Node.js。

1. **下載**: 前往 [nvm-windows GitHub](https://github.com/coreybutler/nvm-windows/releases) 下載 `nvm-setup.exe`。
2. **安裝**: 執行安裝程式。
3. **常用指令**:
```bash
nvm list available    # 查看可安裝的版本
nvm install 20.10.0   # 安裝特定版本 (例如 LTS 版)
nvm use 20.10.0       # 切換到該版本
nvm list              # 查看已安裝版本
```
Example:
```
C:\Users\user>nvm list available

|   CURRENT    |     LTS      |  OLD STABLE  | OLD UNSTABLE |
|--------------|--------------|--------------|--------------|
|    25.2.1    |   24.12.0    |   0.12.18    |   0.11.16    |
|    25.2.0    |   24.11.1    |   0.12.17    |   0.11.15    |
|    25.1.0    |   24.11.0    |   0.12.16    |   0.11.14    |
|    25.0.0    |   22.21.1    |   0.12.15    |   0.11.13    |
|   24.10.0    |   22.21.0    |   0.12.14    |   0.11.12    |
|    24.9.0    |   22.20.0    |   0.12.13    |   0.11.11    |
|    24.8.0    |   22.19.0    |   0.12.12    |   0.11.10    |
|    24.7.0    |   22.18.0    |   0.12.11    |    0.11.9    |
|    24.6.0    |   22.17.1    |   0.12.10    |    0.11.8    |
|    24.5.0    |   22.17.0    |    0.12.9    |    0.11.7    |
|    24.4.1    |   22.16.0    |    0.12.8    |    0.11.6    |
|    24.4.0    |   22.15.1    |    0.12.7    |    0.11.5    |
|    24.3.0    |   22.15.0    |    0.12.6    |    0.11.4    |
|    24.2.0    |   22.14.0    |    0.12.5    |    0.11.3    |
|    24.1.0    |   22.13.1    |    0.12.4    |    0.11.2    |
|    24.0.2    |   22.13.0    |    0.12.3    |    0.11.1    |
|    24.0.1    |   22.12.0    |    0.12.2    |    0.11.0    |
|    24.0.0    |   22.11.0    |    0.12.1    |    0.9.12    |
|   23.11.1    |   20.19.6    |    0.12.0    |    0.9.11    |
|   23.11.0    |   20.19.5    |   0.10.48    |    0.9.10    |

This is a partial list. For a complete list, visit https://nodejs.org/en/download/releases
```


### 1.2 確認安裝
安裝完成後，開啟終端機確認：
```bash
node -v    # 顯示 Node.js 版本
npm -v     # 顯示 npm 版本
```

---

## 2. 基礎使用

### 2.1 執行 JavaScript 檔案
```bash
node index.js
```

### 2.2 REPL (互動式直譯器)
直接在終端機輸入 `node` 即可進入互動模式，方便測試小段代碼。按兩次 `Ctrl + C` 可退出。

---

## 3. 套件管理工具 (npm)
npm (Node Package Manager) 是隨 Node.js 一併安裝的套件管理系統。

### 3.1 項目初始化
```bash
npm init      # 逐步建立 package.json
npm init -y   # 快速建立預設的 package.json
```

### 3.2 安裝套件
| 功能 | 指令 |
| :--- | :--- |
| **安裝並記錄到專案** | `npm install <package_name>` |
| **僅開發時使用** | `npm install <package_name> --save-dev` |
| **安裝全域工具** | `npm install -g <package_name>` |
| **根據 package.json 安裝所有依賴** | `npm install` |

### 3.3 執行腳本 (Scripts)
在 `package.json` 中的 `"scripts"` 欄位定義指令，然後執行：
```bash
npm run <script_name>  # 例如 npm run dev, npm run start
```

---

## 4. 執行工具 (npx)
npx 允許你「不必安裝到全域」就能直接執行套件工具，這能避免污染系統環境。

### 4.1 執行一次性指令
```bash
# 不需要安裝 create-react-app 就能建立專案
npx create-react-app my-app

# 啟動臨時的靜態伺服器
npx serve .
```

---

## 5. 套件管理工具 (Yarn)
Yarn 是由 Facebook 開發的另一款流行的套件管理工具，以速度快、安全性高著稱。

### 5.1 安裝 Yarn
推薦使用 Node.js 內置的 Corepack 安裝，或使用 npm 全域安裝。

#### 方法 A：使用 Corepack (推薦)
```bash
corepack enable
```

#### 方法 B：使用 npm 全域安裝
```bash
npm install -g yarn
```

### 5.2 常用指令對照 (npm vs Yarn)
| 功能 | npm 指令 | Yarn 指令 |
| :--- | :--- | :--- |
| **初始化項目** | `npm init` | `yarn init` |
| **安裝依賴** | `npm install` | `yarn install` |
| **安裝特定套件** | `npm install <pkg>` | `yarn add <pkg>` |
| **安裝開發依賴** | `npm install <pkg> -D` | `yarn add <pkg> -D` |
| **移除套件** | `npm uninstall <pkg>` | `yarn remove <pkg>` |
| **執行腳本** | `npm run <script>` | `yarn <script>` |

---

## 6. 常見公用程式與工具

### 6.1 Nodemon (開發利器)
自動偵測代碼修改並重啟應用程式。
```bash
npx nodemon index.js
```

### 6.2 Corepack (管理 Yarn/pnpm)
Node.js 16.9+ 內置工具，用於快速啟用其他套件管理器（詳見第 5.1 節）。
```bash
corepack enable
yarn -v
pnpm -v
```

---

## 7. 清理快取
若遇到奇怪的安裝錯誤，可嘗試清理快取：
```bash
npm cache clean --force
yarn cache clean
```

---
## 8. Node.js 版本歷史與支援週期 (Release Lifecycle)

Node.js 有一套嚴謹的發佈計畫，分為以下幾個階段：

*   **Current (當前版本)**: 每半年發佈一次大版本。偶數號版本會進入 LTS，奇數號版本為實驗性版本。
*   **Active LTS (長期支援)**: 專注於穩定性與安全性，適用於生產環境。通常持續 12 個月。
*   **Maintenance LTS (維護期)**: 僅提供關鍵安全更新與錯誤修復。通常持續 18 個月。
*   **End-of-Life (EOL)**: 停止所有更新，建議立即升級。

### 主要版本概覽 (截至 2025 年 12 月)

| 版本 | 狀態 | 代號 (Codename) | 最初發佈日期 | LTS 開始日期 | 結束支援 (EOL) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **v25.x** | Current | - | 2025-10-15 | - | 2026-06-01 |
| **v24.x** | Active LTS | Krypton | 2025-05-06 | 2025-10-28 | 2028-04-30 |
| **v23.x** | EOL | - | 2024-10-15 | - | 2025-06-01 |
| **v22.x** | Maintenance | Jod | 2024-04-24 | 2024-10-29 | 2027-04-30 |
| **v20.x** | Maintenance | Iron | 2023-04-18 | 2023-10-24 | 2026-04-30 |
| **v18.x** | EOL | Hydrogen | 2022-04-19 | 2022-10-25 | 2025-04-30 |
| **v16.x** | EOL | Gallium | 2021-04-20 | 2021-10-26 | 2023-09-11 |
| **v14.x** | EOL | Fermium | 2020-04-21 | 2020-10-27 | 2023-04-30 |
| **v12.x** | EOL | Erbium | 2019-04-23 | 2019-10-22 | 2022-04-30 |
| **v10.x** | EOL | Dubnium | 2018-04-24 | 2018-10-30 | 2021-04-30 |

---
> [!TIP]
> 建議在生產環境中始終選用帶有 **LTS (Long Term Support)** 標籤的版本。如果你需要開發最新的功能，則可以使用 **Current** 版本。
