# API Spec - Enterprise Agentic-RAG Knowledge Base

## 1. API 概述

### 1.1 基础信息
- **Base URL**: `http://localhost:8000/api`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **认证方式**: JWT Bearer Token

### 1.2 通用响应格式

**成功响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应**：
```json
{
  "code": 400,
  "message": "Error description",
  "detail": "Detailed error message"
}
```

### 1.3 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 2. 认证 API

### 2.1 用户注册

**POST** `/api/auth/register`

**请求体**：
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**：
```json
{
  "code": 201,
  "message": "User registered successfully",
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "created_at": "datetime"
  }
}
```

### 2.2 用户登录

**POST** `/api/auth/login`

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

---

## 3. 文档 API

### 3.1 上传文档

**POST** `/api/documents/upload`

**Content-Type**: `multipart/form-data`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 文档文件 |

**响应**：
```json
{
  "code": 201,
  "message": "Document uploaded successfully",
  "data": {
    "id": "uuid",
    "filename": "string",
    "file_size": 1024,
    "status": "pending",
    "created_at": "datetime"
  }
}
```

### 3.2 处理文档

**POST** `/api/documents/{document_id}/process`

**路径参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| document_id | UUID | 文档 ID |

**响应**：
```json
{
  "code": 200,
  "message": "Document processing started",
  "data": {
    "id": "uuid",
    "status": "processing"
  }
}
```

### 3.3 获取文档列表

**GET** `/api/documents/`

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20 |
| status | string | 否 | 状态过滤 |
| keyword | string | 否 | 关键词搜索 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "uuid",
        "filename": "string",
        "file_size": 1024,
        "status": "completed",
        "chunk_count": 50,
        "created_at": "datetime"
      }
    ]
  }
}
```

### 3.4 获取文档详情

**GET** `/api/documents/{document_id}`

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "uuid",
    "filename": "string",
    "file_path": "string",
    "file_size": 1024,
    "status": "completed",
    "chunk_count": 50,
    "created_at": "datetime",
    "processed_at": "datetime"
  }
}
```

### 3.5 删除文档

**DELETE** `/api/documents/{document_id}`

**响应**：
```json
{
  "code": 200,
  "message": "Document deleted successfully"
}
```

---

## 4. 聊天 API

### 4.1 发送消息

**POST** `/api/chat`

**请求体**：
```json
{
  "query": "string",
  "conversation_id": "uuid (optional)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": "uuid",
    "conversation_id": "uuid",
    "answer": "string",
    "citations": [
      {
        "document_id": "uuid",
        "document_name": "string",
        "page": 12,
        "chunk_id": "string",
        "content": "string",
        "score": 0.95
      }
    ],
    "created_at": "datetime"
  }
}
```

### 4.2 流式聊天 (SSE)

**POST** `/api/chat/stream`

**请求体**：同 4.1

**响应** (SSE Events)：

```
event: agent_start
data: {"agent": "planner", "timestamp": "..."}

event: agent_complete
data: {"agent": "planner", "output": {...}, "duration_ms": 150}

event: agent_start
data: {"agent": "query", "timestamp": "..."}

event: agent_complete
data: {"agent": "query", "output": {...}, "duration_ms": 200}

event: agent_start
data: {"agent": "retriever", "timestamp": "..."}

event: retrieval_result
data: {"documents": [...], "scores": [...]}

event: agent_complete
data: {"agent": "retriever", "duration_ms": 500}

event: agent_start
data: {"agent": "rerank", "timestamp": "..."}

event: agent_complete
data: {"agent": "rerank", "duration_ms": 100}

event: reflection
data: {"is_sufficient": true, "reason": "..."}

event: answer_delta
data: {"content": "根据"}

event: answer_delta
data: {"content": "《员工手册》"}

event: answer_complete
data: {"message_id": "...", "citations": [...]}
```

---

## 5. 会话 API

### 5.1 获取会话列表

**GET** `/api/conversations/`

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "items": [
      {
        "id": "uuid",
        "title": "string",
        "message_count": 10,
        "last_message_at": "datetime",
        "created_at": "datetime"
      }
    ]
  }
}
```

### 5.2 获取会话详情

**GET** `/api/conversations/{conversation_id}`

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "uuid",
    "title": "string",
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "string",
        "created_at": "datetime"
      },
      {
        "id": "uuid",
        "role": "assistant",
        "content": "string",
        "citations": [...],
        "created_at": "datetime"
      }
    ],
    "created_at": "datetime"
  }
}
```

### 5.3 删除会话

**DELETE** `/api/conversations/{conversation_id}`

**响应**：
```json
{
  "code": 200,
  "message": "Conversation deleted successfully"
}
```

---

## 6. 检索调试 API

### 6.1 获取检索调试信息

**GET** `/api/retrieval/debug/{message_id}`

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": "uuid",
    "query": "string",
    "agents": [
      {
        "name": "planner",
        "input": {...},
        "output": {...},
        "duration_ms": 150
      },
      {
        "name": "query",
        "input": {...},
        "output": {
          "rewritten_query": "string",
          "expanded_queries": ["string"]
        },
        "duration_ms": 200
      },
      {
        "name": "retriever",
        "input": {...},
        "output": {
          "documents": [...],
          "scores": [...]
        },
        "duration_ms": 500
      },
      {
        "name": "rerank",
        "input": {...},
        "output": {
          "reranked_documents": [...]
        },
        "duration_ms": 100
      },
      {
        "name": "reflection",
        "input": {...},
        "output": {
          "is_sufficient": true,
          "reason": "string"
        },
        "duration_ms": 50
      }
    ],
    "total_duration_ms": 1000
  }
}
```

---

## 7. 健康检查 API

### 7.1 系统健康检查

**GET** `/api/health`

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "datetime",
    "services": {
      "database": "connected",
      "milvus": "connected",
      "redis": "connected"
    }
  }
}
```

---

## 8. Schema 定义

### 8.1 请求 Schema

```python
# Chat Request
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None

# Document Upload
class DocumentUpload(BaseModel):
    file: UploadFile

# Login Request
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

# Register Request
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
```

### 8.2 响应 Schema

```python
# Citation
class Citation(BaseModel):
    document_id: UUID
    document_name: str
    page: Optional[int]
    chunk_id: str
    content: str
    score: float

# Chat Response
class ChatResponse(BaseModel):
    message_id: UUID
    conversation_id: UUID
    answer: str
    citations: List[Citation]
    created_at: datetime

# Document Response
class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_size: int
    status: str
    chunk_count: Optional[int]
    created_at: datetime

# Conversation Response
class ConversationResponse(BaseModel):
    id: UUID
    title: str
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime

# Paginated Response
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]

# API Response
class APIResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any]
```

---

## 9. 错误码

| 错误码 | 说明 |
|--------|------|
| 40001 | 请求参数验证失败 |
| 40101 | 未提供认证 Token |
| 40102 | Token 已过期 |
| 40103 | Token 无效 |
| 40301 | 无权访问该资源 |
| 40401 | 资源不存在 |
| 41301 | 文件过大 |
| 41501 | 不支持的文件格式 |
| 50001 | 内部服务器错误 |
| 50002 | 数据库连接失败 |
| 50003 | 向量数据库连接失败 |
| 50004 | Redis 连接失败 |
| 50005 | LLM API 调用失败 |
