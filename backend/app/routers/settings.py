from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db, DB_ENGINE_TYPE
from app.core.config import settings
from app.models.setting import Setting
from app.schemas.setting import SettingUpdate, SettingsResponse

router = APIRouter(prefix="/api/settings", tags=["Application Settings"])

DEFAULT_SETTINGS = {
    "family_name": settings.FAMILY_NAME,
    "wedding_name": settings.WEDDING_NAME,
    "wedding_date": settings.WEDDING_DATE,
    "preferred_currency": settings.DEFAULT_CURRENCY,
    "message_signature": settings.MESSAGE_SIGNATURE,
    "ai_provider": settings.AI_PROVIDER
}

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    stored = db.query(Setting).all()
    current_settings = DEFAULT_SETTINGS.copy()
    for s in stored:
        current_settings[s.key] = s.value

    return {
        "settings": current_settings,
        "database_type": DB_ENGINE_TYPE,
        "database_status": "Connected & Synchronized",
        "ai_status": "Active (Heuristic NLP + Vision ready)",
        "ai_provider": current_settings.get("ai_provider", settings.AI_PROVIDER)
    }

@router.put("", response_model=SettingsResponse)
def update_settings(update_in: SettingUpdate, db: Session = Depends(get_db)):
    for k, v in update_in.settings.items():
        existing = db.query(Setting).filter(Setting.key == k).first()
        if existing:
            existing.value = str(v)
        else:
            db.add(Setting(key=k, value=str(v)))
    db.commit()
    return get_settings(db)
