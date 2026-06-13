# AI Web Generator

URL即Prompt — 访问任意路径，AI即时生成对应的网页。

## 用法

浏览器地址栏输入 `/{host}/{path}`，后端调用 AI 还原该页面的 HTML。

```text
http://localhost:8000/baidu.com       → 还原百度首页
http://localhost:8000/github.com/login → 还原 GitHub 登录页
http://localhost:8000/google.com/search → 还原 Google 搜索页
```

所有链接、表单、按钮都真实可用，跳转在同一站点内完成。

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
| `app.py` | FastAPI 后端，核心逻辑 |
| `index.html` | 引导页面 |
| `.env.example` | 环境变量模板 |
| `requirements.txt` | Python 依赖 |
