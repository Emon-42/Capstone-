from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ai_service import AIService
from app.services.report_service import ReportService
from app.schemas.ai import (
    ProcessNoteRequest,
    ProcessNoteResponse,
    AssistantQueryRequest,
    AssistantQueryResponse
)

router = APIRouter(prefix="/api/ai", tags=["AI Engine"])

@router.post("/process-note", response_model=ProcessNoteResponse)
def process_note(req: ProcessNoteRequest):
    if not req.note_text.strip():
        raise HTTPException(status_code=400, detail="Note text cannot be empty")
    return AIService.process_handwritten_note(req.note_text, req.image_base64)

@router.post("/assistant", response_model=AssistantQueryResponse)
def query_ai_assistant(req: AssistantQueryRequest, db: Session = Depends(get_db)):
    # Provide actual DB context metrics to prevent hallucination
    stats = ReportService.get_dashboard_stats(db)
    context = {
        "total_guests": stats.total_guests,
        "total_gift_records": stats.total_gift_records,
        "total_contributors": stats.total_contributors,
        "thank_you_sent": stats.thank_you_sent,
        "thank_you_pending": stats.thank_you_pending,
        "unidentified_gifts": stats.unidentified_gifts,
        "gifts_requiring_review": stats.gifts_requiring_review,
        "total_cash_gifts": stats.total_cash_gifts,
        "total_recorded_cash_value": float(stats.total_recorded_cash_value)
    }
    res = AIService.answer_assistant_query(req.query, context)
    return res
