# Enterprise Agentic-RAG Knowledge Base

基于 LangGraph 的企业级 Agentic-RAG 智能知识库系统。

## 项目简介

本项目构建了一个企业级 Agentic-RAG 智能知识库系统，实现企业文档智能问答、多阶段检索、Query Planning、Reflection、自适应检索优化与多轮上下文对话。系统不是传统 RAG（retrieve → answer），而是基于多阶段 Agent Workflow 的 Agentic-RAG。

## 方向

**方向一：Agentic AI 原生开发**

## 技术栈

| 类别 | 技术 |
|------|------|
| AI IDE | Claude Code |
| Backend | Python 3.11, FastAPI, LangGraph, LangChain |
| Vector DB | Milvus |
| Cache | Redis |
| Embedding | BGE Large Zh (bge-large-zh-v1.5) |
| Reranker | BGE Reranker (bge-reranker-large) |
| Frontend | Vue3, TailwindCSS, Pinia |
| LLM | mimo-v2.5-pro（小米 MiMo，OpenAI 兼容 API） |
| 容器化 | Docker, Docker Compose |

## 系统架构

```
User Query
    ↓
Planner Agent → 分析问题，拆解检索任务
    ↓
Query Agent → Query Rewrite / Expansion / Optimization
    ↓
Retriever Agent → Hybrid Retrieval (Vector + BM25)
    ↓
Rerank Agent → BGE Reranker 重排序
    ↓
Reflection Agent → 判断检索质量
    ├─ pass → Answer Agent → 生成答案 + 引用来源
    └─ fail → 重试检索 (max 2次)
```

## Agent 设计

1. **Planner Agent** - 分析复杂问题，拆解检索任务，生成 Retrieval Plan
2. **Query Agent** - Query Rewrite, Expansion, Optimization
3. **Retriever Agent** - Hybrid Retrieval (Vector + BM25 + Keyword)
4. **Rerank Agent** - BGE Reranker 重排序，提升相关性
5. **Reflection Agent** - 判断检索质量，检查信息完整性，触发重试
6. **Answer Agent** - 生成答案并附带引用来源

## 目录结构

> 采用前后端分离架构，`backend/` 和 `frontend/` 对应课程模板中的 `src/` 源代码目录。

```
cs599-project/
├── docs/                         # 项目文档
│   ├── CS599_大作业报告.pdf        # 最终提交的报告
│   ├── specs/                    # SDD 规格文档
│   │   ├── product-spec.md       # Product Spec
│   │   ├── architecture-spec.md  # Architecture Spec
│   │   └── api-spec.md           # API Spec
│   └── architecture.md           # 架构说明
├── backend/                      # 后端服务（对应模板 src/）
│   └── src/
│       ├── agents/               # 6 个 Agent 实现
│       ├── retrieval/            # 检索管线 (Vector, BM25, Hybrid, Reranker)
│       ├── workflows/            # LangGraph 工作流
│       ├── memory/               # 对话记忆 (Redis)
│       ├── models/               # SQLAlchemy 模型
│       ├── repositories/         # 数据访问层
│       ├── services/             # 业务逻辑层
│       ├── api/                  # FastAPI 路由
│       ├── core/                 # 配置、日志、依赖注入
│       ├── schemas/              # Pydantic Schema
│       ├── utils/                # 工具函数
│       └── tests/                # 单元测试
├── frontend/                     # 前端应用（对应模板 src/）
│   └── src/
│       ├── components/           # Vue 组件
│       ├── views/                # 页面视图
│       ├── stores/               # Pinia 状态管理
│       └── services/             # API 调用
├── eval/                         # 评估框架
│   ├── evaluate.py               # 评估脚本
│   └── test_set.jsonl            # 测试用例集
├── nginx/                        # Nginx 配置
├── scripts/                      # 启动脚本
├── docker-compose.yml            # 开发环境
├── docker-compose.prod.yml       # 生产环境
├── .env.example                  # 环境变量模板
├── .gitignore
├── LICENSE                       # MIT 开源协议
└── README.md
```

## 环境搭建

### 1. 依赖安装

```bash
# 后端
cd backend
pip install -e .

# 前端
cd frontend
npm install
```

### 2. 环境变量配置

```bash
# 复制环境配置
cp .env.example .env
# 编辑 .env 填入你的 API Key
# ⚠️ 不要硬编码 API Key
```

### 3. 启动基础设施

```bash
docker compose up -d
```

### 4. 启动后端

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 5. 启动前端

```bash
cd frontend
npm run dev
```

### 6. 访问

- 前端: http://localhost:5173
- API 文档: http://localhost:8000/docs

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

## 核心功能

- [x] 企业文档上传 (PDF, DOCX, TXT, Markdown)
- [x] 文档切分与 Embedding 生成
- [x] Vector Retrieval (Milvus)
- [x] BM25 Retrieval
- [x] Hybrid Retrieval
- [x] Query Rewrite
- [x] Query Expansion
- [x] Rerank (BGE Reranker)
- [x] Reflection (检索质量判断)
- [x] Retry Retrieval (自动重试)
- [x] Citation Generation (引用来源)
- [x] 多轮上下文问答
- [x] Conversation Memory (Redis)
- [x] SSE 流式输出
- [x] Retrieval Debug 可视化
- [x] Docker 容器化部署

## 项目状态

- [x] Proposal - 设计文档、架构图、Spec 初稿
- [x] MVP - 核心闭环 Demo
- [x] Final - 最终版本

## References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Milvus Documentation](https://milvus.io/docs)
- [BGE Embedding](https://huggingface.co/BAAI/bge-large-zh-v1.5)
- [Agentic RAG Paper](https://arxiv.org/abs/2401.15884)
