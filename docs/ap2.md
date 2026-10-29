# Agent Payments Protocol (AP2) Representation & Simulation Specification

This document details the exact representation of Agent Payments Protocol (AP2) concepts within the FlightAgent application.

## Overview
FlightAgent implements an agent-assisted checkout flow that reflects AP2 workflow concepts for autonomous agent payments. **This implementation is strictly a DEMO/SIMULATED environment and does NOT handle real monetary transactions or real payment networks.**

---

## 1. AP2 Protocol Concepts Represented

| AP2 Concept | Application Entity / Field | Description |
| :--- | :--- | :--- |
| **Payment Intent** | `Payment.payment_intent_id` (`pi_sim_...`) | Immutable line-item request generated prior to authorization containing the breakdown of base fare, taxes, seat fees, and total amount. |
| **Merchant Mandate ID** | `Payment.ap2_mandate_id` (`man_sim_...`) | Simulated agreement ID between the merchant (airline platform) and the user's booking mandate. |
| **User Consent Token** | `Payment.ap2_consent_token` (`ap2_consent_tok_...`) | Cryptographic token representing user authorization consent passed from the client UI after demo PIN verification. |
| **Transaction Execution** | `execute_simulated_ap2_transaction()` | Transaction processor that verifies the consent token before finalizing booking confirmation and recording audit trail. |
| **Payment Audit Record** | `Payment.payment_details_masked` | Masked transaction record maintaining proof of user consent for compliance without exposing sensitive details. |

---

## 2. Simulated vs. Production Differences

### What IS Simulated:
- Generation of deterministic Payment Intent IDs (`pi_sim_...`) and Merchant Mandate IDs.
- User Consent Token issuance upon user entry of demo PIN (`1234` or any non-empty value).
- Masked audit logging (`r***@upi` or `**** **** **** 4444`).
- Atomic booking status update (`PAYMENT_PENDING` → `CONFIRMED`).

### What is NOT Implemented (Demo Exclusions):
- Real banking API calls, UPI network handshakes, or Visa/Mastercard payment gateway settlement.
- Real cryptographic signature verification of OAuth/OpenID payment mandates.
- Real hardware enclave (TEE) token storage.
- Real monetary movement or bank ledger mutation.

> [!IMPORTANT]
> Real financial credentials (real UPI PINs, real card CVVs, or real OTPs) are NEVER collected, stored, or processed by this platform.
