# Supabase 開發完全指南 (繁體中文版)

Supabase 是一個開源的 Firebase 替代方案，基於 PostgreSQL 資料庫提供完整的後端功能。本文將引導你逐步開發一個 Supabase 專案。

---

## 1. 建立 Supabase 專案

1. **註冊/登入**: 前往 [Supabase Dashboard](https://supabase.com/dashboard) 並使用 GitHub 帳號登入。
2. **建立新專案**: 點擊 "New Project"，選擇你的組織 (Organization)。
3. **設定專案資訊**:
   - **Name**: 輸入專案名稱。
   - **Database Password**: 設定資料庫密碼。
   - **Region**: 選擇離你使用者最近的區域 (例如 Tokyo 或 Singapore)。
4. **等待初始化**: 系統需要約 1-2 分鐘來準備你的虛擬機器。

---

## 2. 資料庫與安全 (RLS)

Supabase 的核心是 PostgreSQL，並且預設啟用了 Row Level Security (RLS) 以確保資料安全。

### 2.1 建立資料表 (Table)
你可以使用 Table Editor 或 SQL Editor 建立資料表。
```sql
-- 在 SQL Editor 中建立一個簡單的 notes 表
create table notes (
  id bigint generated always as identity primary key,
  content text not null,
  user_id uuid references auth.users (id) default auth.uid()
);
```

### 2.2 設定 RLS 策略 (Policies)
RLS 允許你定義誰可以讀取、插入或更新資料。
```sql
-- 啟用 RLS
alter table notes enable row level security;

-- 允許使用者只讀取自己的資料
create policy "Individuals can view their own notes." 
on notes for select
using ( auth.uid() = user_id );
```

### 2.3 進階 RLS 範例 (關聯表)
若要根據另一個表（例如 `profiles`）的狀態來判斷權限：
```sql
-- 僅允許 'admin' 角色查看所有備註
create policy "Admins can view all notes."
on notes for select
using (
  exists (
    select 1 from profiles
    where profiles.id = auth.uid()
    and profiles.role = 'admin'
  )
);
```

### 2.4 資料庫函式 (RPC)
當邏輯太複雜不適合在前端處理時，可以使用 Postgres 函式。
```sql
-- 建立一個統計使用者備註數量的函式
create or replace function get_note_count(user_id uuid)
returns clong as $$
  select count(*) from notes where notes.user_id = $1;
$$ language sql security definer;
```
前端呼叫方式：
```typescript
const { data, error } = await supabase.rpc('get_note_count', { user_id: '...' })
```

---

## 3. 本地開發與 CLI

Supabase 提供 CLI 工具，讓你在自己的電腦上運行完整的 Supabase 環境。

### 3.1 安裝與初始化
```bash
# 安裝 CLI
npm install supabase --save-dev

# 初始化本地配置
npx supabase init

# 啟動本地服務 (需安裝 Docker)
npx supabase start
```

### 3.2 資料庫遷移 (Migrations)
```bash
# 建立新的遷移檔案
npx supabase migration new setup_tables

# 將本地更動部署到雲端
npx supabase db push
```

---

## 4. 前端整合 (以 Next.js 為例)

### 4.1 設定環境變數
在專案根目錄建立 `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=你的_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=你的_SUPABASE_ANON_KEY
```

### 4.2 初始化客戶端
安裝套件:
```bash
npm install @supabase/supabase-js
```

建立 `utils/supabase.ts`:
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

---

## 5. 核心功能介紹

### 5.1 身份驗證 (Auth)
Supabase Auth 支援 Email、OAuth、Magic Link 等。

#### 使用者元數據 (User Metadata)
在註冊時儲存額外資訊（如姓名、頭像）：
```typescript
const { data, error } = await supabase.auth.signUp({
  email: 'example@email.com',
  password: 'your-password',
  options: {
    data: {
      full_name: 'John Doe',
      avatar_url: 'https://example.com/avatar.png'
    }
  }
})
```

#### 第三方登入 (OAuth)
支援 Google, GitHub, Apple 等。
```typescript
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
  options: {
    redirectTo: 'http://localhost:3000/auth/callback'
  }
})
```

### 5.2 儲存空間 (Storage)
用於儲存大型檔案。

#### 簽名 URL (Signed URLs)
針對私密檔案，產生一個具有時效性的存取連結：
```typescript
const { data, error } = await supabase.storage
  .from('avatars')
  .createSignedUrl('private/avatar1.png', 60) // 60 秒後失效
```

#### 圖片處理 (Image Transformation)
直接在 URL 中指定大小與格式：
```typescript
const { data } = supabase.storage
  .from('public-bucket')
  .getPublicUrl('image.jpg', {
    transform: {
      width: 500,
      height: 500,
      resize: 'contain', // 'cover', 'fill'
    },
  })
```

### 5.3 即時功能 (Realtime)

#### 監聽表格變化
```typescript
const channel = supabase.channel('table-db-changes')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'notes' }, (payload) => {
    console.log('新資料插入:', payload)
  })
  .subscribe()
```

#### 線上狀態 (Presence)
追蹤目前線上的使用者：
```typescript
const room = supabase.channel('room-1')

room
  .on('presence', { event: 'sync' }, () => {
    const newState = room.presenceState()
    console.log('當前線上清單:', newState)
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      const statusText = '線上升級中'
      await room.track({ online_at: new Date().toISOString(), statusText })
    }
  })
```

### 5.4 Edge Functions
Edge Functions 是分散式的 TypeScript 函式。

#### 部署範例
```bash
# 建立函數
npx supabase functions new hello-world

# 部署到雲端
npx supabase functions deploy hello-world
```

#### 內部資料庫存取
在 Function 中使用 `Deno` 與 `service_role` key 以跳過 RLS (僅限內部邏輯)：
```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )
  // 執行資料庫操作...
  return new Response("Done")
})
```

---

## 6. 部署與 CI/CD
1. **GitHub 整合**: 在專案設定中連結 GitHub。
2. **自動部署**: 每當 push 到 main 分支時，Supabase 可以自動執行資料庫遷移與 Edge Functions 部署。

---

## 7. SDK 語言範例 (JavaScript vs Python)

本節提供常用操作在 JavaScript 與 Python 中的寫法對比。

### 7.1 客戶端初始化 (Initialization)

| 語言 | 套件安裝 | 初始化代碼 |
| :--- | :--- | :--- |
| **JavaScript** | `npm install @supabase/supabase-js` | `const supabase = createClient(url, key)` |
| **Python** | `pip install supabase` | `supabase: Client = create_client(url, key)` |

### 7.2 資料讀取 (Select)

#### JavaScript (JavaScript)
```javascript
const { data, error } = await supabase
  .from('notes')
  .select('*')
  .eq('status', 'active')
```

#### Python (Python)
```python
response = (
    supabase.table("notes")
    .select("*")
    .eq("status", "active")
    .execute()
)
notes = response.data
```

### 7.3 身份驗證 (Auth - Sign Up)

#### JavaScript (JavaScript)
```javascript
const { data, error } = await supabase.auth.signUp({
  email: 'example@email.com',
  password: 'password123',
})
```

#### Python (Python)
```python
response = supabase.auth.sign_up({
    "email": "example@email.com",
    "password": "password123",
})
```

### 7.4 檔案上傳 (Storage - Upload)

#### JavaScript (JavaScript)
```javascript
const { data, error } = await supabase.storage
  .from('avatars')
  .upload('folder/avatar.png', fileBody)
```

#### Python (Python)
```python
# 需使用 .from_() 以避免與 Python 關鍵字衝突
with open('local_file.png', 'rb') as f:
    supabase.storage.from_('avatars').upload(
        path="folder/avatar.png",
        file=f,
        file_options={"content-type": "image/png"}
    )
```

---
> [!TIP]
> 建議在正式開發前先閱讀 [Supabase 官方文件](https://supabase.com/docs)，特別是關於 PostgreSQL 優化的部分。
