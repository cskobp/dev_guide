# 網頁渲染技術詳解：CSR、SSR 與 SSG 及 React/Next.js 實作指南

在現代網站開發中，選擇合適的渲染策略（Rendering Strategy）對於提升使用者體驗、SEO 表現以及整體效能至關重要。以下將詳細介紹 CSR（客戶端渲染）、SSR（伺服器端渲染）與 SSG（靜態網站生成）這三種主要技術，並探討它們在 React 及 Next.js 中的詳細設計與設定。

---

## 1. CSR (Client-Side Rendering) 客戶端渲染

### 什麼是 CSR？
CSR 是一種將網頁渲染工作交由使用者瀏覽器（客戶端）執行的技術。伺服器最初只會回傳一份近乎空白的 HTML（通常只包含一個 `<div id="root"></div>`）與打包好的 JavaScript 檔案。待瀏覽器下載並解析執行這些 JavaScript 後，才會動態生成並繪製出完整的網頁內容及綁定互動邏輯。

**優點：**
- **後續互動流暢**：首次載入後，頁面切換或互動不需重新整頁刷新，帶來如原生 App 般流暢的單頁應用程式（SPA）體驗。
- **伺服器負載較低**：伺服器只需提供靜態資源與 API，計算與 UI 生成壓力轉移至客戶端。

**缺點：**
- **首次載入時間（FCP）較長**：因為必須等 JS 下載、解析並執行後才能看到內容，若是 JS 檔案過大或網路較慢，就會出現白畫面。
- **SEO 表現通常較差**：早期的爬蟲可能無法執行 JS，導致無法抓取實際內容。

### 詳細設計與實作範例

#### 傳統 React (Vite / Create React App)
在傳統 React 專案中，所有的組件都是在客戶端渲染。通常會透過 `useEffect` 來發送 API 請求獲取資料，並以 `useState` 管理載入狀態。

```jsx
// src/App.jsx (React CSR 範例)
import { useState, useEffect } from 'react';

function UserProfile() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // 在元件掛載後才發送請求
  useEffect(() => {
    fetch('https://api.example.com/user')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>載入中...</div>;
  return <div>用戶名稱：{data.name}</div>;
}

export default UserProfile;
```

#### Next.js (App Router) 中的 CSR
在 Next.js 的 App Router (v13+) 中，預設所有組件都是 Server Components。若要使用 CSR 以及 React Hooks (如 `useState`, `useEffect`)，或綁定瀏覽器事件 (`onClick`)，必須在檔案最上方加上 `'use client'` 指令來宣告這是一個客戶端元件。

```jsx
// app/components/ClientCounter.jsx (Next.js CSR 範例)
'use client'; // 宣告這是 Client Component

import { useState } from 'react';

export default function ClientCounter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>目前計數：{count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

---

## 2. SSR (Server-Side Rendering) 伺服器端渲染

### 什麼是 SSR？
SSR 是在 **每次使用者發出請求（Request）** 時，伺服器端會即時取得所需資料，並將包含完整內容的 HTML 字串組裝好後，傳送給瀏覽器顯示。隨後，瀏覽器會在背景載入所需的 JS 並進行水合（Hydration），讓頁面具備互動性。

**優點：**
- **首次載入速度快且無白畫面**：瀏覽器收到 HTML 就能顯示完整頁面結構內容。
- **SEO 表現優異**：搜尋引擎爬蟲能輕易取得包含關鍵字與結構的完整 HTML 原始碼。

**缺點：**
- **伺服器運算壓力大**：每次造訪都需要重新執行渲染邏輯，流量大時會成為瓶頸。
- **TTFB (Time to First Byte) 增加**：在產生 HTML 及向資料庫要資料期間，伺服器準備回應會花費時間。

### 詳細設計與實作範例

#### Next.js App Router (v13+)
在 App Router 中，伺服器組件 (Server Components) 可以在伺服器端非同步抓取資料。若要強制每次請求都重新抓取資料 (SSR)，可以在 `fetch` 中帶入 `cache: 'no-store'` 選項。這等同於之前 Pages Router 中的 `getServerSideProps`。

```jsx
// app/dashboard/page.jsx (Next.js Server Component SSR 範例)
export default async function DashboardPage() {
  // 設定 cache: 'no-store' 代表略過快取，每次 request 都重新拉取資料
  const res = await fetch('https://api.example.com/stats', {
    cache: 'no-store' 
  });
  const stats = await res.json();

  return (
    <main>
      <h1>即時儀表板</h1>
      <p>今日流量：{stats.traffic}</p>
      <p>活躍用戶：{stats.activeUsers}</p>
    </main>
  );
}
```

#### Next.js Pages Router (舊版)
在舊版 Pages Router 中，必須在頁面檔案中匯出 `getServerSideProps` 函數，確保每次頁面請求都會從伺服器端抓取該資料並渲染。

```jsx
// pages/dashboard.jsx
export async function getServerSideProps(context) {
  // 每次 Request 時都會在伺服器端執行
  const res = await fetch('https://api.example.com/stats');
  const stats = await res.json();
  
  return {
    props: { stats }, // 傳遞給 Dashboard 元件
  };
}

