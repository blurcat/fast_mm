# AI 日志分析工具

基于 **DeepSeek V3** 的智能日志分析工具，帮助开发者快速定位错误、识别异常、发现性能瓶颈并获取解决建议。

## 功能特性

- **多种输入方式** — 直接粘贴日志文本，或上传日志文件（支持拖拽）
- **智能错误检测** — 自动识别 ERROR / CRITICAL / FATAL 等级别错误并定位根因
- **异常行为分析** — 检测日志中的异常模式和非预期行为
- **性能问题排查** — 识别超时、慢查询、资源瓶颈等性能问题
- **解决建议** — 针对每个问题给出具体可操作的修复建议
- **详细分析报告** — 生成结构化 Markdown 报告
- **Token 成本控制** — 发送前自动过滤去重，减少不必要的 API 费用

支持常见日志格式：Nginx、Java（Log4j / Logback）、Python、Docker、系统日志等。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12 · FastAPI |
| AI   | DeepSeek V3 (`deepseek-chat`) |
| 前端 | 原生 HTML / CSS / JavaScript |

---

## 快速开始

### 前置条件

- Python 3.12+
- [DeepSeek API Key](https://platform.deepseek.com/)

### 本地运行

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd fast_mm

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 4. 启动服务
uvicorn main:app --reload
```

打开浏览器访问 [http://localhost:8000](http://localhost:8000)

---

## Docker 部署

### 方式一：docker compose（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 2. 构建并启动
docker compose up -d

# 查看运行日志
docker compose logs -f

# 停止服务
docker compose down
```

### 方式二：docker 直接运行

```bash
# 构建镜像
docker build -t ai-log-analyzer .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e DEEPSEEK_API_KEY=your_api_key_here \
  --name ai-log-analyzer \
  ai-log-analyzer
```

服务启动后访问 [http://localhost:8000](http://localhost:8000)

---

## 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | 是 | — | DeepSeek 平台 API Key |
| `DEEPSEEK_MODEL` | 否 | `deepseek-chat` | 使用的模型名称 |
| `MAX_LOG_CHARS` | 否 | `8000` | 发送给 AI 的最大字符数，调小可降低成本 |

`.env` 文件示例：

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
MAX_LOG_CHARS=8000
```

---

## API 接口

### `POST /api/analyze` — 分析文本日志

**请求体**

```json
{
  "log_text": "2024-01-01 10:00:00 ERROR ..."
}
```

### `POST /api/upload` — 上传日志文件

`multipart/form-data`，字段名为 `file`，支持 `.log` `.txt` `.out` `.err` 格式。

### 响应格式（两个接口相同）

```json
{
  "summary": "分析摘要",
  "errors": [
    {
      "type": "错误类型",
      "description": "错误描述及根因",
      "severity": "high | medium | low",
      "count": 3,
      "context": "相关上下文"
    }
  ],
  "anomalies": ["异常行为描述"],
  "performance_issues": ["性能问题描述"],
  "suggestions": [
    {
      "issue": "问题描述",
      "suggestion": "具体解决方案",
      "priority": "high | medium | low"
    }
  ],
  "report": "## 详细报告\n\n...",
  "tokens_used": 512,
  "log_stats": {
    "total_lines": 1000,
    "error_count": 5,
    "warning_count": 12,
    "info_count": 983
  }
}
```

---

## Token 成本控制

日志在发送给 AI 之前会经过以下处理，以减少不必要的费用：

1. **级别过滤** — 优先提取 ERROR / WARN 行及其上下文，跳过大量 INFO / DEBUG 行
2. **去重合并** — 相同错误多次出现时只发送一条，附带出现次数
3. **大小限制** — 超出 `MAX_LOG_CHARS` 的内容自动截断
4. **采样回退** — 若未检测到显式错误级别，自动取日志头尾作为样本

---

## 项目结构

```
fast_mm/
├── main.py                  # FastAPI 入口
├── core/
│   └── config.py            # 配置管理（读取 .env）
├── routers/
│   └── logs.py              # API 路由
├── services/
│   ├── log_parser.py        # 日志预处理与成本控制
│   └── ai_analyzer.py       # DeepSeek API 调用
├── schemas/
│   └── log.py               # 请求/响应数据模型
├── static/                  # 前端静态文件
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## License

MIT License
