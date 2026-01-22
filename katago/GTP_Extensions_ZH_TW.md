# KataGo GTP 擴展 (KataGo GTP Extensions)

除了基本的 [GTP 指令集](https://www.lysator.liu.se/~gunnar/gtp/) 之外，KataGo 還支援一些額外的指令：

## 棋盤與規則相關

*   `rectangular_boardsize X Y`
    *   設置棋盤為非正方形尺寸，寬度 `X` 和高度 `Y`。
*   `set_position COLOR VERTEX COLOR VERTEX ...`
    *   直接指定初始棋盤位置，替換當前棋盤。新設置的位置假設沒有移動歷史（無劫或超劫限制）。
*   `clear_cache`
    *   清除搜索樹和神經網路緩存。可用於強制 KataGo 重新搜索某個位置。
*   `get_komi`
    *   報告 KataGo 當前使用的貼目。
*   `kata-get-rules`
    *   返回一個 JSON 字典，指示 KataGo 當前使用的規則。
    *   例如：`{"hasButton":false,"ko":"POSITIONAL","scoring":"AREA","suicide":true,"tax":"NONE","whiteHandicapBonus":"N-1","friendlyPassOk":true}`
    *   包含 `ko` (劫), `scoring` (計分), `tax` (貼目修正), `suicide` (自殺), `hasButton` (按鈕), `whiteHandicapBonus` (白棋讓子補償), `friendlyPassOk` (友好停著) 等欄位。
*   `kata-set-rules RULES`
    *   設置 KataGo 應使用的當前規則。
    *   `RULES` 可以是 JSON 字典或簡寫字串（如 `tromp-taylor`, `chinese`, `japanese`, `aga`, `new-zealand` 等）。
*   `kata-set-rule RULE VALUE`
    *   設置當前規則的單個欄位。
*   `kgs-rules RULES`
    *   用於 KGS 的擴展，類似 `kata-set-rules` 但支援 KGS 特定的規則名稱。

## 時間設定

*   `kgs-time_settings KIND ...`
    *   用於 KGS 的擴展，支援 `none`, `absolute`, `canadian`, `byoyomi`。
*   `kata-time_settings KIND ...`
    *   KataGo 的擴展，支援所有 `kgs-time_settings`，並增加了 `fischer` (費雪制) 和 `fischer-capped` (有上限的費雪制)。
    *   明確支援浮點數時間值。
*   `kata-list_time_settings`
    *   報告 `kata-time_settings` 支援的所有時間設置。

## 分析與搜索

*   `lz-analyze [player] [interval] KEYVALUEPAIR ...`
    *   開始搜索並可選地將實時分析輸出到 stdout。
    *   支援 `minmoves`, `maxmoves`, `avoid` (禁止移動), `allow` (允許移動) 等參數。
    *   輸出格式包含 `move`, `visits`, `winrate`, `prior`, `lcb`, `order`, `pv` 等資訊。
*   `kata-analyze [player] [interval] KEYVALUEPAIR ...`
    *   與 `lz-analyze` 類似，但輸出格式略有不同，並有更多選項。
    *   額外支援 `rootInfo` (根節點資訊), `ownership` (所有權), `movesOwnership` 等。
    *   輸出欄位包括 `utility`, `scoreMean`, `scoreStdev`, `scoreLead`, `scoreSelfplay` 等。
*   `lz-genmove_analyze` / `kata-genmove_analyze`
    *   與 `genmove` 相同，但會在搜索時產生類似 `lz-analyze` / `kata-analyze` 的輸出。
*   `analyze`, `genmove_analyze`
    *   專為 Sabaki GUI 應用程式設計的 `kata-analyze` 和 `kata-genmove_analyze` 版本。
*   `kata-search`, `kata-search_cancellable`
    *   與 `genmove` 相同，但**不**由引擎在棋盤上實際執行該移動。控制器需要發送 `play` 指令來確認移動。
    *   `cancellable` 版本可以被中斷。
*   `kata-search_analyze`, `kata-search_analyze_cancellable`
    *   類似 `kata-genmove_analyze`，但不實際執行移動。

## 原始神經網路評估

*   `kata-raw-nn SYMMETRY`
    *   報告 KataGo 的原始神經網路評估結果（無搜索）。
    *   輸出包含 `whiteWin`, `whiteLoss`, `whiteLead`, `policy`, `whiteOwnership` 等。
*   `kata-raw-human-nn SYMMETRY`
    *   類似 `kata-raw-nn`，但使用人類 SL 模型進行評估（如果已加載）。
*   `kata-get-models`
    *   返回有關已加載模型的 JSON 數組資訊。

## 參數與除錯

*   `kata-get-param PARAM` / `kata-set-param PARAM VALUE`
    *   獲取或設置參數值。幾乎所有搜索相關的 GTP 配置參數都可調整。
    *   例如 `playoutDoublingAdvantage`, `numSearchThreads`, `maxVisits`, `humanSLProfile` 等。
*   `kata-list-params`
    *   列出所有支援的參數。
*   `kata-get-params` / `kata-set-params PARAMS`
    *   一次獲取或設置多個參數。
*   `cputime` / `gomill-cpu_time`
    *   返回大致的掛鐘時間 (wall-clock-time) 秒數。
*   `kata-benchmark NVISITS`
    *   使用當前設置運行基準測試。
*   `printsgf [FILENAME]`
    *   將當前局面轉存為 SGF 文件。
*   `debug_moves`, `genmove_debug`, `kata-debug-print-tc`
    *   各種除錯指令。

---
*文件生成時間: 2026-01-22*
