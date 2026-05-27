# Enterprise Agentic-RAG Knowledge Base

基于 LangGraph 的企业级 Agentic-RAG 智能知识库系统。

## 系统架构

```
User Query → Planner Agent → Query Agent → Retriever → Rerank → Reflection
                                                                     ├─ pass → Answer → END
                                                                     └─ fail → Query Agent (retry)
```

## 技术栈

- **Backend**: Python 3.11, FastAPI, LangGraph, LangChain
- **Vector DB**: Milvus
- **Cache**: Redis
- **Embedding**: BGE Large Zh (bge-large-zh-v1.5)
- **Reranker**: BGE Reranker (bge-reranker-large)
- **Frontend**: Vue3, TailwindCSS, Pinia
- **LLM**: OpenAI-compatible API (支持 Qwen/MiMo 等)

## Agent 设计

1. **Planner Agent** - 分析复杂问题，拆解检索任务
2. **Query Agent** - Query Rewrite, Expansion, Optimization
3. **Retriever Agent** - Hybrid Retrieval (Vector + BM25)
4. **Rerank Agent** - BGE Reranker 重排序
5. **Reflection Agent** - 判断检索质量，触发重试
6. **Answer Agent** - 生成答案并附带引用来源

## 快速开始

### 1. 环境准备

```bash
# 复制环境配置
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 2. 启动基础设施

```bash
docker compose up -d
```

### 3. 启动后端

```bash
cd backend
pip install -e .
uvicorn src.main:app --reload --port 8000
```

### 4. 访问 API 文档

打开浏览器访问 http://localhost:8000/docs

## API 接口

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/documents/upload` | 上传文档 |
| POST | `/api/documents/{id}/process` | 解析文档 |
| GET | `/api/documents/` | 文档列表 |
| DELETE | `/api/documents/{id}` | 删除文档 |
| POST | `/api/chat` | 聊天问答 |
| POST | `/api/chat/stream` | SSE 流式问答 |
| GET | `/api/conversations/` | 会话列表 |
| GET | `/api/conversations/{id}` | 会话详情 |
| GET | `/api/retrieval/debug/{message_id}` | 检索调试 |

## 项目结构

```
enterprise-rag/
├── backend/
│   └── src/
│       ├── agents/        # 6 个 Agent 实现
│       ├── retrieval/     # 检索管线
│       ├── workflows/     # LangGraph 工作流
│       ├── memory/        # 对话记忆
│       ├── models/        # SQLAlchemy 模型
│       ├── repositories/  # 数据访问层
│       ├── services/      # 业务逻辑层
│       ├── api/           # FastAPI 路由
│       └── core/          # 配置、日志、依赖
├── frontend/              # Vue3 前端
├── docker-compose.yml     # 开发环境
└── docker-compose.prod.yml
```
