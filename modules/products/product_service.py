"""
Product service — Phase 5.
Business logic for product management.

Rules:
  - product_name_english must be unique
  - Milk product unit is fixed as LITER
  - Other products use KG
  - default_rate must be >= 0 (None allowed = not set)
  - Products cannot be deleted (may have transaction history)
  - is_milk flag cannot be changed after creation (data integrity)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from database.database import get_session, write_audit_log
from database.models import Product


# ── Data class returned to UI ──────────────────────────────────────────────────
@dataclass
class ProductRow:
    product_id:           int
    product_name_english: str
    product_name_nepali:  str
    unit:                 str
    is_milk:              int    # 1 = milk, 0 = other
    default_rate:         Optional[float]

    @property
    def display_name(self) -> str:
        return self.product_name_nepali if self.product_name_nepali else self.product_name_english


class ProductError(Exception):
    pass


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


def _to_row(p: Product) -> ProductRow:
    return ProductRow(
        product_id           = p.product_id,
        product_name_english = p.product_name_english,
        product_name_nepali  = p.product_name_nepali or "",
        unit                 = p.unit,
        is_milk              = p.is_milk,
        default_rate         = float(p.default_rate) if p.default_rate is not None else None,
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def get_all_products(milk_only: bool = False, non_milk_only: bool = False) -> list[ProductRow]:
    """Return all products, optionally filtered."""
    with get_session() as session:
        q = session.query(Product)
        if milk_only:
            q = q.filter_by(is_milk=1)
        elif non_milk_only:
            q = q.filter_by(is_milk=0)
        return [_to_row(p) for p in q.order_by(Product.product_id).all()]


def get_product_by_id(product_id: int) -> Optional[ProductRow]:
    with get_session() as session:
        p = session.query(Product).filter_by(product_id=product_id).first()
        return _to_row(p) if p else None


def get_product_by_name(name_english: str) -> Optional[ProductRow]:
    with get_session() as session:
        p = session.query(Product).filter(
            Product.product_name_english.ilike(name_english.strip())
        ).first()
        return _to_row(p) if p else None


def add_product(
    name_english:  str,
    name_nepali:   str = "",
    unit:          str = "KG",
    is_milk:       int = 0,
    default_rate:  Optional[float] = None,
) -> ProductRow:
    """
    Add a new product.
    Raises ProductError on validation failure.
    """
    name_english = name_english.strip()
    name_nepali  = name_nepali.strip()

    if not name_english:
        raise ProductError(_t("product_name_required"))

    # Milk unit is always LITER
    if is_milk == 1:
        unit = "LITER"
    else:
        unit = "KG"

    # Validate default_rate
    if default_rate is not None:
        if default_rate < 0:
            raise ProductError(_t("default_rate_invalid"))
        # Treat 0.0 as None (not set) — zero rate has no meaning for a product
        if default_rate == 0.0:
            default_rate = None

    with get_session() as session:
        # Duplicate name check (case-insensitive)
        existing = session.query(Product).filter(
            Product.product_name_english.ilike(name_english)
        ).first()
        if existing:
            raise ProductError(_t("product_name_exists"))

        product = Product(
            product_name_english = name_english,
            product_name_nepali  = name_nepali or None,
            unit                 = unit,
            is_milk              = is_milk,
            default_rate         = default_rate,
            created_at           = datetime.utcnow(),
        )
        session.add(product)
        session.flush()

        write_audit_log(session, "PRODUCT_CREATED",
                        f"Product added: {name_english}",
                        reference_id=product.product_id)
        session.commit()
        return _to_row(product)


def edit_product(
    product_id:    int,
    name_english:  str,
    name_nepali:   str = "",
    default_rate:  Optional[float] = None,
) -> ProductRow:
    """
    Edit an existing product.
    Note: unit and is_milk cannot be changed (data integrity).
    Raises ProductError on validation failure.
    """
    name_english = name_english.strip()
    name_nepali  = name_nepali.strip()

    if not name_english:
        raise ProductError(_t("product_name_required"))

    if default_rate is not None and default_rate < 0:
        raise ProductError(_t("default_rate_invalid"))
    if default_rate == 0.0:
        default_rate = None

    with get_session() as session:
        product = session.query(Product).filter_by(product_id=product_id).first()
        if not product:
            raise ProductError(_t("farmer_not_found"))  # generic not-found

        # Name uniqueness — allow same name for same product
        existing = session.query(Product).filter(
            Product.product_name_english.ilike(name_english)
        ).first()
        if existing and existing.product_id != product_id:
            raise ProductError(_t("product_name_exists"))

        product.product_name_english = name_english
        product.product_name_nepali  = name_nepali or None
        product.default_rate         = default_rate
        # unit and is_milk intentionally NOT changed

        write_audit_log(session, "PRODUCT_UPDATED",
                        f"Product updated: {name_english}",
                        reference_id=product_id)
        session.commit()
        return _to_row(product)
