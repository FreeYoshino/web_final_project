
<h1 align="center">
  🧾 Roommate Sync
</h1>

<p align="center">
  <strong>群組分帳系統 · Group Expense Splitting System</strong>
  <br>
  智慧拆帳、動態結算、債務最小化 —— 讓每一筆帳都清清楚楚
</p>

<p align="center">
  <!-- Frontend -->
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/React_Router-7-CA4245?style=for-the-badge&logo=reactrouter&logoColor=white" alt="React Router">
  <img src="https://img.shields.io/badge/TanStack_Query-5-FF4154?style=for-the-badge&logo=reactquery&logoColor=white" alt="TanStack Query">
  <img src="https://img.shields.io/badge/Zustand-5-443E38?style=for-the-badge" alt="Zustand">
  <br>
  <!-- Backend -->
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Pydantic-2.12-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/JWT-OAuth2-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

## 👥 團隊成員

<table align="center">
  <tr>
    <td align="center" width="50%">
      <a href="https://github.com/前端開發者GitHubID">
        <img src="https://github.com/前端開發者GitHubID.png" width="100px" style="border-radius: 50%;" alt="前端開發者"/>
        <br />
        <sub><b>👤 Atlas0319</b></sub>
        <br />
        <sub>📧 email@example.com</sub>
      </a>
      <br />
      <sub>🎨 <strong>前端工程師 · Frontend Developer</strong></sub>
      <br />
      <sub>負責 UI/UX 設計、React 元件開發、</sub>
      <br />
      <sub>狀態管理、API 串接與前端部署</sub>
    </td>
    <td align="center" width="50%">
      <a href="https://github.com/後端開發者GitHubID">
        <img src="https://github.com/後端開發者GitHubID.png" width="100px" style="border-radius: 50%;" alt="後端開發者"/>
        <br />
        <sub><b>👤 FreeYoshino</b></sub>
        <br />
        <sub>📧 abc0940415@gmail.com</sub>
      </a>
      <br />
      <sub>⚙️ <strong>後端工程師 · Backend Developer</strong></sub>
      <br />
      <sub>負責資料庫架構設計、RESTful API 開發、</sub>
      <br />
      <sub>JWT 身分驗證、債務簡化演算法與後端部署</sub>
    </td>
  </tr>
</table>

> 💡 **協作模式**：本專案採用前後端分離架構，兩人各自獨立開發前端與後端，透過定義好的 RESTful API 契約進行整合。前後端皆以 Git 進行版本控管，並透過 GitHub 協作。

---

## 📖 專案簡介

### 開發動機

在多人合租、出遊、聚餐的場景中，誰先墊錢？每個人該分攤多少？最後誰要給誰多少錢？這些看似簡單的問題，隨著人數與交易筆數增加，往往變得一團混亂。

**Roommate Sync** 正是為了解決這個痛點而生 —— 它是一個全端群組分帳系統，讓使用者可以建立群組、記錄每一筆共同支出、自動計算每人應付金額，並智慧化簡化最終的結算流程。前端採用現代 React 生態系打造流暢的使用者體驗，後端則以 FastAPI 提供高效穩定的 API 服務。

### 核心設計哲學：Stateless Balance

> **「餘額不是存在資料庫的欄位，而是從交易紀錄中動態計算出來的。」**

本系統堅持 **無狀態（Stateless）** 設計原則 —— 每位成員的帳務餘額（balance）完全由底層的 `expenses`（支出紀錄）與 `settlements`（還款紀錄）即時聚合計算而成。這意味著：

- 🛡️ **財務數據 100% 可審計**：每一分錢的來龍去脈都有跡可循，不存在「餘額欄位與交易明細不符」的風險
- 🔄 **Single Source of Truth**：所有計算以原始交易為唯一資料源，避免狀態同步問題
- 🧹 **零髒資料風險**：不存在快取過期或手動修改餘額導致的不一致

---

## ⚙️ 全端技術棧

### 🎨 前端 (Frontend)

