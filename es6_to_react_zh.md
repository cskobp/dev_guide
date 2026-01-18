# Javascript 基礎到 React / Next.js 全攻略 (詳解版)

這份指南專為「想從 JS 基礎一路學到 React」的開發者設計。我們不只列出語法，更會用**白話文比喻**與**步驟拆解**，告訴你「為什麼要這樣寫」以及「React 為什麼需要它」。

---

# 第一部分：JavaScript 核心基礎 (The Foundation)

這些是建造摩天大樓的地基。React 只是蓋在這些地基上的房子。

## 1. 變數宣告 (Variables)

### 觀念比喻：箱子 📦
想像變數就是一個用來裝資料的 **「箱子」**。

*   **`const` (密封箱)**：一旦把東西放進去，就封死箱子，不能再把內容物拿出來換別的。
*   **`let` (開口箱)**：東西放進去後，隨時可以拿出來，換別的東西進去。

### 步驟說明

在現代 JS 開發 (尤其是 React)，我們有一個黃金法則：**「預設使用 `const`，真的需要改才用 `let`」**。

```javascript
// 1. const: 宣告後「不能」重新賦值 (Reassign)
const PI = 3.14;
// PI = 3.14159; // ❌ 錯誤！這是密封箱，不能換值

// 2. let: 宣告後「可以」重新賦值
let score = 0;   // 一開始是 0
score = 10;      // ✅ OK，換成 10 了
score = 20;      // ✅ OK，又換成 20 了

// 3. 特別注意：const 的物件/陣列是「內容」可變
// 箱子本身沒換 (地址沒變)，但箱子像多拉A夢的百寶袋，裡面的東西可以變
const user = { name: "Amy" };
user.name = "Bob"; // ✅ OK！我們沒換掉 user 這個變數，是改了屬性
```

### Summary
*   絕大多數情況用 **`const`** (讓程式碼穩定，比較不會出意外)。
*   只有像 `for` 迴圈計數器 (`i++`) 或真的會變的值才用 **`let`**。
*   **永遠別用 `var`** (它是舊時代的產物，容易讓變數到處亂跑)。

---

## 2. 函式演進史 (Functions)

React 大量使用「箭頭函式」，我們來看看它是怎麼演變來的。

### 階段 1：傳統函式 (Function Declaration)
以前我們這樣寫，中規中矩。

```javascript
function add(a, b) {
  return a + b;
}
```

### 階段 2：箭頭函式 (Arrow Function) - ES6
為了寫起來更爽、更簡潔，並解決 `this` 指向問題 (React 很在意這點)。

```javascript
const add = (a, b) => {
  return a + b;
};
```

### 階段 3：極簡模式 (Implicit Return)
如果函式內容 **只有一行** 且是回傳值，我們可以把 `{}` 和 `return` 都省掉！

```javascript
// 「接受 a 和 b，直接回傳 a+b」
const add = (a, b) => a + b;
```

> **為什麼 React 愛用？**
> 在 React 元件中，我們常需要把函式傳給別人，箭頭函式讓程式碼看起來更乾淨，而且不會有 `this` 抓不到的問題。

---

## 3. 物件與解構 (Destructuring)

### 觀念比喻：行李箱 🧳
以前要拿行李箱裡的東西，要一件一件拿。解構賦值就像是 **「一次把需要的東西變出來」**。

### 傳統寫法 (麻煩)

```javascript
const user = { name: "Tom", age: 18, country: "Taiwan" };

const name = user.name;
const age = user.age;
// 要寫好多次 user.xxx... 煩死人 😫
```

### 現代寫法 (優雅 ✨)

```javascript
const user = { name: "Tom", age: 18, country: "Taiwan" };

// 語法意思：從 user 裡面，把 name 和 age 抓出來，變成獨立變數
const { name, age } = user;

console.log(name); // "Tom"
```

> **React 實戰**
> 當你寫 Component 接收 Props 時，這招天天用：
> ```javascript
> // 不用寫 props.title, props.color
> function Button({ title, color }) { 
>   return <button style={{ color }}>{title}</button>;
> }
> ```

---

# 第二部分：ES6+ 邁向 React 的關鍵橋樑 (The Bridge)

如果不熟悉這些陣列方法，看 React 程式碼會像看天書。

## 1. `map`: 資料加工廠 🏭

### 觀念比喻
`map` 就像一條 **「生產線」**。
原料 (原始陣列) 進去 -> 經過機器加工 (Callback Function) -> 產品 (新陣列) 出來。
**重點：原料不會不見，而且產出的數量跟原料依樣多。**

### 語法拆解

```javascript
const prices = [10, 20, 30]; // 原料

// 機器：把每個數字 * 2
const newPrices = prices.map((price) => {
  return price * 2;
});

console.log(newPrices); // [20, 40, 60] (產品)
```

> **React 實戰 (超級重要 🔥)**
> 我們用 `map` 把 **「資料陣列」** 轉成 **「HTML 標籤陣列」**。
> ```javascript
> const users = ["Amy", "Bob"];
> // 資料 -> UI
> {users.map(user => <div>{user}</div>)}
> ```

