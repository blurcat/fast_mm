from pydantic import BaseModel
from typing import Optional


ALLOWED_MODELS = {"deepseek-chat", "deepseek-reasoner"}


class LogAnalysisRequest(BaseModel):
    log_text: str
    model: str = "deepseek-chat"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    def model_post_init(self, __context):
        if self.model not in ALLOWED_MODELS:
            self.model = "deepseek-chat"


class LogAnalysisResponse(BaseModel):
    summary: str
    errors: list[dict] = []
    anomalies: list[str] = []
    performance_issues: list[str] = []
    suggestions: list[dict] = []
    report: str = ""
    tokens_used: Optional[int] = None
    log_stats: dict = {}
