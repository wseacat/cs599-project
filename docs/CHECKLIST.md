# CS599 项目提交检查清单

## 一、仓库结构检查

### 1.1 必需文件
- [x] `README.md` - 项目入口文档
- [x] `.gitignore` - 排除规则
- [x] `LICENSE` - 开源协议
- [x] `src/` - 源代码目录
- [x] `docs/` - 文档目录

### 1.2 README.md 内容
- [x] 项目名称
- [x] 项目简介
- [x] 方向说明
- [x] 技术栈
- [x] 目录结构
- [x] 环境搭建步骤
- [x] 项目状态 checklist

---

## 二、文档检查

### 2.1 Specs 规格文档
- [x] `docs/specs/product-spec.md` - Product Spec
- [x] `docs/specs/architecture-spec.md` - Architecture Spec
- [x] `docs/specs/api-spec.md` - API Spec

### 2.2 架构文档
- [x] `docs/architecture.md` - 系统架构说明

### 2.3 报告模板
- [x] `docs/CS599_大作业报告模板.md` - 包含所有章节

---

## 三、代码检查

### 3.1 后端代码
- [x] `backend/src/agents/` - 6 个 Agent 实现
- [x] `backend/src/workflows/` - LangGraph 工作流
- [x] `backend/src/retrieval/` - 检索管线
- [x] `backend/src/api/` - API 路由
- [x] `backend/src/models/` - 数据模型
- [x] `backend/src/services/` - 业务逻辑
- [x] `backend/src/repositories/` - 数据访问
- [x] `backend/src/tests/` - 单元测试

### 3.2 前端代码
- [x] `frontend/src/views/` - 页面视图
- [x] `frontend/src/components/` - Vue 组件
- [x] `frontend/src/stores/` - Pinia 状态
- [x] `frontend/src/services/` - API 调用

---

## 四、配置检查

### 4.1 环境配置
- [x] `.env.example` - 环境变量模板
- [x] `docker-compose.yml` - 开发环境
- [x] `docker-compose.prod.yml` - 生产环境

### 4.2 构建配置
- [x] `backend/pyproject.toml` - Python 依赖
- [x] `frontend/package.json` - Node.js 依赖
- [x] `backend/Dockerfile` - 后端容器
- [x] `nginx/nginx.conf` - Nginx 配置

---

## 五、功能检查

### 5.1 核心功能
- [x] 文档上传 (PDF, DOCX, TXT, Markdown)
- [x] 文档处理 (解析、切分、Embedding)
- [x] 混合检索 (Vector + BM25)
- [x] Query Rewrite / Expansion
- [x] Rerank (BGE Reranker)
- [x] Reflection (质量判断)
- [x] 多轮对话
- [x] SSE 流式输出
- [x] 引用来源展示
- [x] 检索调试

### 5.2 Agent 实现
- [x] Planner Agent
- [x] Query Agent
- [x] Retriever Agent
- [x] Rerank Agent
- [x] Reflection Agent
- [x] Answer Agent

---

## 六、安全检查

### 6.1 API Key 安全
- [x] 使用环境变量
- [x] `.env` 已在 `.gitignore` 中
- [x] `.env.example` 不包含真实 Key

### 6.2 认证鉴权
- [x] JWT Token 认证
- [x] 用户登录/注册

---

## 七、部署检查

### 7.1 Docker 支持
- [x] `docker-compose.yml` - 开发环境
- [x] `docker-compose.prod.yml` - 生产环境
- [x] `backend/Dockerfile` - 后端镜像

### 7.2 启动脚本
- [x] `scripts/setup.sh` - Linux/Mac
- [x] `scripts/setup.bat` - Windows
- [x] `scripts/test.sh` - 测试脚本

---

## 八、Git 检查

### 8.1 提交规范
- [ ] 提交信息清晰
- [ ] 代码已暂存
- [ ] 无敏感信息泄露

### 8.2 Tag 标记
- [ ] `v0.1` - MVP 版本

---

## 九、最终提交

### 9.1 提交命令
```bash
cd enterprise-rag
git add .
git commit -m "feat: complete CS599 project with Agentic-RAG system"
git tag v0.1
git push origin main
git push origin v0.1
```

### 9.2 提交内容
- 完整的后端代码
- 完整的前端代码
- 项目文档
- Specs 规格文档
- Docker 配置
- 启动脚本

---

## 十、注意事项

1. **API Key**：确保 `.env` 中的 Key 已配置
2. **数据库**：首次运行需执行迁移
3. **模型下载**：首次运行会自动下载 BGE 模型
4. **端口占用**：确保所需端口未被占用
