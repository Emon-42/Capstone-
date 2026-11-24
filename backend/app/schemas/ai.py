from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ProcessNoteRequest(BaseModel):
    note_text: str
    image_base64: Optional[str] = None

class ExtractedGiftItem(BaseModel):
    original_text: str
    possible_guest_names: List[str] = []
    relationship_guess: Optional[str] = None
    family_group: Optional[str] = None
    gift_name: str
    gift_description: Optional[str] = None
    gift_category: str = "Other"
    quantity: int = 1
    is_cash: bool = False
    cash_amount: Optional[Decimal] = None
    is_joint_gift: bool = False
    confidence_score: float = 1.0  # 0.0 to 1.0
    missing_fields: List[str] = []
    uncertain_fields: List[str] = []
    review_reasons: List[str] = []
    suggested_action: str = "review"  # "confirm", "review", "flag_unknown"

class ProcessNoteResponse(BaseModel):
    success: bool
    original_note: str
    extracted_data: ExtractedGiftItem
    source: str = "ai_parser"  # "gemini_llm" or "heuristic_nlp"
    disclaimer: str = "Review all extracted details before saving. Accuracy is prioritized over guessing."

class AssistantQueryRequest(BaseModel):
    query: str
    context_type: Optional[str] = "general"

class AssistantQueryResponse(BaseModel):
    answer: str
    insights: List[str] = []
    related_records: List[Dict[str, Any]] = []
    suggested_actions: List[str] = []
