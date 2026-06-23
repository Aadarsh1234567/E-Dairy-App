"""
Milk collection service — Phase 6.
The most critical module in the system.

Rules enforced:
  - Farmer must exist and be ACTIVE
  - Duplicate prevention: same farmer + date + session blocked (DB UNIQUE + app check)
  - Quantity, FAT, SNF validated
  - Rate calculated via pricing_service (simpleeval, never raw eval)
  - formula_used snapshot stored with every transaction (audit trail, DB-02)
  - amount is NEVER stored — always computed as quantity * rate
  - Cancellation requires a mandatory reason (BL-03)
  - Cancelled transactions excluded from all balance/report calculations (AC-02)
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from sqlalchemy.exc import IntegrityError
from database.database import get_session, write_audit_log
from database.models import Farmer, Product, Transaction, MilkDetail
from services.pricing_service import calculate_rate, get_active_formula, PricingError


# ── Data classes ───────────────────────────────────────────────────────────────
@dataclass
class FarmerLookup:
    farmer_id:    int
    farmer_code:  str
    name_english: str
    name_nepali:  str
    phone:        str
    address:      str
    status:       str

    @property
    def display_name(self) -> str:
        return self.name_nepali if self.name_nepali else self.name_english


@dataclass
class MilkEntryRow:
    transaction_id:      int
    transaction_date:    date
    farmer_id:            int
    farmer_code:           str
    farmer_name:           str
    session:              str
    milk_type:             str
    quantity:              float
    fat:                   float
    snf:                   float
    rate:                  float
    amount:                float
    status:                str
    cancellation_reason:    str


class MilkError(Exception):
    pass


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


# ── Farmer lookup (for the collection screen) ──────────────────────────────────

def lookup_farmer(farmer_code: str) -> FarmerLookup:
    """
    Look up a farmer by code for the milk collection screen.
    Raises MilkError if not found or inactive.
    """
    farmer_code = farmer_code.strip()
    if not farmer_code:
        raise MilkError(_t("farmer_not_found"))

    with get_session() as session:
        f = session.query(Farmer).filter_by(farmer_code=farmer_code).first()
        if not f:
            raise MilkError(_t("farmer_not_found"))
        if f.status != "ACTIVE":
            raise MilkError(_t("farmer_inactive"))

        return FarmerLookup(
            farmer_id    = f.farmer_id,
            farmer_code  = f.farmer_code,
            name_english = f.name_english,
            name_nepali  = f.name_nepali or "",
            phone        = f.phone or "",
            address      = f.address or "",
            status       = f.status,
        )


# ── Duplicate check (used by UI for live feedback before save) ─────────────────

def check_duplicate(farmer_id: int, transaction_date: date, session_value: str) -> bool:
    """Return True if a milk entry already exists for this farmer/date/session."""
    with get_session() as session:
        existing = session.query(MilkDetail).filter_by(
            farmer_id=farmer_id,
            transaction_date=transaction_date,
            session=session_value,
        ).first()
        return existing is not None


# ── Rate preview (live calculation as operator types FAT/SNF) ──────────────────

def preview_rate(fat: float, snf: float) -> float:
    """Calculate the rate for given FAT/SNF using the active formula. For UI preview."""
    return calculate_rate(fat, snf)


# ── Save milk collection ────────────────────────────────────────────────────────

def save_milk_collection(
    farmer_code:      str,
    transaction_date: date,
    session_value:    str,     # MORNING or EVENING
    milk_type:        str,     # COW or BUFFALO
    quantity:         float,
    fat:               float,
    snf:               float,
) -> MilkEntryRow:
    """
    Save a new milk collection transaction.
    Raises MilkError on any validation failure.
    """
    # ── Validation ──────────────────────────────────────────────
    if quantity is None or quantity <= 0:
        raise MilkError(_t("qty_invalid"))
    if fat is None or fat < 0:
        raise MilkError(_t("fat_invalid"))
    if snf is None or snf < 0:
        raise MilkError(_t("snf_invalid"))
    if session_value not in ("MORNING", "EVENING"):
        raise MilkError(_t("farmer_not_found"))  # defensive — UI should never allow this
    if milk_type not in ("COW", "BUFFALO"):
        raise MilkError(_t("farmer_not_found"))  # defensive

    with get_session() as session:
        # Re-verify farmer (fresh, inside transaction)
        farmer = session.query(Farmer).filter_by(farmer_code=farmer_code.strip()).first()
        if not farmer:
            raise MilkError(_t("farmer_not_found"))
        if farmer.status != "ACTIVE":
            raise MilkError(_t("farmer_inactive"))

        # Application-level duplicate check (fast feedback before DB constraint)
        existing = session.query(MilkDetail).filter_by(
            farmer_id=farmer.farmer_id,
            transaction_date=transaction_date,
            session=session_value,
        ).first()
        if existing:
            raise MilkError(_t("duplicate_entry"))

        # Milk product lookup
        milk_product = session.query(Product).filter_by(is_milk=1).first()
        if not milk_product:
            raise MilkError(_t("farmer_not_found"))  # defensive — should never happen

        # Calculate rate using active formula (simpleeval — safe)
        try:
            formula = get_active_formula()
            rate = calculate_rate(fat, snf, formula=formula)
        except PricingError as e:
            raise MilkError(str(e))

        # Create transaction (amount is NEVER stored — computed property)
        txn = Transaction(
            transaction_date = transaction_date,
            farmer_id        = farmer.farmer_id,
            product_id       = milk_product.product_id,
            quantity         = quantity,
            rate             = rate,
            status           = "ACTIVE",
            created_at       = datetime.utcnow(),
        )
        session.add(txn)
        session.flush()   # get transaction_id

        # Create milk detail with formula_used snapshot (audit trail — DB-02)
        detail = MilkDetail(
            transaction_id   = txn.transaction_id,
            transaction_date = transaction_date,
            farmer_id        = farmer.farmer_id,
            session          = session_value,
            milk_type        = milk_type,
            fat              = fat,
            snf              = snf,
            formula_used     = formula,
        )
        session.add(detail)

        try:
            session.flush()
        except IntegrityError:
            # DB-level UNIQUE constraint caught a race condition
            session.rollback()
            raise MilkError(_t("duplicate_entry"))

        write_audit_log(session, "TRANSACTION_CREATED",
                        f"Milk collection: {farmer.farmer_code} — "
                        f"{session_value} {milk_type} {quantity}L "
                        f"FAT={fat} SNF={snf} Rate={rate}",
                        reference_id=txn.transaction_id)
        session.commit()

        return MilkEntryRow(
            transaction_id      = txn.transaction_id,
            transaction_date    = txn.transaction_date,
            farmer_id           = farmer.farmer_id,
            farmer_code         = farmer.farmer_code,
            farmer_name         = farmer.display_name,
            session              = session_value,
            milk_type            = milk_type,
            quantity              = float(quantity),
            fat                   = float(fat),
            snf                   = float(snf),
            rate                  = rate,
            amount                = round(float(quantity) * rate, 2),
            status                = "ACTIVE",
            cancellation_reason   = "",
        )


# ── Cancel milk transaction ─────────────────────────────────────────────────────

def cancel_milk_transaction(transaction_id: int, reason: str) -> None:
    """
    Cancel a milk transaction. Reason is mandatory (BL-03).
    Cancelled transactions remain visible but excluded from all balance calcs.
    """
    reason = reason.strip()
    if not reason:
        raise MilkError(_t("reason_required"))

    with get_session() as session:
        txn = session.query(Transaction).filter_by(transaction_id=transaction_id).first()
        if not txn:
            raise MilkError(_t("farmer_not_found"))
        if txn.status == "CANCELLED":
            return   # already cancelled, idempotent

        txn.status              = "CANCELLED"
        txn.cancellation_reason = reason
        txn.cancelled_at        = datetime.utcnow()

        write_audit_log(session, "TRANSACTION_CANCELLED",
                        f"Milk transaction #{transaction_id} cancelled. Reason: {reason}",
                        reference_id=transaction_id)
        session.commit()


# ── Recent entries (for the collection screen activity panel) ──────────────────

def get_recent_milk_entries(limit: int = 10) -> list[MilkEntryRow]:
    """Return the most recent milk transactions (both ACTIVE and CANCELLED)."""
    with get_session() as session:
        rows = (
            session.query(Transaction, MilkDetail)
            .join(MilkDetail, MilkDetail.transaction_id == Transaction.transaction_id)
            .order_by(Transaction.transaction_id.desc())
            .limit(limit)
            .all()
        )
        result = []
        for txn, detail in rows:
            farmer = session.query(Farmer).filter_by(farmer_id=txn.farmer_id).first()
            result.append(MilkEntryRow(
                transaction_id      = txn.transaction_id,
                transaction_date    = txn.transaction_date,
                farmer_id           = txn.farmer_id,
                farmer_code         = farmer.farmer_code if farmer else "—",
                farmer_name         = farmer.display_name if farmer else "—",
                session              = detail.session,
                milk_type             = detail.milk_type,
                quantity               = float(txn.quantity),
                fat                     = float(detail.fat),
                snf                     = float(detail.snf),
                rate                    = float(txn.rate),
                amount                  = round(float(txn.quantity) * float(txn.rate), 2),
                status                  = txn.status,
                cancellation_reason     = txn.cancellation_reason or "",
            ))
        return result
