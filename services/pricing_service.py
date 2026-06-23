"""
Pricing service — Phase 6 dependency.
Handles safe evaluation of the milk pricing formula and formula history.

Rules enforced (per SRS Module 6 / DB-07):
  - Formula evaluated using simpleeval (NEVER Python eval())
  - Formula validated at save time with test inputs
  - Every transaction stores the exact formula_used string (audit trail)
  - Changing the formula never alters historical transaction rates
"""

from datetime import date, datetime
from simpleeval import simple_eval, InvalidExpression, NameNotDefined
from database.database import get_session, write_audit_log
from database.models import PricingFormulaHistory


class PricingError(Exception):
    pass


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


def get_active_formula() -> str:
    """Return the currently active pricing formula string."""
    with get_session() as session:
        active = session.query(PricingFormulaHistory).filter_by(
            effective_to=None
        ).order_by(PricingFormulaHistory.formula_id.desc()).first()
        if active:
            return active.formula
        return "(fat*8)+(snf*4)"   # fallback default


def calculate_rate(fat: float, snf: float, formula: str | None = None) -> float:
    """
    Calculate the milk rate using the given (or currently active) formula.
    Uses simpleeval — NEVER Python eval().

    Raises PricingError if the formula is invalid or produces a non-numeric
    or negative result.
    """
    if formula is None:
        formula = get_active_formula()

    try:
        result = simple_eval(formula, names={"fat": float(fat), "snf": float(snf)})
    except (InvalidExpression, NameNotDefined, SyntaxError, ZeroDivisionError, Exception) as e:
        raise PricingError(_t("formula_invalid"))

    try:
        result = float(result)
    except (TypeError, ValueError):
        raise PricingError(_t("formula_invalid"))

    if result < 0:
        raise PricingError(_t("formula_invalid"))

    return round(result, 2)


def validate_formula(formula: str) -> bool:
    """
    Validate a formula string by evaluating it with test inputs.
    Returns True if valid, raises PricingError if not.
    """
    formula = formula.strip()
    if not formula:
        raise PricingError(_t("formula_invalid"))

    try:
        result = simple_eval(formula, names={"fat": 4.0, "snf": 8.0})
        result = float(result)
        if result <= 0:
            raise PricingError(_t("formula_invalid"))
    except PricingError:
        raise
    except Exception:
        raise PricingError(_t("formula_invalid"))

    return True


def set_new_formula(formula: str, notes: str = "") -> None:
    """
    Set a new active pricing formula.
    Closes the current active record and opens a new one.
    Raises PricingError if formula is invalid.
    """
    formula = formula.strip()
    validate_formula(formula)   # raises if invalid

    today = date.today()
    with get_session() as session:
        current = session.query(PricingFormulaHistory).filter_by(
            effective_to=None
        ).order_by(PricingFormulaHistory.formula_id.desc()).first()

        if current and current.formula == formula:
            return   # no change

        if current:
            current.effective_to = today

        new_record = PricingFormulaHistory(
            formula=formula,
            effective_from=today,
            effective_to=None,
            notes=notes,
            created_at=datetime.utcnow(),
        )
        session.add(new_record)

        write_audit_log(session, "FORMULA_CHANGED",
                        f"Pricing formula changed to: {formula}")
        session.commit()
