# AGENTS.md (Code Mode)

This file provides guidance to agents when working with code in this repository.

## 编码规则（非显而易见的约定）

- **AI 输出必须清洗**：调用 [`extract_html()`](../../app.py:51) 处理 LLM 返回内容，它自动移除 ` ```html ` / ` ``` ` 等 markdown 围栏标记。
- **System prompt 即契约**：修改 [`SYSTEM_PROMPT`](../../app.py:29) 会影响所有生成的页面行为。特别注意其中的链接格式约定（`/{host}/{path}`）不能被破坏。
- **Host 头重写规则**：在 [`build_raw_request()`](../../app.py:84-86) 中，原始请求的 `host` 头会被虚拟 URL 的 host 替换。如果引入新的 header 处理逻辑，必须保持此重写逻辑。
- **无测试框架 / 无 linter**：本项目无 pytest、ruff 等配置。代码修改需人工验证。
- **Python 3.11+**：使用了 `|` 类型联合语法（如 `except (APIError, ...)`），确保兼容。
