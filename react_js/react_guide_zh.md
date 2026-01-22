# React 核心知識與技能指南 (繁體中文版)

React 是一個用於構建使用者介面的 JavaScript 函式庫。本文檔將帶領你掌握前端開發中最重要的 React 技術與思維。

---

## 1. React 的核心思維
React 與傳統 DOM 操作最大的不同在於：
- **聲明式 (Declarative)**: 你只需描述 UI 「看起來應該像什麼」，React 會負責更新 DOM。
- **組件化 (Component-Based)**: 將 UI 拆分成獨立、可複用的微小單元。

---

## 2. JSX：在 JavaScript 中寫 HTML
JSX 是 JavaScript 的語法擴展，讓代碼結構更直觀。
```jsx
function Welcome() {
  const name = "小明";
  return (
    <div className="container">
      <h1>你好, {name}!</h1>
      <p>歡迎來到 React 的世界。</p>
    </div>
  );
}
```
> [!NOTE]
> 在 JSX 中，HTML 標籤屬性要使用小駝峰命名（如 `className` 代替 `class`）。

---

## 3. 組件 (Components) 與 Props
組件是 React 應用的基石，`Props` 則是傳遞資料的管道。

### 3.1 定義組件 (函數式)
```jsx
function UserProfile(props) {
  return <h2>使用者：{props.name}</h2>;
}
```

### 3.2 使用組件
```jsx
function App() {
  return (
    <div>
      <UserProfile name="Antigravity" />
    </div>
  );
}
```

---

## 4. 深度解析 React Hooks
Hooks 是 React 的精髓。以下是核心 Hooks 的詳細說明與進階用法。

### 4.1 useState：管理動態資料
除了基礎計數器，`useState` 常用於處理複雜物件。

```jsx
const [user, setUser] = useState({ name: 'Ant', age: 25 });

// 正確更新物件的方式（需保留舊屬性）
const updateName = () => {
  setUser(prev => ({ ...prev, name: 'Gravity' }));
};
```
> [!IMPORTANT]
> 狀態更新是**非同步**的。若新狀態依賴於舊狀態，請務必使用「函數式更新」格式 `setCount(prev => prev + 1)`。

---

### 4.2 useEffect：同步與副作用
`useEffect` 讓你在組件中執行外部操作（如 API 呼叫、計時器）。

#### 依賴陣列 (Dependency Array) 的規則：
- `[]`: 僅在組件掛載 (Mount) 時執行一次。
- `[data]`: 當 `data` 發生變化時執行。
- 無陣列: 每次渲染後都執行 (較少見，需謹慎)。

#### 清理機制 (Cleanup)：
當組件解除掛載或重新執行 Effect 前，會執行回傳的函數。
```jsx
useEffect(() => {
  const timer = setInterval(() => console.log('Tick'), 1000);
  return () => clearInterval(timer); // 清除計時器，防止記憶體洩漏
}, []);
```

---

### 4.3 useContext：跨層級資料傳遞
避免層層傳遞 Props (Prop Drilling)。

```jsx
const ThemeContext = createContext('light');

function Display() {
  const theme = useContext(ThemeContext);
  return <div className={theme}>當前主題：{theme}</div>;
}
```

---

### 4.4 useRef：不觸發渲染的「記憶體」
用於存取 DOM 或保留在多次渲染之間不會改變、且改變時不需重新渲染的變數。

```jsx
const inputRef = useRef(null);
const handleClick = () => inputRef.current.focus(); // 直接操作 DOM

return <input ref={inputRef} />;
```

---

### 4.5 useMemo & useCallback：效能優化
- **useMemo**: 記住「計算後的數值」，只有依賴項改變時才重新計算。
- **useCallback**: 記住「函數本身」，防止子組件因為父組件重新渲染而收到新的函數實體。

```jsx
// 只有當 list 改變時才重新計算過濾結果
const filteredList = useMemo(() => heavyFilter(list), [list]);

// 記住點擊處理函數，防止傳遞給 Memoized 組件時失效
const handleAdd = useCallback(() => setCount(c => c + 1), []);
```

---

### 4.6 自定義 Hooks (Custom Hooks)
將邏輯提取出來實現高度複用。自定義 Hook 必須以 `use` 開頭。

```jsx
// useFetch.js
function useFetch(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch(url).then(res => res.json()).then(setData);
  }, [url]);
  return data;
}

// 使用方式
const data = useFetch('https://api.example.com/info');
```

---

## 5. 列表渲染與事件處理
渲染多個資料時，必須為每個元素提供唯一的 `key`。

```jsx
function TodoList() {
  const items = ['學習 React', '練習 Git', '睡覺'];

  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}
```

---

## 6. 現代開發工具：Vite
建議使用 **Vite** 快速啟動 React 專案，速度比傳統 `create-react-app` 快得多。

```bash
# 使用 npm 建立專案
npm create vite@latest my-react-app -- --template react

# 進入目錄並安裝依賴
cd my-react-app
npm install

# 啟動開發伺服器
npm run dev
```

---

## 7. 進階技能建議
要成為優秀的 React 開發者，你需要掌握：
1. **組件拆分原則**: 單一功能原則，保持組件精簡。
2. **狀態提升 (Lifting State Up)**: 當多個組件需要共享資料時，將狀態移動到它們共同的父組件中。
3. **學習狀態管理工具**: 簡單應用用 Context API，大型應用選用 Redux Toolkit 或 Zustand。
4. **效能優化**: 理解 `memo`, `useMemo`, `useCallback` 的使用時機。

---
> [!TIP]
> 始終保持「單向資料流」的觀念：資料由父組件向下流向子組件。