| 類別 | 技術 | 說明 |
|------|------|------|
| **UI 框架** | React 19 | 最新版 React，採用函式元件與 Hooks |
| **建構工具** | Vite 8 | 極速 HMR 開發體驗與高效生產打包 |
| **路由** | React Router DOM 7 | 客戶端 SPA 路由管理 |
| **樣式** | Tailwind CSS 3 | Utility-first CSS 框架，快速打造回應式 UI |
| **HTTP 客戶端** | Axios | 統一的 API 請求封裝與攔截器 |
| **伺服器狀態** | TanStack React Query 5 | 自動快取、背景重取與樂觀更新 |
| **客戶端狀態** | Zustand 5 | 輕量級全域狀態管理 |
| **圖示** | Lucide React | 開源 SVG 圖示庫 |
| **程式碼品質** | ESLint 9 + Prettier | 程式碼風格統一與自動格式化 |

### ⚙️ 後端 (Backend)

| 類別 | 技術 | 說明 |
|------|------|------|
| **Web 框架** | FastAPI 0.135 | 高效能非同步 Python API 框架，內建自動 OpenAPI 文件生成 |
| **ORM** | SQLAlchemy 2.0 | 成熟穩定的 Python ORM，支援宣告式模型與關聯載入 |
| **資料庫** | PostgreSQL 15 | 企業級關聯式資料庫，使用 UUID 主鍵與 DECIMAL 精確金額 |
| **資料驗證** | Pydantic 2.12 | 請求/回應 Schema 定義與自動型別驗證 |
| **身分驗證** | python-jose + OAuth2 | JWT Token 簽發與驗證，標準 OAuth2PasswordBearer 流程 |
| **資料庫遷移** | Alembic 1.18 | 資料庫 Schema 版本控管與自動遷移 |
| **部署** | Docker Compose | PostgreSQL 本地開發環境一鍵啟動 |

---

## ✨ 系統亮點特色

### 🧠 貪婪演算法債務最小化 (Greedy Debt Simplification)

> **這是本系統最具技術深度的核心演算法，由後端工程師獨立設計與實作。**

在一個 N 人的群組中，若直接按每筆交易的借貸關係各自結算，最壞情況需要 **N(N−1)** 次轉帳才能完成所有人的債務清償。本系統將問題建模為圖論中的**最小邊覆蓋問題**，並以貪婪策略將轉帳次數優化至 **最多 N−1 次**。

#### 演算法流程

```
輸入：每位成員的淨餘額（正數 = 應收款，負數 = 應付款）

1. 分離角色
   ├── debtors[]  ← net_balance < 0（債務人，應付款）
   └── creditors[] ← net_balance > 0（債權人，應收款）

2. 排序（絕對值由大至小）
   ├── debtors:   [-800, -300, -100]
   └── creditors: [+900, +300]

3. 雙指針貪婪配對
   i → 指向最大債務人，j → 指向最大債權人
   while i < len(debtors) and j < len(creditors):
       amount = min(|debtors[i]|, creditors[j])
       產生建議: debtors[i] 支付 amount 給 creditors[j]
       更新餘額，若歸零則移動指針
```

#### 圖論視覺化

```
    簡化前（N=5，最多 20 筆轉帳）           簡化後（最多 4 筆轉帳）

       A ──→ B                                A ──→ C
       A ──→ C              貪婪演算法          B ──→ C
       B ──→ C           ════════════>         B ──→ D
       B ──→ D                                 E ──→ A
       C ──→ A
         ⋯
```

> 💡 **複雜度分析**：時間 O(N log N)（排序主導），空間 O(N)。由於群組人數 N 通常遠小於交易筆數 M，此演算法在實際應用中幾乎是常數時間完成。API 端點 `GET /groups/{id}/balances` 直接回傳簡化後的結算建議清單，前端無需額外計算即可渲染。

### 🔐 JWT 身分驗證與依賴注入權限控制

完整實作 OAuth2 + JWT 標準認證流程：

