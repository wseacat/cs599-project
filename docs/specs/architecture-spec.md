# Architecture Spec - Enterprise Agentic-RAG Knowledge Base

## 1. 架构概述

### 1.1 架构风格
- 前后端分离架构
- 分层架构（API → Service → Repository）
- Agent 驱动的工作流架构

### 1.2 设计原则
1. **关注点分离**：每层职责明确
2. **依赖倒置**：高层不依赖低层实现
3. **开闭原则**：对扩展开放，对修改关闭
4. **单一职责**：每个模块只做一件事

## 2. 系统分层

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│              (Vue3 Frontend + Nginx)                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     API Layer                           │
│           (FastAPI Routes + Pydantic)                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                         │
│        (Business Logic + Agent Orchestration)           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Agent Layer                            │
│     (LangGraph Workflow + Individual Agents)            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                Repository Layer                         │
│           (Data Access + Cache)                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                    │
│      (MySQL + Milvus + Redis + External APIs)      │
└─────────────────────────────────────────────────────────┘
```

## 3. 核心组件设计

### 3.1 Agent 组件

#### 3.1.1 Planner Agent

**职责**：分析用户问题，判断复杂度，决定是否需要拆解

**输入**：
```python
class PlannerInput:
    query: str
    chat_history: List[Message]
```

**输出**：
```python
class PlannerOutput:
    is_complex: bool
    sub_queries: List[str]
    retrieval_plan: str
```

**状态转换**：
```
INIT → PLANNING → QUERY_OPTIMIZATION
```

#### 3.1.2 Query Agent

**职责**：Query Rewrite 和 Query Expansion

**功能**：
1. **Query Rewrite**：改写用户问题，使其更适合检索
2. **Query Expansion**：扩展相关问题，提高召回率

**输入**：
```python
class QueryInput:
    original_query: str
    retrieval_plan: str
```

**输出**：
```python
class QueryOutput:
    rewritten_query: str
    expanded_queries: List[str]
```

#### 3.1.3 Retriever Agent

**职责**：执行混合检索

**检索策略**：
1. **Vector Search**：Milvus 相似度检索
2. **BM25 Retrieval**：关键词全文检索
3. **Hybrid Retrieval**：融合两种结果

**输入**：
```python
class RetrieverInput:
    queries: List[str]
    top_k: int = 10
```

**输出**：
```python
class RetrieverOutput:
    documents: List[Document]
    scores: List[float]
```

#### 3.1.4 Rerank Agent

**职责**：对检索结果重排序

**实现**：BGE Reranker

**输入**：
```python
class RerankInput:
    query: str
    documents: List[Document]
```

**输出**：
```python
class RerankOutput:
    reranked_documents: List[Document]
    scores: List[float]
```

#### 3.1.5 Reflection Agent

**职责**：判断检索质量，决定是否需要重试

**判断条件**：
1. 文档相关性是否过低
2. 信息是否不足
3. 是否无法回答问题
4. 是否存在冲突信息

**输入**：
```python
class ReflectionInput:
    query: str
    documents: List[Document]
    retry_count: int
```

**输出**：
```python
class ReflectionOutput:
    is_sufficient: bool
    reason: str
    should_retry: bool
```

#### 3.1.6 Answer Agent

**职责**：生成最终答案并附带引用

**输入**：
```python
class AnswerInput:
    query: str
    documents: List[Document]
    chat_history: List[Message]
```

**输出**：
```python
class AnswerOutput:
    answer: str
    citations: List[Citation]
```

### 3.2 LangGraph State 设计

```python
class RAGState(TypedDict):
    # 输入
    original_query: str
    conversation_id: str
    
    # Planner 输出
    is_complex: bool
    sub_queries: List[str]
    retrieval_plan: str
    
    # Query Agent 输出
    rewritten_query: str
    expanded_queries: List[str]
    
    # Retriever 输出
    retrieved_documents: List[Document]
    
    # Rerank 输出
    reranked_documents: List[Document]
    
    # Reflection 输出
    reflection_result: ReflectionResult
    retry_count: int
    
    # Answer 输出
    final_answer: str
    citations: List[Citation]
    
    # 对话上下文
    chat_history: List[Message]
```

### 3.3 Workflow 图定义

```python
workflow = StateGraph(RAGState)

# 添加节点
workflow.add_node("planner", planner_agent)
workflow.add_node("query", query_agent)
workflow.add_node("retriever", retriever_agent)
workflow.add_node("rerank", rerank_agent)
workflow.add_node("reflection", reflection_agent)
workflow.add_node("answer", answer_agent)

# 定义边
workflow.add_edge("planner", "query")
workflow.add_edge("query", "retriever")
workflow.add_edge("retriever", "rerank")
workflow.add_edge("rerank", "reflection")

