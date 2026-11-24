from app.schemas.auth import Token, TokenData, UserLogin, UserCreate, UserOut
from app.schemas.event import EventCreate, EventUpdate, EventOut
from app.schemas.guest import GuestCreate, GuestUpdate, GuestOut, GuestListResponse
from app.schemas.contributor import ContributorCreate, ContributorOut
from app.schemas.gift import GiftCreate, GiftUpdate, GiftOut, GiftListResponse
from app.schemas.thank_you import (
    ThankYouGenerateRequest,
    ThankYouCreate,
    ThankYouUpdate,
    ThankYouOut,
    ThankYouListResponse
)
from app.schemas.history import HistoryCreate, HistoryUpdate, HistoryOut, ReciprocityComparisonOut
from app.schemas.ai import ProcessNoteRequest, ProcessNoteResponse, ExtractedGiftItem, AssistantQueryRequest, AssistantQueryResponse
from app.schemas.report import DashboardStats, ReportSummary, CategoryStat, MonthlyStat, RecentActivityItem
from app.schemas.setting import SettingUpdate, SettingsResponse
