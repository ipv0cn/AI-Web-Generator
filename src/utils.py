import re
from urllib.parse import urlparse, urlunparse

from fastapi import HTTPException, Request

from .prompts import PROMPT_TEMPLATE


def strip_code_fences(text: str) -> str:
    """剥离外层 markdown 代码块标记（```xxx ... ```）。"""
    text = text.strip()
    text = re.sub(r"^```\w*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_content_type(text: str) -> tuple[str, str]:
    """
    从 AI 输出首行提取 Content-Type，返回 (media_type, body)。
    """
    if not text.startswith("Content-Type:"):
        return "text/html", text

    idx = text.index("\n")
    header_line = text[:idx].strip()
    rest = text[idx + 1:].strip()
    m = re.match(r"Content-Type:\s*(\S+)", header_line)
    media_type = m.group(1) if m else "text/html"
    return media_type, rest


def resolve_virtual_url(request: Request) -> str:
    """解析并验证路径格式：/{host}/{subpath}，返回完整虚拟URL。
    /baidu.com/search -> http://baidu.com/search
    """
    raw = request.url.path.lstrip("/")
    first = raw.split("/", 1)[0]
    if not first:
        raise HTTPException(status_code=400, detail="Invalid path format")

    parsed = urlparse("http://" + raw)
    return urlunparse(("http", parsed.netloc, parsed.path or "/", "",
                       request.url.query, ""))


def build_headers_string(request: Request, virtual_host: str) -> str:
    """构建请求头字符串，重写 host 为虚拟 URL 中的 host。"""
    lines = []
    for k, v in request.headers.items():
        lines.append(f"host: {virtual_host}" if k.lower() == "host"
                     else f"{k}: {v}")
    return "\n".join(lines)


async def build_raw_request(
    request: Request, include_body: bool = False
) -> str:
    method = request.method
    target = resolve_virtual_url(request)
    host = urlparse(target).netloc
    headers = build_headers_string(request, host)

    body = ""
    if include_body:
        if (b := await request.body()):
            body = "\n" + b.decode("utf-8", errors="replace")

    return PROMPT_TEMPLATE.format(
        method=method, path=target, headers=headers, body=body
    )
