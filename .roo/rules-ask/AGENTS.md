# AGENTS.md (Ask Mode)

This file provides guidance to agents when working with code in this repository.

## 文档上下文（非显而易见的结构）

- **实际规格在代码中**：`README.md` 只描述基本用法，而 [`SYSTEM_PROMPT`](../../app.py:29-40) 和 [`PROMPT_TEMPLATE`](../../app.py:42-46) 才是真正的行为规格文档，定义了 LLM 的输出格式约束。
- **虚拟 URL 机制**：路径 `/{host}/{path}` 中的 host 会被提取并重写到请求头中。这不是标准代理，而是一种"URL 即 Prompt"的设计模式。
- **链接格式是核心契约**：AI 生成的 HTML 中所有链接必须遵循 `/{host}/{path}` 格式，这是前后端协作的基础约定，定义在 [`SYSTEM_PROMPT`](../../app.py:34-35)。
- **默认使用 DeepSeek**：尽管使用 OpenAI SDK，但默认指向 `https://api.deepseek.com`，模型为 `deepseek-chat`。
