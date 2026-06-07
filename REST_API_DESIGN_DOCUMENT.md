# Roommate Sync — REST API 設計文件

> **專案名稱**：群組分帳系統 (Group Expense Splitting System)   
> **API 版本**：0.1.0  
> **框架**：FastAPI (Python)  
> **認證機制**：JWT (OAuth2 Password Bearer)  
> **文件生成**：OpenAPI 3.1.0（由 FastAPI 自動生成，Swagger UI 可直接測試）

---

## 1. API 架構與設計準則

### 1.1 RESTful 設計風格

本 API 嚴格遵循 REST（Representational State Transfer）架構風格，核心設計原則如下：

| 原則 | 實踐方式 |
|------|----------|
| **資源導向** | 所有端點以名詞表達資源（`/users`、`/groups`、`/expenses`、`/settlements`），不以動詞暴露行為 |
| **階層式路由** | 一對多關係透過路徑階層表達，如 `/groups/{group_id}/expenses` 明確表示「隸屬於特定群組的費用」 |
| **HTTP 方法語義** | `GET` 查詢、`POST` 建立、未來規劃 `PUT/PATCH` 修改、`DELETE` 刪除 |
| **標準狀態碼** | 精確使用 `200`、`201`、`400`、`401`、`403`、`404`、`422`、`500`，不濫用 200 包裹錯誤 |
| **無狀態認證** | 採用 JWT Bearer Token，每次請求攜帶 `Authorization: Bearer <token>`，伺服器不維護 session |

### 1.2 認證與授權架構

```
Client                          Server
  │                               │
  │  POST /login                  │
  │  {email, password}            │
  │ ──────────────────────────>   │
  │                               │ 驗證密碼 → 簽發 JWT
  │  {access_token, token_type}   │
  │ <──────────────────────────   │
  │                               │
  │  GET /groups/{id}/balances    │
  │  Authorization: Bearer <jwt>  │
  │ ──────────────────────────>   │
  │                               │ 解碼 JWT → 提取 user_id
  │                               │ 檢查是否為群組成員 (403)
  │                               │ 查詢餘額 → 執行簡化演算法
  │  GroupBalanceResponse         │
  │ <──────────────────────────   │
```

- **Token 發放**：`POST /login` 使用 OAuth2 Password Grant 流程，回傳 JWT access token
- **Token 攜帶**：所有受保護端點需在 Header 中攜帶 `Authorization: Bearer <token>`
- **身分推斷**：後端從 JWT 的 `sub` 欄位自動解碼出 `user_id`，前端無需明傳使用者 ID
- **授權檢查**：每個端點在 service 層獨立驗證「目前使用者是否為群組成員」，非成員回傳 `403 Forbidden`

### 1.3 錯誤回應設計

| 狀態碼 | 語義 | 使用場景 |
|--------|------|----------|
| `200 OK` | 請求成功 | 所有 GET 查詢、登入成功 |
| `201 Created` | 資源建立成功 | 所有 POST 建立操作 |
| `400 Bad Request` | 請求參數錯誤 | 商業邏輯驗證失敗（重複名稱、非群組成員等） |
| `401 Unauthorized` | 未認證 | Token 遺失、無效或過期；密碼錯誤 |
| `403 Forbidden` | 已認證但無權限 | 使用者不屬於該群組 |
| `404 Not Found` | 資源不存在 | 群組、使用者、費用不存在 |
| `422 Unprocessable Entity` | 請求格式錯誤 | Pydantic schema 驗證失敗（由 FastAPI 自動處理） |
| `500 Internal Server Error` | 伺服器錯誤 | 未預期的內部異常 |

---

## 2. 核心 API 端點說明

### 2.1 使用者模組 (Users)

#### `POST /users` — 建立使用者（註冊）

- **認證**：不需要
- **Request Body**（JSON）：

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `username` | string (1–50) | ✅ | 使用者帳號名稱 |
| `email` | string (email) | ✅ | 電子郵件信箱 |
| `name` | string (1–100) | ✅ | 真實姓名 |
| `password` | string (8–128) | ✅ | 登入密碼 |
| `phone` | string (≤20) | ❌ | 電話號碼 |

- **Response `201`**：`UserResponse` — 包含 `id`、`username`、`email`、`name`、`phone`、`created_at`、`updated_at`
- **錯誤**：`400`（email 或 username 重複）、`422`（格式不符）

---

#### `POST /login` — 使用者登入