# 条件边
workflow.add_conditional_edges(
    "reflection",
    should_retry,
    {
        "retry": "query",
        "pass": "answer"
    }
)

workflow.add_edge("answer", END)
```

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────┐       ┌─────────────────┐
│    users    │       │   documents     │
├─────────────┤       ├─────────────────┤
│ id (PK)     │←──┐   │ id (PK)         │
│ username    │   │   │ user_id (FK)    │←──┐
│ email       │   │   │ filename        │   │
│ password    │   │   │ file_path       │   │
│ created_at  │   │   │ file_size       │   │
└─────────────┘   │   │ status          │   │
                  │   │ created_at      │   │
                  │   └─────────────────┘   │
                  │                         │
                  │   ┌─────────────────┐   │
                  │   │document_chunks  │   │
                  │   ├─────────────────┤   │
                  │   │ id (PK)         │   │
                  │   │ document_id (FK)│───┘
                  │   │ content         │
                  │   │ embedding_id    │
                  │   │ chunk_index     │
                  │   └─────────────────┘
                  │
                  │   ┌─────────────────┐
                  │   │  conversations  │
                  │   ├─────────────────┤
                  │   │ id (PK)         │
                  │   │ user_id (FK)    │←──┐
                  │   │ title           │   │
                  │   │ created_at      │   │
                  │   └─────────────────┘   │
                  │                         │
                  │   ┌─────────────────┐   │
                  │   │    messages     │   │
                  │   ├─────────────────┤   │
                  │   │ id (PK)         │   │
                  │   │ conversation_id │───┘
                  │   │ role            │
                  │   │ content         │
                  │   │ citations       │
                  │   │ created_at      │
                  │   └─────────────────┘
                  │
                  │   ┌─────────────────┐
                  └───│ retrieval_logs  │
                      ├─────────────────┤
                      │ id (PK)         │
                      │ message_id (FK) │
                      │ query           │
                      │ agent_name      │
                      │ input_data      │
                      │ output_data     │
                      │ duration_ms     │
                      │ created_at      │
                      └─────────────────┘
```

### 4.2 SQLAlchemy Model

```python
# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Document Model
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

# DocumentChunk Model
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    document_id = Column(UUID, ForeignKey("documents.id"))
    content = Column(Text, nullable=False)
    embedding_id = Column(String(100))
    chunk_index = Column(Integer)

# Conversation Model
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

# Message Model
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    conversation_id = Column(UUID, ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# RetrievalLog Model
class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    message_id = Column(UUID, ForeignKey("messages.id"))
    query = Column(Text)
    agent_name = Column(String(50))
    input_data = Column(JSON)
    output_data = Column(JSON)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 5. 缓存设计

### 5.1 Redis 数据结构

```python
# 对话历史
conversation:{conversation_id}:messages = List[Message]

# 会话元数据
conversation:{conversation_id}:meta = {
    "user_id": "...",
    "title": "...",
    "created_at": "..."
}

# 检索缓存
retrieval_cache:{query_hash} = {
    "documents": [...],
    "timestamp": ...,
    "ttl": 3600
}

# 用户会话
user:{user_id}:sessions = Set[conversation_id]
```

### 5.2 缓存策略

| 数据类型 | 缓存策略 | TTL |
|----------|----------|-----|
| 对话历史 | Write-Through | 24h |
| 检索结果 | Cache-Aside | 1h |
| 会话元数据 | Write-Through | 7d |

## 6. 向量存储设计

### 6.1 Milvus Collection

```python
# Document Embeddings Collection
collection_name = "document_embeddings"

fields = [
    FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=100),
    FieldSchema("document_id", DataType.VARCHAR, max_length=100),
    FieldSchema("chunk_index", DataType.INT64),
    FieldSchema("content", DataType.VARCHAR, max_length=10000),
    FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=1024),
]

# 索引
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}
```

## 7. 安全设计

### 7.1 认证鉴权

- JWT Token 访问控制
- Token 有效期：24小时
- Refresh Token 机制

### 7.2 数据安全

- API Key 环境变量管理
- 敏感数据加密存储
- SQL 注入防护

### 7.3 访问控制

- 基于用户的文档访问权限
- Rate Limiting 防止滥用

## 8. 可观测性设计

### 8.1 日志系统

```python
# 结构化日志
logger.info("Agent executed", extra={
    "agent": "planner",
    "duration_ms": 150,
    "input_tokens": 100,
    "output_tokens": 50
})
```

### 8.2 追踪

- LangSmith 集成（可选）
- 每个 Agent 的执行追踪
- 性能指标收集

### 8.3 监控指标

- 请求量 / 响应时间
- Agent 执行时间
- 检索成功率
- 缓存命中率
