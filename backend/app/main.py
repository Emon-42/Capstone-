import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.core.config import settings
from app.core.database import engine, DB_ENGINE_TYPE, Base, SessionLocal
import app.models
from app.models.user import User
from app.models.event import WeddingEvent
from app.core.security import hash_password

from app.routers import (
    auth,
    dashboard,
    guests,
    gifts,
    contributors,
    events,
    thank_you,
    ai,
    history,
    reports,
    settings as settings_router
)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Wedding Gift Management System with Note Processing, Thank-You Tracking & Reciprocity Ledger"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(guests.router)
app.include_router(gifts.router)
app.include_router(contributors.router)
app.include_router(events.router)
app.include_router(thank_you.router)
app.include_router(ai.router)
app.include_router(history.router)
app.include_router(reports.router)
app.include_router(settings_router.router)

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "database": DB_ENGINE_TYPE,
        "version": settings.APP_VERSION
    }

# Bootstrap seed admin user and default primary wedding event
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Check admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                email="farhana.family@weddingledger.com",
                username="admin",
                hashed_password=hash_password("admin123"),
                full_name="Farhana Rahman",
                role="admin"
            )
            db.add(admin)

        # Check primary wedding event
        primary_event = db.query(WeddingEvent).filter(WeddingEvent.is_primary == True).first()
        if not primary_event:
            from datetime import date
            primary_event = WeddingEvent(
                event_name="Farhana & Tanvir's Wedding",
                event_date=date(2026, 11, 20),
                venue="Dhaka Regency Convention Hall",
                host_family="Farhana's Family",
                is_primary=True,
                notes="Farhana's wedding ceremony. Attended by ~400 guests."
            )
            db.add(primary_event)

        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

# Frontend Static Files Mount
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    @app.get("/")
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{page_name}.html")
    def serve_html_page(page_name: str):
        target_path = FRONTEND_DIR / f"{page_name}.html"
        if target_path.exists():
            return FileResponse(str(target_path))
        return FileResponse(str(FRONTEND_DIR / "dashboard.html"))
