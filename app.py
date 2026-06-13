"""
AI Web Generator — URL即Prompt
访问任意路径 -> 构建原始HTTP请求文本 -> AI生成对应HTML页面返回
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI

load_dotenv()

# 配置
BASE_URL = os.getenv("LLM_API_BASE_URL", "https://api.deepseek.com")
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = os.getenv("LLM_MODEL_NAME", "deepseek-chat")
PORT = int(os.getenv("SERVER_PORT", "8000"))
TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# ── Prompt 模板 ──

SYSTEM_PROMPT = """
你是网站的忠实还原者。根据收到的HTTP请求，输出该页面真实应有的HTML内容。

要求：
- 所有链接、表单、按钮真实可用，放心使用站内跳转（本站会处理）
- 链接/表单路径格式：/{host}/{path}，如 baidu.com 上的链接写为 /baidu.com/news
- CSS用内联<style>，JS可用内联<script>或CDN
- 响应式设计
- 只输出HTML代码，不含任何解释或标记
- 用尽可能少的代码最大程度还原页面，过度冗长的代码会被截断导致页面缺失内容
"""


PROMPT_TEMPLATE = """
以下是收到的原始HTTP请求：

{method} {path} HTTP/1.1
{headers}
{body}

---
请根据以上请求生成完整HTML页面。
"""


# ── 工具函数 ──

def extract_html(text: str) -> str:
    text = text.strip()
    for p in [r"^```html\s*", r"^```\s*", r"\s*```$"]:
        text = re.sub(p, "", text)
    return text.strip()


def resolve_virtual_url(request: Request) -> str:
    """解析并验证路径格式：/{host}/{subpath}，返回完整虚拟URL。

    路径首段必须包含"."（如 baidu.com），否则抛出400异常。
    /baidu.com/search -> http://baidu.com/search
    """
    raw = request.url.path.lstrip("/")
    first = raw.split("/", 1)[0]
    if not first or "." not in first:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid path format")

    parsed = urlparse("http://" + raw)
    return urlunparse(("http", parsed.netloc, parsed.path or "/", "",
                       request.url.query, ""))


async def build_raw_request(
    request: Request, include_body: bool = False
) -> str:
    method = request.method
    target = resolve_virtual_url(request)

    host = urlparse(target).netloc
    header_lines = []
    for k, v in request.headers.items():
        if k.lower() == "host":
            header_lines.append(f"host: {host}")
        else:
            header_lines.append(f"{k}: {v}")
    headers = "\n".join(header_lines)

    body = ""
    if include_body:
        b = await request.body()
        if b:
            body = "\n" + b.decode("utf-8", errors="replace")

    return PROMPT_TEMPLATE.format(
        method=method, path=target, headers=headers, body=body
    )

# ── FastAPI 应用 ──

app = FastAPI(title="AI Web Generator", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def root():
    p = Path(__file__).parent.joinpath("index.html")
    return HTMLResponse(p.read_text("utf-8"))


@app.get("/favicon.ico", status_code=404)
async def favicon():
    return ""


@app.get("/{path:path}", response_class=HTMLResponse)
async def handle_get(request: Request):
    return await generate_page(request)


@app.post("/{path:path}", response_class=HTMLResponse)
async def handle_post(request: Request):
    return await generate_page(request, include_body=True)


async def generate_page(
    request: Request, include_body: bool = False
) -> HTMLResponse:
    prompt = await build_raw_request(request, include_body)

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE,
            timeout=120,
        )
    except (APIError, APIConnectionError, APITimeoutError):
        return HTMLResponse(content="", status_code=502)

    html = resp.choices[0].message.content
    if not html:
        raise ValueError("AI returned empty content")

    return HTMLResponse(content=extract_html(html))


# ── 入口 ──

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
