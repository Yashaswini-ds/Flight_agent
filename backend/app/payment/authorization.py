import secrets
from typing import Optional

def generate_ap2_consent_token(
    payment_intent_id: str,
    demo_pin_or_auth: str,
    demo_identifier: str
) -> str:
    """
    Simulates AP2 User Consent Token generation.
    Validates demo authorization input (e.g. demo PIN/UPI ID) and produces a cryptographic token representation.
    """
    if not demo_pin_or_auth or len(demo_pin_or_auth.strip()) == 0:
        raise ValueError("Invalid authorization consent credentials")
    
    token = f"ap2_consent_tok_{secrets.token_hex(16)}"
    return token