## 2. `filter`: 海關安檢 👮‍♂️

### 觀念比喻
`filter` 就像 **「安檢門」**。
每個人 (陣列元素) 都要經過檢查。
*   符合條件 (True) -> 通過 (留在新陣列)。
*   不符合 (False) -> 攔下 (被丟掉)。

### 語法拆解

```javascript
const scores = [80, 50, 90, 40];

// 規則：及格 (>= 60) 才能通過
const passList = scores.filter((score) => {
  return score >= 60;
});

console.log(passList); // [80, 90] (50 和 40 被擋下了)
```

> **React 實戰**
> 常用來做「刪除」功能。把「id 不等於要刪除 id」的項目留下來 = 刪除那個項目。

## 3. 非同步處理 (Async / Await)

### 觀念比喻：點餐取號 🍔
1.  **Promise**: 去櫃檯點餐，拿到一張「號碼牌」。
2.  **Await**: 你站在櫃台 **「等」**，直到店員把漢堡做好給你，你才做下一件事（吃漢堡）。

### 傳統 Promise (稍微難讀)

```javascript
fetch('https://api.com/data')
  .then(res => res.json())
  .then(data => console.log(data));
```

### 現代 Async / Await (直觀像同步)

```javascript
// 1. 宣告這是一個「會花時間」的函式 (async)
const getData = async () => {
  // 2. 暫停下來，等 fetch 做完 (await)
  const res = await fetch('https://api.com/data');
  
  // 3. 繼續等轉成 json
  const data = await res.json();
  
  console.log(data); // 拿到資料了！
};
```

---

# 第三部分：React Hooks 實戰拆解 (React Mindset)

學 React 最難的不是語法，是 **「思維轉換」**。

## 1. 核心公式：`UI = f(State)`

*   **JS 思維**：我要改畫面 -> 抓 DOM (`document.getElementById`) -> 改內容。
*   **React 思維**：我要改畫面 -> **改資料 (State)** -> React 自動幫我重畫畫面。

**你只管資料，畫面交給 React。**

## 2. `useState`: 狀態管理員

這是讓 React 知道「資料變了」的唯一手段。

```javascript
//   變數名稱,  修改它的專用函式       初始值
const [count,   setCount]     = useState(0);
```

### 常見錯誤與修正

```javascript
// ❌ 錯誤：直接改變數，React 根本不知道，畫面不會變
count = 100;

// ✅ 正確：用專用函式通知 React
setCount(100);
```

### 進階：為什麼要 `prev => prev + 1`？

當你要根據「現在的值」做計算時，直接拿 `count` 會有風險 (閉包陷阱)，要拿 React 確保是最新的 `prev`。

```javascript
// 推薦寫法：Functional Update
setCount(prevCount => prevCount + 1);
```

## 3. `useEffect`: 副作用管家

React 元件主要是拿來「回傳 UI」的。如果你要在這裡做別的事 (打 API、設計時器、手動改 DOM)，這些都叫 **副作用 (Side Effects)**，必須放在 `useEffect` 裡。

### 什麼時候執行？看 Dependency Array (依賴陣列)

```javascript
useEffect(() => {
  console.log("執行了！");
}, [ /* 這裡放什麼很重要 */ ]);
```

1.  **`[]` (空陣列)**：**只執行一次** (剛出生的時候)。像 `componentDidMount`。
    *   *用途*：打 API 抓初始資料。
2.  **`[count]` (有變數)**：**出生 + count 變的時候** 執行。
    *   *用途*：當搜尋關鍵字變了，重新搜尋。
3.  **不寫陣列**：**每次**畫面一動就執行。 (⚠️ 危險，易當機)

---

# 第四部分：Coding Guidelines (寫出高品質 React)

把這張清單貼在電腦旁，寫 Code 時檢查一下。

### 1. 變數與邏輯
*   [ ] 預設使用 `const`，除非真的要改才用 `let`。
*   [ ] 變數命名要明確：`const userList` 優於 `const list`。
*   [ ] 判斷相等永遠用 `===` (三個等號)。
*   [ ] 使用 Optional Chaining `?.` 避免 `undefined` 錯誤 (例：`user?.address?.city`)。

### 2. 函式與結構
*   [ ] Component 內的回傳函式優先用箭頭函式。
*   [ ] 善用解構賦值讓 `props` 更乾淨。
*   [ ] 盡量保持 Component 純粹 (Pure)，副作用全部丟進 `useEffect`。

### 3. Async 非同步
*   [ ] 優先使用 `async / await` 取代 Promise `.then`。
*   [ ] 記得用 `try...catch` 包住 `await` 來處理錯誤。

### 4. React 效能與規範
*   [ ] 列表渲染 (`map`) 一定要加唯一的 `key`。
*   [ ] `useEffect` 的依賴陣列如果不確定，先檢查 ESLint 的建議。
*   [ ] 修改 State 依賴舊值時，使用 `setCount(prev => ...)`。

---

這份指南希望能幫助你建立「直覺」。多寫、多練習，你會發現 React 其實就是一組設計得很精妙的 JavaScript 函式庫！