```python
# 後端：使用 FastAPI Depends 注入當前使用者身分，零侵入性權限控制
@router.post("/expenses")
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),  # ← JWT 自動解析
):
```

- JWT Token 簽發（`POST /login`）與驗證（`Depends(get_current_user_id)`）
- Token 過期自動偵測，回傳 `401 Unauthorized` 與標準 `WWW-Authenticate` 標頭
- 前端透過 Axios 攔截器自動附加 `Authorization: Bearer <token>` 標頭
- 金鑰與演算法透過環境變數注入，符合 [12-Factor App](https://12factor.net/) 原則

### 🔄 Transaction 事務處理：確保資料一致性

每當建立一筆費用時，系統必須**同時**寫入 `expenses`（帳單總表）與 `expense_splits`（分攤明細）。透過 SQLAlchemy 的 Transaction 機制確保原子性：

```python
try:
    db.add(new_expense)
    db.flush()              # 取得 expense ID
    db.add_all(split_records)  # 寫入所有分攤明細
    db.commit()             # ← 全部成功才提交
    db.refresh(new_expense)
except Exception:
    db.rollback()           # ← 任一失敗即全部回溯
    raise
```

> 若分攤明細寫入失敗，整筆費用也會一併回溯，絕不會出現「有帳單沒明細」或「有明細沒帳單」的資料不一致狀況。

### 🎨 現代前端開發體驗

- **React 19 + Vite 8**：極速熱模組替換（HMR），開發體驗流暢
- **TanStack React Query**：自動管理 API 資料的快取、背景重取、樂觀更新，減少手動狀態管理
- **Zustand**：輕量級客戶端狀態管理，無 Boilerplate 程式碼
- **Tailwind CSS**：Utility-first 原子化 CSS，快速打造一致且響應式的 UI
- **React Router DOM**：宣告式路由，支援巢狀佈局與動態路由參數

---

## 🏗️ 全端系統架構

```
final-project/
├── frontend/                    # 🎨 前端 React 應用 (Vite)
│   ├── src/
│   │   ├── main.jsx             # React 應用入口
│   │   ├── App.jsx              # 路由與全域配置
│   │   ├── pages/               # 頁面元件
│   │   │   ├── AuthPage.jsx     # 登入/註冊頁面
│   │   │   ├── GroupsPage.jsx   # 群組管理頁面
│   │   │   ├── NewBillPage.jsx  # 新增帳單頁面
│   │   │   └── ProfilePage.jsx  # 個人檔案頁面
│   │   ├── components/          # 共用 UI 元件
│   │   ├── layouts/             # 頁面佈局
│   │   ├── services/api.js      # Axios API 請求封裝
│   │   └── store/               # Zustand 全域狀態
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/                     # ⚙️ 後端 API 服務 (FastAPI)
│   ├── app/
│   │   ├── main.py              # FastAPI 應用入口、CORS 設定
│   │   ├── core/
│   │   │   ├── config.py        # 環境變數設定 (Pydantic Settings)
│   │   │   └── security.py      # JWT 簽發/驗證、OAuth2 依賴注入
│   │   ├── db/
│   │   │   └── database.py      # SQLAlchemy 引擎、Session、Base 宣告
│   │   ├── models/              # ORM 模型 (User, Group, Expense, Settlement)
│   │   ├── schemas/             # Pydantic Schema (請求/回應驗證)
│   │   ├── routers/             # API 路由層
│   │   ├── services/            # 商業邏輯層
│   │   │   ├── balance.py       # 餘額計算服務
│   │   │   ├── simplification.py # 🧠 債務最小化演算法
│   │   │   └── expense_split_helper.py  # 均分/指定金額分攤邏輯
│   │   ├── crud/                # 資料存取層
│   │   └── scripts/             # 種子資料腳本
│   ├── alembic/                 # 資料庫遷移版本
│   ├── docker-compose.yml       # PostgreSQL 容器
│   └── requirements.txt
│
└── README.md
```

> 💡 **前後端分離架構**：前端執行於 `localhost:5173`（Vite Dev Server），後端執行於 `localhost:8000`（Uvicorn），透過 CORS 設定允許跨來源請求。前後端僅透過 RESTful API 交換 JSON 資料，彼此完全解耦。

---

## 🚀 本地端快速啟動指南

### 前置需求

- Python 3.12+
- Node.js 20+
- Docker Desktop（用於啟動 PostgreSQL）
- Git

---

### 🎨 前端啟動

```bash
# 1. 進入前端目錄
cd frontend

# 2. 安裝依賴
npm install

# 3. 啟動 Vite 開發伺服器
npm run dev
```

前端開發伺服器將運行於 **http://localhost:5173**。

---

### ⚙️ 後端啟動

```bash
# 1. 進入後端目錄
cd backend

# 2. 啟動 PostgreSQL 資料庫
docker-compose up -d

# 3. 建立虛擬環境與安裝依賴
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# 4. 設定環境變數（於 backend/ 目錄下建立 .env 檔案）
```

`.env` 檔案範例：

```env
# 資料庫連線
DATABASE_URL=postgresql://root:rootpassword@localhost:5432/roommate_db

# JWT 密鑰（請使用 openssl rand -hex 32 自行生成）
JWT_SECRET_KEY=your-secret-key-here

# JWT 過期時間（分鐘）
ACCESS_TOKEN_EXPIRE_MINUTES=30

# JWT 演算法
JWT_ALGORITHM=HS256
```

```bash
# 5. 執行資料庫遷移
alembic upgrade head

# 6. 匯入種子資料（選用）
python -m app.scripts.seed_data

# 7. 啟動開發伺服器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

後端 API 伺服器將運行於 **http://localhost:8000**。

---

## 📚 API 文件導覽

FastAPI 內建自動生成 **OpenAPI / Swagger UI** 互動式文件。啟動伺服器後，瀏覽器開啟以下網址即可直接測試所有 API：

| 文件類型 | URL |
|----------|-----|
| **Swagger UI**（互動式測試） | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **ReDoc**（唯讀瀏覽） | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

> 💡 Swagger UI 上每個端點都有 **「Try it out」** 按鈕，你可以直接在瀏覽器上呼叫 API、填寫參數、查看回應，無需 Postman。這也是前後端開發時的共同溝通介面。

### API 端點總覽

| 方法 | 端點 | 說明 | 認證 | 負責 |
|------|------|------|------|------|
| `POST` | `/users` | 註冊新使用者 | — | 後端 |
| `POST` | `/login` | 使用者登入，取得 JWT Token | — | 後端 |
| `GET` | `/users/me` | 查詢目前登入的使用者資訊 | 🔒 | 後端 |
| `GET` | `/users?q=...` | 搜尋使用者（模糊比對） | 🔒 | 後端 |
| `POST` | `/groups` | 建立新群組 | 🔒 | 後端 |
| `GET` | `/groups` | 查詢我的群組列表 | 🔒 | 後端 |
| `POST` | `/groups/{id}/members` | 加入成員至群組 | 🔒 | 後端 |
| `GET` | `/groups/{id}/members` | 取得群組成員清單 | 🔒 | 後端 |
| `GET` | `/groups/{id}/balances` | 取得結算餘額 & 債務簡化建議 | 🔒 | 後端 |
| `POST` | `/expenses` | 建立一筆費用（均分/指定金額） | 🔒 | 後端 |
| `GET` | `/groups/{id}/expenses` | 查詢群組費用列表（分頁） | 🔒 | 後端 |
| `POST` | `/settlements` | 建立一筆還款結算紀錄 | 🔒 | 後端 |
| `GET` | `/groups/{id}/settlements` | 查詢群組結算列表（分頁） | 🔒 | 後端 |

---

## 👤 個人貢獻與分工區塊

<table align="center">
  <tr>
    <td width="50%" valign="top">

### 🎨 前端工程師

**GitHub:** [@Atlas0319](https://github.com/Atlas0319)

#### UI/UX 設計與頁面實作
- 設計整體使用者介面風格與操作流程
- 使用 **React 19** 函式元件與 Hooks 實作所有頁面
- 以 **Tailwind CSS** 打造響應式（RWD）佈局，適配桌面與行動裝置
- 使用 **Lucide React** 圖示庫統一視覺語言

#### 狀態管理與資料流
- 以 **TanStack React Query 5** 管理所有伺服器狀態（快取、背景重取、錯誤處理）
- 以 **Zustand 5** 管理客戶端全域狀態（如目前登入使用者資訊）
- 設計統一的 **Axios** 請求封裝，包含 JWT Token 攔截器自動附加驗證標頭

#### 前端路由與元件化
- 使用 **React Router DOM 7** 實作巢狀路由與頁面佈局
- 元件化開發：`TopNavbar`、`GroupDetailModal` 等可重用 UI 元件
- 頁面涵蓋：登入註冊、群組管理、新增帳單、個人檔案

#### 前後端整合
- 根據 RESTful API 文件（Swagger UI）進行介面對接
- 處理 API 錯誤回應與 Loading/Empty/Error 狀態展示

    </td>
    <td width="50%" valign="top">

### ⚙️ 後端工程師

**GitHub:** [@FreeYoshino](https://github.com/FreeYoshino)

#### 資料庫架構設計
- 獨立設計完整的 6 表關聯式資料庫架構：`users`、`groups`、`group_members`、`expenses`、`expense_splits`、`settlements`
- 選用 PostgreSQL **UUID** 作為主鍵，搭配 `gen_random_uuid()` server default
- 所有金額欄位使用 **`DECIMAL(10, 2)`** 而非浮點數，杜絕財務計算浮點精度誤差
- 設計 `UniqueConstraint` 防止重複分攤與重複加入群組，確保資料完整性
- 精細設置 `ondelete` 外鍵約束策略（`CASCADE` / `RESTRICT` / `SET NULL`）
- 使用 **Alembic** 進行資料庫版本控管與自動遷移

#### RESTful API 開發
- 以 **FastAPI** 實作完整 RESTful API，遵循 **Router → Service → CRUD** 三層分離架構
- 設計清晰的 HTTP 狀態碼策略（201 / 400 / 401 / 403 / 404 / 500）
- 所有端點皆提供 `openapi_examples`，Swagger UI 可直接以範例資料測試
- 實作分頁查詢、使用者搜尋、多種分攤模式（均分 EQUAL / 指定金額 EXACT）
- 處理均分時的餘數公平分配邏輯（以 0.01 為單位依序分配）

#### JWT 身分驗證與資安防護
- 實作標準 **OAuth2PasswordBearer** 流程，簽發與驗證 JWT access token
- 使用 `python-jose` 進行 Token 簽發/驗證，支援過期偵測與非法 Token 攔截
- 透過 FastAPI `Depends` 實作依賴注入權限控制，Router 層零侵入性
- 所有機敏資訊透過 `.env` 環境變數注入，符合 12-Factor App 安全原則

#### 🧠 核心債務簡化演算法
- 獨立設計與實作「**貪婪債務最小化演算法**」
- 將多人債務網路建模為**有向圖邊壓縮問題**，採用雙指針貪婪策略
- 將原 N(N−1) 次轉帳壓縮至最多 N−1 次
- 處理浮點捨入邊界條件，確保演算法穩定收斂
- 整合至 `GET /groups/{id}/balances` API，前端無需額外計算

    </td>
  </tr>
</table>

---

## 📂 專案連結

| 類型 | 連結 |
|------|------|
| **GitHub Repository** | [https://github.com/FreeYoshino/web_final_project](https://github.com/FreeYoshino/web_final_project) |
| **線上 Demo** | 部署後提供 |

---

## 📄 授權條款

本專案為學術用途，僅供學習與展示使用。如欲引用或基於本專案進行二次開發，請標註原作者與團隊成員。

---
