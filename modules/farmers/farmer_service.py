"""
Farmer service — Phase 4.
All business logic for farmer management.
Rules enforced:
  - farmer_code unique
  - name_english required
  - deactivation blocked if outstanding balance > 0
  - inactive farmers excluded from active screens
  - balance calculation uses only ACTIVE transactions
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import func, and_
from database.database import get_session, write_audit_log
from database.models import Farmer, Transaction, Payment


# ── Data class returned to UI ──────────────────────────────────────────────────
@dataclass
class FarmerRow:
    farmer_id:    int
    farmer_code:  str
    name_english: str
    name_nepali:  str
    phone:        str
    address:      str
    status:       str
    outstanding:  float   # live balance


# ── Custom exceptions ──────────────────────────────────────────────────────────
class FarmerError(Exception):
    pass


# ── Helpers ────────────────────────────────────────────────────────────────────
def _t(key, **kw):
    from translations import t
    return t(key, **kw)


def _outstanding_balance(session, farmer_id: int) -> float:
    """Outstanding = SUM(active transaction amounts) - SUM(payments)."""
    active_txns = session.query(
        Transaction.quantity, Transaction.rate
    ).filter_by(farmer_id=farmer_id, status="ACTIVE").all()
    total_owed = sum(float(q) * float(r) for q, r in active_txns)

    paid_row = session.query(func.sum(Payment.amount_paid)).filter_by(
        farmer_id=farmer_id
    ).scalar()
    total_paid = float(paid_row or 0)
    return round(total_owed - total_paid, 2)


def _to_row(f: Farmer, session) -> FarmerRow:
    return FarmerRow(
        farmer_id    = f.farmer_id,
        farmer_code  = f.farmer_code,
        name_english = f.name_english,
        name_nepali  = f.name_nepali or "",
        phone        = f.phone or "",
        address      = f.address or "",
        status       = f.status,
        outstanding  = _outstanding_balance(session, f.farmer_id),
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def get_all_farmers(include_inactive: bool = True) -> list[FarmerRow]:
    """Return all farmers, optionally filtered to active only."""
    with get_session() as session:
        q = session.query(Farmer)
        if not include_inactive:
            q = q.filter_by(status="ACTIVE")
        farmers = q.order_by(Farmer.farmer_code).all()
        return [_to_row(f, session) for f in farmers]


def search_farmers(query: str, include_inactive: bool = True) -> list[FarmerRow]:
    """
    Search by farmer_code (exact prefix), name_english (contains),
    name_nepali (contains), or phone (contains).
    """
    with get_session() as session:
        q = session.query(Farmer)
        if not include_inactive:
            q = q.filter_by(status="ACTIVE")
        like = f"%{query}%"
        q = q.filter(
            (Farmer.farmer_code.ilike(like)) |
            (Farmer.name_english.ilike(like)) |
            (Farmer.name_nepali.ilike(like)) |
            (Farmer.phone.ilike(like))
        )
        return [_to_row(f, session) for f in q.order_by(Farmer.farmer_code).all()]


def get_farmer_by_code(code: str) -> Optional[FarmerRow]:
    """Fetch a single farmer by farmer_code. Returns None if not found."""
    with get_session() as session:
        f = session.query(Farmer).filter_by(farmer_code=code.strip()).first()
        return _to_row(f, session) if f else None


def get_farmer_by_id(farmer_id: int) -> Optional[FarmerRow]:
    with get_session() as session:
        f = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        return _to_row(f, session) if f else None


def add_farmer(
    farmer_code:  str,
    name_english: str,
    name_nepali:  str = "",
    phone:        str = "",
    address:      str = "",
) -> FarmerRow:
    """
    Create a new farmer. Raises FarmerError on validation failure.
    """
    farmer_code  = farmer_code.strip()
    name_english = name_english.strip()
    name_nepali  = name_nepali.strip()
    phone        = phone.strip()
    address      = address.strip()

    if not farmer_code:
        raise FarmerError(_t("code_required"))
    if not name_english:
        raise FarmerError(_t("name_required"))

    with get_session() as session:
        # Duplicate code check
        if session.query(Farmer).filter_by(farmer_code=farmer_code).first():
            raise FarmerError(_t("code_exists"))

        farmer = Farmer(
            farmer_code  = farmer_code,
            name_english = name_english,
            name_nepali  = name_nepali or None,
            phone        = phone or None,
            address      = address or None,
            status       = "ACTIVE",
            created_at   = datetime.utcnow(),
        )
        session.add(farmer)
        session.flush()   # get farmer_id before commit

        write_audit_log(session, "FARMER_CREATED",
                        f"Farmer added: {farmer_code} — {name_english}",
                        reference_id=farmer.farmer_id)
        session.commit()

        return _to_row(farmer, session)


def edit_farmer(
    farmer_id:    int,
    farmer_code:  str,
    name_english: str,
    name_nepali:  str = "",
    phone:        str = "",
    address:      str = "",
) -> FarmerRow:
    """
    Update an existing farmer's details. farmer_code uniqueness re-checked.
    """
    farmer_code  = farmer_code.strip()
    name_english = name_english.strip()
    name_nepali  = name_nepali.strip()
    phone        = phone.strip()
    address      = address.strip()

    if not farmer_code:
        raise FarmerError(_t("code_required"))
    if not name_english:
        raise FarmerError(_t("name_required"))

    with get_session() as session:
        farmer = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        if not farmer:
            raise FarmerError(_t("farmer_not_found"))

        # Code uniqueness — allow same code for same farmer
        existing = session.query(Farmer).filter_by(farmer_code=farmer_code).first()
        if existing and existing.farmer_id != farmer_id:
            raise FarmerError(_t("code_exists"))

        farmer.farmer_code  = farmer_code
        farmer.name_english = name_english
        farmer.name_nepali  = name_nepali or None
        farmer.phone        = phone or None
        farmer.address      = address or None

        write_audit_log(session, "FARMER_UPDATED",
                        f"Farmer updated: {farmer_code} — {name_english}",
                        reference_id=farmer_id)
        session.commit()
        return _to_row(farmer, session)


def deactivate_farmer(farmer_id: int) -> FarmerRow:
    """
    Deactivate a farmer. Blocked if outstanding balance > 0.
    """
    with get_session() as session:
        farmer = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        if not farmer:
            raise FarmerError(_t("farmer_not_found"))

        balance = _outstanding_balance(session, farmer_id)
        if balance > 0:
            raise FarmerError(_t("deactivate_balance", amount=f"{balance:,.2f}"))

        farmer.status = "INACTIVE"
        write_audit_log(session, "FARMER_DEACTIVATED",
                        f"Farmer deactivated: {farmer.farmer_code} — {farmer.name_english}",
                        reference_id=farmer_id)
        session.commit()
        return _to_row(farmer, session)


def activate_farmer(farmer_id: int) -> FarmerRow:
    """Re-activate a previously deactivated farmer."""
    with get_session() as session:
        farmer = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        if not farmer:
            raise FarmerError(_t("farmer_not_found"))
        farmer.status = "ACTIVE"
        write_audit_log(session, "FARMER_ACTIVATED",
                        f"Farmer activated: {farmer.farmer_code} — {farmer.name_english}",
                        reference_id=farmer_id)
        session.commit()
        return _to_row(farmer, session)
