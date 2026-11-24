from typing import Dict, Any, Optional
from pydantic import BaseModel

class SettingUpdate(BaseModel):
    settings: Dict[str, str]

class SettingsResponse(BaseModel):
    settings: Dict[str, str]
    database_type: str
    database_status: str
    ai_status: str
    ai_provider: str
