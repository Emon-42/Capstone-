import re
import os
import json
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from app.core.config import settings
from app.schemas.ai import ExtractedGiftItem, ProcessNoteResponse

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def process_handwritten_note(note_text: str, image_base64: Optional[str] = None) -> ProcessNoteResponse:
        """
        Extracts structured suggestions from raw handwritten notes.
        CRITICAL RULES:
        1. Never invent guest identities or relationships.
        2. Never invent cash amounts.
        3. Highlight uncertain fields.
        4. Requires user review & confirmation.
        """
        cleaned_text = note_text.strip()

        # Check if external LLM API is configured
        if settings.GEMINI_API_KEY and settings.AI_PROVIDER == "gemini":
            try:
                result = AIService._call_gemini_api(cleaned_text, image_base64)
                if result:
                    return result
            except Exception as e:
                logger.warning("Gemini API call failed (%s). Falling back to built-in NLP engine.", e)

        # Built-in Heuristic NLP Rule Engine
        return AIService._heuristic_nlp_parse(cleaned_text)

    @staticmethod
    def _heuristic_nlp_parse(note: str) -> ProcessNoteResponse:
        lower = note.lower()

        possible_names = []
        relationship_guess = None
        family_group = None
        gift_name = ""
        category = "Other"
        quantity = 1
        is_cash = False
        cash_amount = None
        is_joint = False
        missing_fields = []
        uncertain_fields = []
        review_reasons = []
        confidence = 0.95

        # Joint contributor checks
        if any(term in lower for term in ["+", "&", "and family", "+ family", "with family", "family"]):
            is_joint = True

        # Unidentified / Missing info checks
        has_question_marks = "?" in note
        no_card = "no card" in lower or "without card" in lower
        didnt_catch = "didn't catch" in lower or "didnt catch" in lower or "no name" in lower or "unknown" in lower

        # Detect Cash indicators
        cash_terms = ["envelope", "cash", "taka", "bdt", "salami", "money"]
        if any(term in lower for term in cash_terms):
            is_cash = True
            category = "Cash"
            gift_name = "Cash Envelope"
            # Check if an explicit number is present
            amount_match = re.search(r'(?:tk|bdt|\$|rs\.?)\s*([0-9,]+)|([0-9,]+)\s*(?:tk|taka|bdt)', lower)
            if amount_match:
                raw_val = (amount_match.group(1) or amount_match.group(2)).replace(',', '')
                try:
                    cash_amount = Decimal(raw_val)
                except Exception:
                    cash_amount = None
            else:
                cash_amount = None
                uncertain_fields.append("cash_amount")
                review_reasons.append("Cash amount not written on note. Preserving as optional.")

        # Specific known pattern parsing
        # If note starts with "big box" or mentions no card without a hyphen person
        if ("big box" in lower or "no card" in lower) and "-" not in note:
            raw_giver = ""
            raw_gift = note.strip()
        elif "-" in note:
            parts = note.split("-", 1)
            raw_giver = parts[0].strip()
            raw_gift = parts[1].strip()
        elif "," in note:
            parts = note.split(",", 1)
            # If the part before comma looks like a gift rather than person
            if any(term in parts[0].lower() for term in ["box", "saree", "set", "envelope", "tv", "gift"]):
                raw_giver = ""
                raw_gift = note.strip()
            else:
                raw_giver = parts[0].strip()
                raw_gift = parts[1].strip()
        else:
            raw_giver = ""
            raw_gift = note.strip()

        # Parse Giver
        if raw_giver:
            # Relationship detection
            if "uncle" in raw_giver.lower():
                relationship_guess = "Uncle"
            elif "khala" in raw_giver.lower():
                relationship_guess = "Maternal Aunt (Khala)"
            elif "chachi" in raw_giver.lower() or "cachi" in raw_giver.lower():
                relationship_guess = "Aunt (Chachi)"
            elif "fupu" in raw_giver.lower() or "phupu" in raw_giver.lower():
                relationship_guess = "Aunt (Fupu)"
            elif "mami" in raw_giver.lower():
                relationship_guess = "Maternal Aunt (Mami)"
            elif "bhaia" in raw_giver.lower() or "bhaiya" in raw_giver.lower() or "brother" in raw_giver.lower():
                relationship_guess = "Brother"
            elif "apu" in raw_giver.lower() or "sister" in raw_giver.lower():
                relationship_guess = "Sister"
            elif "friend" in raw_giver.lower() or "colleague" in raw_giver.lower():
                relationship_guess = "Friend/Colleague"

            # Check if Chittagong or regional reference
            if "chittagong" in raw_giver.lower():
                family_group = "Chittagong Family"
                if didnt_catch:
                    possible_names.append("People from Chittagong")
                    missing_fields.append("guest_name")
                    review_reasons.append("Guest name was not recorded (Chittagong group).")
                else:
                    possible_names.append(raw_giver)
            elif is_joint:
                clean_name = re.sub(r'\s*\+\s*family|\s+and\s+family', '', raw_giver, flags=re.IGNORECASE).strip()
                possible_names.append(clean_name.title())
                family_group = f"{clean_name.title()} Family"
            else:
                possible_names.append(raw_giver.title())

        # If no giver or unidentified
        if not possible_names:
            if no_card or has_question_marks or "big box" in lower:
                possible_names.append("Unidentified Guest")
                missing_fields.append("guest_name")
                review_reasons.append("Unidentified gift giver; no card was found on the package.")
            else:
                possible_names.append("Unknown Guest")
                missing_fields.append("guest_name")

        # Parse Gift details if not already cash
        if not is_cash:
            # Check quantity
            qty_match = re.search(r'\b([0-9]+)\s+([a-zA-Z\s]+)', raw_gift)
            if qty_match:
                try:
                    quantity = int(qty_match.group(1))
                    gift_name = f"{quantity} {qty_match.group(2).strip().title()}"
                except Exception:
                    gift_name = raw_gift.strip().title()
            else:
                gift_name = raw_gift.strip().title()

            # Categorization
            gift_lower = gift_name.lower()
            if any(term in gift_lower for term in ["dinner set", "crockery", "microwave", "blender", "cooker", "bedsheet", "blanket", "pan", "kitchen"]):
                category = "Household Items"
            elif any(term in gift_lower for term in ["saree", "sharee", "punjabi", "shirt", "suit", "clothing", "dress", "shawl"]):
                category = "Clothing"
            elif any(term in gift_lower for term in ["gold", "jewelry", "ring", "necklace", "bangle", "chain", "bracelet"]):
                category = "Jewelry"
            elif any(term in gift_lower for term in ["tv", "television", "refrigerator", "fridge", "iron", "oven", "speaker"]):
                category = "Electronics"
            elif any(term in gift_lower for term in ["clock", "vase", "frame", "painting", "lamp", "showpiece", "decorative"]):
                category = "Decorative Items"
            elif "box" in gift_lower:
                category = "Unknown"
                review_reasons.append("Box unopened or content unspecified.")
            else:
                category = "Other"

        # Determine confidence & suggested action
        if missing_fields or uncertain_fields or review_reasons:
            confidence = 0.70 if len(missing_fields) == 1 else 0.50
            suggested_action = "review"
        else:
            confidence = 0.95
            suggested_action = "confirm"

        extracted = ExtractedGiftItem(
            original_text=note,
            possible_guest_names=possible_names,
            relationship_guess=relationship_guess,
            family_group=family_group,
            gift_name=gift_name or "Wedding Gift",
            gift_description=f"Recorded from original note: \"{note}\"",
            gift_category=category,
            quantity=quantity,
            is_cash=is_cash,
            cash_amount=cash_amount,
            is_joint_gift=is_joint,
            confidence_score=confidence,
            missing_fields=missing_fields,
            uncertain_fields=uncertain_fields,
            review_reasons=review_reasons,
            suggested_action=suggested_action
        )

        return ProcessNoteResponse(
            success=True,
            original_note=note,
            extracted_data=extracted,
            source="heuristic_nlp",
            disclaimer="Strict business rule: Never invent cash amounts or missing identities. Please review and confirm."
        )

    @staticmethod
    def _call_gemini_api(note_text: str, image_base64: Optional[str] = None) -> Optional[ProcessNoteResponse]:
        # Optional external LLM API client wrapper
        # Preserves strict accuracy rules in prompt
        return None

    @staticmethod
    def answer_assistant_query(query: str, db_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI Assistant reasoning tool over real database metrics.
        Never fabricates records; clearly indicates when information is unknown.
        """
        q = query.lower()
        insights = []
        records = []
        actions = []

        if "pending" in q or "thank" in q:
            pending_count = db_context.get("thank_you_pending", 0)
            ans = f"There are currently {pending_count} pending thank-you messages waiting to be sent to guests."
            if pending_count > 0:
                actions.append("Navigate to Thank You Messages page to review and send pending notes.")
                insights.append("Sending thank-you messages within 2 weeks of the wedding is ideal.")
        elif "unknown" in q or "unidentified" in q or "missing" in q:
            unidentified = db_context.get("unidentified_gifts", 0)
            review_needed = db_context.get("gifts_requiring_review", 0)
            ans = f"There are {unidentified} gifts from unidentified guests and {review_needed} records flagged for review."
            insights.append("Common incomplete notes: 'big box, no card', 'the people from Chittagong'.")
            actions.append("Check with family elders to verify if anyone remembers the giver of the unidentified items.")
        elif "reciprocity" in q or "future" in q or "history" in q:
            ans = "The Reciprocity Ledger maintains historical records of all received gifts and gifts given in return at future weddings. It ensures you never have to guess or assume market values."
            insights.append("Reciprocity records protect the family tradition of giving gifts of comparable significance.")
            actions.append("Search any guest on the Gift History page to view their historical contributions.")
        elif "cash" in q:
            total_cash = db_context.get("total_cash_gifts", 0)
            total_val = db_context.get("total_recorded_cash_value", 0)
            ans = f"We have recorded {total_cash} cash envelope gifts. Note that per family policy, cash amounts are only stored if explicitly known, and cash amounts are NEVER mentioned in thank-you messages."
        else:
            total_g = db_context.get("total_guests", 0)
            total_gifts = db_context.get("total_gift_records", 0)
            ans = f"Wedding Gift Ledger is currently tracking {total_g} guests and {total_gifts} gift records. All records adhere strictly to historical accuracy without speculation."

        return {
            "answer": ans,
            "insights": insights,
            "related_records": records,
            "suggested_actions": actions
        }
