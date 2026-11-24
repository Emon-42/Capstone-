import io
import csv
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.guest import Guest
from app.models.gift import Gift
from app.models.contributor import GiftContributor
from app.models.thank_you import ThankYouMessage
from app.models.history import GiftExchangeHistory
from app.schemas.report import (
    DashboardStats,
    CategoryStat,
    MonthlyStat,
    RecentActivityItem,
    ReportSummary
)

class ReportService:
    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStats:
        total_guests = db.query(Guest).filter(Guest.is_deleted == False).count()
        total_gifts = db.query(Gift).filter(Gift.is_deleted == False).count()
        total_contributors = db.query(GiftContributor).count()

        thank_you_sent = db.query(ThankYouMessage).filter(ThankYouMessage.status == "sent").count()
        thank_you_pending = db.query(ThankYouMessage).filter(ThankYouMessage.status == "pending").count()
        thank_you_draft = db.query(ThankYouMessage).filter(ThankYouMessage.status == "draft").count()

        unidentified_gifts = db.query(Gift).filter(
            Gift.is_deleted == False,
            Gift.review_status == "unidentified"
        ).count()

        gifts_requiring_review = db.query(Gift).filter(
            Gift.is_deleted == False,
            Gift.review_status == "requires_review"
        ).count()

        total_cash_gifts = db.query(Gift).filter(
            Gift.is_deleted == False,
            Gift.is_cash == True
        ).count()

        cash_sum_res = db.query(func.sum(Gift.cash_amount)).filter(
            Gift.is_deleted == False,
            Gift.is_cash == True,
            Gift.cash_amount.isnot(None)
        ).scalar()
        total_recorded_cash_value = Decimal(str(cash_sum_res or 0.00))

        total_ty = thank_you_sent + thank_you_pending + thank_you_draft
        completion_rate = (thank_you_sent / total_ty * 100.0) if total_ty > 0 else 0.0

        return DashboardStats(
            total_guests=total_guests,
            total_gift_records=total_gifts,
            total_contributors=total_contributors,
            thank_you_sent=thank_you_sent,
            thank_you_pending=thank_you_pending,
            thank_you_draft=thank_you_draft,
            unidentified_gifts=unidentified_gifts,
            gifts_requiring_review=gifts_requiring_review,
            total_cash_gifts=total_cash_gifts,
            total_recorded_cash_value=total_recorded_cash_value,
            completion_rate_percentage=round(completion_rate, 1)
        )

    @staticmethod
    def get_category_distribution(db: Session) -> List[CategoryStat]:
        total_gifts = db.query(Gift).filter(Gift.is_deleted == False).count()
        if total_gifts == 0:
            return []

        counts = (
            db.query(Gift.gift_category, func.count(Gift.id))
            .filter(Gift.is_deleted == False)
            .group_by(Gift.gift_category)
            .all()
        )

        results = []
        for cat, cnt in counts:
            pct = round((cnt / total_gifts) * 100.0, 1)
            results.append(CategoryStat(category=cat, count=cnt, percentage=pct))
        return results

    @staticmethod
    def get_recent_activities(db: Session, limit: int = 10) -> List[RecentActivityItem]:
        activities = []
        # Recent Gifts
        recent_gifts = (
            db.query(Gift)
            .filter(Gift.is_deleted == False)
            .order_by(Gift.created_at.desc())
            .limit(limit)
            .all()
        )
        for g in recent_gifts:
            activities.append(
                RecentActivityItem(
                    id=g.id,
                    type="gift",
                    title=f"Gift Recorded: {g.gift_name}",
                    description=f"Note: \"{g.original_note}\" ({g.gift_category})",
                    timestamp=g.created_at.strftime("%Y-%m-%d %H:%M"),
                    status=g.review_status
                )
            )

        # Recent Thank You actions
        recent_ty = (
            db.query(ThankYouMessage)
            .order_by(ThankYouMessage.updated_at.desc())
            .limit(5)
            .all()
        )
        for t in recent_ty:
            activities.append(
                RecentActivityItem(
                    id=t.id,
                    type="thank_you",
                    title=f"Thank You Message ({t.status.capitalize()})",
                    description=t.message_text[:80] + ("..." if len(t.message_text) > 80 else ""),
                    timestamp=t.updated_at.strftime("%Y-%m-%d %H:%M"),
                    status=t.status
                )
            )

        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]

    @staticmethod
    def export_csv(db: Session, export_type: str) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        if export_type == "guests":
            writer.writerow(["ID", "Full Name", "Relationship", "Phone", "Email", "Family Group", "Is Unidentified", "Notes"])
            guests = db.query(Guest).filter(Guest.is_deleted == False).all()
            for g in guests:
                writer.writerow([g.id, g.full_name, g.relationship_type, g.phone_number or "", g.email or "", g.family_group or "", g.is_unidentified, g.notes or ""])

        elif export_type == "gifts":
            writer.writerow(["ID", "Gift Name", "Category", "Quantity", "Is Cash", "Cash Amount", "Currency", "Original Handwritten Note", "Review Status", "Created At"])
            gifts = db.query(Gift).filter(Gift.is_deleted == False).all()
            for g in gifts:
                writer.writerow([g.id, g.gift_name, g.gift_category, g.quantity, g.is_cash, g.cash_amount or "", g.currency, g.original_note, g.review_status, g.created_at])

        elif export_type == "thank_you":
            writer.writerow(["ID", "Gift ID", "Guest ID", "Status", "Tone", "Message Text", "Sent Date", "Sent Via"])
            messages = db.query(ThankYouMessage).all()
            for m in messages:
                writer.writerow([m.id, m.gift_id, m.guest_id, m.status, m.tone, m.message_text.replace("\n", " "), m.sent_date or "", m.sent_via or ""])

        elif export_type == "history":
            writer.writerow(["ID", "Guest ID", "Family Group", "Event Name", "Event Type", "Gift Description", "Category", "Recorded Value", "Currency", "Event Date"])
            history = db.query(GiftExchangeHistory).all()
            for h in history:
                writer.writerow([h.id, h.guest_id or "", h.family_group or "", h.event_name, h.event_type, h.gift_description, h.category, h.recorded_value or "", h.currency, h.event_date])

        return output.getvalue()
