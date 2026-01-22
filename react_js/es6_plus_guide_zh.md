# ES6 & ES6+ 現代 JavaScript 開發指南 (進階詳解版)

本指南涵蓋了從 ES6 (ECMAScript 2015) 到目前（ES2023+）的核心與進階語法，並提供豐富的範例。

---

## 1. 變數宣告與作用域 (Variable Declarations & Scope)

### `let` 與 `const` 的深度解析
- **區塊作用域 (Block Scope)**: 變數只在 `{}` 內部有效。
- **暫時性死區 (Temporal Dead Zone, TDZ)**: 在宣告之前存取 `let`/`const` 會報錯，避免了 `var` 的變數提昇 (Hoisting) 陷阱。

```javascript
{
  // console.log(a); // 錯誤：ReferenceError (TDZ)
  let a = 10;
  const B = 20;
}
// console.log(a); // 錯誤：a is not defined
```

---

## 2. 物件字面值的增強 (Object Literal Enhancements)

### 屬性簡寫與計算屬性名
```javascript
const name = "Antigravity";
const ageKey = "user_age";

const user = {
  name, // 等同於 name: name (屬性簡寫)
  [ageKey]: 5, // 動態計算屬性名
  
  greet() { // 方法簡寫
    console.log(`Hello, ${this.name}`);
  }
};
```

---

## 3. 進階解構賦值 (Advanced Destructuring)

### 巢狀解構與預設值
```javascript
const metadata = {
  title: "ES6 Guide",
  author: {
    firstName: "Admin",
    lastName: "User"
  },
  tags: ["JS", "Programming"]
};

// 巢狀解構 + 重新命名 + 預設值
const { 
  title, 
  author: { firstName: fName }, 
  category = "Technology" 
} = metadata;

// 陣列解構：跳過元素與預設值
const [firstTag, , thirdTag = "None"] = metadata.tags;
```

---

## 4. 箭頭函數與 `this` (Arrow Functions & this)

箭頭函數沒有自己的 `this`，它會捕獲其所在地（定義時）的上下文 `this` 值。

```javascript
const timer = {
  seconds: 0,
  start() {
    // 使用箭頭函數，this 會指向 timer 物件
    setInterval(() => {
      this.seconds++;
      console.log(this.seconds);
    }, 1000);
  }
};
```

---

## 5. 字串與陣列的高級方法 (Advanced String & Array Methods)

### 字串方法
- `includes()`, `startsWith()`, `endsWith()`
- `repeat(count)`
- `padStart()`, `padEnd()` (ES2017)

### 陣列方法 (ES6+)
- `find()`, `findIndex()`
- `includes()` (ES2016)
- `flat()`, `flatMap()` (ES2019): 用於扁平化巢狀陣列。
- `Array.from()`: 將類陣列物件轉為真正的陣列。

```javascript
const nested = [1, [2, [3]]];
console.log(nested.flat(2)); // [1, 2, 3]

const tags = "js,react,node";
const tagArray = Array.from(tags.split(','));
```

---

## 6. Map 與 Set 資料結構 (Map & Set)

### Set: 儲存唯一值的集合 (常用於去重)
```javascript
const numbers = [1, 2, 2, 3, 4, 4];
const unique = [...new Set(numbers)]; // [1, 2, 3, 4]
```

### Map: 鍵值對集合，鍵可以是任何類型 (包含物件)
```javascript
const registry = new Map();
const keyObj = { id: 1 };

registry.set(keyObj, "Premium User");
console.log(registry.get(keyObj)); // "Premium User"
```

---

## 7. 進階非同步處理 (Advanced Async/await)

### Promise 靜態方法
- `Promise.all([p1, p2])`: 所有 Promise 都成功才成功。
- `Promise.allSettled([p1, p2])`: 等待所有 Promise 完成，不論成功或失敗 (ES2020)。
- `Promise.race([p1, p2])`: 只要其中一個完成就回傳結果。

```javascript
async function fetchMultple() {
  const [res1, res2] = await Promise.all([
    fetch('/api/users'),
    fetch('/api/posts')
  ]);
}
```

---

## 8. 生成器與迭代器 (Generators & Iterators)

使用 `function*` 定義，可以暫停與恢復執行。

```javascript
function* numberGenerator() {
  yield 1;
  yield 2;
  yield 3;
}

const gen = numberGenerator();
console.log(gen.next().value); // 1
console.log(gen.next().value); // 2
```

---

## 9. 類別進階：私有欄位 (Class Private Fields)

使用 `#` 宣告私有屬性與方法 (ES2022+)。

```javascript
class BankAccount {
  #balance = 0; // 私有屬性，外部無法存取

  constructor(initial) {
    this.#balance = initial;
  }

  deposit(amount) {
    this.#balance += amount;
  }

  showBalance() {
    console.log(`餘額: ${this.#balance}`);
  }
}

const account = new BankAccount(100);
// console.log(account.#balance); // 報錯：Private field must be declared in an enclosing class
```

---

## 10. 選用鏈接與空值合併 (Optional Chaining & Nullish Coalescing)

這在處理 API 回傳資料時非常強大。

```javascript
const apiResponse = {
  data: {
    user: {
      settings: null
    }
  }
};

// 即使 settings 為 null，也不會噴錯，回傳 10
const fontSize = apiResponse.data?.user?.settings?.theme?.fontSize ?? 10;
```

---

## 11. 動態匯入 (Dynamic Import)

按需加載模組，優化效能 (ES2020)。

```javascript
button.onclick = async () => {
  const module = await import('./heavy-module.js');
  module.doSomething();
};
```

---

## 12. Symbol 與私有性質 (Symbols)

`Symbol` 是唯一且不可變的原始型別，常用作物件屬性鍵以避免衝突。

```javascript
const INTERNAL_KEY = Symbol('internal');
const obj = {
  [INTERNAL_KEY]: "Secret"
};
console.log(obj[INTERNAL_KEY]); // "Secret"
```
