# React 全方位事件與 API 權威指南 (Exhaustive Reference)

本文件提供 React 開發中所有標準合成事件、組件 API 及 Hooks 的完整清單與詳細說明，適用於現代 ES6+ 開發環境。

---

## 1. 合成事件完整清單 (Exhaustive Synthetic Events)

React 的合成事件 (SyntheticEvent) 涵蓋了幾乎所有瀏覽器原生事件。

### 剪貼簿事件 (Clipboard Events)
- `onCopy`, `onCut`, `onPaste`

### 複合事件 (Composition Events)
- `onCompositionEnd`, `onCompositionStart`, `onCompositionUpdate`

### 鍵盤事件 (Keyboard Events)
- `onKeyDown`, `onKeyPress`, `onKeyUp` (屬性：`key`, `code`, `shiftKey`, `ctrlKey`, `altKey` 等)

### 焦點事件 (Focus Events)
- `onFocus`, `onBlur` (屬性：`relatedTarget`)

### 表單事件 (Form Events)
- `onChange`, `onInput`, `onInvalid`, `onReset`, `onSubmit`

### 鼠標與拖拽事件 (Mouse & Drag Events)
- `onClick`, `onContextMenu`, `onDoubleClick`
- `onDrag`, `onDragEnd`, `onDragEnter`, `onDragExit`, `onDragLeave`, `onDragOver`, `onDragStart`, `onDrop`
- `onMouseDown`, `onMouseEnter`, `onMouseLeave`, `onMouseMove`, `onMouseOut`, `onMouseOver`, `onMouseUp`

### 選擇事件 (Selection Events)
- `onSelect`

### 觸摸事件 (Touch Events)
- `onTouchCancel`, `onTouchEnd`, `onTouchMove`, `onTouchStart`

### UI 與滾動事件 (UI Events)
- `onScroll`

### 滾輪事件 (Wheel Events)
- `onWheel` (屬性：`deltaX`, `deltaY`, `deltaZ`, `deltaMode`)

### 多媒體事件 (Media Events)
- `onAbort`, `onCanPlay`, `onCanPlayThrough`, `onDurationChange`, `onEmptied`, `onEncrypted`, `onEnded`, `onError`, `onLoadedData`, `onLoadedMetadata`, `onLoadStart`, `onPause`, `onPlay`, `onPlaying`, `onProgress`, `onRateChange`, `onSeeked`, `onSeeking`, `onStalled`, `onSuspend`, `onTimeUpdate`, `onVolumeChange`, `onWaiting`

### 動畫與過渡事件 (Animation & Transition Events)
- `onAnimationStart`, `onAnimationEnd`, `onAnimationIteration`
- `onTransitionEnd`

---

## 2. React Hooks 完整指南 (The Full Hooks API)

### 基礎 Hooks
- `useState(initialState)`: 狀態管理。
- `useEffect(effect, [deps])`: 處理副作用與清理邏輯。
- `useContext(Context)`: 存取 Context。

### 進階 Hooks
- `useReducer(reducer, initialArg, init)`: 複雜狀態管理。
- `useCallback(fn, [deps])`: 記憶化函數。
- `useMemo(() => value, [deps])`: 記憶化計算結果。
- `useRef(initialValue)`: 存取 DOM 或保持跨渲染變數。
- `useLayoutEffect(effect, [deps])`: 在 DOM 變動後同步執行 (阻塞渲染)。
- `useImperativeHandle(ref, createHandle, [deps])`: 自定義暴露給父組件的實例值。
- `useDebugValue(value, format)`: 在 React 開發者工具中顯示標籤。

### React 18+ 新增 Hooks
- `useId()`: 生成唯一的客戶端與服務端一致的 ID。
- `useTransition()`: 標記非緊急的 UI 轉換。
- `useDeferredValue(value)`: 延遲更新特定的 UI 部分。
- `useSyncExternalStore(subscribe, getSnapshot)`: 讀取外部數據源。
- `useInsertionEffect(effect)`: 用於 CSS-in-JS 庫注入樣式 (早於 `useLayoutEffect`)。

---

## 3. Class 組件完整生命週期 (Detailed Lifecycle)

### 掛載階段 (Mounting)
1. `constructor()`
2. `static getDerivedStateFromProps(props, state)`: 根據 props 更新 state。
3. `render()`
4. `componentDidMount()`

### 更新階段 (Updating)
1. `static getDerivedStateFromProps(props, state)`
2. `shouldComponentUpdate(nextProps, nextState)`: 效能優化開關。
3. `render()`
4. `getSnapshotBeforeUpdate(prevProps, prevState)`: 捕獲 DOM 資訊 (如滾動位置)。
5. `componentDidUpdate(prevProps, prevState, snapshot)`

### 卸載與錯誤處理
- `componentWillUnmount()`
- `static getDerivedStateFromError(error)`
- `componentDidCatch(error, info)`

---

## 4. React 頂層 API 與工具

- `React.memo()`: HOC 效能優化。
- `React.lazy()` / `React.Suspense`: 代碼分割。
- `React.Fragment`: 免 DOM 節點群組。
- `React.StrictMode`: 嚴格模式偵測。
- `React.Children`: 操作 `this.props.children` 的工具庫 (`map`, `forEach`, `count`, `only`, `toArray`)。
- `ReactDOM.createPortal(child, container)`: 將組件渲染到外部 DOM 節點。
- `ReactDOM.flushSync(callback)`: 強制同步更新。

---

## 5. 實踐與進階範例

### 1. `useLayoutEffect` 範例 (測量 DOM)
```javascript
const MeasureBox = () => {
  const [width, setWidth] = useState(0);
  const boxRef = useRef();

  useLayoutEffect(() => {
    // 渲染前測量，避免閃爍
    setWidth(boxRef.current.getBoundingClientRect().width);
  }, []);

  return <div ref={boxRef}>寬度為: {width}px</div>;
};
```

### 2. `useId` 範例 (表單綁定)
```javascript
const FormField = () => {
  const id = useId();
  return (
    <>
      <label htmlFor={id}>用戶名:</label>
      <input id={id} type="text" />
    </>
  );
};
```

### 3. `createPortal` 範例 (模態框)
```javascript
import { createPortal } from 'react-dom';

const Modal = ({ children }) => {
  return createPortal(
    <div className="modal-overlay">{children}</div>,
    document.body // 渲染到 body 下，而非當前組件視圖內
  );
};
```
