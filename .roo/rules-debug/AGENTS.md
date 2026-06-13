# AGENTS.md (Debug Mode)

This file provides guidance to agents when working with code in this repository.

## 调试规则（非显而易见的发现）

- **LLM 错误静默降级为 502**：[`generate_page()`](../../app.py:141-142) 捕获 `APIError` / `APIConnectionError` / `APITimeoutError` 后返回空内容 + 502，**无任何日志输出**。调试时需手动添加日志。
- **`/favicon.ico` 返回 404 是预期行为**：第 111 行显式返回 404，不是 bug。
- **路径缺少 "." 返回 400**：[`resolve_virtual_url()`](../../app.py:66-68) 校验路径首段必须包含 "."。访问 `/about` 会 400，访问 `/about.com` 才会正常路由。这常被误认为路由配置问题。
- **无日志配置**：项目未配置 `logging`，调试时建议临时添加 `print()` 或 `logging`。
- **超时时间为 120s**：LLM 调用设置 `timeout=120`（第 139 行），响应慢时需等待。
