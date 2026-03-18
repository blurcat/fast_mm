import json
import re
from openai import AsyncOpenAI
from core.config import settings

client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
)

SYSTEM_PROMPT = """你是一名专业的日志分析专家。请分析提供的日志内容，并返回结构化的 JSON 响应。

分析重点：
1. 错误检测与根因分析
2. 异常行为与非预期行为检测
3. 性能瓶颈识别
4. 具体可操作的修复建议

请仅返回符合以下结构的有效 JSON，所有字段内容必须使用中文：
{
  "summary": "2-3句话概述分析发现",
  "errors": [
    {
      "type": "错误类别（例如：空指针异常、连接超时）",
      "description": "错误描述及可能的根本原因",
      "severity": "high|medium|low",
      "count": 1,
      "context": "相关服务或组件上下文"
    }
  ],
  "anomalies": [
    "异常行为描述"
  ],
  "performance_issues": [
    "性能问题描述"
  ],
  "suggestions": [
    {
      "issue": "具体问题描述",
      "suggestion": "具体的修复操作建议",
      "priority": "high|medium|low"
    }
  ],
  "report": "## 分析报告\\n\\n包含各章节的详细 Markdown 分析报告"
}

请简洁而全面，优先提供可操作的具体建议，避免泛泛而谈。"""


def _extract_json(text: str) -> dict:
    """从文本中提取 JSON，兼容 reasoner 模型可能附带的 markdown 代码块。"""
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 提取 ```json ... ``` 或 ``` ... ``` 代码块
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # 提取裸 JSON 对象
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError("无法从响应中解析 JSON")


async def analyze_logs(preprocessed_text: str, stats: dict, model: str = "deepseek-chat") -> dict:
    stats_str = (
        f"总行数: {stats.get('total_lines', 0)} | "
        f"错误数: {stats.get('error_count', 0)} | "
        f"警告数: {stats.get('warning_count', 0)}"
    )

    user_message = f"日志统计: {stats_str}\n\n{preprocessed_text}"

    # deepseek-reasoner 不支持 response_format 和 temperature 参数
    is_reasoner = model == "deepseek-reasoner"
    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=4096 if is_reasoner else 2048,
    )
    if not is_reasoner:
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["temperature"] = 0.1

    response = await client.chat.completions.create(**kwargs)

    result = _extract_json(response.choices[0].message.content)
    result["tokens_used"] = response.usage.total_tokens
    return result
