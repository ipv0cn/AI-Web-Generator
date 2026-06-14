# AI API 响应支持方案

## 核心理念
HTML 和 API 响应本质上都是字符串，无需区分。唯一需要做的：**告诉 AI 按请求要求输出对应格式，后端自动推断 Content-Type 返回**。

## 现状
- System prompt 强制输出 HTML
- 输出清洗只支持 ` ```html ` 标记
- 固定返回 `HTMLResponse`

## 设计方案

### 调用流程（简化前后对比）

```
改造前：
请求 → 选HTML_PROMPT → LLM → extract_html() → HTMLResponse

改造后：
请求 → 统一PROMPT → LLM → extract_body() → Response(media_type=auto)
```

### 核心改动

#### 1. 统一 System Prompt

修改现有 prompt，加入格式自适应指令：

```
你是网站的忠实还原者。根据收到的HTTP请求，输出该资源真实应有的响应内容。

要求：
- 匹配请求头中的格式（浏览器→HTML，API→JSON/XML/其他）
- 如果输出网页：CSS用内联<style>，JS可用内联<script>或CDN
- 所有链接使用 /{host}/{path} 格式
- 响应式设计
- 只输出内容本身，不含任何解释或标记
- 用尽可能少的代码最大程度还原
```

#### 2. 通用清洗函数 `extract_body()`

```python
def extract_body(text: str) -> str:
    """剥离任意 markdown 代码块标记，格式无关。"""
    text = text.strip()
    text = re.sub(r"^```\w*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
```

#### 3. Content-Type 自动推断

```python
def detect_content_type(accept: str, body: str) -> str:
    """根据内容形状推断 Content-Type，不硬编码任何格式。"""
    s = body.strip()
    if s.startswith(("{", "[")):
        return "application/json"
    if s.startswith("<"):
        return "application/xml" if "xml" in accept else "text/xml"
    for t in re.split(r"[,;]", accept):
        t = t.strip().split(";")[0].strip()
        if t and t != "*/*" and t != "text/html":
            return t
    return "text/html"  # 默认 HTML
```

#### 4. `generate_page()` 统一返回 `Response`

```python
async def generate_page(request, include_body=False):
    prompt = await build_raw_request(request, include_body)
    resp = await client.chat.completions.create(...)
    raw = resp.choices[0].message.content
    body = extract_body(raw)
    content_type = detect_content_type(
        request.headers.get("accept", ""), body
    )
    return Response(content=body, media_type=content_type)
```

### 需要修改的文件

| 文件 | 改动 |
|------|------|
| `app.py` | 修改 System Prompt；新增 `extract_body()`、`detect_content_type()`；改造 `generate_page()`；路由改为返回 `Response` |
| `AGENTS.md` | 更新架构说明 |
| `README.md` | 添加 API 用法示例 |

### 不改动的文件
`index.html`、`.env.example`、`requirements.txt`

### 使用示例

```bash
# HTML 模式（不变）
curl http://localhost:8000/baidu.com

# API 模式（自动匹配格式）
curl -H "Accept: application/json" http://localhost:8000/api.example.com/users
curl -H "Accept: application/xml"  http://localhost:8000/api.example.com/data
curl -H "Accept: text/plain"       http://localhost:8000/example.com/config
```

### 实现顺序
1. 修改 System Prompt（格式自适应）
2. 新增 `extract_body()` 通用清洗函数
3. 新增 `detect_content_type()` 推断函数
4. 改造 `generate_page()` 返回 `Response`
5. 更新 `README.md` 和 `AGENTS.md`