- **認證**：不需要
- **Request Body**（`application/x-www-form-urlencoded`）：

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `username` | string | ✅ | **請填 email**（OAuth2 規範） |
| `password` | string | ✅ | 登入密碼 |

- **Response `200`**：`Token` — 包含 `access_token`（JWT 字串）、`token_type`（固定為 `"bearer"`）
- **錯誤**：`401`（密碼錯誤）、`404`（使用者不存在）

---

#### `GET /users/me` — 查詢目前登入者資料

- **認證**：需要（從 JWT 推斷身分）
- **Response `200`**：`UserResponse`
- **錯誤**：`401`（未登入）、`404`（使用者已被刪除）

> **安全設計亮點**：使用者 ID 由後端從 JWT token 自動推斷，前端無需在 URL 中傳遞任何使用者識別碼，徹底避免了 IDOR（Insecure Direct Object Reference）攻擊面。

---

#### `GET /users?q=...` — 搜尋使用者

- **認證**：需要
- **Query Parameters**：

| 參數 | 型別 | 必填 | 預設 | 說明 |
|------|------|------|------|------|
| `q` | string (1–50) | ✅ | — | 搜尋關鍵字，比對 username 或 name（不區分大小寫） |
| `limit` | int (1–50) | ❌ | 20 | 回傳筆數上限 |
| `exclude_group_id` | UUID | ❌ | null | 排除已在此群組的成員（用於邀請場景） |

- **Response `200`**：`UserSearchResponse` — 包含 `users[]`（每項僅含 `id`、`username`、`name`）、`total`
- **錯誤**：`400`（關鍵字空白）、`401`（未登入）、`404`（指定的 exclude_group_id 不存在）

> **隱私保護設計**：搜尋結果僅回傳 `id`、`username`、`name` 三個欄位，**不暴露 `email` 和 `phone`**。同時自動排除搜尋者本人，並支援過濾已存在於特定群組中的成員。

---

### 2.2 群組模組 (Groups)

#### `GET /groups` — 查詢我的群組列表

- **認證**：需要
- **Response `200`**：`UserGroupListResponse`

```json
{
  "groups": [
    {
      "id": "uuid",
      "name": "室友群",
      "description": "一起住的室友",
      "role": "admin",
      "member_count": 4,
      "creator_id": "uuid",
      "created_at": "2026-04-01T10:00:00+08:00",
      "updated_at": "2026-04-01T10:00:00+08:00"
    }
  ],
  "total": 1
}
```

- **錯誤**：`401`（未登入）

---

#### `POST /groups` — 建立群組

- **認證**：需要（建立者自動成為 admin）
- **Request Body**：

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `name` | string (1–100) | ✅ | 群組名稱 |
| `description` | string (≤255) | ❌ | 群組描述 |
| `avatar_url` | string (≤500) | ❌ | 群組頭像 |

- **Response `201`**：`GroupResponse`
- **錯誤**：`400`（同建立者已有同名群組）

---

#### `GET /groups/{group_id}/members` — 取得群組成員清單

- **Response `200`**：`GroupMemberListResponse` — 含每位成員的 `id`、`username`、`name`、`role`、`joined_at`

#### `POST /groups/{group_id}/members` — 加入成員

- **Request Body**：`{ "user_ids": ["uuid1", "uuid2"] }` — 支援批次加入
- **Response `201`**：`GroupMemberListResponse`
- **錯誤**：`400`（user_ids 為空／重複／使用者不存在／已在群組中）、`403`（操作者非群組成員）、`404`（群組不存在）

---

#### `GET /groups/{group_id}/expenses` — 取得群組費用列表

- **Query**：`page`（預設 1）、`size`（預設 10）— 支援分頁
- **錯誤**：`403`（非群組成員）、`404`（群組不存在）

#### `GET /groups/{group_id}/settlements` — 取得群組結算列表

- **Query**：`page`（預設 1）、`size`（預設 10）— 支援分頁
- **Response `200`**：`SettlementListResponse` — 含分頁 meta（`total`、`page`、`size`、`pages`）與結算記錄陣列

#### `GET /groups/{group_id}/balances` — 取得群組帳務餘額（含債務簡化建議）

- **詳細說明見第三章**

---

### 2.3 支出模組 (Expenses)

#### `POST /expenses` — 建立一筆費用

