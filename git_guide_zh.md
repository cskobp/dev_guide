# Git 常用操作詳盡指南 (繁體中文版)

本文檔提供 Git 版本控制系統的完整教學，涵蓋從基礎設定到進階協作的所有常用指令。

---

## 1. 基礎設定 (Configuration)
在開始使用 Git 之前，應先設定使用者資訊。

```bash
# 設定全域使用者名稱
git config --global user.name "Your Name"

# 設定全域電子郵件
git config --global user.email "your.email@example.com"

# 查看所有設定
git config --list
```

---

## 2. 建立儲存庫 (Repository)

```bash
# 在當前目錄初始化新的 Git 儲存庫
git init

# 複製遠端儲存庫到本地
git clone <url>
```

---

## 3. 日常工作流 (Basic Workflow)

### 3.1 狀態與追蹤
| 功能 | 指令 |
| :--- | :--- |
| **查看目前的檔案狀態** | `git status` |
| **將檔案加入暫存區 (Staging)** | `git add <file>` 或 `git add .` (全部) |
| **查看尚未暫存的修改內容** | `git diff` |
| **查看已暫存但尚未提交的修改** | `git diff --cached` |

### 3.2 提交更改
```bash
# 提交暫存區的內容並加上說明訊息
git commit -m "描述你的更改內容"

# 修改最後一次提交的訊息 (尚未 push 前)
git commit --amend
```

---

## 4. 分支與合併 (Branching, Merge & Rebase)

分支是 Git 的核心。這裡深入探討如何整合不同分支的變更。

### 4.1 基礎分支指令
```bash
git branch <name>      # 建立分支
git switch <name>      # 切換分支
git switch -c <name>   # 建立並切換
git branch -d <name>   # 刪除分支 (已合併)
git branch -D <name>   # 強制刪除分支 (未合併)
```

---

### 4.2 合併 (Merge)
`merge` 會將兩個分支的歷史結合成一個新的「合併提交」(Merge Commit)。

#### A. 快進合併 (Fast-forward)
當目標分支在分叉後沒有新提交時發生。
```bash
# 在 main 分支執行
git merge feature-a
```
**示意圖：**
```text
A---B (main)
     \
      C---D (feature-a)
           ↑
        合體後：A---B---C---D (main, feature-a)
```

#### B. 三路合併 (3-way Merge)
當兩個分支都有新提交時，Git 會找共同祖先並建立新提交。
```text
      C---D (feature-a)
     /
A---B---E---F (main)
             ↑
          合體後：...F---G (main) <- G 是合併提交，包含 C,D,E,F 的內容
```

---

### 4.3 衍合 (Rebase)
`rebase` 會將你的分支「重新基準化」到另一個分支的最新提交上，創造線性的歷史。

#### 範例與指令
```bash
git switch feature-b
git rebase main
```
**示意圖：**
```text
      C---D (feature-b)
     /
A---B---E---F (main)

   執行 Rebase 後：
            C'---D' (feature-b)
           /
A---B---E---F (main)
```
> [!WARNING]
> **黃金法則**：絕不要在公共分支（如 `main`）上執行 Rebase！這會改寫歷史，導致同事的儲存庫出錯。

---

### 4.4 衝突處理實戰 (Conflict Resolution)
不論是 `merge` 還是 `rebase`，只要兩邊改到同一行就會發生衝突。

#### 步驟 1：檢視衝突
Git 會提示發生衝突，執行 `git status` 查看哪些檔案衝突。

#### 步驟 2：手動修復
打開檔案，你會看到：
```text
<<<<<<< HEAD
這是你目前分支的內容 (例如 main)
=======
這是要合併進來的內容 (例如 feature)
>>>>>>> feature
```
手動編輯檔案，刪除標記並保留正確代碼。

#### 步驟 3：繼續整合
- **Merge**: `git add <file>` -> `git commit`
- **Rebase**: `git add <file>` -> `git rebase --continue` (不需要也不可以 commit)

---

### 4.5 該用 Merge 還是 Rebase？
| 特性 | Merge | Rebase |
| :--- | :--- | :--- |
| **歷史紀錄** | 保留完整的歷史與分支結構 | 創造簡潔、線性的歷史 |
| **複雜度** | 較簡單，適合初學者 | 較複雜，需要處理多次 commit 衝突 |
| **推薦場景** | 整合大型功能、公共分支合併 | 個人開發分支、保持本地提交整潔 |

---

## 5. 遠端操作 (Remote)

```bash
# 查看遠端儲存庫資訊
git remote -v

# 下載遠端更改並合併到目前分支 (Fetch + Merge)
git pull

# 僅下載遠端更改，不自動合併
git fetch

# 將本地提交推送到遠端
git push origin <branch_name>

# 設定遠端分支追蹤 (第一次推送到新分支時)
git push -u origin <branch_name>
```

---

## 6. 暫存功能 (Stash)
當你工作到一半需要切換分支，但又不想提交不完整的代碼時使用。

```bash
# 將目前的修改暫存起來
git stash

# 查看暫存列表
git stash list

# 取出最近一次的暫存並移除紀錄
git stash pop

# 取出最近一次的暫存但保留紀錄
git stash apply
```

---

## 7. 歷史記錄 (History)

```bash
# 查看提交歷史
git log

# 查看精簡的提交歷史 (一行顯示)
git log --oneline --graph --all

# 查看特定檔案的每一行修改者
git blame <file>
```

---

## 8. 撤銷與復原 (Undo)
> [!CAUTION]
> `reset --hard` 會直接刪除未提交的修改，請謹慎使用。

```bash
# 放棄工作區中特定檔案的修改 (回到最後一次 commit 狀態)
git checkout -- <file>

# 移出暫存區的檔案 (但保留內容在工作區)
git reset HEAD <file>

# 撤銷最後一次 commit，但保留修改內容在暫存區
git reset --soft HEAD~1

# 撤銷最後一次 commit，並刪除所有修改 (慎用!)
git reset --hard HEAD~1

# 建立一個新的提交來反轉指定的提交內容 (安全做法)
git revert <commit_hash>
```

---

## 9. 常見技巧 (Tips)

### .gitignore 檔案
建立一個 `.gitignore` 文字檔，列出不需要被 Git 追蹤的檔案（如 `node_modules/`, `*.log`, `.env` 等）。

### 合併衝突處理
當 `merge` 發生衝突時，編輯衝突檔案，尋找 `<<<<<<<`, `=======`, `>>>>>>>` 標記，手動選擇保留的內容後，再次 `git add` 並 `git commit`。

---
> [!TIP]
> 養成「小步提交」(Commit early, commit often) 的習慣，這能讓代碼回溯和團隊協作變得更加輕鬆。
