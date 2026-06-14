# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## 项目概览

AI Web Generator — URL 即 Prompt。访问 `/{host}/{path}`，后端将 HTTP 请求原文作为提示词发送给 LLM（默认 DeepSeek），AI 生成对应内容返回。

## 非显而易见的架构约定

- **单一 System Prompt，格式自适应**：一个 prompt 同时处理 HTML 页面和 API 响应。AI 根据请求头中的 `Accept` 字段自动决定输出格式（HTML/JSON/XML/纯文本），并在输出中声明 `Content-Type`。后端通过 [`parse_content_type()`](src/utils.py:16) 解析 AI 声明的类型，不自行推断格式。

- **虚拟 URL 路由**：路径首段**必须包含 "."**（如 `/baidu.com/search`），否则返回 400。这是安全校验，防止普通路径被当作站点名。
- **LLM 输出声明 Content-Type**：AI 响应格式为 `Content-Type: <MIME>\n\n<body>`。[`strip_code_fences()`](src/utils.py:9) 先剥离 markdown 标记，[`parse_content_type()`](src/utils.py:16) 再解析 Content-Type。
- **Host 头重写**：构建 prompt 时，原始请求的 `host` 头被替换为虚拟 URL 中的 host（[`build_raw_request()`](src/utils.py:48)）。
- **链接格式约定**：System prompt 要求 AI 生成的链接使用 `/{host}/{path}` 格式（如 `/baidu.com/news`），所有链接相对此代理根路径。
- **默认模型为 DeepSeek**（非 OpenAI）：`LLM_BASE_URL` 默认 `https://api.deepseek.com`，`LLM_MODEL` 默认 `deepseek-chat`。
- **Favicon 返回 404**：[`/favicon.ico`](app.py:30) 显式返回 404 状态码（无图标文件）。
- **LLM 错误返回 502**：[`generate_page()`](app.py:46) 捕获 `APIError` / `APIConnectionError` / `APITimeoutError` 并返回空内容 + 502。
- **异步 LLM 客户端**：使用 `AsyncOpenAI`（见 [`src/client_.py`](src/client_.py)），避免阻塞事件循环。

## 模块结构

```
app.py       入口 → 路由 + generate_page()
src/
  config.py    配置 → 环境变量加载
  prompts.py   提示词 → SYSTEM_PROMPT, PROMPT_TEMPLATE
  client_.py   LLM 客户端 → AsyncOpenAI 实例
  utils.py     工具函数 → strip_code_fences, parse_content_type, resolve_virtual_url, build_raw_request
```

## 命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动（热重载）
python app.py
# 或
uvicorn app:app --reload --port 8000
```

- 无测试框架、无 linter、无类型检查配置。
- `.env` 必须包含 `LLM_API_KEY` 才能运行。
