from app.models.payment import Payment, PaymentStatus

def execute_simulated_ap2_transaction(
    payment: Payment,
    ap2_consent_token: str,
    demo_identifier: str
) -> bool:
    """
    Executes the AP2 simulated payment transaction against the authorization token.
    Updates payment status to SUCCESS and attaches consent token audit record.
    """
    if not ap2_consent_token:
        payment.status = PaymentStatus.FAILED
        return False
    
    payment.ap2_consent_token = ap2_consent_token
    # Mask identifier for audit record (e.g. user@upi -> u***@upi or card ****1234)
    if "@" in demo_identifier:
        user_part, domain = demo_identifier.split("@", 1)
        masked_id = f"{user_part[0]}***@{domain}"
    elif len(demo_identifier) >= 4:
        masked_id = f"**** **** **** {demo_identifier[-4:]}"
    else:
        masked_id = "Demo Payment User"
        
    payment.payment_details_masked = f"AP2 Verified: {payment.payment_method.value} ({masked_id})"
    payment.status = PaymentStatus.SUCCESS
    return True