- **認證**：需要（付款人由 JWT 自動推斷）
- **Request Body**：

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `description` | string (1–255) | ✅ | 費用描述（如「晚餐」） |
| `amount` | decimal (>0) | ✅ | 費用總金額 |
| `group_id` | UUID | ✅ | 所屬群組 |
| `expense_date` | datetime | ✅ | 費用發生日期（ISO 8601） |
| `splits` | array | ✅ | 分攤明細（至少一人） |
| `category` | string (≤50) | ❌ | 費用類別（如 `food`、`drinks`） |
| `split_type` | enum | ❌ | `EQUAL`（均分，預設）或 `EXACT`（指定金額） |

- **`splits[]` 結構**：

| 欄位 | 型別 | 說明 |
|------|------|------|
| `user_id` | UUID | 分攤者 ID |
| `split_amount` | decimal (≥0) | 分攤金額（EQUAL 模式可填 0，後端自動計算） |

- **Response `201`**：`{ "id": "uuid", "message": "Expense created successfully" }`
- **錯誤**：`400`（付款人不存在／非群組成員／分攤者含非成員／重複分攤／金額不符）、`404`（群組不存在）

> **雙分帳模式設計**：
> - `EQUAL` 模式：只需傳 `split_amount: 0`，後端自動均分 `amount / len(splits)`
> - `EXACT` 模式：各分攤者的 `split_amount` 總和必須等於 `amount`

---

### 2.4 結算模組 (Settlements)

#### `POST /settlements` — 建立一筆結算記錄

- **認證**：需要（付款人由 JWT 自動推斷）
- **Request Body**：

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| `receiver_id` | UUID | ✅ | 收款人 ID |
| `amount` | decimal (>0) | ✅ | 還款金額 |
| `group_id` | UUID | ✅ | 所屬群組 |
| `transaction_date` | datetime | ✅ | 交易日期（ISO 8601） |
| `method` | enum | ❌ | `cash`、`credit_card`、`bank_transfer` |
| `status` | enum | ❌ | `pending`（預設）、`completed`、`cancelled` |
| `expense_id` | UUID | ❌ | 關聯的特定費用（批次結清時為 null） |
| `notes` | string | ❌ | 交易備註 |

- **Response `201`**：`{ "id": "uuid", "message": "Settlement created successfully" }`
- **錯誤**：`400`（付款人=收款人／付款人或收款人不存在）、`403`（付款人或收款人非群組成員）、`404`（群組不存在）

> **兩種使用場景**：
> 1. **針對特定費用的立即還款**：帶入 `expense_id`，如「還昨天的午餐錢 $150」
> 2. **批次 / 週期性總結算**：`expense_id` 為 `null`，如「五月份淨額轉帳 $1,250」

---

## 3. 技術亮點：債務最小化演算法

### 3.1 API 端點

```
GET /groups/{group_id}/balances
```

### 3.2 Response 結構

```json
{
  "group_id": "550e8400-e29b-41d4-a716-446655440000",
  "balances": [
    {
      "user_id": "...",
      "user_name": "Alice",
      "total_paid_raw": "300.00",
      "total_owed_raw": "100.00",
      "settlements_paid": "50.00",
      "settlements_received": "0.00",
      "balance": "150.00"
    }
  ],
  "settlements": [
    {
      "from_user_id": "...",
      "from_user_name": "Bob",
      "to_user_id": "...",
      "to_user_name": "Alice",
      "amount": "50.00"
    }
  ]
}
```

Response 包含兩個核心陣列：
- **`balances[]`**：每位成員的完整收支明細，包含原始墊付金額、原始分攤金額、已完成的結算金額，以及最終淨額（正數 = 應收款，負數 = 應付款）
- **`settlements[]`**：由演算法運算出的最簡還款建議清單，直接告訴每個人「該付多少錢給誰」

### 3.3 演算法設計

此端點的 `settlements` 欄位並非單純從資料庫撈取，而是後端即時執行 **貪婪債務簡化演算法 (Greedy Debt Simplification Algorithm)** 的計算結果。

#### 問題定義

假設一個 4 人群組（Alice、Bob、Carol、Dave）經過多筆費用分攤後，各自的淨額如下：

| 成員 | Net Balance |
|------|-------------|
| Alice | +150（應收 $150） |
| Bob | −80（應付 $80） |
| Carol | −60（應付 $60） |
| Dave | −10（應付 $10） |

**樸素解法**：Bob → Alice $80、Carol → Alice $60、Dave → Alice $10，共 **3 筆交易**。

