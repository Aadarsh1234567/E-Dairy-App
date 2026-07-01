"""
Payment service — Phase 8.
Business logic for recording farmer payments.

UPDATED RULE (per explicit product decision):
  - The dairy can give farmers money in advance against future milk deliveries.
  - This means a payment is NO LONGER capped at the outstanding balance.
  - Balance formula is unchanged: SUM(active transactions) - SUM(payments).
    It now naturally goes negative when an advance has been given.
  - Negative balance = dairy owes farmer (advance outstanding).
    Positive balance = farmer owes dairy (normal case).
  - New transactions reduce a negative balance back toward zero exactly
    like they reduce any positive debt — no special-case logic needed,
    the same SUM formula already does this correctly.

Other rules still enforced:
  - amount_paid must be > 0
  - Farmer must exist
  - Receipt number auto-generated as REC-YYYY-NNNN (sequential per year)
  - Balance is re-queried live at save time (never trusts a stale UI value)
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func
from database.database import get_session, write_audit_log
from database.models import Farmer, Payment, Transaction


class PaymentError(Exception):
    pass


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


# ── Data classes ───────────────────────────────────────────────────────────────
@dataclass
class PaymentRow:
    payment_id:      int
    farmer_id:        int
    farmer_code:       str
    farmer_name:        str
    payment_date:        date
    amount_paid:          float
    receipt_number:       str
    remarks:               str


# ── Helpers ────────────────────────────────────────────────────────────────────

def _outstanding_balance(session, farmer_id: int) -> float:
    """
    Live outstanding balance = SUM(ACTIVE transaction amounts incl. bonus) - SUM(payments).
    Can be negative (dairy owes farmer an advance).
    """
    active_txns = session.query(
        Transaction.quantity, Transaction.rate, Transaction.bonus_amount
    ).filter_by(farmer_id=farmer_id, status="ACTIVE").all()
    total_owed = sum(float(q) * float(r) + float(b or 0) for q, r, b in active_txns)

    paid_row = session.query(func.sum(Payment.amount_paid)).filter_by(
        farmer_id=farmer_id
    ).scalar()
    total_paid = float(paid_row or 0)
    return round(total_owed - total_paid, 2)


def _next_receipt_number(session, year: int) -> str:
    """Generate the next sequential receipt number for the given year: REC-YYYY-NNNN."""
    prefix = f"REC-{year}-"
    count = session.query(func.count(Payment.payment_id)).filter(
        Payment.receipt_number.like(f"{prefix}%")
    ).scalar() or 0
    next_seq = count + 1
    return f"{prefix}{next_seq:04d}"


# ── Public API ─────────────────────────────────────────────────────────────────

def get_outstanding_balance(farmer_id: int) -> float:
    """Public accessor for live outstanding balance (can be negative)."""
    with get_session() as session:
        return _outstanding_balance(session, farmer_id)


def record_payment(
    farmer_id:     int,
    payment_date:   date,
    amount_paid:    float,
    remarks:        str = "",
    generate_receipt: bool = True,
) -> PaymentRow:
    """
    Record a payment to a farmer.

    Validation:
      - amount_paid must be > 0
      - farmer must exist
      - NO upper limit check — payments may exceed balance (advance allowed)

    Raises PaymentError on validation failure.
    """
    if amount_paid is None or amount_paid <= 0:
        raise PaymentError(_t("zero_payment"))

    remarks = (remarks or "").strip()

    with get_session() as session:
        farmer = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        if not farmer:
            raise PaymentError(_t("farmer_not_found"))

        # Balance is queried fresh here but is informational only —
        # it does NOT block the payment. Advances are allowed by design.
        _ = _outstanding_balance(session, farmer_id)

        receipt_number = None
        if generate_receipt:
            receipt_number = _next_receipt_number(session, payment_date.year)

        payment = Payment(
            farmer_id          = farmer_id,
            payment_date        = payment_date,
            amount_paid          = amount_paid,
            receipt_number        = receipt_number,
            remarks                = remarks or None,
            receipt_generated      = 1 if generate_receipt else 0,
            created_at              = datetime.utcnow(),
        )
        session.add(payment)
        session.flush()

        write_audit_log(session, "PAYMENT_CREATED",
                        f"Payment recorded: {farmer.farmer_code} — "
                        f"NPR {amount_paid:,.2f}"
                        + (f" (Receipt {receipt_number})" if receipt_number else ""),
                        reference_id=payment.payment_id)
        session.commit()

        return PaymentRow(
            payment_id      = payment.payment_id,
            farmer_id       = farmer_id,
            farmer_code     = farmer.farmer_code,
            farmer_name     = farmer.display_name,
            payment_date     = payment_date,
            amount_paid       = float(amount_paid),
            receipt_number     = receipt_number or "",
            remarks             = remarks,
        )


def get_payment_history(farmer_id: int, limit: int = 50) -> list[PaymentRow]:
    """Return payment history for a farmer, most recent first."""
    with get_session() as session:
        farmer = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        if not farmer:
            return []
        rows = (
            session.query(Payment)
            .filter_by(farmer_id=farmer_id)
            .order_by(Payment.payment_id.desc())
            .limit(limit)
            .all()
        )
        return [
            PaymentRow(
                payment_id   = p.payment_id,
                farmer_id    = farmer_id,
                farmer_code  = farmer.farmer_code,
                farmer_name  = farmer.display_name,
                payment_date  = p.payment_date,
                amount_paid    = float(p.amount_paid),
                receipt_number  = p.receipt_number or "",
                remarks          = p.remarks or "",
            )
            for p in rows
        ]


def get_recent_payments(limit: int = 10) -> list[PaymentRow]:
    """Return the most recent payments across all farmers."""
    with get_session() as session:
        rows = (
            session.query(Payment)
            .order_by(Payment.payment_id.desc())
            .limit(limit)
            .all()
        )
        result = []
        for p in rows:
            farmer = session.query(Farmer).filter_by(farmer_id=p.farmer_id).first()
            result.append(PaymentRow(
                payment_id   = p.payment_id,
                farmer_id    = p.farmer_id,
                farmer_code  = farmer.farmer_code if farmer else "—",
                farmer_name  = farmer.display_name if farmer else "—",
                payment_date  = p.payment_date,
                amount_paid    = float(p.amount_paid),
                receipt_number  = p.receipt_number or "",
                remarks          = p.remarks or "",
            ))
        return result
