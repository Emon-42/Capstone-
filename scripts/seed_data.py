import sys
import os
from pathlib import Path
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.event import WeddingEvent
from app.models.guest import Guest
from app.models.gift import Gift
from app.models.contributor import GiftContributor
from app.models.thank_you import ThankYouMessage, ThankYouStatusHistory
from app.models.history import GiftExchangeHistory
from app.models.setting import Setting
from app.core.security import hash_password

def seed_database():
    db = SessionLocal()
    try:
        print("Starting realistic database seeding...")

        # 1. Admin User
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
            db.commit()
            db.refresh(admin)
            print("  Created Admin user: admin / admin123")

        # 2. Wedding Events
        farhana_wedding = db.query(WeddingEvent).filter(WeddingEvent.is_primary == True).first()
        if not farhana_wedding:
            farhana_wedding = WeddingEvent(
                event_name="Farhana & Tanvir's Wedding",
                event_date=date(2026, 11, 20),
                venue="Dhaka Regency Grand Ballroom",
                host_family="Farhana's Family",
                is_primary=True,
                notes="Farhana's wedding ceremony. Attended by ~400 guests."
            )
            db.add(farhana_wedding)
            db.commit()
            db.refresh(farhana_wedding)

        future_wedding = db.query(WeddingEvent).filter(WeddingEvent.event_name.like("%Rahman%")).first()
        if not future_wedding:
            future_wedding = WeddingEvent(
                event_name="Rahman Uncle's Son's Wedding",
                event_date=date(2027, 2, 14),
                venue="Gulshan Club, Dhaka",
                host_family="Rahman Family",
                is_primary=False,
                notes="Upcoming wedding of Rahman Uncle's elder son Tariq."
            )
            db.add(future_wedding)
            db.commit()
            db.refresh(future_wedding)

        # 3. Guests from Assessment Prompt & Realistic Wedding Attendees
        guests_data = [
            # The core 4 cases from prompt:
            {
                "full_name": "Rahman Uncle",
                "relationship_type": "Paternal Uncle",
                "phone_number": "+8801711223344",
                "email": "rahman.uncle@gmail.com",
                "family_group": "Rahman Family",
                "is_unidentified": False,
                "notes": "Close family elder. Attended with wife and two sons."
            },
            {
                "full_name": "Shilpi Khala",
                "relationship_type": "Maternal Aunt (Khala)",
                "phone_number": "+8801819334455",
                "email": "shilpi.khala@yahoo.com",
                "family_group": "Shilpi Khala Family",
                "is_unidentified": False,
                "notes": "Mother's elder sister. Came jointly with family."
            },
            {
                "full_name": "Shilpi Khala's Family Members",
                "relationship_type": "Cousins / Extended Family",
                "phone_number": None,
                "email": None,
                "family_group": "Shilpi Khala Family",
                "is_unidentified": False,
                "notes": "Joint contributors with Shilpi Khala."
            },
            {
                "full_name": "The People from Chittagong",
                "relationship_type": "Distant Relatives / Family Friends",
                "phone_number": None,
                "email": None,
                "family_group": "Chittagong Family",
                "is_unidentified": True,
                "notes": "Original note: 'the people from Chittagong - 2 sarees, didn't catch name'. Identity incomplete."
            },
            {
                "full_name": "Unidentified Gift Giver (Big Box)",
                "relationship_type": "Unknown",
                "phone_number": None,
                "email": None,
                "family_group": None,
                "is_unidentified": True,
                "notes": "Original note: 'big box, no card???'. Identity unknown."
            },
            # Additional realistic guests
            {
                "full_name": "Dr. Kamal Hossain",
                "relationship_type": "Family Friend / Senior Physician",
                "phone_number": "+8801912556677",
                "email": "dr.kamal@apollo.com",
                "family_group": "Hossain Family",
                "is_unidentified": False,
                "notes": "Father's medical college batchmate."
            },
            {
                "full_name": "Anika Tabassum",
                "relationship_type": "Bride's Best Friend",
                "phone_number": "+8801611889900",
                "email": "anika.t@gmail.com",
                "family_group": None,
                "is_unidentified": False,
                "notes": "University friend of Farhana."
            },
            {
                "full_name": "Tariq Chacha & Chachi",
                "relationship_type": "Paternal Uncle & Aunt",
                "phone_number": "+8801552331122",
                "email": None,
                "family_group": "Tariq Family",
                "is_unidentified": False,
                "notes": "Traveled from Sylhet for the wedding."
            },
            {
                "full_name": "Tanvir's University Friends Group",
                "relationship_type": "Groom's Friends",
                "phone_number": "+8801700998877",
                "email": "buet.batch14@gmail.com",
                "family_group": "Tanvir's Friends",
                "is_unidentified": False,
                "notes": "Joint gift from 6 university friends."
            }
        ]

        guest_map = {}
        for g_data in guests_data:
            existing = db.query(Guest).filter(Guest.full_name == g_data["full_name"]).first()
            if not existing:
                existing = Guest(**g_data)
                db.add(existing)
                db.commit()
                db.refresh(existing)
            guest_map[g_data["full_name"]] = existing

        print(f"  Synced {len(guest_map)} guests.")

        # 4. Gifts & Contributors
        gifts_data = [
            # Case 1: "Rahman uncle - dinner set"
            {
                "gift_name": "Dinner Set",
                "gift_description": "Premium 64-piece Bone China dinner set with floral gold trim.",
                "gift_category": "Household Items",
                "quantity": 1,
                "is_cash": False,
                "cash_amount": None,
                "currency": "BDT",
                "original_note": "Rahman uncle - dinner set",
                "additional_notes": "Very elegant dinner set for dining room display.",
                "review_status": "confirmed",
                "contributors": [guest_map["Rahman Uncle"].id]
            },
            # Case 2: "Shilpi khala + family, envelope" (amount unknown, joint contributors)
            {
                "gift_name": "Cash Envelope",
                "gift_description": "Decorative golden envelope containing cash from Shilpi Khala and her family.",
                "gift_category": "Cash",
                "quantity": 1,
                "is_cash": True,
                "cash_amount": None,  # Crucial: NEVER invent cash amount!
                "currency": "BDT",
                "original_note": "Shilpi khala + family, envelope",
                "additional_notes": "Joint contribution from Shilpi Khala and her family. Mother remembers envelope was thick, but exact amount was not written down at time of collection.",
                "review_status": "confirmed",
                "contributors": [
                    guest_map["Shilpi Khala"].id,
                    guest_map["Shilpi Khala's Family Members"].id
                ]
            },
            # Case 3: "the people from Chittagong - 2 sarees, didn't catch name"
            {
                "gift_name": "2 Sarees",
                "gift_description": "Two traditional handloom silk Jamdani sarees.",
                "gift_category": "Clothing",
                "quantity": 2,
                "is_cash": False,
                "cash_amount": None,
                "currency": "BDT",
                "original_note": "the people from Chittagong - 2 sarees, didn't catch name",
                "additional_notes": "The guests arrived during peak dinner rush. Family remembers they traveled from Chittagong. Need to ask mother to clarify exact names.",
                "review_status": "requires_review",
                "contributors": [guest_map["The People from Chittagong"].id]
            },
            # Case 4: "big box, no card???"
            {
                "gift_name": "Big Box (Unidentified)",
                "gift_description": "Large wrapped parcel placed on the gift table with no card or name tag.",
                "gift_category": "Unknown",
                "quantity": 1,
                "is_cash": False,
                "cash_amount": None,
                "currency": "BDT",
                "original_note": "big box, no card???",
                "additional_notes": "Box placed near the stage. Opened box contains a high-end stand mixer/food processor, but card is missing.",
                "review_status": "unidentified",
                "contributors": [guest_map["Unidentified Gift Giver (Big Box)"].id]
            },
            # Case 5: Known cash gift with explicit amount
            {
                "gift_name": "Cash Salami Envelope",
                "gift_description": "Cash gift with card explicitly noting 10,000 BDT blessings.",
                "gift_category": "Cash",
                "quantity": 1,
                "is_cash": True,
                "cash_amount": Decimal("10000.00"),
                "currency": "BDT",
                "original_note": "Dr. Kamal Hossain - envelope Tk 10,000",
                "additional_notes": "Amount explicitly verified from card enclosed inside.",
                "review_status": "confirmed",
                "contributors": [guest_map["Dr. Kamal Hossain"].id]
            },
            # Case 6: Anika Tabassum - Gold Ring
            {
                "gift_name": "22K Gold Ring",
                "gift_description": "Delicate 22K yellow gold floral ring.",
                "gift_category": "Jewelry",
                "quantity": 1,
                "is_cash": False,
                "cash_amount": None,
                "currency": "BDT",
                "original_note": "Anika - gold ring in red velvet box",
                "additional_notes": "Best friend gift.",
                "review_status": "confirmed",
                "contributors": [guest_map["Anika Tabassum"].id]
            },
            # Case 7: Tariq Chacha - Microwave Oven
            {
                "gift_name": "Convection Microwave Oven",
                "gift_description": "Panasonic 27L Convection Microwave Oven.",
                "gift_category": "Electronics",
                "quantity": 1,
                "is_cash": False,
                "cash_amount": None,
                "currency": "BDT",
                "original_note": "Tariq Chacha & Chachi - Panasonic microwave",
                "additional_notes": "Electronics item with 1-year warranty card included.",
                "review_status": "confirmed",
                "contributors": [guest_map["Tariq Chacha & Chachi"].id]
            },
            # Case 8: Tanvir's University Friends - 55-inch Smart TV (Joint Gift)
            {
                "gift_name": "55-inch 4K Smart TV",
                "gift_description": "Sony Bravia 55-inch 4K UHD Google TV.",
                "gift_category": "Electronics",
                "quantity": 1,
                "is_cash": False,
                "cash_amount": None,
                "currency": "BDT",
                "original_note": "BUET batch friends - Sony 55 inch TV",
                "additional_notes": "Group contribution from groom's university friends.",
                "review_status": "confirmed",
                "contributors": [guest_map["Tanvir's University Friends Group"].id]
            }
        ]

        for g_dict in gifts_data:
            existing_gift = db.query(Gift).filter(Gift.original_note == g_dict["original_note"]).first()
            if not existing_gift:
                contrib_ids = g_dict.pop("contributors")
                gift = Gift(
                    event_id=farhana_wedding.id,
                    gift_date=farhana_wedding.event_date,
                    **g_dict
                )
                db.add(gift)
                db.commit()
                db.refresh(gift)

                for idx, c_id in enumerate(contrib_ids):
                    contrib = GiftContributor(
                        gift_id=gift.id,
                        guest_id=c_id,
                        contribution_note="Joint Contributor" if len(contrib_ids) > 1 else "Primary Contributor",
                        is_primary=(idx == 0)
                    )
                    db.add(contrib)

                db.commit()

        print("  Synced gifts and contributor relations.")

        # 5. Thank You Messages
        # Ensure status tracking: Rahman Uncle (Sent), Shilpi Khala (Pending), Dr. Kamal (Sent), Chittagong (Draft/Requires Review)
        all_gifts = db.query(Gift).all()
        for g in all_gifts:
            for c in g.contributors:
                existing_ty = db.query(ThankYouMessage).filter(
                    ThankYouMessage.gift_id == g.id,
                    ThankYouMessage.guest_id == c.guest_id
                ).first()

                if not existing_ty:
                    guest = c.guest
                    # Determine status
                    if "Rahman" in guest.full_name or "Kamal" in guest.full_name:
                        ty_status = "sent"
                        sent_dt = datetime(2026, 11, 22, 16, 30)
                        sent_via = "WhatsApp"
                    elif guest.is_unidentified:
                        ty_status = "draft"
                        sent_dt = None
                        sent_via = None
                    else:
                        ty_status = "pending"
                        sent_dt = None
                        sent_via = None

                    # Craft message - CRITICAL: never mention cash amount!
                    if g.is_cash:
                        gift_mention = "thoughtful gift and kind blessings"
                    else:
                        gift_mention = f"wonderful {g.gift_name}"

                    msg_text = (
                        f"Dear {guest.full_name},\n\n"
                        f"Thank you so much for the {gift_mention}. We truly appreciate your thoughtful gesture and your presence at our wedding.\n\n"
                        f"With love and warm regards,\nFarhana and Family"
                    )

                    ty = ThankYouMessage(
                        gift_id=g.id,
                        guest_id=guest.id,
                        status=ty_status,
                        tone="warm",
                        message_text=msg_text,
                        sent_date=sent_dt,
                        sent_via=sent_via,
                        notes="Generated personalized message"
                    )
                    db.add(ty)
                    db.commit()
                    db.refresh(ty)

                    # Add status history
                    hist = ThankYouStatusHistory(
                        message_id=ty.id,
                        previous_status="draft" if ty_status != "draft" else "initial",
                        new_status=ty_status,
                        change_reason=f"Status set to {ty_status}"
                    )
                    db.add(hist)
                    db.commit()

        print("  Synced Thank You messages and history.")

        # 6. Reciprocity Ledger (Gift Exchange History)
        # Record all received gifts from Farhana's wedding
        for g in all_gifts:
            for c in g.contributors:
                guest = c.guest
                existing_rec = db.query(GiftExchangeHistory).filter(
                    GiftExchangeHistory.reference_gift_id == g.id,
                    GiftExchangeHistory.guest_id == guest.id
                ).first()

                if not existing_rec:
                    rec = GiftExchangeHistory(
                        guest_id=guest.id,
                        family_group=guest.family_group,
                        event_id=farhana_wedding.id,
                        event_name="Farhana & Tanvir's Wedding",
                        event_type="received",
                        gift_description=g.gift_name,
                        category=g.gift_category,
                        recorded_value=g.cash_amount if g.is_cash else None,
                        currency=g.currency,
                        event_date=g.gift_date,
                        reference_gift_id=g.id,
                        notes=f"Original note: {g.original_note}"
                    )
                    db.add(rec)
                    db.commit()

        # Add a recorded reciprocity return gift for Rahman Uncle's family!
        # Farhana's family will attend Rahman Uncle's son's wedding in Feb 2027 and planned/gave a dinner set in return!
        rahman_guest = guest_map["Rahman Uncle"]
        existing_return = db.query(GiftExchangeHistory).filter(
            GiftExchangeHistory.guest_id == rahman_guest.id,
            GiftExchangeHistory.event_type == "given_return"
        ).first()

        if not existing_return:
            return_gift = GiftExchangeHistory(
                guest_id=rahman_guest.id,
                family_group="Rahman Family",
                event_id=future_wedding.id,
                event_name="Rahman Uncle's Son's Wedding",
                event_type="given_return",
                gift_description="Premium Crystal 72-pc Dinner & Cutlery Set (Reciprocal Gift)",
                category="Household Items",
                recorded_value=None,  # Not guessing value
                currency="BDT",
                event_date=future_wedding.event_date,
                notes="Farhana's family giving in return for the Bone China dinner set received at Farhana's wedding."
            )
            db.add(return_gift)
            db.commit()
            print("  Added reciprocal return gift record for Rahman Uncle's family.")

        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
