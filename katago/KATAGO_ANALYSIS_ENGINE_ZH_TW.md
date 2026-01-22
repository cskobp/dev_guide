# KataGo 平行分析引擎

KataGo 包含一個引擎，可用於平行分析大量的局面（整盤對局，或多個對局）。
當正確設定並使用可處理大批量大小 (batch sizes) 的現代 GPU 時，此引擎可能比使用 GTP 引擎和 `kata-analyze` 快得多，因為能夠利用跨局面的批次處理，並且希望擁有更友善的 API。分析引擎主要是為了撰寫工具的人員設計的 - 例如，做為分析伺服器或網站的後端執行。

此引擎可透過以下方式執行：

```./katago analysis -config CONFIG_FILE -model MODEL_FILE```

`cpp/configs/analysis_example.cfg` 中提供了一個範例設定檔。建議調整此設定，例如根據您擁有的記憶體量調整 `nnCacheSizePowerOfTwo`，以及調整 `numSearchThreadsPerAnalysisThread`（在同一局面上同時運作的 MCTS 執行緒數）和 `numAnalysisThreads`（將同時分析的局面數，*每個*局面將使用 `numSearchThreadsPerAnalysisThread` 多個搜尋執行緒）。

請參閱 [分析設定範例](https://github.com/lightvector/KataGo/blob/master/cpp/configs/analysis_example.cfg#L60) 以獲得關於如何調校這些參數的相當詳細的討論。

## 範例程式碼

關於示範如何從 Python 呼叫分析引擎的範例程式碼，請見 [這裡](https://github.com/lightvector/KataGo/blob/master/python/query_analysis_engine_example.py)！

## 協定 (Protocol)

引擎接受標準輸入 (stdin) 上的查詢，並在標準輸出 (stdout) 上輸出結果。每個查詢和每個結果都應該是一行。
協定完全是非同步的 - 可以在任何時候接受 stdin 上的新請求，並且每當這些分析完成時，結果就會出現在 stdout 上，順序可能與提供請求的順序不同。如下所述，每個查詢可能指定要分析的*多個*局面，因此可能產生*多個*結果。

如果 stdin 關閉，引擎將在離開前完成所有已排隊查詢的分析，除非在初始命令列中提供了 `-quit-without-waiting`，在這種情況下，它將嘗試停止所有執行緒並仍然乾淨地離開，但不一定完成當時開啟的任何查詢的分析。

### 查詢 (Queries)

寫入 stdin 的每一行查詢應該是一個具有特定欄位的 JSON 字典。再次注意，每個查詢必須是*單行* - **不**支援多行 JSON 查詢。一個範例查詢如下：

```json
{"id":"foo","initialStones":[["B","Q4"],["B","C4"]],"moves":[["W","P5"],["B","P6"]],"rules":"tromp-taylor","komi":7.5,"boardXSize":19,"boardYSize":19,"analyzeTurns":[0,1,2]}
```

<details>
<summary>
查看格式化後的查詢以利閱讀（但請注意這不是 KataGo 的有效輸入，因為它跨越多行）。
</summary>

```json
{
    "id": "foo",
    "initialStones": [
        ["B", "Q4"],
        ["B", "C4"]
    ],
    "moves": [
        ["W", "P5"],
        ["B", "P6"]
    ],
    "rules": "tromp-taylor",
    "komi": 7.5,
    "boardXSize": 19,
    "boardYSize": 19,
    "analyzeTurns": [0, 1, 2]
}
```
</details>

範例查詢指定了一個具有特定屬性的讓 2 子棋譜，並請求分析對局的第 0, 1, 2 手，這應該會產生三個結果。

欄位說明（包括上述查詢中未出現的一些選用欄位）：

   * `id (string)`: 必填。查詢的任意字串識別碼。
   * `moves (list of [player string, location string] tuples)`: 必填。對局中下的棋步，按照下的順序排列。
     * `player string` 應為 `"B"` 或 `"W"`。
     * `location` 應為像 `"C4"` 這樣的字串，與 [GTP 協定](http://www.lysator.liu.se/~gunnar/gtp/gtp2-spec-draft2/gtp2-spec.html#SECTION000311000000000000000) 中相同。KataGo 也支援超過 `"Z"` 的擴充欄座標位置，例如 `"AA"`, `"AB"`, `"AC"`, ... 或者也可以指定像 `"(0,13)"` 這樣的字串，明確給出整數 X 和 Y 座標。
     * 如果您有一個沒有移動歷史的初始局面，請將此陣列留空（不要編造任意或「假」的移動順序）。
   * `initialStones (list of [player string, location string] tuples)`: 選用。指定對局開始時棋盤上已有的棋子。例如，這些可以是讓子棋的棋子。或者，您可以使用它來指定中盤局面或全盤詰棋，而無需移動歷史。
     * 如果您知道達到某個局面的真實對局棋步，通常最好使用 `moves` 而不是在此指定所有棋子並將 `moves` 留空，因為使用 `moves` 可確保正確的劫/長生劫 (ko/superko) 處理，且類神經網路在未來的預測中也可能會考慮移動歷史。
   * `initialPlayer (player string)`: 選用。指定用於分析對局第一手（第 0 手）的玩家，如果 `moves` 是空列表這會很有用。
   * `rules (string or JSON)`: 必填。使用簡寫字串或完整的 JSON 物件指定對局規則。
     * 請參閱 [GTP 擴充](./GTP_Extensions.md) 中 `kata-get-rules` 和 `kata-set-rules` 的文件，以了解支援規則的描述。
     * KataGo 的一些舊版神經網路不支援某些規則選項。如果是這種情況，將發出警告，且規則將自動轉換為神經網路支援的最接近規則。
   * `komi (integer or half-integer)`: 選用但**強烈**建議。指定對局的貼目。如果未指定，KataGo 將猜測預設值，通常數子法 (area scoring) 為 7.5，但如果是比目法 (territory scoring) 則為 6.5，如果是數子法加按鈕 (area scoring with a button) 則為 7.0。不支援 [-150,150] 範圍之外的貼目值。
   * `whiteHandicapBonus (0|N|N-1)`: 選用。請參閱 [GTP 擴充](./GTP_Extensions.md) 中的 `kata-get-rules` 以了解這些含義。可用於覆蓋讓子紅利 (handicap bonus) 的處理，優先於 `rules`。例如，如果您想要 `chinese` 規則但讓子補償與中國規則通常使用的不同。您也可以總是將此指定為 0 並自行進行任何您喜歡的調整，透過報告適當的 `komi`。
   * `boardXSize (integer)`: 必填。棋盤寬度。不支援大於 19 的尺寸，除非 KataGo 已編譯為支援它們 (cpp/game/board.h, MAX_LEN = 19)。KataGo 的官方神經網路也沒有針對更大的棋盤進行訓練，但對於稍微大一點的尺寸 (21,23,25) 應該可以正常運作。
   * `boardYSize (integer)`: 必填。棋盤高度。不支援大於 19 的尺寸，除非 KataGo 已編譯為支援它們 (cpp/game/board.h, MAX_LEN = 19)。KataGo 的官方神經網路也沒有針對更大的棋盤進行訓練，但對於稍微大一點的尺寸 (21,23,25) 應該可以正常運作。
   * `analyzeTurns (list of integers)`: 選用。要分析對局的哪些回合。0 是初始局面，1 是 `moves[0]` 之後的局面，2 是 `moves[1]` 之後的局面，依此類推。如果未指定此欄位，預設僅分析最後一回合，即所有指定的 `moves` 都下完後的局面。
   * `maxVisits (integer)`: 選用。使用的最大訪問次數 (visits)。如果未指定，預設為分析設定檔中的值。如果指定，則覆蓋它。
   * `rootPolicyTemperature (float)`: 選用。將此設定為 > 1 的值以讓 KataGo 進行更廣泛的搜尋。
   * `rootFpuReductionMax (float)`: 選用。將此設定為 0 以讓 KataGo 更願意嘗試各種棋步。
   * `analysisPVLen (integer)`: 選用。傳送每步棋的 PV（主要變例）的最大長度（不包括第一步）。
   * `includeOwnership (boolean)`: 選用。如果為 true，則報告擁有權預測做為結果。將加倍記憶體使用量並稍微降低效能。
   * `includeOwnershipStdev (boolean)`: 選用。如果為 true，也報告整個搜尋過程中擁有權預測的標準差。
   * `includeMovesOwnership (boolean)`: 選用。如果為 true，也報告每個單獨棋步的擁有權預測。
   * `includeMovesOwnershipStdev (boolean)`: 選用。如果為 true，也報告每個單獨棋步的擁有權預測標準差。
   * `includePolicy (boolean)`: 選用。如果為 true，則報告神經網路原始策略 (raw policy) 做為結果。不會顯著影響效能。
   * `includePVVisits (boolean)`: 選用。如果為 true，報告任何報告的 pv 中每步棋的訪問次數。
   * `includeNoResultValue (boolean)`: 選用。如果為 true，報告每步棋預測的無結果 (no-result) 機率。
   * `avoidMoves (list of dicts)`: 選用。禁止搜尋探索指定玩家的指定棋步，直到搜尋達到一定深度。每個 dict 必須包含這些欄位：
      * `player` - 要被禁止的玩家，`"B"` 或 `"W"`。
      * `moves` - 要被禁止的棋步位置陣列，例如 `["C3","Q4","pass"]`
      * `untilDepth` - 一個正整數，表示在該深度之前禁止棋步。
      * 多個 dict 可以為不同的棋步集合指定不同的 `untilDepth`。如果一個棋步被指定多次且具有不同的 `untilDepth`，行為未定義。
   * `allowMoves (list of dicts)`: 選用。與 `avoidMoves` 相同，除了禁止所有棋步**除了**指定的棋步。目前，dicts 的列表長度也必須為 1。
   * `overrideSettings (object)`: 選用。在此物件中指定任意數量的 `"paramName":value` 條目，以覆蓋此查詢的命令列 `CONFIG_FILE` 中的那些參數。大多數搜尋參數可以被覆蓋：`cpuctExploration`, `winLossUtilityFactor` 等。一些值得注意的參數包括：
      * `playoutDoublingAdvantage (float)`. PDA 值從 -3 到 3 將調整 KataGo 的評估，假設對手在強度/計算上不相等，而是當前玩家擁有的 playouts 是對手的 2^(PDA) 倍。動態版本在 GTP 模式的讓子棋中被用於顯著效果，請參閱 [GTP 範例設定](../cpp/configs/gtp_example.cfg)。
        * `wideRootNoise (float)`. 請參閱 [範例設定](../cpp/configs/analysis_example.cfg) 中此參數的文件
        * `ignorePreRootHistory (boolean)`. 是否在分析期間忽略根節點前的歷史紀錄。
        * `antiMirror (boolean)`. 是否在分析期間啟用反模仿棋。預設關閉。可能會導致有偏差且無意義的勝率和其他分析值，但棋步可能會偵測到並粗略地回應模仿棋。
        * `rootNumSymmetriesToSample (int from 1 to 8)`. 使用多少個（8 個可能的）隨機對稱性來評估神經網路並取平均。預設為 1，但如果將此設定為 2 或 8，由於雜訊減少，您可能會在根節點獲得品質稍高的策略。
        * `humanSLProfile (string)`. 設定 KataGo 應該模仿的人類風格。需要使用像 `b18c384nbt-humanv0.bin.gz` 這樣的人類 SL 模型，通常透過命令列參數 `-human-model`。可用的設定檔 (profiles) 包括：
           * `preaz_20k` 到 `preaz_9d`: 模仿給定等級的人類玩家。（基於 2016 年 AlphaZero 前的佈局風格）。
           * `rank_20k` 到 `rank_9d`: 模仿給定等級的人類玩家（現代佈局風格）。
           * `preaz_{BR}_{WR}` 或 `rank_{BR}_{WR}`: 同上，但預測等級為 BR 的黑棋和等級為 WR 的白棋對抗時會如何下棋，*知道*另一個玩家比他們強/弱。警告：對於等級差異 > 9 級，或與對局中使用的讓子極度不匹配的情況，這可能會由於缺乏訓練數據而超出分佈範圍，模型可能表現不佳！請謹慎實驗。
           * `proyear_1800` 到 `proyear_2023`: 基於指定年份和周圍年份的歷史棋譜，模仿職業和強院生的棋步。
           * 另請參閱下方的「人類 SL 分析指南」一節，了解其他結合此設定會很有趣的參數。
   * `reportDuringSearchEvery (float)`: 選用。指定秒數，在此局面被搜尋時，KataGo 將每隔這麼多秒報告部分分析。
   * `priority (int)`: 選用。分析執行緒將優先處理具有最高優先順序的查詢，除非已開始另一項任務，打破平局時有利於較早的查詢。如果未指定，預設為 0。
   * `priorities (list of integers)`: 選用。當使用 analyzeTurns 時，如果您想要每回合有不同的優先順序，可以使用此代替 `priority`。長度必須與 `analyzeTurns` 相同，`priorities[0]` 是 `analyzeTurns[0]` 的優先順序，`priorities[1]` 是 `analyzeTurns[1]` 的優先順序，依此類推。


### 回應 (Responses)

發生錯誤或警告時，回應將具有以下格式之一：
```
# 一般錯誤
{"error":"ERROR_MESSAGE"}
# 特定查詢欄位的解析錯誤
{"error":"ERROR_MESSAGE","field":"name of the query field","id":"The id string for the query with the error"}
# 特定查詢欄位的解析警告
{"warning":"WARNING_MESSAGE","field":"name of the query field","id":"The id string for the query with the error"}
```
在警告的情況下，查詢仍將繼續產生分析回應。

一個成功的分析回應範例可能是：
```json
{"id":"foo","isDuringSearch":false,"moveInfos":[{"lcb":0.8740855166489953,"move":"Q5","order":0,"prior":0.8934692740440369,"pv":["Q5","R5","Q6","P4","O5","O4","R6","S5","N4","N5","N3"],"scoreLead":8.18535151076558,"scoreMean":8.18535151076558,"scoreSelfplay":10.414442461570038,"scoreStdev":23.987067985850913,"utility":0.7509536097709347,"utilityLcb":0.7717092488727239,"visits":495,"edgeVisits":495,"winrate":0.8666727883983563},{"lcb":1.936558574438095,"move":"D4","order":1,"prior":0.021620146930217743,"pv":["D4","Q5"],"scoreLead":12.300520420074463,"scoreMean":12.300520420074463,"scoreSelfplay":15.386500358581543,"scoreStdev":24.661467510313432,"utility":0.9287495791972984,"utilityLcb":2.8000000000000003,"visits":2,"edgeVisits":2,"winrate":0.9365585744380951},{"lcb":1.9393062554299831,"move":"Q16","order":2,"prior":0.006689758971333504,"pv":["Q16"],"scoreLead":12.97426986694336,"scoreMean":12.97426986694336,"scoreSelfplay":16.423904418945313,"scoreStdev":25.34494674587838,"utility":0.9410896213959669,"utilityLcb":2.8000000000000003,"visits":1,"edgeVisits":1,"winrate":0.9393062554299831},{"lcb":1.9348860532045364,"move":"D16","order":3,"prior":0.0064553022384643555,"pv":["D16"],"scoreLead":12.066888809204102,"scoreMean":12.066888809204102,"scoreSelfplay":15.591397285461426,"scoreStdev":25.65390196745236,"utility":0.9256971928661066,"utilityLcb":2.8000000000000003,"visits":1,"edgeVisits":1,"winrate":0.9348860532045364}],"rootInfo":{"currentPlayer":"B","lcb":0.8672585456293346,"scoreLead":8.219540952281882,"scoreSelfplay":10.456476293719811,"scoreStdev":23.99829921716391,"symHash":"1D25038E8FC8C26C456B8DF2DBF70C02","thisHash":"F8FAEDA0E0C89DDC5AA5CCBB5E7B859D","utility":0.7524437705003542,"visits":500,"winrate":0.8672585456293346},"turnNumber":2}
```
<details>
<summary>
查看格式化後的回應。
</summary>

```json
{
    "id": "foo",
    "isDuringSearch": false,
    "moveInfos": [{
        "lcb": 0.8740855166489953,
        "move": "Q5",
        "order": 0,
        "prior": 0.8934692740440369,
        "pv": ["Q5", "R5", "Q6", "P4", "O5", "O4", "R6", "S5", "N4", "N5", "N3"],
        "scoreLead": 8.18535151076558,
        "scoreMean": 8.18535151076558,
        "scoreSelfplay": 10.414442461570038,
        "scoreStdev": 23.987067985850913,
        "utility": 0.7509536097709347,
        "utilityLcb": 0.7717092488727239,
        "visits": 495,
        "edgeVisits": 495,
        "winrate": 0.8666727883983563
    }, {
        "lcb": 1.936558574438095,
        "move": "D4",
        "order": 1,
        "prior": 0.021620146930217743,
        "pv": ["D4", "Q5"],
        "scoreLead": 12.300520420074463,
        "scoreMean": 12.300520420074463,
        "scoreSelfplay": 15.386500358581543,
        "scoreStdev": 24.661467510313432,
        "utility": 0.9287495791972984,
        "utilityLcb": 2.8000000000000003,
        "visits": 2,
        "edgeVisits": 2,
        "winrate": 0.9365585744380951
    }, {
        "lcb": 1.9393062554299831,
        "move": "Q16",
        "order": 2,
        "prior": 0.006689758971333504,
        "pv": ["Q16"],
        "scoreLead": 12.97426986694336,
        "scoreMean": 12.97426986694336,
        "scoreSelfplay": 16.423904418945313,
        "scoreStdev": 25.34494674587838,
        "utility": 0.9410896213959669,
        "utilityLcb": 2.8000000000000003,
        "visits": 1,
        "edgeVisits": 1,
        "winrate": 0.9393062554299831
    }, {
        "lcb": 1.9348860532045364,
        "move": "D16",
        "order": 3,
        "prior": 0.0064553022384643555,
        "pv": ["D16"],
        "scoreLead": 12.066888809204102,
        "scoreMean": 12.066888809204102,
        "scoreSelfplay": 15.591397285461426,
        "scoreStdev": 25.65390196745236,
        "utility": 0.9256971928661066,
        "utilityLcb": 2.8000000000000003,
        "visits": 1,
        "edgeVisits": 1,
        "winrate": 0.9348860532045364
    }],
    "rootInfo": {
        "currentPlayer": "B",
        "lcb": 0.8672585456293346,
        "scoreLead": 8.219540952281882,
        "scoreSelfplay": 10.456476293719811,
        "scoreStdev": 23.99829921716391,
        "symHash":"1D25038E8FC8C26C456B8DF2DBF70C02",
        "thisHash":"F8FAEDA0E0C89DDC5AA5CCBB5E7B859D",
        "utility": 0.7524437705003542,
        "visits": 500,
        "winrate": 0.8672585456293346
    },
    "turnNumber": 2
}
```
</details>


**所有數值都將以分析設定檔中 `reportAnalysisWinratesAs` 指定的觀點為準。**

此資料的取用者應該嘗試對未來可能新增的頂層欄位，以及 `moveInfos` 或 `rootInfo` 中欄位的增加保持穩健性。

如果提供了 -human-model 並設定了 humanSLProfile，則可以使用各種「人類」欄位。

目前的欄位有：

   * `id`: 查詢時提供的相同 id 字串。
   * `isDuringSearch`: 通常為 false。如果提供了 `reportDuringSearchEvery`，則在搜尋完成前的搜尋過程中，報告時將為 true。每個被搜尋的局面在搜尋完成時，仍然總是會以一個 `isDuringSearch` 為 `false` 的最終回應結束。
   * `turnNumber`: 正在分析的回合數。
   * `moveInfos`: 一個 JSON 字典列表，每個 KataGo 考慮的棋步一個，包含表示分析結果的欄位。目前欄位有：
      * `move` - 正在分析的棋步。
      * `visits` - 子節點收到的訪問次數。
      * `edgeVisits` - 根節點「想要」投入該棋步的訪問次數，因為認為它是合理的或值得搜尋的棋步。可能會因為人類 SL 無權重探索或圖搜尋置換而與 `visits` 不同。
      * `winrate` - 棋步的勝率，[0,1] 之間的浮點數。
      * `scoreMean` - 與 scoreLead 相同。「平均數 (Mean)」有點用詞不當，但此欄位是為了與現有工具保持相容性而存在。
      * `scoreStdev` - 此步棋後最終得分的預測標準差，單位為目。 (注意：由於 MCTS 的機制，目前此數值會有**顯著的高偏差**，儘管它仍然可以作為*相對*指標)。
      * `scoreLead` - 預測當前一方領先的平均目數（少於這麼多目就是一局平局）。
      * `scoreSelfplay` - 在自我對弈期間，此步棋後最終得分的預測平均值，單位為目。 (注意：使用者通常應偏好 scoreLead，因為 scoreSelfplay 可能會因為 KataGo 並非完美地最大化分數而產生偏差)。
      * `prior` - 棋步的策略先驗 (policy prior)，[0,1] 之間的浮點數。
      * `noResultValue` - 預測對局以無結果（例如三劫/長循環）結束的機率，[0,1] 之間的浮點數。僅在 `includeNoResultValue` 為 true 時存在。與類似日本規則但無長生劫規則的規則集相關。
      * `humanPrior` - 棋步的人類策略，[0,1] 之間的浮點數，如果可用的話。
      * `utility` - 棋步的效用，結合了勝率和分數，為 [-C,C] 之間的浮點數，其中 C 是最大可能的效用。最大勝率效用可以由設定中的 `winLossUtilityFactor` 設定，而最大分數效用是 `staticScoreUtilityFactor` 和 `dynamicScoreUtilityFactor` 的總和。
      * `lcb` - 棋步勝率的 [LCB](https://github.com/leela-zero/leela-zero/issues/2282)。單位與勝率相同，但可能落在 [0,1] 之外，因為目前的實作沒有嚴格考慮 0-1 邊界。
      * `utilityLcb` - 棋步效用的 LCB。
      * `weight` - 子節點收到的訪問總權重。較不確定時平均訪問權重可能較低，較確定時較大。
      * `edgeWeight` - 父節點想要投入該棋步的訪問總權重。較不確定時平均訪問權重可能較低，較確定時較大。
      * `order` - KataGo 對棋步的序數排名。0 是最好的，1 是次好的，依此類推。
      * `playSelectionValue` - 用於計算 `order` 的值。KataGo 選擇具有最大 playSelectionValue 的棋步，這是基於勝率、分數和其他屬性的組合。當帶有隨機性下棋時（即在 GTP 中，而不是分析引擎），KataGo 選擇棋步的機率與此值成正比，其次數取決於溫度 (temperature)。
      * `isSymmetryOf` - 另一個合法的棋步。如果 KataGo 設定為由於對稱性而避免搜尋某些棋步 (`rootSymmetryPruning=true`)，則可能出現。如果存在，則此棋步實際上未被搜尋，其所有統計數據和 PV 都是從另一個棋步對稱複製而來的。
      * `pv` - 此步棋之後的主要變例 ("Principal Variation", PV)。長度可能不定，甚至是空的。
      * `pvVisits` - 用於探索 `pv` 中每步棋產生的局面的訪問次數。僅在 `includePVVisits` 為 true 時存在。
      * `pvEdgeVisits` - 用於探索 `pv` 中每步棋的訪問次數。僅在 `includePVVisits` 為 true 時存在。在進行圖搜尋且多個移動序列導致相同局面時與 pvVisits 不同 - pvVisits 將計算該點 PV 局面的總訪問次數，pvEdgeVisits 僅計算使用來自前一個局面的 PV 中的棋步到達該局面的訪問次數。
      * `ownership` - 如果 `includeMovesOwnership` 為 true，則將包含此欄位。這是一個長度為 `boardYSize * boardXSize` 的 JSON 陣列，值從 -1 到 1，表示此步棋後的預測擁有權。值以列優先順序排列，從棋盤左上角 (例如 A19) 開始到右下角 (例如 T1)。
      * `ownershipStdev` - 如果 `includeMovesOwnershipStdev` 為 true，則將包含此欄位。這是一個長度為 `boardYSize * boardXSize` 的 JSON 陣列，值從 0 到 1，表示此步棋後搜尋樹中預測擁有權的每個位置標準差。值以列優先順序排列，從棋盤左上角 (例如 A19) 開始到右下角 (例如 T1)。
   * `rootInfo`: 一個 JSON 字典，包含所請求回合本身的整體統計數據，其計算方式與下一步棋的計算方式相同。目前欄位有：`winrate`, `scoreLead`, `scoreSelfplay`, `utility`, `visits`。以及額外欄位：
      * `thisHash` - 對於每個不同的（棋盤局面，輪到誰下，單劫禁著）組合，極高機率會是唯一的字串。
      * `symHash` - 類似 `thisHash`，除了在對稱等效的局面之間字串將相同。**不**一定考慮超級劫 (superko)。
      * `currentPlayer` - 当前正在分析其可能棋步選擇的玩家，`"B"` 或 `"W"`。
      * `rawWinrate` - 神經網路本身的勝率預測，無任何搜尋。
      * `rawLead` - 神經網路本身的領先預測，無任何搜尋。
      * `rawScoreSelfplay` - 神經網路本身的自我對弈分數預測，無任何搜尋。
      * `rawScoreSelfplayStdev` - 神經網路本身預測的最終對局分數標準差，無任何搜尋。
      * `rawNoResultProb` - 類日規則中無結果對局的原始預測機率。
      * `rawStWrError` - 原始神經網路認為局面勝率的短期不確定性，在搜尋之前。
      * `rawStScoreError` - 原始神經網路認為局面分數的短期不確定性，在搜尋之前。
      * `rawVarTimeLeft` - 原始神經網路對「還剩下多久有意義的對局？」的猜測，無特定單位。當預期這將是一場漫長的對局且勝負變得明朗之前時為大數字。當網路認為勝負已經明朗，或者勝負不明朗但很快就會變得明朗時為小數字。
      * `humanWinrate` - 與 `rawWinrate` 相同，但使用人類模型，如果可用的話。
      * `humanScoreMean` - 與 `rawScoreSelfplay` 相同，但使用人類模型，如果可用的話。
      * `humanScoreStdev` - 與 `rawScoreSelfplayStdev` 相同，但使用人類模型，如果可用的話。
      * `humanStWrError` - 原始神經網路認為當局面由設定的人類風格玩家下出時，勝率的短期不確定性，使用人類模型（如果可用）。
      * `humanStScoreError` - 原始神經網路認為當局面由設定的人類風格玩家下出時，分數評估的短期不確定性，使用人類模型（如果可用）。
      * 注意，像 "winrate" 和 score 這樣的根節點屬性，會比最佳棋步的對應屬性變化更平滑且稍微遲緩，因為 rootInfo 平滑地平均了所有訪問，而最佳棋步可能會快速波動。這是否優於報告最佳棋步的統計數據，取決於目的。
   * `ownership` - 如果 `includeOwnership` 為 true，則將包含此欄位。這是一個長度為 `boardYSize * boardXSize` 的 JSON 陣列，值從 -1 到 1，表示預測擁有權。值以列優先順序排列，從棋盤左上角 (例如 A19) 開始到右下角 (例如 T1)。
   * `ownershipStdev` - 如果 `includeOwnershipStdev` 為 true，則將包含此欄位。這是一個長度為 `boardYSize * boardXSize` 的 JSON 陣列，值從 0 到 1，表示搜尋樹中預測擁有權的每個位置標準差。值以列優先順序排列，從棋盤左上角 (例如 A19) 開始到右下角 (例如 T1)。
   * `policy` - 如果 `includePolicy` 為 true，則將包含此欄位。這是一個長度為 `boardYSize * boardXSize + 1` 的 JSON 陣列，正值總和為 1，表示神經網路在任何搜尋之前的最佳棋步預測，`-1` 表示非法棋步。值以列優先順序排列，從棋盤左上角 (例如 A19) 開始到右下角 (例如 T1)。陣列中的最後一個值是 pass 的策略值。
   * `humanPolicy` - 如果 `includePolicy` 為 true，且有人類模型可用，則將包含此欄位。格式與 `policy` 相同，但它根據設定的 `humanSLProfile` 報告來自人類模型的策略。另請參閱下方的「人類 SL 分析指南」一節。


### 特殊動作查詢 (Special Action Queries)

目前支援一些特殊動作查詢，指示分析引擎執行除了將新局面或一組局面排入分析佇列之外的其他操作。
特殊動作查詢也以 JSON 物件傳送，但根據查詢的不同，具有不同的欄位集。

#### query_version
請求 KataGo 報告其目前版本。必填欄位：

   * `id (string)`: 必填。此查詢的任意字串識別碼。
   * `action (string)`: 必填。應為字串 `query_version`。

範例：
```
{"id":"foo","action":"query_version"}
```

此查詢的回應是回傳一個具有與查詢完全相同的資料和欄位的 json 物件，但有兩個額外欄位：

   * `version (string)`: 一個字串，表示此版本是其後代的最新 KataGo 發布版本，例如 `1.6.1`。
   * `git_hash (string)`: 編譯此 KataGo 版本的精確 git hash，如果 KataGo 是從其 repo 分開編譯或沒有 Git 支援，則為字串 `<omitted>`。

範例：
```
{"action":"query_version","git_hash":"0b0c29750fd351a8364440a2c9c83dc50195c05b","id":"foo","version":"1.6.1"}
```

#### clear_cache
請求 KataGo 清空其類神經網路快取。必填欄位：

   * `id (string)`: 必填。此查詢的任意字串識別碼。
   * `action (string)`: 必填。應為字串 `clear_cache`。

範例：
```
{"id":"foo","action":"clear_cache"}
```
此查詢的回應只是簡單地回傳一個具有與查詢完全相同的資料和欄位的 json 物件。此回應在快取成功清除後發送。如果在當時還有任何正在進行的分析查詢，這些查詢當然會在傳送回應的同時並發地重新填充快取。

說明：KataGo 使用類神經網路查詢結果的快取，當它在搜尋樹中遇到石子配置、輪到誰下、劫狀態、貼目、規則和其他相關選項與之前見過的局面完全相同的局面時，跳過查詢類神經網路。例如，如果某些查詢的搜尋樹由於在同一對局的附近棋步上而重疊，可能會發生這種情況，或者即使在單個分析查詢中，如果搜尋探索了導致相同局面的不同棋步順序（通常，約 20% 的搜尋樹節點因轉置到棋步順序而命中快取，儘管根據局面和搜尋深度，此比例可能會高得多或低得多）。想要清除快取的原因可能包括：

*釋放記憶體使用量 - 清空快取應該會釋放快取中結果所使用的記憶體，這通常是 KataGo 中最大的記憶體使用量。隨著快取重新填充，記憶體使用量當然會再次上升。

*測試或研究 KataGo 在給定訪問次數下的搜尋結果變異性。在清除快取後再次分析一個局面將提供該局面的「新鮮」觀點，更符合 KataGo 可能回傳的各種可能結果，類似於分析引擎完全重啟。每個查詢將重新隨機化用於該查詢的類神經網路對稱性，而不是使用快取的結果，從而給出一個新的且更多樣化的意見。


#### terminate

請求 KataGo 終止零個或多個分析查詢，而不等待它們正常完成。當查詢被終止時，引擎將盡最大努力盡快停止它們的分析，報告到那時為止執行的任何訪問次數的結果。必填欄位：

   * `id (string)`: 必填。此查詢的任意字串識別碼。
   * `action (string)`: 必填。應為字串 `terminate`。
   * `terminateId (string)`: 必填。終止以此 `id` 欄位提交的查詢，而不分析或完成分析它們。
   * `turnNumbers (array of ints)`: 選用。如果提供，僅限制終止該 id 中針對這些回合數的查詢。

範例：
```
{"id":"bar","action":"terminate","terminateId":"foo"}
{"id":"bar","action":"terminate","terminateId":"foo","turnNumbers":[1,2]}
```

終止查詢的回應如果完全沒有在終止前執行任何分析，可能會缺少其資料欄位。在這種情況下，唯一保證在回應上的欄位是 `id` 和 `turnNumber`，以及 `isDuringSearch`（始終為 false），以及一個對於完全未分析的終止查詢唯一的額外布林欄位 `noResults`（始終為 true）。範例：
```
{"id":"foo","isDuringSearch":false,"noResults":true,"turnNumber":2}
```

terminate 查詢本身也會產生一個回應，以確認收到和處理了該動作。回應包括回傳一個與查詢具有完全相同欄位和資料的 json 物件。

回應通常**不**會等待動作的所有效果發生 - 正在進行的搜尋可能需要少量的額外時間才能實際終止並報告其部分結果。想要等待所有終止查詢完成的此 API 客戶端應該自行追蹤其已傳送分析的查詢集，並等待所有查詢完成。這可以透過依賴以下屬性來完成：每個分析查詢，無論是否終止，以及不管 `reportDuringSearchEvery` 為何，都將以恰好一個 `isDuringSearch` 為 `false` 的回覆結束 - 因此，這樣的回覆可以用作分析查詢已完成的標記。（除了在指定了 `-quit-without-waiting` 的引擎關閉期間）。

#### terminate_all

與 terminate 相同，但不需要提供 `terminateId` 欄位，適用於所有查詢，無論其 `id` 為何。必填欄位：

   * `id (string)`: 必填。此查詢的任意字串識別碼。
   * `action (string)`: 必填。應為字串 `terminate_all`。
   * `turnNumbers (array of ints)`: 選用。如果提供，僅限制終止針對這些回合數的查詢。

範例：
```
{"id":"bar","action":"terminate_all"}
{"id":"bar","action":"terminate_all","turnNumbers":[1,2]}
```
terminate_all 查詢本身也會產生一個回應，以確認收到和處理了該動作。回應包括回傳一個與查詢具有完全相同欄位和資料的 json 物件。

請參閱上方關於 terminate 的文件，了解終止查詢的輸出。與 terminate 一樣，terminate_all 的回應**不**會等待動作的所有效果發生，所有舊查詢在終止時的結果將會非同步地回報。

#### query_models

請求 KataGo 報告有關已載入模型的資訊。必填欄位：

   * `id (string)`: 必填。此查詢的任意字串識別碼。
   * `action (string)`: 必填。應為字串 `query_models`。

範例：
```json
{"id":"foo","action":"query_models"}
```

此查詢的回應將回傳傳入的相同鍵，以及包含已載入模型陣列的鍵 "models"。陣列中的每個模型都包含諸如模型名稱、內部名稱、最大批次大小、是否使用人類 SL 設定檔、版本和 FP16 使用情況等詳細資訊。範例：

```json
{
  "id": "foo",
  "action": "query_models",
  "models": [
    {
      "name": "kata1-b18c384nbt-s9732312320-d4245566942.bin.gz",
      "internalName": "kata1-b18c384nbt-s9732312320-d4245566942",
      "maxBatchSize": 256,
      "usesHumanSLProfile": false,
      "version": 14,
      "usingFP16": "auto"
    },
    {
      "name": "b18c384nbt-humanv0.bin.gz",
      "internalName": "b18c384nbt-humanv0",
      "maxBatchSize": 256,
      "usesHumanSLProfile": true,
      "version": 15,
      "usingFP16": "auto"
    }
  ]
}
```

## 人類 SL 分析指南 (Human SL Analysis Guide)

截至 2024 年 7 月發布的 1.15.0 版本，KataGo 支援一個新的人類監督學習 ("human SL") 模型 `b18c384nbt-humanv0.bin.gz`，該模型在大量人類對局上進行訓練，以預測各個不同等級玩家的棋步以及這些對局的結果。人們才剛開始嘗試使用此模型，在分析或對局方面可能有許多創造性的可能性。

另請參閱 [GTP 人類 5k 範例設定](../cpp/configs/gtp_human5k_example.cfg) 中關於 "humanSL" 和其他參數的註解。雖然這是一個 GTP 設定檔，而不是分析引擎設定檔，但關於 "humanSL" 參數行為的內嵌文件同樣適用於分析引擎。

同樣地，對於 GTP 使用者，儘管以下說明是從分析引擎的角度撰寫的，但大部分說明同樣適用於 GTP 對局和分析（由 Lizzie 或 Sabaki 等引擎使用）。

以下是一些關於使用人類 SL 模型的註解和建議起點。

### 設定使用模型

有兩種傳入人類 SL 模型的方式。

* 基本預期方式：除了傳入 KataGo 的正常模型外，還傳入額外的參數 `-human-model b18c384nbt-humanv0.bin.gz`。
   * 例如：`./katago analysis -config configs/analysis_example.cfg -model models/kata1-b28c512nbt-s7382862592-d4374571218.bin.gz -human-model models/b18c384nbt-humanv0.bin.gz`。
   * 此外，透過查詢上的 `overrideSettings` 提供 `humanSLProfile`。請參閱上方關於 `overrideSettings` 的文件。
   * 此外，請確保在查詢中請求 `"includePolicy":true`。
   * 然後，新的 `humanPolicy` 欄位將在結果中報告，表示 KataGo 對符合給定 humanSLProfile（例如 5 級 rank）的隨機人類玩家可能如何下棋的預測。
   * 如果未設定更多參數，KataGo 的主模型仍將用於所有其他分析。
   * 如果設定了更多參數，KataGo 的主模型和人類 SL 模型的有趣*混合*用法是可能的。請參閱下方的一些「食譜」。

* 替代方式：通過 `-model b18c384nbt-humanv0.bin.gz` 代替 KataGo 的正常模型，獨佔使用人類模型。
   * 例如：`./katago analysis -config configs/analysis_example.cfg -model models/b18c384nbt-humanv0.bin.gz`。
   * 此外，透過查詢上的 `overrideSettings` 提供 `humanSLProfile`。請參閱上方關於 `overrideSettings` 的文件。（在 GTP 的情況下，在 GTP 設定檔中設定 `humanSLProfile`，如果您想動態更改，則在執行時透過 `kata-set-param` 更新）。
   * 然後，KataGo 將在設定的設定檔下使用人類模型進行所有分析，而不是其正常的典型超人類分析。
   * 注意，如果您使用許多訪問次數進行搜尋（甚至只是少數訪問！），通常您可以預期 KataGo 將**不會**符合給定 humanSLProfile 玩家的強度，而是會更強，因為搜尋可能會解決較弱等級玩家無法解決的許多戰術。
      * 人類 SL 模型的訓練方式是，僅使用*一次*訪問和完全溫度（即按比例選擇隨機棋步，而不是總是選擇最佳棋步），將最接近給定等級玩家可能下出的棋。這應該直到中高段位均為真，此時原始模型可能會開始不足，需要超過 1 次訪問才能保持強度。

   * 如果作為主模型使用，人類 SL 模型報告的勝率和分數可能會比 KataGo 的正常模型有更多病態和偏差，這是因為它訓練的 SGF 數據所致。
      * 例如，在讓子棋中，它可能無法報告準確的分數或勝率，因為在記錄的人類讓子棋 SGF 中，白方通常是比黑方強的玩家，和/或某些伺服器可能讓子不足，導致結果偏差。
      * 例如，在分先對局中，它可能會在大幅波動後或極端局面中報告錯誤的分數和勝率，這是由於人類玩家可能如何認輸或情緒化下棋 (go on tilt)，或者由於訓練數據中記錄的玩家等級不準確，或者由於訓練數據中有一定比例的「降級/升級」(sandbagger/airbagger) 對局或 AI 作弊對局。


### 各種 HumanSL 用法的食譜

這是一些範例用法的簡要指南，希望能為可能的嘗試提供一點靈感。

除了早先明確記錄為屬於外部 json 查詢物件的參數（例如 `includePolicy`, `maxVisits`）外，以下描述的參數應設定在查詢的 `overrideSettings` 內。例如：

```
"overrideSettings":{"humanSLProfile":"rank_3d","ignorePreRootHistory":false,"humanSLRootExploreProbWeightless":0.5,"humanSLCpuctPermanent":2.0}
```

**不要**將此類參數設定為外部 json 查詢物件的鍵，因為這將無效。如果意外這樣做，KataGo 應該會發出警告。如果需要，您也可以在分析設定檔中硬編碼參數，例如 `humanSLProfile = rank_3d`。

本指南也適用於 GTP 使用者，用於設定對局和基於 GTP 的分析（例如 kata-analyze）。對於 GTP，在 GTP 設定檔中設定參數，並可選地透過 `kata-set-param` 動態更改（[GTP 擴充](./GTP_Extensions.md)）。

#### 類人下棋 (Human-like play)

若只是簡單地模仿給定等級玩家的下棋方式，建議的方式是：

* 適當地設定 `humanSLProfile`。
* 將 `ignorePreRootHistory` 設定為 `false`（通常分析會忽略歷史以避免受移動順序偏差影響，但人類絕對會根據最近的棋步表現出不同行為！）。
* 發送一個帶有任意數量訪問（甚至 1 次訪問）且在外部 json 查詢物件上指定 `"includePolicy":true` 的查詢。
* 從結果中讀取 `humanPolicy` 並根據策略機率選擇一個隨機棋步。

注意，由於訓練中的舊歷史人類對局在記錄 pass 方面可能有所不同，人類 SL 網路在某些 humanSLProfiles 的某些棋盤局面下可能會難以適當地 pass。對於某些較弱的等級，人類 SL 網路可能會過早 pass 並以不希望的方式留下未完成的局面。如果是這樣，那麼以下方法應該很有效：

* 適當地設定 `humanSLProfile`。
* 將 `ignorePreRootHistory` 設定為 `false`。
* 發送一個至少有幾次訪問的查詢，以便 KataGo 可以自行搜尋該局面（例如 > 50 次訪問），仍然帶有 `"includePolicy":true`。
* 如果結果中的最佳 moveInfo（`"order":0` 的 moveInfo）是 pass，則 pass。
* 否則，讀取 `humanPolicy` 並根據策略機率選擇一個隨機棋步，但排除 pass。

(注意：對於 GTP 使用者，[gtp_human5k_example.cfg](../cpp/configs/gtp_human5k_example.cfg) 已經預設進行人類模仿對局，並帶有一些 GTP 特定的 hack 和參數，以讓 KataGo 的棋步選擇以上述方式使用人類 SL 模型。請參閱該設定檔中的文件。)

選用：您也可以將 `rootNumSymmetriesToSample` 設定為 `2`，或設定為 `8` 而不是預設的 `1`。這將稍微增加延遲，但透過平均更多對稱性來提高人類策略的品質，這在嚴重依賴原始人類策略而沒有任何搜尋時可能會很好。

#### 確保分析所有可能的人類棋步

對於分析和對局檢討，如果您想確保所有具有高人類策略的棋步都獲得大量訪問，您可以嘗試如下設定：

* 按需設定 `humanSLProfile` 和 `ignorePreRootHistory` 和 `rootNumSymmetriesToSample`。
* 將 `humanSLRootExploreProbWeightless` 設定為 `0.5`（花費約 50% 的 playouts 來探索人類棋步，以一種不影響 KataGo 評估的無權重方式）。
* 將 `humanSLCpuctPermanent` 設定為 `2.0` 或類似值（當探索人類棋步時，確保高人類策略的棋步獲得許多訪問，即使它們輸很多）。如果您想減少被判定為非常糟糕的棋步的訪問，請將其設定得較低。
* 確保整體使用大量訪問。

#### 可能有趣的指標

如果您已確保分析了所有可能的人類棋步，那麼可能有一些有趣的指標可以從人類策略中推導出來：

* 如果從人類策略中採樣，玩家在當前棋步後的平均得分，`sum(scoreLead * humanPrior) / sum(humanPrior)`。
* 如果從人類策略中採樣，由於當前棋步導致的得分變化的標準差，`sqrt(sum((scoreLead-m)**2 * humanPrior) / sum(humanPrior))`，其中 m 是上述平均值。
* 當前等級與高幾級的玩家之間，所下棋步的人類策略差異（發送帶有其他 humanSLProfiles 的 1 次訪問查詢以獲取其他等級的 humanPolicy）。
* 像是「(實際得分 - 平均得分) / 得分標準差」這樣的東西，是否是除了單純的絕對得分損失之外，判斷錯誤的一種有趣的替代方案？
* 根據高 4 級的玩家下那一手棋的可能性降低的程度來排序或加權錯誤，或其他類似的指標，是否是將對局檢討偏向更適合玩家等級的錯誤的好方法？

#### 如何獲得更強的人類風格對局

如果您想獲得人類*風格*的棋步，但下得比給定人類等級*更強*（即僅匹配風格，但不一定匹配強度），或者補償高段位對局中原始神經網路的強度差距，您可以嘗試這樣做：

* 確保分析所有人類可能的棋步，如前一節所述。
* 在所有 `moveInfos` 中選擇一個隨機棋步，機率與 `humanPrior * exp(utility / 0.5)` 成正比。這將遵循 humanPrior，但當棋步開始損失超過 0.5 效用（約 25% 勝率和/或一定數量的分數）時，平滑地衰減其機率。按需調整除數 0.5。
* 選用：還可以將 `staticScoreUtilityFactor` 設定為 `0.5`。（顯著增加分數對效用的影響，相對於僅勝率）。
* 另一個影響強度的重要方式是降低溫度設定。
    * 在分析引擎中，這將通過額外提高 `humanPrior ** (1/temperature)` 來實現，並重新正規化。
    * 在 GTP 中，這可以通過將 `chosenMoveTemperatureOnlyBelowProb` 設定為 `1.0` 然後降低 `chosenMoveTemperatureEarly` 和 `chosenMoveTemperature` 來完成。
    * 在任何一種情況下，降低溫度都會使機器人下得更具決定性，並模仿更窄部分的人類分佈，但也可能提高強度。
* 像這樣的混合方法，配合適當調整的數值，是補償人類 SL 模型在僅 1 次訪問時不再能匹配頂尖玩家強度差距的好方法，但可能需要實驗來調整數值。

注意：對於 GTP 使用者，參數 `humanSLChosenMovePiklLambda` 正是用於執行此基於 exp 的機率縮放。
[gtp_human9d_search_example.cfg](../cpp/configs/gtp_human9d_search_example.cfg) 中給出了一組範例參數，即使您使用的是分析引擎模式而不是 GTP，閱讀其中一些內容也可能有指導意義。

#### 強烈偏向搜尋以預期類人順序而非 KataGo 順序

目前還沒有多少人嘗試過這個，但在理論上這可能會產生非常有趣的效果！這將影響 KataGo 分配給各種棋步的勝率和分數，使其更接近它預期如果按照設定的人類風格玩家可能下出的方式進行的各種變化，但仍然使用 KataGo 自己的判斷來評估這些變化的終點。

* 按需設定 `humanSLProfile` 和 `ignorePreRootHistory` 和 `rootNumSymmetriesToSample`。
* 將 `humanSLPlaExploreProbWeightful` 和 `humanSLOppExploreProbWeightful` 設定為 `0.9`（在每個節點花費約 90% 的訪問使用人類策略，以一種*有權重*的方式，這*會*使 KataGo 的評估產生偏差）。
* 將 `humanSLRootExploreProbWeightful` 設定為 `0.5`（在根節點使用約 50% 的 playouts 來探索人類棋步，另外 50% 使用 KataGo 的正常策略）。
* 將 `humanSLCpuctPermanent` 設定為 `1.0` 或按需設定（當使用人類策略時，衰減策略，避免將 *太多* 訪問投入到效用為 1.0 或勝率差 50% 的事物上）。
* 將 `useUncertainty` 設定為 `false`，`subtreeValueBiasFactor` 設定為 `0.0`，`useNoisePruning` 設定為 `false`（重要，停用一些增加強度但極有可能干擾此種有權重偏差的搜尋功能）。

#### 偏向搜尋以預期類人順序而非 KataGo 順序，但僅針對對手

這種設定對於讓子棋或試圖引出陷阱和其他對手感知戰術可能很有趣。當然，可能需要實驗和調校才能使其運作良好，它可能運作不佳，或者運作得「太」好而適得其反。

* 按需設定 `humanSLProfile` 和 `ignorePreRootHistory` 和 `rootNumSymmetriesToSample`。
   * 這也可能是一個實驗各種具有不對稱等級的 `preaz_{BR}_{WR}` 或 `rank_{BR}_{WR}` 設定的非常有趣的地方。
* 將 `humanSLOppExploreProbWeightful` 設定為 `0.8`（在每個節點花費約 80% 的訪問使用人類策略，以一種有權重的方式使 KataGo 的數值產生偏差，但僅針對對手！）。
* 將 `humanSLCpuctPermanent` 設定為 `0.5` 或按需設定（當使用人類策略時，衰減策略，避免將 *太多* 訪問投入到效用為 0.5 或勝率差 25% 的事物上）。
* 按需或按讓子棋典型設定 `playoutDoublingAdvantage`。
* 將 `useUncertainty` 設定為 `false`，`subtreeValueBiasFactor` 設定為 `0.0`，`useNoisePruning` 設定為 `false`（重要，停用一些增加強度但極有可能干擾此種有權重偏差的搜尋功能）。
   * 將 `useNoisePruning` 設定為 `false` 可能是這些之中最重要的 - 它在正常使用中增加的強度最少，但可能干擾最大。人們可以嘗試仍然啟用其他兩個以增加強度。
