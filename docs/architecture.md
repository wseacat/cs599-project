# 系统架构说明

## 1. 系统概述

本系统是一个基于 LangGraph 的企业级 Agentic-RAG 智能知识库，采用前后端分离架构。

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue3)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  Login   │  │  Chat   │  │Document │  │Retrieval│       │
│  │   Page   │  │  Page   │  │Upload   │  │ Debug   │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    API Layer                         │   │
│  │  /api/documents  /api/chat  /api/conversations      │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Service Layer                        │   │
│  │  DocumentService  ChatService  RetrievalService      │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LangGraph Workflow                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│  │  │Planner  │→ │ Query   │→ │Retriever│             │   │
│  │  │ Agent   │  │ Agent   │  │ Agent   │             │   │
│  │  └─────────┘  └─────────┘  └─────────┘             │   │
│  │       │                         │                   │   │
│  │       ▼                         ▼                   │   │
│  │  ┌─────────┐            ┌─────────┐                 │   │
│  │  │Rerank   │            │Reflection│                │   │
│  │  │ Agent   │←───────────│ Agent   │                │   │
│  │  └─────────┘            └─────────┘                 │   │
│  │       │                     │                       │   │
│  │       ▼                     ▼                       │   │
│  │  ┌─────────┐         ┌─────────┐                   │   │
│  │  │ Answer  │←────────│ Retry   │                   │   │
│  │  │ Agent   │         │ Logic   │                   │   │
│  │  └─────────┘         └─────────┘                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Repository Layer                        │   │
│  │  DocumentRepo  ConversationRepo  RetrievalRepo      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  MySQL   │     │  Milvus  │     │  Redis   │
    │ (关系)   │     │ (向量)   │     │ (缓存)   │
    └──────────┘     └──────────┘     └──────────┘
```

## 3. 核心模块

### 3.1 Agent 层

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| Planner | 分析问题，拆解任务 | User Query | Retrieval Plan |
| Query | Query Rewrite/Expansion | Original Query | Rewritten/Expanded Queries |
| Retriever | 混合检索 | Queries | Retrieved Documents |
| Rerank | 重排序 | Documents | Reranked Documents |
| Reflection | 质量判断 | Documents | Pass/Fail Decision |
| Answer | 生成答案 | Documents + Query | Answer + Citations |

### 3.2 Retrieval 层

- **Vector Store**: Milvus 存储文档向量，支持 Top-K 相似度检索
- **BM25**: 基于关键词的全文检索
- **Hybrid**: 融合 Vector 和 BM25 结果
- **Reranker**: BGE Reranker 对结果重排序

### 3.3 Memory 层

- **Conversation Memory**: Redis 存储对话历史
- **Session Storage**: Redis 存储会话状态
- **Retrieval Cache**: Redis 缓存检索结果

## 4. 数据流

### 4.1 文档处理流程

```
文档上传 → 文档解析 → 文本切分 → Embedding 生成 → 存入 Milvus
                                                    ↓
                                              BM25 索引更新
```

### 4.2 问答流程

```
用户提问 → Planner 拆解 → Query 优化 → 混合检索 → Rerank
    ↓                                              ↓
    ←─────────── 生成答案 ←─── Reflection 判断 ←───┘
```

## 5. 技术选型理由

| 组件 | 选型 | 理由 |
|------|------|------|
| Agent 框架 | LangGraph | 原生支持状态机、条件分支、循环 |
| 向量数据库 | Milvus | 高性能、分布式、生产级 |
| 缓存 | Redis | 高性能、支持多种数据结构 |
| Embedding | BGE Large Zh | 中文效果最佳 |
| Reranker | BGE Reranker | 与 Embedding 配套 |
| 后端框架 | FastAPI | 异步、自动文档、类型安全 |
| 前端框架 | Vue3 | 响应式、组合式 API |

## 6. 部署架构

```
┌─────────────────────────────────────────┐
│           Docker Compose                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Frontend │  │ Backend │  │  Nginx  │ │
│  │ (Vue3)  │  │(FastAPI)│  │ (Proxy) │ │
│  └─────────┘  └─────────┘  └─────────┘ │
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  MySQL   │  │  Milvus │  │  Redis  │ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘
```