#### 演算法目標

從一群淨額資料中，找出**交易筆數最少**的還款方案。

#### 演算法步驟（Greedy + Two-Pointer）

```
輸入：每位成員的 net_balance（正 = 應收，負 = 應付）

Step 1 ─ 角色分離
  debtors  ← [Bob: -80, Carol: -60, Dave: -10]   (balance < 0)
  creditors ← [Alice: +150]                       (balance > 0)
  排除 balance = 0 的成員（已無債務）

Step 2 ─ 排序（絕對值遞減，優先處理大額）
  debtors  ← [Bob: -80, Carol: -60, Dave: -10]    (升冪，因負數)
  creditors ← [Alice: +150]                        (降冪)

Step 3 ─ 雙指針迭代
  i = 0 (指向 Bob, debt=80)
  j = 0 (指向 Alice, credit=150)

  Iteration 1:
    amount = min(80, 150) = 80
    生成建議: Bob → Alice $80
    Bob: -80 + 80 = 0   → i += 1 (Bob 已清償)
    Alice: 150 - 80 = 70

  Iteration 2:
    i = 1 (指向 Carol, debt=60)
    j = 0 (指向 Alice, credit=70)
    amount = min(60, 70) = 60
    生成建議: Carol → Alice $60
    Carol: -60 + 60 = 0  → i += 1
    Alice: 70 - 60 = 10

  Iteration 3:
    i = 2 (指向 Dave, debt=10)
    j = 0 (指向 Alice, credit=10)
    amount = min(10, 10) = 10
    生成建議: Dave → Alice $10
    Dave: -10 + 10 = 0   → i += 1
    Alice: 10 - 10 = 0   → j += 1

  i >= len(debtors), 結束

輸出：
  Bob   → Alice  $80
  Carol → Alice  $60
  Dave  → Alice  $10
```

#### 演算法特性分析

| 特性 | 說明 |
|------|------|
| **時間複雜度** | O(n log n)，瓶頸在排序；雙指針迭代為 O(n) |
| **空間複雜度** | O(n)，僅需兩個輔助陣列 |
| **最優性** | 對於「所有債權人淨額總和 = 所有債務人淨額總和（絕對值）」的約束下，此貪婪策略保證產出**交易筆數下界**（至少 max(|debtors|, |creditors|) 筆） |
| **數值穩定性** | 使用 Python `Decimal` 型別進行所有金額運算，消除浮點數精度誤差；餘額趨近零時以 `0.01` 閾值判定清償 |

### 3.4 實戰價值

這個端點展現了「**API 不只是 CRUD 包裝層**」的設計理念：

1. **分層架構的優勢**：`router → service → simplification` 的三層分離，使演算法邏輯獨立於 HTTP 層與資料庫層，可單獨測試、獨立演進
2. **即時計算 vs. 預存結果**：settlements 建議是即時運算而非預先寫入資料庫，確保任何新費用或新結算發生後，下一次查詢立即反映最新狀態
3. **前端零運算負擔**：所有計算在後端完成，前端只需直接渲染 `settlements[]` 陣列，降低了前端的開發複雜度與測試成本

---

## 附錄：完整 API 端點速查表

| HTTP | 路徑 | 說明 | 認證 | 成功碼 |
|------|------|------|------|--------|
| `POST` | `/users` | 註冊新使用者 | ❌ | 201 |
| `POST` | `/login` | 登入取得 JWT | ❌ | 200 |
| `GET` | `/users/me` | 查詢目前登入者 | ✅ | 200 |
| `GET` | `/users?q=` | 搜尋使用者 | ✅ | 200 |
| `GET` | `/groups` | 我的群組列表 | ✅ | 200 |
| `POST` | `/groups` | 建立群組 | ✅ | 201 |
| `GET` | `/groups/{id}/members` | 群組成員清單 | ✅ | 200 |
| `POST` | `/groups/{id}/members` | 加入成員 | ✅ | 201 |
| `GET` | `/groups/{id}/expenses` | 群組費用列表 | ✅ | 200 |
| `GET` | `/groups/{id}/settlements` | 群組結算列表 | ✅ | 200 |
| `GET` | `/groups/{id}/balances` | 群組餘額 + 債務簡化建議 | ✅ | 200 |
| `POST` | `/expenses` | 建立費用 | ✅ | 201 |
| `POST` | `/settlements` | 建立結算記錄 | ✅ | 201 |

---

