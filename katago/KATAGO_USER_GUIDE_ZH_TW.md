# KataGo 使用指南

* [概覽](#概覽)
* [訓練歷史與研究](#訓練歷史與研究)
* [下載位置](#下載位置)
* [設定與執行 KataGo](#設定與執行-katago)
  * [圖形介面 (GUIs)](#圖形介面-guis)
  * [Windows 與 Linux](#windows-與-linux)
  * [MacOS](#macos)
  * [OpenCL vs CUDA vs TensorRT vs Eigen](#opencl-vs-cuda-vs-tensorrt-vs-eigen)
  * [如何使用](#如何使用)
  * [效能調校](#效能調校)
  * [常見問題與故障排除](#常見問題與故障排除)
    * [特定 GPU 或驅動程式問題](#特定-gpu-或驅動程式問題)
    * [常見問題](#常見問題)
    * [其他問題](#其他問題)
* [開發者功能](#開發者功能)
  * [GTP 擴充指令](#gtp-擴充指令)
  * [分析引擎](#分析引擎)
* [編譯 KataGo](#編譯-katago)
* [原始碼概覽](#原始碼概覽)
* [自我對弈訓練](#自我對弈訓練)
* [貢獻者](#貢獻者)
* [授權條款](#授權條款)

## 概覽

KataGo 的公開分散式訓練正在進行中！請至 https://katagotraining.org/ 查看更多詳情，下載最新最強的類神經網路，如果您想協助 KataGo 更上一層樓，也可以了解如何貢獻！也歡迎查看電腦圍棋 [discord 頻道](https://discord.gg/bqkZAz3)！

截至 2025 年，KataGo 仍然是網路上可取得的最強開源圍棋機器人之一。KataGo 使用類似 AlphaZero 的流程進行訓練，並加入了許多增強和改進，能夠完全從零開始迅速達到頂尖水準，無需任何外部資料，僅透過自我對弈進步。部分改進利用了圍棋特有的特徵和訓練目標，但許多技術是通用的，也可應用於其他遊戲。因此，早期訓練比其他自我對弈訓練的機器人快得多——只需幾張強大的 GPU 跑幾天，任何研究人員或愛好者都能將一個類神經網路從零訓練到 19x19 棋盤上的業餘高段水準。如果調校得當，使用*單張*高階消費級 GPU 進行訓練，可能在幾個月內就能從零訓練出超人類水準的機器人。

實驗上，KataGo 在 2020 年 6 月的訓練結束時，確嘗試了一些使用外部資料的有限方式，並持續在最近的公開分散式訓練 "kata1" (https://katagotraining.org/) 中使用。外部資料對於達到頂尖水準並非必要，但在對抗某些對手時似乎能提供些微優勢，並且作為分析工具時，對於那些在自我對弈中未出現但在人類對局或使用者希望分析的局面，能提供顯著的幫助。

KataGo 引擎旨在成為圍棋玩家和開發者的實用工具，支援以下功能：
* 估算地與目數差，而不僅僅是「勝率」，這有助於分析級位和業餘段位玩家的對局，而不僅限於職業/超人類水準中會影響勝負的著手。
* 注重最大化目數，使其在讓子棋中落後很多時仍能強力追趕，並在領先的官子階段減少鬆懈的著手。
* 支援非標準的貼目值（包括整數值）以及良好的高讓子棋對局能力。
* 支援 7x7 到 19x19 的棋盤大小，截至 2020 年 5 月，它在 9x9 和 13x13 棋盤上也可能是最強的開源機器人。
* 支援多種[規則](https://lightvector.github.io/KataGo/rules.html)，包括在幾乎所有常見情況下符合日本規則的規則，以及類似古石數法規則。
* 對於工具/後端開發者 - 支援基於 JSON 的分析引擎，可以高效地批次評估多個對局，並且比 GTP 更易於使用。

## 訓練歷史與研究

以下是一些關於 KataGo 研究和訓練的文件/論文/文章連結！

* 關於 KataGo 使用的主要新想法和技術的論文：[Accelerating Self-Play Learning in Go (arXiv)](https://arxiv.org/abs/1902.10565)。許多具體參數已過時，但通用方法仍被沿用。

* 自那時以來已發現許多重大的進一步改進，並已納入 KataGo 更近期的訓練中，記錄於此：[KataGoMethods.md](docs/KataGoMethods.md)。

* KataGo 擁有蒙地卡羅圖搜尋 (Monte-Carlo Graph Search) 的完整實作，將 MCTS 擴展至在圖 (Graph) 上運作，而不僅僅是樹 (Tree)！相關解釋可見此處：[Monte-Carlo Graph Search from First Principles](docs/GraphSearch.md)。此解釋寫得較為通用（非特定於 KataGo），旨在填補學術文獻中解釋材料的一大空白，希望能對他人有所幫助！

* 非常感謝 [Jane Street](https://www.janestreet.com/) 支援 KataGo 主要早期公開訓練的運算資源，以及許多小型的測試訓練和實驗。關於初始發布及後續一些有趣實驗的部落格文章：
    * [Accelerating Self-Play Learning in Go](https://blog.janestreet.com/accelerating-self-play-learning-in-go/)
    * [Deep-Learning the Hardest Go Problem in the World](https://blog.janestreet.com/deep-learning-the-hardest-go-problem-in-the-world/).

關於 KataGo 較舊訓練的更多細節，包括與其他機器人的比較，請見 [Older Training History and Research](TrainingHistory.md)！

如果您想詢問關於 KataGo 的一般資訊或運作原理，或是關於 KataGo 以外的過去圍棋機器人，可以考慮加入電腦圍棋 [discord 頻道](https://discord.gg/bqkZAz3)。

## 下載位置
KataGo 的 Windows 和 Linux 預編譯執行檔可以在 [發布頁面 (releases page)](https://github.com/lightvector/KataGo/releases) 找到。

最新的類神經網路可在 [https://katagotraining.org/](https://katagotraining.org/) 取得。

## 設定與執行 KataGo
KataGo 僅實作了一個 GTP 引擎，這是一種圍棋軟體使用的簡單文字協定。它本身**沒有**圖形介面。因此，通常您會希望將 KataGo 與 GUI 或分析程式一起使用。其中一些程式會在下載中包含 KataGo，這樣您就可以從一個地方取得所有東西，而無需分開下載並管理檔案路徑和指令。

### 圖形介面 (GUIs)
這絕不是一份完整的清單 - 市面上有很多選擇。但是，截至 2020 年，一些較簡單和/或受歡迎的選擇可能是：

* [KaTrain](https://github.com/sanderland/katrain) - KaTrain 可能是非技術使用者最容易設定的，提供一體化的套件（無需分開下載 KataGo！），適合較弱玩家的調整強度機器人，以及良好的分析功能。
* [Lizzie](https://github.com/featurecat/lizzie) - Lizzie 對於長時間互動分析和視覺化分析過程非常受歡迎。Lizzie 也提供一體化套件。但是請記住，KataGo 的 OpenCL 版本在第一次啟動時可能需要相當長的時間進行調校和載入，如[此處](#opencl-vs-cuda)所述，而 Lizzie 在顯示此進度方面做得不好。如果發生實際錯誤或失敗，Lizzie 的介面也不擅長解釋這些錯誤，可能會看起來像永遠卡住。Lizzie 包含的 KataGo 版本相當強，但可能不總是最新的或最強的，所以一旦您使其運作，您可能會想要從 [發布頁面](https://github.com/lightvector/KataGo/releases) 下載 KataGo 和較新的網路並替換 Lizzie 的版本。
* [Ogatak](https://github.com/rooklift/ogatak) 是一個專為 KataGo 設計的 GUI，強調以快速、反應靈敏的方式顯示基礎資訊。它不包含 KataGo。
* [q5Go](https://github.com/bernds/q5Go) 和 [Sabaki](https://sabaki.yichuanshen.de/) 是通用的 SGF 編輯器和 GUI，支援 KataGo，包括 KataGo 的目數估算和許多高品質功能。

通常，對於不提供一體化套件的 GUI，您需要下載 KataGo（或您選擇的任何其他圍棋引擎！）並告訴 GUI 執行您的引擎的正確命令列，包含正確的檔案路徑。關於 KataGo 的命令列介面詳情，請參閱下方的 [如何使用](#如何使用)。

### Windows 與 Linux

KataGo 目前官方支援 Windows 和 Linux，[每次發布都提供預編譯執行檔](https://github.com/lightvector/KataGo/releases)。在 Windows 上，執行檔通常可以直接運作；在 Linux 上，如果遇到系統函式庫版本問題，作為替代方案，[從原始碼編譯](KATAGO_COMPILING_ZH_TW.md) 通常很直接。並非所有不同的作業系統版本和編譯器都經過測試，所以如果遇到問題，請隨時開啟 issue。當然，KataGo 也可以在 Windows 或 Linux 上從原始碼編譯。在 Windows 上支援 MSVC 或 MinGW 編譯器，在 Linux 上支援常見編譯器如 g++，詳情見下文。

### MacOS
社群也為 MacOS 上的 [Homebrew](https://brew.sh) 提供 KataGo 套件 - 那裏的發布可能會比官方發布稍慢。

使用 `brew install katago`。最新的設定檔和網路安裝在 KataGo 的 `share` 目錄中。透過 `brew list --verbose katago` 找到它們。執行 katago 的基本方式是 `katago gtp -config $(brew list --verbose katago | grep 'gtp.*\.cfg') -model $(brew list --verbose katago | grep .gz | head -1)`。您應該根據此處的發布說明選擇網路，並像安裝 KataGo 的其他方式一樣自訂提供的範例設定。

### OpenCL vs CUDA vs TensorRT vs Eigen
KataGo 有四種後端：OpenCL (GPU)、CUDA (GPU)、TensorRT (GPU) 和 Eigen (CPU)。

快速摘要：
  * **為了輕鬆讓它運作，如果您有任何不錯或一般的 GPU，請嘗試 OpenCL。**
  * **為了在 NVIDIA GPU 上獲得通常更好的效能，請嘗試 TensorRT**，但您可能需要從 Nvidia 安裝 TensorRT。
  * 如果您沒有 GPU 或您的 GPU 太舊/太弱無法運作 OpenCL，而您只想要一個純 CPU 的 KataGo，請使用 Eigen 搭配 AVX2。
  * 如果您的 CPU 很舊或在不支援 AVX2 的低階裝置上，請使用不帶 AVX2 的 Eigen。
  * CUDA 後端可以用於安裝了 CUDA+CUDNN 的 NVIDIA GPU，但效能可能比 TensorRT 差。

更詳細說明：
  * OpenCL 是一個通用 GPU 後端，應該能與任何支援 [OpenCL](https://zh.wikipedia.org/wiki/OpenCL) 的 GPU 或加速器運作，包括 NVIDIA GPU、AMD GPU，以及基於 CPU 的 OpenCL 實作或像 Intel 整合顯示卡之類的東西。這是 KataGo 最通用的 GPU 版本，不需要像 CUDA 那樣複雜的安裝，所以只要您有相當現代的 GPU，它最有可能直接運作。**但是，第一次執行時也需要花一些時間進行自我調校。** 對於許多系統，這將花費 5-30 秒，但在少數較舊/較慢的系統上，可能需要幾分鐘或更長時間。此外，OpenCL 實作的品質有時不一致，特別是對於 Intel 整合顯示卡和超過幾年的 AMD GPU，所以它可能無法在非常舊的機器上運作，以及特定的有 Bug 的較新 AMD GPU，另請參閱 [特定 GPU 或驅動程式問題](#特定-gpu-或驅動程式問題)。
  * CUDA 是專屬於 NVIDIA GPU 的 GPU 後端（無法與 AMD 或 Intel 或任何其他 GPU 運作），需要安裝 [CUDA](https://developer.nvidia.com/cuda-zone) 和 [CUDNN](https://developer.nvidia.com/cudnn) 以及現代 NVIDIA GPU。在大多數 GPU 上，OpenCL 實作的效能實際上會擊敗 NVIDIA 自己的 CUDA/CUDNN。例外情況是支援 FP16 和 Tensor Cores 的高階 NVIDIA GPU，在這種情況下，有時這個更好，有時那個更好。
  * TensorRT 類似於 CUDA，但僅使用 NVIDIA 的 TensorRT 框架，透過更最佳化的核心來執行類神經網路。對於現代 NVIDIA GPU，只要 CUDA 能運作它應該也能運作，並且通常比 CUDA 或任何其他後端更快。
  * Eigen 是一個 *CPU* 後端，應該能廣泛運作而*不需要* GPU 或特殊的驅動程式。如果您沒有好的 GPU 或根本沒有 GPU，請使用此選項。它會比 OpenCL 或 CUDA 慢得多，但在好的 CPU 上，如果使用較小的（15 或 20）區塊類神經網路，通常仍能達到每秒 10 到 20 個 playouts。Eigen 也可以編譯為支援 AVX2 和 FMA，這能為過去幾年的 Intel 和 AMD CPU 提供巨大的效能提升。但是，它根本無法在不支援這些進階向量指令的舊 CPU（甚至可能是一些近期但低功耗的現代 CPU）上運作。

對於**任何**實作，如果您關心最佳效能，建議您調校使用的執行緒數量，因為這可能會造成 2-3 倍的速度差異。請參閱下方的「效能調校」。然而，如果您主要只是想讓它運作，那麼預設未調校的設定應該也還算合理。

### 如何使用
KataGo 只是一個引擎，沒有自己的圖形介面。所以通常您會希望將 KataGo 與 [GUI 或分析程式](#圖形介面-guis)一起使用。
如果您在設定時遇到任何問題，請查看 [常見問題與故障排除](#常見問題與故障排除)。

**首先**：執行類似以下的指令以確保 KataGo 正常運作，並使用您[下載](https://github.com/lightvector/KataGo/releases/tag/v1.4.5)的類神經網路檔案。在 OpenCL 上，它也會針對您的 GPU 進行調校。
```
./katago.exe benchmark                                                   # 如果您有 default_gtp.cfg 和 default_model.bin.gz
./katago.exe benchmark -model <NEURALNET>.bin.gz                         # 如果您有 default_gtp.cfg
./katago.exe benchmark -model <NEURALNET>.bin.gz -config gtp_custom.cfg  # 使用此 .bin.gz 類神經網路和此 .cfg 檔案
```
它會告訴您一個好的執行緒數量。編輯您的 .cfg 檔案並將 "numSearchThreads" 設定為該數量以獲得最佳效能。

**或者**：執行此指令讓 KataGo 根據回答一些問題為您產生自訂的 gtp 設定檔：
```
./katago.exe genconfig -model <NEURALNET>.bin.gz -output gtp_custom.cfg
```

**接著**：類似以下的指令將執行 KataGo 引擎。這是要給您的 [GUI 或分析程式](#圖形介面-guis) 的指令，以便它可以執行 KataGo。
```
./katago.exe gtp                                                   # 如果您有 default_gtp.cfg 和 default_model.bin.gz
./katago.exe gtp -model <NEURALNET>.bin.gz                         # 如果您有 default_gtp.cfg
./katago.exe gtp -model <NEURALNET>.bin.gz -config gtp_custom.cfg  # 使用此 .bin.gz 類神經網路和此 .cfg 檔案
```

在輸入 GUI 程式的 KataGo 指令時，您可能需要指定不同的路徑，例如：
```
path/to/katago.exe gtp -model path/to/<NEURALNET>.bin.gz
path/to/katago.exe gtp -model path/to/<NEURALNET>.bin.gz -config path/to/gtp_custom.cfg
```

#### 擬人風格對弈與分析

如果您從 https://github.com/lightvector/KataGo/releases/tag/v1.15.0 下載人類 SL 模型 b18c384nbt-humanv0.bin.gz，並執行類似以下的指令，同時提供一般模型和人類 SL 模型，您也可以讓 KataGo 模仿人類下棋：
```
./katago.exe gtp -model <NEURALNET>.bin.gz -human-model b18c384nbt-humanv0.bin.gz -config gtp_human5k_example.cfg
```

[gtp_human5k_example.cfg](cpp/configs/gtp_human5k_example.cfg) 設定 KataGo 模仿 5 級 (5k) 水準的玩家。您也可以更改它以模仿其他等級，以及做更多事情，包括讓 KataGo 以人類風格下棋但仍保持強大水準，或以有趣的方式進行分析。請閱讀設定檔本身以了解其中一些可能性的文件！

另請參閱[此指南](https://github.com/lightvector/KataGo/blob/master/docs/Analysis_Engine.md#human-sl-analysis-guide)以了解如何使用人類 SL 模型，這是從下面提到的基於 JSON 的分析引擎的角度撰寫的，但也適用於 gtp。

#### 其他指令：

執行基於 JSON 的 [分析引擎](KATAGO_ANALYSIS_ENGINE_ZH_TW.md)，可以為後端圍棋服務進行高效的批次評估：

   * `./katago analysis -model <NEURALNET>.gz -config <ANALYSIS_CONFIG>.cfg`

執行高效能的競賽引擎，將讓一組機器人互相對弈，共享相同的 GPU 批次和 CPU：

   * `./katago match -config <MATCH_CONFIG>.cfg -log-file match.log -sgf-output-dir <DIR TO WRITE THE SGFS>`

強制 OpenCL 調校器重新調校：

   * `./katago tuner -config <GTP_CONFIG>.cfg`

列印版本：

   * `./katago version`


### 效能調校

最佳化 KataGo 效能最重要的參數是使用的執行緒數量 - 這很容易造成 2 或 3 倍的差異。

其次，您也可以閱讀 GTP 設定檔 (`default_gtp.cfg` 或 `gtp_example.cfg` 或 `configs/gtp_example.cfg` 等) 中的參數。裡面描述了許多其他設定，您可以設定它們來調整 KataGo 的資源使用，或選擇使用哪些 GPU。您也可以調整像是 KataGo 的認輸門檻、思考行為 (pondering) 或效用函數 (utility function) 等項目。大多數參數直接記錄在 [範例設定檔](cpp/configs/gtp_example.cfg) 中。許多參數也可以在透過上述 `genconfig` 指令產生設定檔時互動式地設定。


### 常見問題與故障排除
本節總結了執行 KataGo 時的一些常見問題與疑難雜症。

#### 特定 GPU 或驅動程式問題
如果您在嘗試執行 benchmark 或程式本身時觀察到 KataGo 當機，且您擁有以下其中一種 GPU，這可能是原因。

* **AMD Radeon RX 5700** - 自從此 GPU 發布以來，AMD 的 OpenCL 驅動程式就一直有 Bug，截至 2020 年 5 月，AMD 仍未發布修復程式。如果您使用此 GPU，您將無法執行 KataGo（Leela Zero 和其他圍棋引擎可能也會失敗），如果做其他使用 OpenCL 的科學或數學運算，可能也會獲得錯誤的計算結果或當機。例如請見這些 reddit 討論串：[[1]](https://www.reddit.com/r/Amd/comments/ebso1x/its_not_just_setihome_any_mathematic_or/) 或 [[2]](https://www.reddit.com/r/BOINC/comments/ebiz18/psa_please_remove_your_amd_rx5700xt_from_setihome/) 或這個 [L19 討論串](https://lifein19x19.com/viewtopic.php?f=18&t=17093)。
* **OpenCL Mesa** - 這些 OpenCL 驅動程式有 Bug。特別是如果從啟動到當機之前，您看到 KataGo 印出類似
`Found OpenCL Platform 0: ... (Mesa) (OpenCL 1.1 Mesa ...) ...`
那麼您正在使用 Mesa 驅動程式。您需要更換驅動程式，例如請見此 [KataGo issue](https://github.com/lightvector/KataGo/issues/182#issuecomment-607943405)，其中連結到 [此討論串](https://bbs.archlinux.org/viewtopic.php?pid=1895516#p1895516)。
* **Intel Integrated Graphics (Intel 整合顯示卡)** - 對於較弱/較舊的機器或沒有獨立 GPU 的筆記型電腦或裝置，KataGo 可能最終會使用 CPU 內建的較弱「Intel 整合顯示卡」。通常這會運作良好（雖然 KataGo 會很慢，且與使用真實 GPU 相比只能獲得極少量的 playouts），但各種版本的 Intel 整合顯示卡也可能有 Bug 且完全無法運作。如果更新驅動程式對您無效，那麼唯一的解決方案是升級到更好的 GPU。例如請見此 [issue](https://github.com/lightvector/KataGo/issues/54) 或此 [issue](https://github.com/lightvector/KataGo/issues/78)，或此 [其他 github 的 issue](https://github.com/CNugteren/CLBlast/issues/280)。

#### 常見問題
* **KataGo 在 Lizzie/Sabaki/q5go/GoReviewPartner/等軟體啟動時似乎卡住或永遠在「載入中」。**
   * 可能您有些設定錯誤，指定了錯誤的檔案路徑，壞的 GPU 等等。許多這類 GUI 在回報錯誤方面做得不好，可能會完全吞掉 KataGo 的錯誤訊息，而這些訊息本來可以告訴您出了什麼問題。嘗試直接在命令列上執行 KataGo 的 `benchmark` 或 `gtp`，如 [上文](#如何使用) 所述。
   * 有時根本沒有錯誤，只是在給定的網路大小下，KataGo *第一次* 執行時需要做一些昂貴的調校，這可能需要幾分鐘。同樣地，如果您直接在命令列中執行 `benchmark` 指令，這會更清楚。調校後，後續執行將會更快。

* **KataGo 在命令列上運作正常，但在為 GUI 指定正確的檔案路徑時遇到困難。**
   * 如 [上文](#如何使用) 所述，您可以將設定檔命名為 `default_gtp.cfg` 並將您下載的任何網路檔案命名為 `default_model.bin.gz`（對於較新的 `.bin.gz` 模型）或 `default_model.txt.gz`（對於較舊的 `.txt.gz` 模型）。將它們放入與 KataGo 執行檔相同的目錄中，然後您根本不需要指定 `-config` 或 `-model` 路徑。

* **嘗試執行初始調校時，KataGo 給出類似 `Could not create file` 的錯誤。**
   * KataGo 可能沒有權限在您放置它的目錄中寫入檔案。
   * 例如在 Windows 上，`Program Files` 目錄及其子目錄通常限制僅允許具有管理員權限的寫入。嘗試將 KataGo 放在其他地方。

* **我是命令列新手，仍然不知道該告訴 Lizzie/q5go/Sabaki/whatever 什麼來讓它執行 KataGo。**
   * 再次強調，確保您的目錄路徑正確。
   * 一個常見問題：避免在任何檔案或目錄名稱中有任何空格，因為根據 GUI 的不同，這可能需要您以各種方式引用或跳脫路徑或參數。
   * 如果您不了解命令列參數和標記、相對路徑與絕對路徑等，請上網搜尋。嘗試像 https://superuser.com/questions/1270591/how-to-use-relative-paths-on-windows-cmd 或 https://www.bleepingcomputer.com/tutorials/understanding-command-line-arguments-and-how-to-use-them/ 或您找到的其他頁面，或者找一位懂技術的人在聊天室甚至面對面幫您。
   * 考慮使用 https://github.com/sanderland/katrain - 這是別人為 KataGo 寫的優秀 GUI，通常會為您自動處理所有技術設定。

* **我得到不同的錯誤或仍然需要進一步協助。**
   * 查看 [Leela Zero、KataGo 和其他機器人聚集的 discord 聊天室](https://discord.gg/bqkZAz3) 並在 "#help" 頻道提問。
   * 如果您認為發現了 KataGo 本身的 Bug，也歡迎 [開啟 issue](https://github.com/lightvector/KataGo/issues)。請儘可能提供您執行的確切指令、完整的錯誤訊息和輸出（如果您在 GUI 中，請確保檢查該 GUI 的原始 GTP 控制台或日誌）、您嘗試過的事情、您的設定檔和網路、您的 GPU 和作業系統等詳細資訊。

#### 其他問題
* **如何讓 KataGo 使用日本規則或其他規則？**
   * KataGo 支援一些 [GTP 擴充](docs/GTP_Extensions.md) 讓 GUI 開發者設定規則，但不幸的是截至 2020 年 6 月，只有少數 GUI 使用了此功能。所以作為變通方法，有幾種方式：
     * 編輯 KataGo 的設定檔 (`default_gtp.cfg` 或 `gtp_example.cfg` 或 `gtp.cfg`，或任何您命名的檔案) 使用 `rules=japanese` 或 `rules=chinese` 或任何您需要的，或設定個別規則如 `koRule`,`scoringRule`,`taxRule` 等。請參閱 [此處](https://github.com/lightvector/KataGo/blob/master/cpp/configs/gtp_example.cfg#L91) 了解這在設定檔中的位置，並參閱 [此網頁](https://lightvector.github.io/KataGo/rules.html) 了解 KataGo 規則集的完整描述。
     * 使用 `genconfig` 指令 (`./katago genconfig -model <NEURALNET>.gz -output <PATH_TO_SAVE_GTP_CONFIG>.cfg`) 產生設定檔，它會互動式地協助您，包括詢問您想要什麼預設規則。
     * 如果您的 GUI 允許直接存取 GTP 控制台（例如在 Lizzie 中按 `E`），那麼您可以直接在 GTP 控制台中執行 `kata-set-rules japanese` 或類似的其他規則指令，以便在對局或分析過程中動態更改規則。

* **我應該使用哪個模型/網路？**
   * 通常，使用來自 [主要訓練網站](https://katagotraining.org/) 的最強或最新的 b18 大小的網路 (b18c384nbt)。這即便是對於較弱的機器也是最好的類神經網路，因為儘管比舊的較小網路慢一點，但它的每次評估都更強且更準確。
   * 如果您非常在乎理論上的純粹性 - 沒有外部資料，機器人嚴格靠自己學習 - 使用 [此發布](https://github.com/lightvector/KataGo/releases/tag/v1.4.0) 中的 20 或 40 區塊網路，它們以這種方式是純粹的且仍比 Leela Zero 強得多，但也比更近期的網路弱得多。
   * 如果您想要一些執行速度快得多的網路，且由於學習階段獨特而各自擁有有趣的下棋風格，請嘗試 [這裡](https://katagoarchive.org/g170/neuralnets/index.html) 的任何 "b10c128" 或 "b15c192" 擴展訓練網路，這些是來自訓練較早期的 10 區塊和 15 區塊網路，雖然弱得多但仍具備職業級以上水準。


## 開發者功能

#### GTP 擴充指令：
除了基本的一組 [GTP 指令](https://www.lysator.liu.se/~gunnar/gtp/) 外，KataGo 還支援一些額外的指令，供分析工具和其他程式使用。

KataGo 的 GTP 擴充指令記錄在 **[這裡](docs/GTP_Extensions.md)**。

   * 值得注意的是：KataGo 暴露了一個 GTP 指令 `kata-analyze`，除了策略和勝率外，還會報告*預期目數差*的估計值以及棋盤每個位置的預測地盤擁有權熱圖。預期目數差對於檢討讓子棋或較弱玩家的對局特別有用。而在讓子棋中，即使黑棋犯了重大錯誤（直到最後局面變得非常接近），黑棋的勝率通常會保持在接近 100%，預期目數差應該能更清楚地顯示哪些早期的著手損失了目數而讓白棋追上，以及那些錯誤確切損失了多少。如果您有興趣將此支援新增到任何分析工具中，歡迎聯繫，我很樂意回答問題並提供協助。

   * KataGo 也暴露了一些 GTP 擴充指令，允許設定生效的規則（中國、AGA、日本等）。詳情請再次參閱 [這裡](docs/GTP_Extensions.md)。

#### 分析引擎：
KataGo 也實作了一個獨立的引擎，如果您想要一次分析整盤對局，由於批次處理，它可以評估得快得多，如果您在 JSON 解析容易的環境中工作，這可能比 GTP 少了很多麻煩。詳情請見 [這裡](KATAGO_ANALYSIS_ENGINE_ZH_TW.md)。

KataGo 也包含範例程式碼，示範如何從 Python 呼叫分析引擎，請見 [這裡](python/query_analysis_engine_example.py)！

## 編譯 KataGo
KataGo 是用 C++ 寫的。它應該可以在 Linux 或 OSX 上透過支援至少 C++14 的 g++ 編譯，或在 Windows 上透過 MSVC 15 (2017) 及更高版本或 MinGW 編譯。說明可以在 [編譯 KataGo](KATAGO_COMPILING_ZH_TW.md) 中找到。

## 原始碼概覽：
請參閱 [cpp readme](cpp/README.md) 或 [python readme](python/README.md) 以了解此 repo 中原始碼的一些高層次概覽，如果您想了解什麼東西在哪裡以及它們如何組合在一起。

## 自我對弈訓練：
如果您也想執行完整的自我對弈迴圈並使用這裡的程式碼訓練您自己的類神經網路，請參閱 [Selfplay Training](SelfplayTraining.md)。

## 貢獻者

非常感謝為此專案做出貢獻的各位！請參閱 [CONTRIBUTORS](CONTRIBUTORS) 查看貢獻者名單。

## 授權條款

除了一起包含在 `cpp/external/` 下的幾個外部函式庫以及單一檔案 `cpp/core/sha2.cpp`（它們都有自己個別的授權）外，此 repo 中的所有程式碼和其他內容均根據以下檔案中的授權發布供免費使用或修改：[LICENSE](LICENSE)。

撇開授權不談，如果您最終使用此 repo 中的任何程式碼來做任何您自己很酷的新自我對弈或類神經網路訓練實驗，我 (lightvector) 很樂意聽聽您的分享。
