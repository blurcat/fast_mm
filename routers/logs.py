from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from schemas.log import LogAnalysisRequest, ALLOWED_MODELS
from services.log_parser import preprocess_logs
from services.ai_analyzer import analyze_logs
from core.config import settings

router = APIRouter()


async def _run_analysis(log_text: str, model: str = "deepseek-chat") -> dict:
    parsed = preprocess_logs(log_text, settings.max_log_chars)
    result = await analyze_logs(parsed["filtered_text"], parsed["stats"], model)
    result["log_stats"] = parsed["stats"]
    return result


@router.post("/analyze")
async def analyze_text(request: LogAnalysisRequest):
    if not request.log_text.strip():
        raise HTTPException(status_code=400, detail="Log text cannot be empty")
    model = request.model if request.model in ALLOWED_MODELS else "deepseek-chat"
    return await _run_analysis(request.log_text, model)


@router.post("/upload")
async def analyze_file(
    file: UploadFile = File(...),
    model: str = Form("deepseek-chat"),
):
    if model not in ALLOWED_MODELS:
        model = "deepseek-chat"
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read file")
    if not text.strip():
        raise HTTPException(status_code=400, detail="File is empty")
    return await _run_analysis(text, model)
