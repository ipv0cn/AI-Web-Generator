"""
AI Web Generator — URL 即 Prompt
访问任意路径 -> 构建原始 HTTP 请求文本 -> AI 生成对应内容返回
"""

from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from openai import APIConnectionError, APIError, APITimeoutError

from src.client_ import client
from src.config import DEFAULT_TEMPERATURE, LLM_MODEL, LLM_TIMEOUT
from src.prompts import SYSTEM_PROMPT
from src.utils import build_raw_request, parse_content_type, strip_code_fences

app = FastAPI(title="AI Web Generator", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def root():
    p = Path(__file__).parent.joinpath("index.html")
    return HTMLResponse(p.read_text("utf-8"))


@app.get("/favicon.ico", status_code=404)
async def favicon():
    return ""


@app.get("/{path:path}")
async def handle_get(request: Request):
    return await generate_page(request)


@app.post("/{path:path}")
async def handle_post(request: Request):
    return await generate_page(request, include_body=True)


async def generate_page(
    request: Request, include_body: bool = False
) -> Response:
    prompt = await build_raw_request(request, include_body)

    try:
        resp = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=DEFAULT_TEMPERATURE,
            timeout=LLM_TIMEOUT,
        )
    except (APIError, APIConnectionError, APITimeoutError) as exc:
        return Response(
            content=f"AI service error: {type(exc).__name__}",
            status_code=502,
            media_type="text/plain",
        )

    raw = resp.choices[0].message.content
    clean = strip_code_fences(raw)
    media_type, body = parse_content_type(clean)
    return Response(content=body, media_type=media_type)


if __name__ == "__main__":
    import uvicorn

    from src.config import SERVER_PORT

    uvicorn.run("app:app", host="0.0.0.0", port=SERVER_PORT, reload=True)
