# PostgreSQL 18.2 官方文件指南

此指南概述了 [PostgreSQL 官方文件 (Current)](https://www.postgresql.org/docs/current/) 的主要結構與章節大綱，幫助使用者快速了解各部分提供的資訊：

## I. Tutorial (教學)
* 適合初學者，涵蓋如何開始使用 PostgreSQL、基本的 SQL 語言語法以及進階功能的簡要示範。主要分為以下三個部分：

### 1. Getting Started (開始使用)
* **詳細說明**: 介紹關聯式資料庫的基礎概念、PostgreSQL 伺服器與用戶端架構 (Client-Server Architecture)。這包含了最基礎但重要的**安裝、服務啟動與連線操作**。在 Mac 上，我們有非常方便的開發者工具可以完成，另外使用 Docker 也是強烈推薦的隔離環境安裝方式。
* **重點概念**: `brew install`, `docker run`, `docker compose`, `initdb` (初始化), `pg_ctl` (控制伺服器), `createdb` (建庫), `psql` (終端互動介面)。
* **實戰範例 (安裝與操作)**:
  ```bash
  # [這是一般 Mac 上的安裝方式]
  # 方式一: 透過 Mac 套件管理工具 Homebrew 安裝 (推薦開發者使用)
  brew install postgresql
  
  # 啟動 PostgreSQL 伺服器 (背景執行，Mac 重開機自動啟動)
  brew services start postgresql
  
  # 方式二: 使用 Postgres.app (推薦喜好圖形化管理介面者)
  # 到 https://postgresapp.com/ 下載並放到應用程式資料夾，點擊 Initialize 即可執行。

  # --------------------------------------------------------------------------
  # [重點推薦: 透過 Docker / Docker Compose 安裝]
  # 對於開發環境來說，Docker 能提供乾淨、隔離且容易重建的環境。

  # 方式三: 使用 docker run (適合快速單次啟動)
  # 啟動最新版 Postgres，設定密碼為 mysecretpassword，並將內部 5432 Port 暴露出來，以及掛載資料卷 psql_data
  docker run --name my-postgres \
    -e POSTGRES_PASSWORD=mysecretpassword \
    -p 5432:5432 \
    -v pgdata:/var/lib/postgresql/data \
    -d postgres

  # 登入 Docker 內的 PostgreSQL
  docker exec -it my-postgres psql -U postgres

  # 方式四: 使用 docker-compose (適合包含 GUI 管理工具 pgAdmin 一起啟動)
  # 準備 `docker-compose.yml` 檔案的內容如下：
  mkdir pgsql_docker && cd pgsql_docker
  touch docker-compose.yml
  ```
  ```yaml
  services:
    postgres:
      image: postgres:16
      container_name: pgdb
      restart: unless-stopped
      environment:
        POSTGRES_USER: root
        POSTGRES_PASSWORD: mysecretpassword
        POSTGRES_DB: my_database
      volumes:
        - ./pg_data:/var/lib/postgresql/data
      ports:
        - "5432:5432"

    pgadmin:
      image: dpage/pgadmin4
      container_name: pgadmin
      restart: unless-stopped
      environment:
        PGADMIN_DEFAULT_EMAIL: admin@admin.com
        PGADMIN_DEFAULT_PASSWORD: root
      ports:
        - "8080:80"
  ```
  ```bash
  # 執行 Docker Compose 背景啟動資料庫與 pgAdmin (http://localhost:8080)
  docker compose up -d
  
  # --------------------------------------------------------------------------
  # [基礎操作] (不論使用哪種啟動方式，以下為連接後的共通操作)
  # 1. 建立一個名為 mydb 的資料庫
  createdb mydb
  
  # 2. 透過 psql 互動式終端機連線進入 mydb 資料庫 (Docker 方式請進入 Container 後執行)
  psql mydb
  
  # 3. 在 psql 介面中，取得目前的連線資訊與 PostgreSQL 版本
  mydb=# SELECT version();
  
  # 4. 離開 psql 介面
  mydb=# \q
  ```

### 2. The SQL Language (SQL 語言基礎)
* **詳細說明**: 針對完全沒有 SQL 經驗的新手，解說最常用的資料庫操作，涵蓋 DDL (定義資料表) 與 DML (操作資料)。包含主鍵的設計、各種資料型態的選擇，以及最重要的 CRUD (Create, Read, Update, Delete) 操作及關聯查詢。
* **重點概念**: `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`, 聚合函數 (`COUNT`, `AVG`, `MAX`), 表格關聯 (`INNER JOIN`, `LEFT JOIN`).
* **實戰範例**:
  ```sql
  -- [建立資料表] 包含自動遞增的 Primary Key (SERIAL)
  CREATE TABLE employees (
      emp_id SERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      department VARCHAR(50),
      salary NUMERIC(10, 2)
  );

  -- [新增資料] 一次插入多筆資料
  INSERT INTO employees (name, department, salary) VALUES 
      ('Alice', 'Engineering', 85000),
      ('Bob', 'Sales', 62000),
      ('Charlie', 'Engineering', 92000);

  -- [查詢資料] 結合條件過濾與排序
  SELECT name, salary FROM employees 
  WHERE department = 'Engineering' 
  ORDER BY salary DESC;

  -- [聚合函數與分組] 計算每個部門的平均薪資
  SELECT department, ROUND(AVG(salary), 2) AS avg_salary, COUNT(*) AS headcount
  FROM employees 
  GROUP BY department;

  -- [更新資料] 將特定員工的薪水調高
  UPDATE employees SET salary = salary * 1.05 WHERE name = 'Bob';

  -- [刪除資料]
  DELETE FROM employees WHERE name = 'Charlie';
  ```

### 3. Advanced Features (進階功能)
* **詳細說明**: 當熟悉基本語法後，此章節會帶入關聯式資料庫進階的核心能力，確保資料的完整性 (Data Integrity) 與簡化應用程式邏輯。包含透過檢視表隱藏複雜的 SQL 邏輯、利用外來鍵確保關聯正確、以交易確保多步操作的原子性 (Atomicity)，以及強大的視窗函數。
* **重點概念**: `VIEW` (檢視表), `FOREIGN KEY` (外來鍵), `BEGIN`/`COMMIT`/`ROLLBACK` (交易控制), `WINDOW FUNCTIONS` (視窗函數)。
* **實戰範例**:
  ```sql
  -- [外來鍵 Foreign Key] 確保資料參照完整性
  CREATE TABLE orders (
      order_id SERIAL PRIMARY KEY,
      emp_id INT REFERENCES employees(emp_id), -- 指向 employees 表
      order_date DATE DEFAULT CURRENT_DATE
  );

  -- [檢視表 View] 簡化複雜查詢，將其儲存為虛擬表
  CREATE VIEW high_paid_engineers AS
      SELECT name, salary FROM employees 
      WHERE department = 'Engineering' AND salary > 80000;
  
  -- 直接查詢視圖
  SELECT * FROM high_paid_engineers;

  -- [交易 Transaction] 確保多條語句要嘛全成功，要嘛全失敗
  BEGIN;
  UPDATE accounts SET balance = balance - 1000 WHERE user_id = 1;
  UPDATE accounts SET balance = balance + 1000 WHERE user_id = 2;
  COMMIT; -- 若發生錯誤，可改用 ROLLBACK 撤銷

  -- [視窗函數 Window Functions] 保留原始資料列的同時，計算跨資料列的聚合數據
  -- 比較每位員工與其「所屬部門平均薪資」的差異
  SELECT 
      name, 
      department, 
      salary,
      AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary
  FROM employees;
  ```

## II. The SQL Language (SQL 語言)
* 這是指南中最核心、也是開發者最常參考的部分，詳細說明 PostgreSQL 中的 SQL 語法與規則。包含以下主要章節：

### 4. SQL Syntax (SQL 語法)
* **詳細說明**: 基礎的 SQL 語法結構，包含了命令辨識字 (Identifiers)、引號跳脫邏輯 (Quotes & Escapes) 以及常數表示法 (Constants)。了解 PostgreSQL 中的大小寫不敏感性（除非加上雙引號）對於處理欄位名稱有極大的幫助。
* **重點概念**: 雙引號 `"column"` vs 單引號 `'string'`, SQL 語法結構。
* **實戰範例**:
  ```sql
  -- [雙引號與單引號區別]
  -- 雙引號用於保留欄位大小寫與特殊字元，單引號用於純數值或字串
  SELECT "UserId", "Created_At" FROM "Users" WHERE status = 'active';
  ```

### 8. Data Types (資料型別)
* **詳細說明**: PostgreSQL 除了傳統整數 (INTEGER)、字串 (VARCHAR)、布林與日期時間外，提供了**極為豐富且具備運算特性的現代非結構化型別**，這是它超越多數同級產品的優勢。
    * **JSON 與 JSONB**: 業界早期即支援 JSON。強烈建議使用 `JSONB` (二進位存取)，因為它能在寫入時解析並去除不必要的空白，並支援高度優化的 GIN 索引，讓巢狀資料檢索速度極快。
    * **Array (陣列)**: 允許在單數欄位中儲存多個值，且可支援多維度。極度適合「標籤 (Tags)」、「多選下拉選單」這種不需要特別切出一張關聯表的輕量一對多狀態。
    * **UUID**: 原生支援 128-bit `UUID` 型別，而非用 `VARCHAR(36)` 儲存。這能大幅降低儲存空間浪費並提昇查詢與索引效率。可使用 `gen_random_uuid()` 自動產生 v4 UUID。
    * **Network Address (網路位址)**: `CIDR`、`INET` 或 `MACADDR` 型別，寫入時會自動驗證 IP 格式是否合法，並內建支援 IP 範圍檢查運算 (如判斷是否在子網段內)。
    * **Range Types (區間型別)**: 支援數值區間 `int4range`、日期區間 `daterange` 等型別，特別適合處理「排程重疊判定」、「價格帶」等情境，免去寫複雜的兩端條件判斷。
    * **Numeric vs Float**: 處理牽涉到金錢計算時，必須使用 `NUMERIC` 來確保精確度，避免 `FLOAT`/`REAL` 所帶來的 IEEE 754 浮點數精度遺失問題。
* **重點概念**: `JSONB`, `TEXT[]`, `UUID`, `INET`, `daterange`, `NUMERIC`.
* **實戰範例**:
  ```sql
  -- [定義多樣化的進階型別建表]
  CREATE TABLE system_events (
      event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      source_ip INET NOT NULL,                 -- 網路位址型別
      flags TEXT[],                            -- 字串陣列型別
      payload JSONB,                           -- JSONB 型別
      active_period DATERANGE,                 -- 日期區間型別
      created_at TIMESTAMPTZ DEFAULT NOW()     -- 帶時區的時間戳記
  );

  -- [新增陣列、區間與 JSON 資料]
  INSERT INTO system_events (source_ip, flags, payload, active_period) VALUES (
      '192.168.1.50/24', 
      ARRAY['urgent', 'security'], 
      '{"severity": "high", "details": {"retries": 3}}'::JSONB,
      '[2026-02-01, 2026-02-28)'               -- 表示從 2/1 開始，直到 2/28 (不含 28 號當日)
  );

  -- [操作進階型別的查詢]
  -- 尋找來源 IP 是否屬於 192.168.1.0/24 網段，且陣列中包含 'urgent'
  SELECT event_id, payload->>'severity' AS error_level
  FROM system_events 
  WHERE source_ip << '192.168.1.0/24' AND 'urgent' = ANY(flags);
  
  -- [透過 JSON 功能新增及更新嵌套的屬性]
  -- jsonb_set 是 PostgreSQL 中針對 JSON 操作極為強大的函數
  UPDATE system_events 
  SET payload = jsonb_set(payload, '{details, resolved}', 'true'::JSONB)
  WHERE 'security' = ANY(flags);
  ```

### 5. Data Definition (資料定義 - DDL)
* **詳細說明**: 結構定義層次。這不僅涵蓋基礎建表，還深入約束條件（Constraints）設計、權限管理（GRANT/REVOKE）、欄位層級安全性、列層級安全政策 (Row Level Security, RLS) 及表分區 (Partitioning) 對大量資料的高效處理。
* **重點概念**: `CHECK`, `UNIQUE`, `ALTER TABLE`, `PARTITION BY`, `CREATE POLICY`.
* **實戰範例**:
  ```sql
  -- [使用多種約束條件] 防止不合理資料寫入
  CREATE TABLE products (
      product_id SERIAL PRIMARY KEY,
      sku VARCHAR(20) UNIQUE NOT NULL,
      price NUMERIC(10, 2) CHECK (price > 0),
      discounted_price NUMERIC(10, 2),
      CHECK (discounted_price <= price) -- 表級約束
  );

  -- [修改資料表結構]
  ALTER TABLE products ADD COLUMN description TEXT;
  ALTER TABLE products ALTER COLUMN description SET NOT NULL;

  -- [表分區 Partitioning] 對於大型時間序列資料很有用
  CREATE TABLE measurement (
      city_id         int not null,
      logdate         date not null,
      peaktemp        int
  ) PARTITION BY RANGE (logdate);
  -- 建立子表
  CREATE TABLE measurement_y2026m02 PARTITION OF measurement 
      FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
  ```

### 6. Data Manipulation (資料操作 - DML) & 7. Queries (查詢)
* **詳細說明**: PostgreSQL 查詢與資料操作能力超越多數同級產品。
    * **RETURNING 語法**: 許多應用程式在新增 (INSERT) 或更新 (UPDATE) 後，還需要馬上知道寫入了什麼值 (例如新產生的 ID，或預設時間)。加上 `RETURNING` 子句，可用一次資料庫操作完成寫入與讀取，省下去回程與連線成本。
    * **UPSERT 機制 (`ON CONFLICT`)**: 當大量新增資料時，常遇到 Primary Key 或 Unique Key 衝突。PostgreSQL 支援 `INSERT ... ON CONFLICT DO UPDATE` (覆寫更新) 或 `DO NOTHING` (略過)，優雅解決重複資料寫入的例外狀態，避免程式端需要先 Select 檢查。
    * **WITH CTE (通用資料表運算式)**: 允許將複雜的子查詢宣告為臨時名稱的虛擬資料表，可大幅提高複雜報表或多層邏輯 SQL 的「可讀性」與「維護性」。
    * **Recursive CTE (遞迴查詢)**: CTE 甚至支援遞迴 `WITH RECURSIVE`，可用來處理圖形結構或樹狀結構，如「員工上下級關係」、「分類目錄樹」。
* **重點概念**: `RETURNING`, `INSERT ... ON CONFLICT (UPSERT)`, `WITH (CTE)`, `WITH RECURSIVE`.
* **實戰範例**:
  ```sql
  -- [UPSERT (插入或更新)]
  -- 如果 username 被 Unique 限制擋下，則不報錯，改為將 login_count 數量加一
  INSERT INTO customer_logins (username, login_count) 
  VALUES ('alice', 1) 
  ON CONFLICT (username) DO UPDATE 
  SET login_count = customer_logins.login_count + EXCLUDED.login_count
  RETURNING username, login_count;  -- [RETURNING] 插入後直接回傳最新狀態

  -- [WITH CTE 通用資料表運算式] 提高複雜查詢的可讀性
  WITH regional_sales AS (
      -- 建立第一層臨時表
      SELECT region, SUM(amount) AS total_sales
      FROM orders
      WHERE order_date >= current_date - interval '1 year'
      GROUP BY region
  ),
  top_regions AS (
      -- 依賴前一個臨時表的結果
      SELECT region FROM regional_sales
      WHERE total_sales > (SELECT SUM(total_sales) / 10 FROM regional_sales)
  )
  -- 最終透過簡單的 JOIN 將最終結果整理出來
  SELECT o.order_id, o.region, o.amount 
  FROM orders o 
  JOIN top_regions t ON o.region = t.region;
  
  -- [遞迴 CTE] 尋找樹狀目錄的所有子節點 (包含自身)
  WITH RECURSIVE category_tree AS (
      -- 基礎查詢 (Base Query)
      SELECT id, name, parent_id
      FROM categories 
      WHERE name = 'Electronics'
    UNION ALL
      -- 遞迴查詢 (Recursive Query)
      SELECT c.id, c.name, c.parent_id
      FROM categories c
      INNER JOIN category_tree ct ON c.parent_id = ct.id
  )
  SELECT * FROM category_tree;
  ```

### 9. Functions and Operators (函數與運算子)
* **詳細說明**: 在資料庫這層直接進行邏輯運算能帶來極大的傳輸效能優勢。此章節匯集 PostgreSQL 提供的大量內建工具，能夠輕鬆取代許多應用程式端的處理。
    * **防空值出錯 (`COALESCE` 與 `NULLIF`)**: PostgreSQL 對 `NULL` 的運算會返回 `NULL` (如 `1 + NULL = NULL`)。`COALESCE` 可順序檢查並給予預設值防呆；相對的，`NULLIF` 能阻止特定的例外 (如防範分母為 0 引發除以零錯誤)。
    * **字串處理機制**: 擁有強大的正規表達式支援符號 (`~`) 以及特有的忽略大小寫模糊比對預定義字元 (`ILIKE`)，也可用 `SUBSTRING` 進行精確拆分。
    * **日期推移 (`interval`)**: 傳統資料庫以難纏的整點或字串來做日期時間推演，PostgreSQL `interval` 卻可以用平易近人的如 `+ interval '1 day 3 hours'` 快速做到精準偏移。
    * **字串拼接與格式化 (`||`, `TO_CHAR`)**: 使用 `||` 直接連接文字不用依靠 `CONCAT()`；利用 `TO_CHAR(date, format)` 以客製化風格產出字串能有效取代應用端的繁雜邏輯。
    * **陣列專屬運算子**: 確認包含關係的 (`@>`, `<@`)，不需要拆開字串或 `IN`。
* **重點概念**: `interval`, `TO_CHAR`, `COALESCE`, `NULLIF`, `||`, `ILIKE`, `~` (regex match),陣列包含 `@>`.
* **實戰範例**:
  ```sql
  -- [COALESCE 確保運算安全] 空值與數字相加會變 NULL，這常導致未知的邏輯臭蟲
  SELECT emp_id, salary + COALESCE(bonus, 0) AS total_compensation FROM compensation;

  -- [NULLIF 防止除以零例外]
  -- 若 denominator 為 0, 強迫回傳 NULL，分子除以 NULL 等於 NULL 就不會造成整個 Query Crash
  SELECT order_id, total_amount / NULLIF(total_items, 0) AS avg_item_price FROM order_stats;

  -- [日期推移與字串格式化] 輕鬆推算每月結算點並輸出自訂格式字串
  SELECT TO_CHAR(CURRENT_DATE + interval '1 month' - interval '1 day', 'YYYY-MM-DD HH24:MI:SS') AS end_of_billing_cycle;

  -- [正規表達式運算子]
  -- 尋找所有信箱開頭為 'admin' 且包含特定網域的紀錄 (無視大小寫正則比對 ~*)
  SELECT email FROM users WHERE email ~* '^admin.*@company\.com$';

  -- [陣列專屬運算子 (@>)] 
  -- 檢查該 user 的 roles 陣列中是否同時具備 ('admin', 'superuser')
  SELECT * FROM users_extended WHERE roles @> ARRAY['admin', 'superuser'];
  ```

### 10. Type Conversion (型別轉換)
* **詳細說明**: PostgreSQL 是個非常嚴格的**強型別** (Strongly Typed) 系統。如果型別不匹配 (例如將 `VARCHAR` 餵給 `INTEGER` 進行運算)，多數關聯資料庫可能會「靜默隱式轉換」而暗藏效能陷阱，但 Postgres 通常會直接報錯，要求開發者提供顯式 (Explicit) 宣告。
    * **簡潔的轉換符號 (`::`)**: 除了標準 SQL 冗長的 `CAST(value AS type)` 外，這是在 Postgres 中最優雅而直觀的轉換語法，可無縫用在多重條件判斷內。
    * **JSON/JSONB 屬性轉換**: 當使用 `->>` 運算子從 JSON 中提煉出的最終結果*必為字串 `TEXT`*。若提煉的數字要做大小比對或相加，絕對必須搭配 `::INT` 或 `::NUMERIC`。
    * **函式重載 (Function Overloading) 支援**: 同一個函式名稱會依賴輸入資料的型別，動態決定調用不同的內建實作，這是嚴格要求型別的一大好處。
* **重點概念**: `::`, `CAST()`, JSON 文字提取強制轉換。
* **實戰範例**:
  ```sql
  -- [基礎型別轉換 :: 替代 CAST]
  SELECT '2026-12-31'::DATE - '2026-01-01'::DATE AS days_diff_in_year;
  SELECT '123'::NUMERIC + 4.5 AS mixed_sum;

  -- [非常關鍵的 JSONB 值轉換] 
  -- 若沒有加 ::INT，字串 '18' 會和整數直接報錯，或進行不可預期的 ASCII 字串比較
  SELECT username, profile->>'age' AS user_age_string
  FROM users_extended
  WHERE (profile->>'age')::INT > 18;  

  -- [布林值處理]
  -- 在舊系統中可能儲存 't' 或 '1'，PostgreSQL 可透過顯式轉換統一理解為 True
  SELECT '1'::BOOLEAN AS is_true, '0'::BOOLEAN AS is_false;
  ```

### 11. Indexes (索引) & 12. Full Text Search (全文檢索)
* **詳細說明**: 資料庫效能的靈魂。從基礎的 B-Tree，到適用於 Array / JSONB 的 GIN 索引、空間資料的 GiST索引。更提供強大的「部分索引 (Partial Index)」與「表達式索引 (Expression Index)」，能做到只針對所需資料建索引，極大化空間與效能最佳化。另外還具備中英文分詞的全文檢索功能。
* **重點概念**: `CREATE INDEX`, `USING GIN`, 表達式索引, `tsvector`, `tsquery`.
* **實戰範例**:
  ```sql
  -- [陣列或 JSONB 使用 GIN 索引] 巨大加速 JSONB 內部結構的查詢
  CREATE INDEX idx_users_profile_gin ON users_extended USING GIN (profile);

  -- [部分索引 Partial Index] 節省索引空間，只對 active 狀態為 true 的紀錄建索引
  CREATE INDEX idx_active_users ON accounts (account_id) WHERE is_active = true;

  -- [表達式索引 Expression Index] 針對無視字母大小寫的查詢最佳化
  CREATE INDEX idx_lower_email ON accounts (LOWER(email));

  -- [全文檢索 Full Text Search]
  -- 將文章標題與內容轉為搜尋向量，並以片語進行檢索
  SELECT title 
  FROM articles 
  WHERE to_tsvector('english', title || ' ' || content) @@ to_tsquery('english', 'PostgreSQL & performance');
  ```

### 13. Concurrency Control (並行控制) & 14. Performance Tips (效能優化)
* **詳細說明**: 面對高併發的產品環境，必須了解多版本並行控制機制 (MVCC)，以避免讀寫互相造成鎖定 (Locking)。同時，必須熟悉利用 `EXPLAIN ANALYZE` 解析執行計畫，找出慢查詢 (Slow Queries) 出現的根本原因 (如 Seq Scan 或 Index Scan)，並透過 `VACUUM` 或分析統計資訊改善。
* **重點概念**: `MVCC`, 隔離層級 (Isolation Levels), 行級鎖定 (`FOR UPDATE`), `EXPLAIN ANALYZE`, `VACUUM`.
* **實戰範例**:
  ```sql
  -- [行級鎖定 FOR UPDATE] 防止兩人同時扣除庫存的併發問題 (Race Condition)
  BEGIN;
  SELECT stock_quantity 
  FROM inventory 
  WHERE product_id = 100 FOR UPDATE; 
  -- 處理應用邏輯...
  UPDATE inventory SET stock_quantity = stock_quantity - 1 WHERE product_id = 100;
  COMMIT;

  -- [效能解析 EXPLAIN ANALYZE] 檢視查詢成本與實際執行時間
  EXPLAIN ANALYZE 
  SELECT * FROM transactions WHERE user_id = 105 AND status = 'COMPLETED';
  -- 輸出結果將顯示資料庫是進行全表掃描 (Seq Scan) 還是走對應的索引 (Index Scan)。
  ```

## III. Server Administration (伺服器管理)
* 針對資料庫管理員 (DBA) 的核心指南。
* 包含從二進位檔或原始碼安裝、伺服器的設定與維護 (Server Setup/Configuration)。
* 教導用戶端認證 (Client Authentication)、角色權限設計、備份與還原 (Backup and Restore)。
* 進階主題如：高可用性、負載平衡與資料複寫 (High Availability and Replication)、資源監控以及寫入前記錄檔 (WAL) 等運作機制。

## IV. Client Interfaces (用戶端程式介面)
* 描述如何透過主要的程式函式庫連接至應用程式。
* 包括 C 語言原生的 `libpq` 函式庫、大型物件處理 (Large Objects)、以及 ECPG (嵌入式 SQL in C)。

## V. Server Programming (伺服器端開發)
* 說明如何利用資料庫的功能來處理伺服器端運作邏輯，進而擴展 SQL (Extending SQL)。
* 涵蓋觸發器 (Triggers)、事件觸發器 (Event Triggers)、規則系統 (The Rule System)。
* 詳細說明如何使用各類程序性語言撰寫函數，例如 `PL/pgSQL` (SQL原生預存程序語言)、`PL/Tcl`、`PL/Perl`、`PL/Python` 等。

## VI. Reference (參考手冊)
* 完整的指令與程式參考字典。
* 詳細列出所有支援的 I. SQL 指令、II. PostgreSQL 用戶端應用程式工具 (如 `psql`, `pg_dump`)、III. PostgreSQL 伺服器端應用程式 (如 `postgres`, `initdb`) 的參數及用法。

## VII. Internals (系統內部原理)
* 適合開發 PostgreSQL 擴充套件或參與核心專案的進階開發者。
* 深入探討：系統目錄 (System Catalogs)、從前端至後端之通訊協定 (Protocol)、PostgreSQL 程式碼撰寫慣例。
* 以及如何實作及客製化自己的資料封裝器 (Foreign Data Wrapper)、存取方法、並行策略、排程器行為與事務處理 (Transaction Processing) 原理。

## VIII. Appendixes (附錄)
* 提供各類補充及查詢資訊：
    * PostgreSQL 錯誤碼對照表
    * 日期/時間支援列表與格式
    * SQL 關鍵字比較與相容性標準
    * 發布說明 (Release Notes，涵蓋升級注意事項)
    * 附加的模組與擴充工具說明 (即 `contrib` 的介紹)
