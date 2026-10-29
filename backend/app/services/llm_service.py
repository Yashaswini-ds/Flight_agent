import json
import logging
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiLLMService:
    """
    Service wrapper for Google Gemini AI models.
    Used by IntentAgent to analyze complex travel queries and extract structured intent JSON.
    Smoothly falls back to local NLP if API key is not configured.
    """
    def __init__(self):
        self.api_key = settings.LLM_API_KEY or ""
        self.model = settings.LLM_MODEL if settings.LLM_MODEL else "gemini-1.5-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def extract_intent_with_gemini(self, user_message: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None

        prompt = f"""
You are an expert flight assistant AI for an Indian domestic airline platform.
Analyze the user request and respond strictly with valid JSON containing the extracted travel parameters.

Supported City Codes:
- Bangalore / Bengaluru -> BLR
- Chennai -> MAA
- Hyderabad -> HYD
- Mumbai -> BOM
- Delhi / New Delhi -> DEL

JSON Schema to return:
{{
  "intent_type": "SEARCH_FLIGHTS" | "BOOK_FLIGHT" | "CANCEL_BOOKING" | "CHECK_STATUS" | "GENERAL_QUERY",
  "source": "BLR" | "MAA" | "HYD" | "BOM" | "DEL" | null,
  "destination": "BLR" | "MAA" | "HYD" | "BOM" | "DEL" | null,
  "travel_date": "YYYY-MM-DD" or null,
  "passenger_count": int (default 1),
  "travel_class": "ECONOMY" | "PREMIUM_ECONOMY" | "BUSINESS",
  "flight_number": "DA-101" or null,
  "booking_reference": "BK-1234" or null,
  "passengers_data": [
     {{"first_name": "string", "last_name": "string", "gender": "MALE"|"FEMALE", "age": int}}
  ]
}}

Rules:
1. If the user wants to book a flight (e.g. "Book a flight...", "Book DA-101"), set intent_type to "BOOK_FLIGHT".
2. If the user wants to search/find options, set intent_type to "SEARCH_FLIGHTS".
3. If the user wants to cancel (e.g. "Cancel BK-1234"), set intent_type to "CANCEL_BOOKING".
4. Return ONLY valid JSON, with no markdown formatting around it if possible, or inside standard json fences.

User message: "{user_message}"
"""

        try:
            url = f"{self.base_url}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json"
                }
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_resp = candidates[0]["content"]["parts"][0]["text"].strip()
                        # Clean code fences if present
                        if text_resp.startswith("```"):
                            text_resp = text_resp.split("```")[1]
                            if text_resp.startswith("json"):
                                text_resp = text_resp[4:]
                        parsed = json.loads(text_resp)
                        return parsed
                else:
                    logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Gemini LLM call failed: {e}")
        
        return None
