# KataGo 平行分析引擎 (KataGo Parallel Analysis Engine)

KataGo 包含一個引擎，可用於並行分析大量局面（整局遊戲或多局遊戲）。當配置得當且使用能夠處理大批量 (batch sizes) 的現代 GPU 時，此引擎比使用 GTP 引擎和 `kata-analyze` 快得多，因為它能夠利用跨局面的批次處理 (batching)，並且具有更友好的 API。分析引擎主要供編寫工具的人員使用，例如作為分析伺服器或網站的後端。

## 運行方式

此引擎可通過以下命令運行：

```bash
./katago analysis -config CONFIG_FILE -model MODEL_FILE
```

`cpp/configs/analysis_example.cfg` 中提供了一個範例設定檔。建議根據您的硬體調整此設定，例如根據記憶體大小調整 `nnCacheSizePowerOfTwo`，以及調整 `numSearchThreadsPerAnalysisThread`（同一局面同時運行的 MCTS 線程數）和 `numAnalysisThreads`（同時分析的局面數）。

有關如何調整這些參數的詳細討論，請參閱 [分析設定檔範例](https://github.com/lightvector/KataGo/blob/master/cpp/configs/analysis_example.cfg#L60)。

## 範例程式碼

有關演示如何從 Python 調用分析引擎的範例代碼，請參閱 [此處](https://github.com/lightvector/KataGo/blob/master/python/query_analysis_engine_example.py)！

## 協議 (Protocol)

引擎在 stdin 上接受查詢，並在 stdout 上輸出結果。每個查詢和每個結果都應為一行。協議是完全異步的——可以在任何時候接受 stdin 上的新請求，結果將在這些分析完成時出現在 stdout 上，並且順序可能與請求提供的順序不同。

### 查詢 (Queries)

寫入 stdin 的每個查詢行應為具有特定欄位的 JSON 字典。
**注意：每個查詢必須是單行——不支援多行 JSON 查詢。**

範例查詢：
```json
{"id":"foo","initialStones":[["B","Q4"],["B","C4"]],"moves":[["W","P5"],["B","P6"]],"rules":"tromp-taylor","komi":7.5,"boardXSize":19,"boardYSize":19,"analyzeTurns":[0,1,2]}
```

#### 欄位說明：

*   `id (string)`: **必填**。查詢的任意字串標識符。
*   `moves (list)`: **必填**。遊戲中已進行的移動，順序為 `[player, location]`。
    *   `player` 應為 `"B"` 或 `"W"`。
    *   `location` 應為如 `"C4"` 的字串，或 `"(0,13)"` 這樣的坐標。
*   `initialStones (list)`: **可選**。指定遊戲開始時棋盤上已有的棋子（例如讓子）。
*   `initialPlayer (string)`: **可選**。指定用於分析遊戲第一回合（第 0 回合）的玩家。
*   `rules (string or JSON)`: **必填**。使用簡寫字串或完整的 JSON 對象指定遊戲規則。
    *   詳情請參考 [GTP Extensions](./GTP_Extensions_ZH_TW.md) 中的 `kata-get-rules`。
*   `komi (number)`: **可選但強烈建議**。指定遊戲的貼目。
*   `whiteHandicapBonus (0|N|N-1)`: **可選**。覆蓋讓子補償的處理方式。
*   `boardXSize (integer)`: **必填**。棋盤寬度。
*   `boardYSize (integer)`: **必填**。棋盤高度。
*   `analyzeTurns (list of integers)`: **可選**。要分析的遊戲回合。0 是初始位置，1 是 `moves[0]` 之後的位置，依此類推。
*   `maxVisits (integer)`: **可選**。使用的最大訪問次數。
*   `rootPolicyTemperature (float)`: **可選**。設置大於 1 的值以使 KataGo 進行更廣泛的搜索。
*   `rootFpuReductionMax (float)`: **可選**。設置為 0 以使 KataGo 更願意嘗試各種移動。
*   `analysisPVLen (integer)`: **可選**。每個移動發送的 PV（主要變例）的最大長度。
*   `includeOwnership (boolean)`: **可選**。如果為真，則報告所有權預測結果。
*   `includeOwnershipStdev (boolean)`: **可選**。如果為真，則報告所有權預測的標準差。
*   `includeMovesOwnership (boolean)`: **可選**。如果為真，則報告每個單獨移動的所有權預測。
*   `includePolicy (boolean)`: **可選**。如果為真，則報告神經網路的原始策略 (policy)。
*   `includePVVisits (boolean)`: **可選**。如果為真，則報告 PV 中每個移動的訪問次數。
*   `avoidMoves (list of dicts)`: **可選**。禁止搜索特定玩家的特定移動，直到搜索達到一定深度。
*   `allowMoves (list of dicts)`: **可選**。與 `avoidMoves` 相反，只允許搜索特定移動。
*   `overrideSettings (object)`: **可選**。在此對象中指定任意數量的 `"paramName":value` 條目，以覆蓋此查詢的命令列 `CONFIG_FILE` 中的參數。例如 `playoutDoublingAdvantage`, `wideRootNoise`, `humanSLProfile` 等。
*   `priority (int)`: **可選**。分析線程將優先處理具有最高優先順序的查詢。

### 回應 (Responses)

發生錯誤或警告時，回應將具有 `error` 或 `warning` 欄位。

成功的分析回應範例：
```json
{"id":"foo","isDuringSearch":false,"moveInfos":[...],"rootInfo":{...},"turnNumber":2}
```

#### 主要欄位：

*   `id`: 查詢提供的 ID。
*   `isDuringSearch`: 通常為 false。如果提供了 `reportDuringSearchEvery`，則在搜索期間的中間報告中為 true。
*   `turnNumber`: 被分析的回合數。
*   `moveInfos`: JSON 字典列表，每個字典代表 KataGo 考慮的一個移動，包含 `move`, `visits`, `winrate`, `scoreLead`, `scoreSelfplay`, `prior`, `utility`, `lcb`, `pv` 等詳細資訊。
    *   `order`: KataGo 對移動的排序排名。0 是最好的。
    *   `ownership`: 如果請求了 `includeMovesOwnership`，將包含此欄位。
*   `rootInfo`: 包含請求回合本身的整體統計資訊的 JSON 字典，如 `winrate`, `scoreLead`, `visits` 等。
*   `ownership`: 如果請求了 `includeOwnership`，這是一個長度為 `boardYSize * boardXSize` 的數組，指示預測的所有權。
*   `policy`: 如果請求了 `includePolicy`，這是一個指示神經網路原始策略預測的數組。

### 特殊操作查詢 (Special Action Queries)

支援一些特殊操作查詢，這些查詢以 JSON 對象發送，根據查詢類型有不同的欄位。

1.  **query_version**: 請求 KataGo 報告其當前版本。
    *   `{"id":"foo","action":"query_version"}`
2.  **clear_cache**: 請求 KataGo 清空其神經網路緩存。
    *   `{"id":"foo","action":"clear_cache"}`
3.  **terminate**: 請求 KataGo 終止零個或多個分析查詢，而不等待它們正常完成。
    *   `{"id":"bar","action":"terminate","terminateId":"foo"}`
4.  **terminate_all**: 與 terminate 相同，但不要求提供 `terminateId`，並適用於所有查詢。
    *   `{"id":"bar","action":"terminate_all"}`
5.  **query_models**: 請求 KataGo 報告有關已加載模型的信息。
    *   `{"id":"foo","action":"query_models"}`

## 人類監督學習分析指南 (Human SL Analysis Guide)

從 1.15.0 版本開始，KataGo 支援一個新的人類監督學習 ("human SL") 模型（如 `b18c384nbt-humanv0.bin.gz`），該模型經過大量人類對局的訓練，可預測不同等級玩家的移動。

### 設定使用模型
有兩種方式傳入人類 SL 模型：
1.  **基本方式**：除了 KataGo 的正常模型外，還傳遞 `-human-model` 參數。
    *   在查詢中使用 `overrideSettings` 提供 `humanSLProfile`。
    *   請求 `"includePolicy":true` 以獲得 `humanPolicy` 欄位。
2.  **替代方式**：使用 `-model` 僅傳遞人類模型，完全取代正常模型。

### 各種 HumanSL 用法配方
*   **模仿人類風格 (Human-like play)**: 設置 `humanSLProfile`，將 `ignorePreRootHistory` 設為 false，並根據 `humanPolicy` 選擇移動。
*   **確保分析所有可能的人類移動**: 設置 `humanSLRootExploreProbWeightless` 和 `humanSLCpuctPermanent`。
*   **獲取更強的人類風格對弈**: 結合 `humanPrior` 和 utility 進行移動選擇，或調整溫度參數。
*   **偏向搜索以預期人類序列**: 設置 `humanSLPlaExploreProbWeightful` 等參數。

---
*文件生成時間: 2026-01-22*
