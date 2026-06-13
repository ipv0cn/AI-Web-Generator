# AGENTS.md (Architect Mode)

This file provides guidance to agents when working with code in this repository.

## 架构约束（非显而易见的发现）

- **虚拟 URL 路由是核心架构决策**：路径首段包含 "." 的校验（[`resolve_virtual_url()`](../../app.py:58-72)）是安全机制，防止内部路径与虚拟站点名冲突。所有请求处理都依赖此机制。
- **Prompt 即后端逻辑**：没有传统的路由-控制器-视图分层。业务逻辑编码在 system prompt 中，LLM 充当动态渲染引擎。修改 [`SYSTEM_PROMPT`](../../app.py:29) 等同于修改"视图层"。
- **Host 头重写是关键耦合点**：[`build_raw_request()`](../../app.py:75-98) 中重写 host header 是保证 AI 生成正确链接的必要条件。任何协议变更（如支持 HTTPS）都需要在此层处理。
- **平台耦合**：模型通过 OpenAI SDK 调用，但默认使用 DeepSeek API。切换平台只需改环境变量，但错误处理（超时、速率限制）行为可能因平台而异。
- **无状态设计**：应用完全无状态——每次请求独立生成页面。无缓存、无会话、无数据库。
