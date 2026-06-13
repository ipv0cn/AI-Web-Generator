# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## 项目概览

AI Web Generator — URL 即 Prompt。访问 `/{host}/{path}`，后端将 HTTP 请求原文作为提示词发送给 LLM（默认 DeepSeek），AI 生成对应 HTML 页面返回。

## 非显而易见的架构约定

- **虚拟 URL 路由**：路径首段**必须包含 "."**（如 `/baidu.com/search`），否则返回 400。这是安全校验，防止普通路径被当作站点名。
- **LLM 输出清洗**：AI 返回的 HTML 可能包裹在 markdown 代码块中，[`extract_html()`](app.py:51) 自动剥离 ` ```html ` / ` ``` ` 标记。
- **Host 头重写**：构建 prompt 时，原始请求的 `host` 头被替换为虚拟 URL 中的 host（`build_raw_request` 第 84-86 行）。
- **链接格式约定**：System prompt 要求 AI 生成的链接使用 `/{host}/{path}` 格式（如 `/baidu.com/news`），所有链接相对此代理根路径。
- **默认模型为 DeepSeek**（非 OpenAI）：`LLM_API_BASE_URL` 默认 `https://api.deepseek.com`，`LLM_MODEL_NAME` 默认 `deepseek-chat`。
- **Favicon 返回 404**：[`/favicon.ico`](app.py:111) 显式返回 404 状态码（无图标文件）。
- **LLM 错误返回 502**：[`generate_page()`](app.py:126) 捕获 `APIError` / `APIConnectionError` / `APITimeoutError` 并返回空内容 + 502。

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
