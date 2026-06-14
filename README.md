# AI Web Generator

URL 即 Prompt — 访问任意路径，AI 即时生成对应的内容。

## 用法

### 网页浏览

浏览器地址栏输入 `/{host}/{path}`，AI 还原该页面的 HTML。

```text
http://localhost:8000/baidu.com           → 还原百度首页
http://localhost:8000/github.com/login    → 还原 GitHub 登录页
```

### API 调用

设置 `Accept` 请求头指定格式，AI 返回对应格式的响应体。

```bash
# JSON
curl -H "Accept: application/json" http://localhost:8000/api.example.com/users

# XML
curl -H "Accept: application/xml" http://localhost:8000/api.example.com/data

# 纯文本 / 配置文件
curl -H "Accept: text/plain" http://localhost:8000/example.com/config

# POST 请求体也会传递给 AI
curl -X POST -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}' \
  http://localhost:8000/api.example.com/users
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY 等信息

# 3. 启动服务
uvicorn app:app --reload --port 8000

# 4. 打开浏览器访问
open http://localhost:8000
```

## 配置

| 变量 | 说明 | 默认值 |
| ------ | ------ | -------- |
| `LLM_API_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `LLM_API_KEY` | API 密钥 | — |
| `LLM_MODEL_NAME` | 模型名 | `deepseek-chat` |
| `SERVER_PORT` | 服务端口 | `8000` |
| `DEFAULT_TEMPERATURE` | 生成温度 | `0.7` |

## 项目文件

| 文件 | 说明 |
| ------ | ------ |
| `app.py` | 入口，FastAPI 应用与路由 |
| `src/config.py` | 环境变量配置 |
| `src/prompts.py` | System Prompt 与 Prompt 模板 |
| `src/client_.py` | AsyncOpenAI 客户端实例 |
| `src/utils.py` | 工具函数（URL解析、内容清洗、Content-Type推断） |
| `index.html` | 引导页面 |
| `.env.example` | 环境变量模板 |
| `requirements.txt` | Python 依赖 |
