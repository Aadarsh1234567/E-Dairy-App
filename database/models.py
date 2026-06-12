"""
SQLAlchemy ORM models for Santosh E-Dairy.
All 11 tables as per Database Design v2.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date,
    DateTime, ForeignKey, UniqueConstraint, CheckConstraint, event
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ─────────────────────────────────────────────────────────────
# TABLE 1: farmers
# ─────────────────────────────────────────────────────────────
class Farmer(Base):
    __tablename__ = "farmers"

    farmer_id    = Column(Integer, primary_key=True, autoincrement=True)
    farmer_code  = Column(String(50),  nullable=False, unique=True)   # user-facing ID e.g. "101"
    name_english = Column(String(200), nullable=False)
    name_nepali  = Column(String(200), nullable=True)
    phone        = Column(String(20),  nullable=True)
    address      = Column(String(300), nullable=True)
    created_at   = Column(DateTime,    default=datetime.utcnow)
    status       = Column(String(10),  nullable=False, default="ACTIVE")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="ck_farmer_status"),
    )

    transactions = relationship("Transaction", back_populates="farmer")
    payments     = relationship("Payment",     back_populates="farmer")

    @property
    def display_name(self):
        """Return Nepali name if available, else English."""
        return self.name_nepali if self.name_nepali else self.name_english


# ─────────────────────────────────────────────────────────────
# TABLE 2: products
# ─────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    product_id           = Column(Integer,      primary_key=True, autoincrement=True)
    product_name_english = Column(String(100),  nullable=False, unique=True)
    product_name_nepali  = Column(String(100),  nullable=True)
    unit                 = Column(String(10),   nullable=False)          # LITER or KG
    is_milk              = Column(Integer,      nullable=False, default=0)  # 1=Milk 0=Other
    default_rate         = Column(Numeric(10,2),nullable=True)
    created_at           = Column(DateTime,     default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("unit IN ('LITER', 'KG')",    name="ck_product_unit"),
        CheckConstraint("is_milk IN (0, 1)",           name="ck_product_is_milk"),
        CheckConstraint("default_rate IS NULL OR default_rate >= 0", name="ck_product_default_rate"),
    )

    transactions        = relationship("Transaction",      back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")

    @property
    def display_name(self):
        return self.product_name_nepali if self.product_name_nepali else self.product_name_english


# ─────────────────────────────────────────────────────────────
# TABLE 3: transactions
# ─────────────────────────────────────────────────────────────
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id      = Column(Integer,      primary_key=True, autoincrement=True)
    transaction_date    = Column(Date,         nullable=False)
    farmer_id           = Column(Integer,      ForeignKey("farmers.farmer_id"), nullable=False)
    product_id          = Column(Integer,      ForeignKey("products.product_id"), nullable=False)
    quantity            = Column(Numeric(10,2),nullable=False)
    rate                = Column(Numeric(10,2),nullable=False)
    # amount is NOT stored — always computed as quantity * rate
    status              = Column(String(10),   nullable=False, default="ACTIVE")
    cancellation_reason = Column(Text,         nullable=True)
    cancelled_at        = Column(DateTime,     nullable=True)
    created_at          = Column(DateTime,     default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'CANCELLED')", name="ck_transaction_status"),
        CheckConstraint("quantity > 0",                      name="ck_transaction_quantity"),
        CheckConstraint("rate > 0",                          name="ck_transaction_rate"),
    )

    farmer      = relationship("Farmer",      back_populates="transactions")
    product     = relationship("Product",     back_populates="transactions")
    milk_detail = relationship("MilkDetail",  back_populates="transaction", uselist=False)

    @property
    def amount(self):
        """Computed amount — never stored."""
        return float(self.quantity) * float(self.rate)


# ─────────────────────────────────────────────────────────────
# TABLE 4: milk_details
# ─────────────────────────────────────────────────────────────
class MilkDetail(Base):
    __tablename__ = "milk_details"

    milk_detail_id   = Column(Integer,      primary_key=True, autoincrement=True)
    transaction_id   = Column(Integer,      ForeignKey("transactions.transaction_id"), nullable=False, unique=True)
    # Denormalized for DB-level UNIQUE constraint (DB-05)
    transaction_date = Column(Date,         nullable=False)
    farmer_id        = Column(Integer,      nullable=False)
    session          = Column(String(10),   nullable=False)   # MORNING or EVENING
    milk_type        = Column(String(10),   nullable=False)   # COW or BUFFALO
    fat              = Column(Numeric(5,2), nullable=False)
    snf              = Column(Numeric(5,2), nullable=False)
    formula_used     = Column(Text,         nullable=False)   # snapshot of formula at save time

    __table_args__ = (
        UniqueConstraint("transaction_date", "farmer_id", "session", name="uq_milk_duplicate"),
        CheckConstraint("session IN ('MORNING', 'EVENING')",     name="ck_milk_session"),
        CheckConstraint("milk_type IN ('COW', 'BUFFALO')",       name="ck_milk_type"),
        CheckConstraint("fat >= 0",                              name="ck_milk_fat"),
        CheckConstraint("snf >= 0",                              name="ck_milk_snf"),
    )

    transaction = relationship("Transaction", back_populates="milk_detail")


# ─────────────────────────────────────────────────────────────
# TABLE 5: payments
# ─────────────────────────────────────────────────────────────
class Payment(Base):
    __tablename__ = "payments"

    payment_id         = Column(Integer,       primary_key=True, autoincrement=True)
    farmer_id          = Column(Integer,       ForeignKey("farmers.farmer_id"), nullable=False)
    payment_date       = Column(Date,          nullable=False)
    amount_paid        = Column(Numeric(10,2), nullable=False)
    receipt_number     = Column(String(20),    nullable=True, unique=True)  # REC-YYYY-NNNN
    remarks            = Column(Text,          nullable=True)
    receipt_generated  = Column(Integer,       nullable=False, default=0)   # 0=No 1=Yes
    created_at         = Column(DateTime,      default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("amount_paid > 0", name="ck_payment_amount"),
        CheckConstraint("receipt_generated IN (0, 1)", name="ck_payment_receipt_generated"),
    )

    farmer = relationship("Farmer", back_populates="payments")


# ─────────────────────────────────────────────────────────────
# TABLE 6: inventory_movements
# ─────────────────────────────────────────────────────────────
class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    movement_id   = Column(Integer,       primary_key=True, autoincrement=True)
    movement_date = Column(Date,          nullable=False)
    product_id    = Column(Integer,       ForeignKey("products.product_id"), nullable=False)
    movement_type = Column(String(3),     nullable=False)    # IN or OUT
    quantity      = Column(Numeric(10,2), nullable=False)
    notes         = Column(Text,          nullable=True)
    created_at    = Column(DateTime,      default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("movement_type IN ('IN', 'OUT')", name="ck_movement_type"),
        CheckConstraint("quantity > 0",                   name="ck_movement_quantity"),
    )

    product = relationship("Product", back_populates="inventory_movements")


# ─────────────────────────────────────────────────────────────
# TABLE 7: settings
# ─────────────────────────────────────────────────────────────
class Setting(Base):
    __tablename__ = "settings"

    setting_key   = Column(String(100), primary_key=True)
    setting_value = Column(Text,        nullable=True)


# ─────────────────────────────────────────────────────────────
# TABLE 8: pricing_formula_history
# ─────────────────────────────────────────────────────────────
class PricingFormulaHistory(Base):
    __tablename__ = "pricing_formula_history"

    formula_id     = Column(Integer,  primary_key=True, autoincrement=True)
    formula        = Column(Text,     nullable=False)
    effective_from = Column(Date,     nullable=False)
    effective_to   = Column(Date,     nullable=True)   # NULL = currently active
    created_at     = Column(DateTime, default=datetime.utcnow)
    notes          = Column(Text,     nullable=True)


# ─────────────────────────────────────────────────────────────
# TABLE 9: audit_logs
# ─────────────────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id       = Column(Integer,  primary_key=True, autoincrement=True)
    action_date  = Column(DateTime, nullable=False, default=datetime.utcnow)
    action_type  = Column(String(50), nullable=False)
    reference_id = Column(Integer,  nullable=True)
    description  = Column(Text,     nullable=True)
    prev_hash    = Column(String(64), nullable=True)  # SHA-256 chain for tamper detection


# ─────────────────────────────────────────────────────────────
# TABLE 10: backups
# ─────────────────────────────────────────────────────────────
class Backup(Base):
    __tablename__ = "backups"

    backup_id   = Column(Integer,   primary_key=True, autoincrement=True)
    backup_date = Column(DateTime,  nullable=False, default=datetime.utcnow)
    backup_path = Column(Text,      nullable=False)
    backup_type = Column(String(10),nullable=False)   # AUTO or MANUAL
    verified    = Column(Integer,   nullable=False, default=0)  # 1=passed integrity_check
    file_size_kb= Column(Integer,   nullable=True)

    __table_args__ = (
        CheckConstraint("backup_type IN ('AUTO', 'MANUAL')", name="ck_backup_type"),
        CheckConstraint("verified IN (0, 1)",                name="ck_backup_verified"),
    )


# ─────────────────────────────────────────────────────────────
# TABLE 11: schema_versions
# ─────────────────────────────────────────────────────────────
class SchemaVersion(Base):
    __tablename__ = "schema_versions"

    version_number = Column(Integer,   primary_key=True)
    applied_at     = Column(DateTime,  nullable=False, default=datetime.utcnow)
    description    = Column(Text,      nullable=True)