export default function Dashboard({ stats }) {
  return (
    <main>
      <h1>即時儀表板</h1>
      <p>今日流量：{stats.traffic}</p>
    </main>
  );
}
```

---

## 3. SSG (Static Site Generation) 靜態網站生成

### 什麼是 SSG？
SSG 是在開發**建置階段（Build time）預先生成**所有的 HTML 頁面。當使用者造訪網站時，直接由伺服器或 CDN 吐出早已準備好的靜態檔案，不必進行資料庫連線或動態運算。這經常與前端 JavaScript 或外部 API 結合成 **JAMStack** 架構。

**優點：**
- **極致的載入速度**：所有頁面早在建置期已產出並可託管至全球連線速度極快的 CDN。
- **最強的資安防護**：沒有後臺及資料庫邏輯暴露。金融企業經常使用以合規。
- **高營運成本效益**：託管靜態圖片/檔案遠比租用應用程式伺服器便宜。

**缺點：**
- **不適合頻繁更新內容**：每次資料變更都需重新 Build。若站點龐大，編譯時間可能很長。
- **動態功能實現較難**：登入/購物車等功能通常必須再額外配合 CSR 技術的 API 服務。

### 詳細設計與實作範例

#### Next.js App Router (v13+)
在 App Router 中，如果在 `fetch` 設定 `cache: 'force-cache'`（或是不傳送該參數，預設即為快取），Next.js 就會在執行 `next build` 階段抓取資料並生成出 SSG 靜態頁面。對於動態路由 (Dynamic Routes)，可以使用 `generateStaticParams` 預先定義要生成的路由參數。

```jsx
// app/blog/[slug]/page.jsx (Next.js SSG 範例)

// 1. 在 Build Time 預先告知 Next.js 有哪些 slug 需要預先生成為實體 HTML
export async function generateStaticParams() {
  const res = await fetch('https://api.example.com/posts');
  const posts = await res.json();

  // 回傳陣列形式的路由參數
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

// 2. 負責取得該路由資料並渲染的元件 (預設會在編譯時做靜態產生)
export default async function BlogPost({ params }) {
  const { slug } = params;
  
  // 預設會有靜態快取行為
  const res = await fetch(`https://api.example.com/posts/${slug}`);
  const post = await res.json();

  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}
```

#### Next.js Pages Router (舊版)
在舊版 Pages Router，需結合使用 `getStaticProps` 在建置時獲取靜態資料，若有動態路徑則需加上 `getStaticPaths` 來列出所有可能。

```jsx
// pages/blog/[slug].jsx
export async function getStaticPaths() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json());
  
  // 定義要預生成哪些路徑
  const paths = posts.map(post => ({ params: { slug: post.slug } }));

  // fallback: false 代表如果瀏覽器訪問不在名單中的路徑，就直接回傳 404
  return { paths, fallback: false }; 
}

export async function getStaticProps({ params }) {
  // 此段程式碼只在 build 期間觸發執行
  const post = await fetch(`https://api.example.com/posts/${params.slug}`).then(r => r.json());
  return { props: { post } };
}

export default function BlogPost({ post }) {
  return <h1>{post.title}</h1>;
}
```

### 進階：ISR (Incremental Static Regeneration) 增量靜態生成
若覺得純 SSG 每次都要重新 Build 整個網站太耗時（例如部落格只是要定時更新幾篇文章），Next.js 提供了 ISR 技術。它允許在背景「定時或是針對特定頁面」重新生成快取，結合了 SSG 的速度與資料的部分即時性。

在 App Router 中，只要在 `fetch` 加上 `next: { revalidate: 每秒數 }` 即可達成：
```jsx
// app/blog/latest/page.jsx (ISR 範例)
export default async function LatestPosts() {
  // 每隔 60 秒，如果有新的請求，就會在背景重新抓取資料並更新快取的 HTML
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 } 
  });
  const posts = await res.json();

  return (
    <ul>
      {posts.map(post => <li key={post.id}>{post.title}</li>)}
    </ul>
  );
}
```
