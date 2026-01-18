# Conda 環境管理完全指南 (繁體中文版)

本文檔提供 Conda 虛擬環境管理的深度教學，涵蓋從基礎操作到進階維護的所有常用指令。

---

## 1. 環境查詢與資訊
在操作前，了解目前的環境狀態非常重要。

| 功能 | 指令 |
| :--- | :--- |
| **列出所有環境** | `conda env list` 或 `conda info --envs` |
| **查看當前環境資訊** | `conda info` |
| **查看當前環境安裝套件** | `conda list` |
| **搜尋特定套件版本** | `conda search <package_name>` |

---

## 2. 建立與管理環境

### 2.1 建立環境
```bash
# 建立基礎環境
conda create --name myenv

# 建立並指定 Python 版本 (推薦)
conda create --name py310 python=3.10

# 建立並安裝特定套件
conda create --name machine_learning python=3.9 numpy pandas scikit-learn
```

### 2.2 複製環境 (重新命名的替代方案)
Conda 無法直接重新命名環境。若要改名，請先複製再刪除：
```bash
# 將 old_env 複製到 new_env
conda create --name new_env --clone old_env

# 刪除舊環境
conda remove --name old_env --all
```

---

## 3. 激活、退出與刪除

### 3.1 激活與退出
```bash
# 激活環境
conda activate myenv

# 退出當前環境 (返回 base)
conda deactivate
```

### 3.2 刪除環境
```bash
# 徹底刪除環境及其所有套件
conda remove --name myenv --all
```

---

## 4. 套件管理 (在已激活的環境中)

### 4.1 安裝、更新與卸載
```bash
# 安裝套件 (從預設通道)
conda install numpy

# 安裝特定版本的套件
conda install numpy=1.24

# 更新特定套件
conda update numpy

# 更新環境中所有套件
conda update --all

# 卸載套件
conda remove numpy
```

### 4.2 使用 pip (當 conda 找不到套件時)
> [!IMPORTANT]
> 建議優先使用 `conda install`。若必須使用 `pip`，請確保已在 active 的 Conda 環境中。
```bash
pip install some-special-package
```

---

## 5. 環境匯入與匯出 (跨裝置遷移)

### 5.1 匯出環境
將環境配置保存為 YAML 檔案：
```bash
conda env export > environment.yml
```

### 5.2 匯入環境
從 YAML 檔案重建環境：
```bash
conda env create -f environment.yml
```

---

## 6. 系統維護與清理
長時間使用 Conda 會產生大量緩存，佔用硬碟空間。

```bash
# 清理索引快取、鎖定檔案、未使用過的套件及 tar 包
conda clean --all

# 僅清理已下載的 tar 包
conda clean --tarballs
```

---

## 7. 常見問題與疑難排解 (FAQ)

### Q1: 指令找不到 (Command Not Found)?
**解決方法**: 請確保已將 Conda 路径加入系統環境變數 (PATH)，或在終端機運行 `conda init`。

### Q2: 激活環境失敗?
在 Linux/macOS 上，有時需要執行：
```bash
source activate myenv
```

### Q3: 安裝速度太慢?
**建議**: 考慮更換國內鏡像源或使用 `mamba` (一個更快的 Conda 替代品)。
```bash
# 使用 conda-forge 通道安裝 (通常包含更多更新的套件)
conda install -c conda-forge <package_name>
```

---
> [!TIP]
> 保持 Base 環境的簡潔，僅在其中安裝 Conda 本身及其管理工具，所有開發任務都應在獨立的虛擬環境中進行。
