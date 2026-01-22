# 蒙特卡羅圖搜索 (Monte-Carlo Graph Search) - 基礎原理

此文檔解釋了如何將蒙特卡羅樹搜索 (MCTS) 應用於有向圖 (Directed Graphs) 而不是樹，即「蒙特卡羅圖搜索」(MCGS)。這對於處理圍棋等遊戲中的「置換」(Transpositions)（即透過不同的移動順序到達相同的局面）非常重要。

## 簡介 / 背景

在遊戲樹搜索中，通常會有許多不同的移動序列導致相同的狀態（置換）。
例如：`1. d4 d5 2. Nf3` 與 `1. Nf3 d5 2. d4` 到達相同的局面。

如果將這些狀態視為樹中的不同節點，會導致重複搜索，效率低下。理想情況下，我們希望在圖中共享這些節點。
然而，直接將 MCTS 應用於有向無環圖 (DAG) 容易導致不正確的算法，因為標準 MCTS 是基於樹的運行統計 (Running Stats) 制定的。

## MCTS 的通常表述 - 運行統計樹

標準 MCTS 在樹的每個節點跟蹤：
*   **N**: 到目前為止對該節點的訪問次數。
*   **Q**: 這些訪問採樣的效用值 (utility values) 的運行平均值。

MCTS 的過程：
1.  從根節點開始，根據探索公式（如 PUCT）向下走。
2.  到達新狀態時，擴展樹並添加節點。
3.  獲得新狀態的效用估計 U（例如從神經網路）。
4.  向上回溯，更新路徑上每個節點的 N 和 Q。

## 圖搜索會出什麼問題？

如果我們簡單地將 MCTS 應用於 DAG，當多條路徑指向同一個節點時，會出現問題：
1.  **效用更新不一致**：如果一個節點 C 通過一條路徑被大量訪問並更新了其 Q 值，而指向它的另一個父節點 A 沒有參與這些訪問，那麼 A 對 C 的評估將是過時的。
2.  **人為偏差**：如果節點 A 的首選子節點 C 已經通過其他路徑被大量訪問，PUCT 公式可能會認為 C "已經被探索得夠多了"，從而導致 A 轉而去探索其他較差的移動，這可能會人為地拉低 A 的 Q 值。
3.  **上游污染**：如果在任何訪問時更新所有父節點，那麼來自低效用分支的訪問可能會污染高質量父節點的 Q 值。

## 回歸理論 - MCTS 作為正則化策略優化

MCTS 可以被視為在每個節點局部運行的一個在線策略學習算法。PUCT 產生的**訪問分佈** (visit distribution) 近似於以下優化問題的解：
尋找最大化預期效用同時最小化與先驗策略 $P$ 的 KL 散度的策略 $\pi$。

從這個角度來看，**Q 值**不應僅僅被視為過往 playouts 的平均值，而應被遞歸地定義為：
**子節點 Q 值的加權平均（類似於後驗策略的預期效用）加上對當前節點原始 U 的正則化。**

$$Q(n) \approx \sum_{a} \hat{\pi}(n,a) Q(n,a)$$

## 正確執行蒙特卡羅圖搜索

為了修復圖搜索的問題，我們需要在每個節點 $n$ 跟蹤：
*   **$N(n)$**: 節點的總訪問次數。
*   **$N(n,a)$**: **動作訪問次數 (Edge visits)** - 也就是 PUCT 在節點 $n$ 選擇動作 $a$ 的次數。這形成了我們的後驗策略。
*   **$Q(n)$**: 使用遞歸公式計算：$(1/N(n)) * (U(n) + \sum_{a} N(n,a) Q(n,a))$，其中 $Q(n,a)$ 是子節點的 $Q$ 值。

**關鍵點**：
*   計算 PUCT 時使用**邊緣訪問計數 (Edge visits)** $N(n,a)$，而不是子節點的總訪問計數 $N(child)$。
*   這保證了即使子節點通過其他路徑被大量訪問，父節點的本地策略優化也不會受到干擾。
*   Q 值直接根據子節點當前的 Q 值和邊緣訪問權重進行計算，確保一致性。

### 基本算法偽代碼

```python
def perform_one_playout(node):
    if is_game_over(node):
        node.U = get_utility(...)
    else if node.N == 0:
        node.U = get_from_neural_net(...)
    else:
        action = select_action_according_to_puct(node) # 使用 N(n,a)
        # ... (處理節點/邊緣創建) ...
        (child, edge_visits) = node.children_and_edge_visits[action]
        perform_one_playout(child)
        node.children_and_edge_visits[action] = (child, edge_visits + 1)

    # 遞歸更新 Q
    children_and_edge_visits = node.children_and_edge_visits.values()
    node.N = 1 + sum(edge_visits for (_,edge_visits) in children_and_edge_visits)
    node.Q = (1/node.N) * (
       node.U +
       sum(child.Q * edge_visits for (child,edge_visits) in children_and_edge_visits)
    )
```

## 實作選擇討論

*   **過時的 Q 值 (Stale Q Values)**: 雖然只更新路徑上的節點會導致非路徑上的父節點持有過時的 Q 值，但在極限情況下這是無問題的，因為所有節點最終都會被訪問。這是一種為了簡單和性能的權衡。
*   **冪等更新與增量更新**: 偽代碼使用了冪等更新（每次重新計算 Q）。也可以制定增量更新，這在計算上可能更便宜，但冪等更新更容易推理且更適合多線程。
*   **Child Visits > Edge Visits**: 當發生置換時，子節點的訪問數可能大於父節點的邊緣訪問數。可以選擇在此時停止 playout 以節省計算資源，或者繼續以獲得更準確的評估。KataGo 默認會停止，但也提供繼續的選項。

## 結論

此文檔提供了一種基於原理的方法來在圖上正確執行 MCTS，避免了簡單移植時出現的統計不一致問題。KataGo 使用了這種方法（以及一些優化）來有效地處理圍棋中的置換。

---
*文件生成時間: 2026-01-22*
