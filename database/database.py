"""
Database connection, initialization, seeding, and index creation.
Handles first-run setup and schema version tracking.
"""

import os
import hashlib
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session

from database.models import (
    Base, Farmer, Product, Setting, PricingFormulaHistory,
    SchemaVersion, AuditLog
)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
CURRENT_SCHEMA_VERSION = 1
APP_VERSION = "1.0.0"
DB_FILENAME = "dairy_management.db"

DEFAULT_FORMULA = "(fat*8)+(snf*4)"

DEFAULT_SETTINGS = {
    "organization_name_english": "Santosh Dairy Cooperative",
    "organization_name_nepali":  "सन्तोष डेरी सहकारी",
    "organization_address_english": "",
    "organization_address_nepali":  "",
    "organization_phone":        "",
    "organization_logo":         "",
    "backup_path":               "",          # resolved at runtime
    "default_language":          "NE",
    "app_version":               APP_VERSION,
    "idle_lock_minutes":         "15",
    "auto_backup_hour":          "18",
}

DEFAULT_PRODUCTS = [
    # (name_english, name_nepali, unit, is_milk, default_rate)
    # Only Milk is seeded — the dairy operates exclusively with milk collection.
    ("Milk",   "दूध",    "LITER", 1, None),
]


# ─────────────────────────────────────────────────────────────
# Engine / Session factory
# ─────────────────────────────────────────────────────────────
_engine = None
_SessionFactory = None


def get_db_path() -> Path:
    """Resolve database path: next to the executable / project root."""
    # When running from source, place DB in project root
    project_root = Path(__file__).resolve().parent.parent
    return project_root / DB_FILENAME


def init_engine(db_path: Path | None = None) -> None:
    """Create the SQLAlchemy engine and session factory."""
    global _engine, _SessionFactory
    if db_path is None:
        db_path = get_db_path()

    db_url = f"sqlite:///{db_path}"
    _engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Enable foreign keys for every connection
    from sqlalchemy import event as sa_event
    @sa_event.listens_for(_engine, "connect")
    def set_fk(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")

    _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)


def get_session() -> Session:
    """Return a new database session."""
    if _SessionFactory is None:
        raise RuntimeError("Database not initialised. Call init_engine() first.")
    return _SessionFactory()


# ─────────────────────────────────────────────────────────────
# Initialization
# ─────────────────────────────────────────────────────────────
def initialize_database(db_path: Path | None = None) -> dict:
    """
    Full database bootstrap sequence.
    Returns a status dict: {is_new_db, schema_version, errors}.
    """
    if db_path is None:
        db_path = get_db_path()

    is_new = not db_path.exists()
    init_engine(db_path)

    errors = []

    try:
        # Create all tables (safe to call on existing DB)
        Base.metadata.create_all(_engine)

        # Create indexes
        _create_indexes()

        # Schema version check / migration
        with get_session() as session:
            _run_migrations(session, is_new)

        # Seed on first run
        if is_new:
            with get_session() as session:
                _seed_default_data(session, db_path)
                session.commit()

        # Resolve and save backup path if not set
        with get_session() as session:
            _ensure_backup_path(session)
            session.commit()

    except Exception as e:
        errors.append(str(e))

    return {
        "is_new_db": is_new,
        "db_path": str(db_path),
        "schema_version": CURRENT_SCHEMA_VERSION,
        "errors": errors,
    }


def _create_indexes():
    """Create all required indexes explicitly."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_farmer_code        ON farmers(farmer_code)",
        "CREATE INDEX IF NOT EXISTS idx_farmer_name_en     ON farmers(name_english)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_date   ON transactions(transaction_date)",
        "CREATE INDEX IF NOT EXISTS idx_farmer_transaction ON transactions(farmer_id)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_status ON transactions(status)",
        "CREATE INDEX IF NOT EXISTS idx_payment_farmer     ON payments(farmer_id)",
        "CREATE INDEX IF NOT EXISTS idx_inventory_product  ON inventory_movements(product_id)",
        # The UNIQUE constraint on milk_details already creates this index,
        # but we declare it explicitly for clarity
        "CREATE INDEX IF NOT EXISTS idx_milk_dup ON milk_details(transaction_date, farmer_id, session)",
    ]
    with _engine.connect() as conn:
        for sql in indexes:
            conn.execute(text(sql))
        conn.commit()


def _run_migrations(session: Session, is_new: bool):
    """Check schema version and apply any pending migrations."""
    if is_new:
        # Brand new DB — record initial version
        session.add(SchemaVersion(
            version_number=CURRENT_SCHEMA_VERSION,
            applied_at=datetime.utcnow(),
            description="Initial schema — Version 1 baseline including bilingual support",
        ))
        session.commit()
        return

    # Existing DB — check version
    latest = (
        session.query(SchemaVersion)
        .order_by(SchemaVersion.version_number.desc())
        .first()
    )
    db_version = latest.version_number if latest else 0

    if db_version < CURRENT_SCHEMA_VERSION:
        # Future migrations go here, keyed by version number
        migrations = {
            # 2: _migrate_v1_to_v2,
        }
        for v in range(db_version + 1, CURRENT_SCHEMA_VERSION + 1):
            if v in migrations:
                migrations[v](session)
            session.add(SchemaVersion(
                version_number=v,
                applied_at=datetime.utcnow(),
                description=f"Migration to version {v}",
            ))
        session.commit()

    elif db_version > CURRENT_SCHEMA_VERSION:
        raise RuntimeError(
            f"Database schema version ({db_version}) is newer than "
            f"the application ({CURRENT_SCHEMA_VERSION}). "
            f"Please update the software."
        )


def _seed_default_data(session: Session, db_path: Path):
    """Seed settings, products, and initial pricing formula."""
    # Settings
    for key, value in DEFAULT_SETTINGS.items():
        session.add(Setting(setting_key=key, setting_value=str(value)))

    # Products
    for name_en, name_np, unit, is_milk, default_rate in DEFAULT_PRODUCTS:
        session.add(Product(
            product_name_english=name_en,
            product_name_nepali=name_np,
            unit=unit,
            is_milk=is_milk,
            default_rate=default_rate,
        ))

    # Initial pricing formula
    session.add(PricingFormulaHistory(
        formula=DEFAULT_FORMULA,
        effective_from=date.today(),
        effective_to=None,
        notes="Default formula at installation",
    ))

    # Genesis audit log entry
    session.add(AuditLog(
        action_type="SYSTEM_INITIALIZED",
        reference_id=None,
        description="Database initialized — Santosh E-Dairy v1.0.0",
        prev_hash="GENESIS",
    ))


def _ensure_backup_path(session: Session):
    """Set backup path if not already configured."""
    row = session.query(Setting).filter_by(setting_key="backup_path").first()
    if row and row.setting_value:
        return  # already set

    # Try D:\DairyBackup first, fall back to Documents
    if os.name == "nt":
        d_drive = Path("D:\\DairyBackup")
        docs = Path.home() / "Documents" / "DairyBackup"
        backup_path = str(d_drive) if Path("D:\\").exists() else str(docs)
    else:
        # Linux/Mac: use project-local backups/ for development
        backup_path = str(Path(__file__).resolve().parent.parent / "backups")

    if row:
        row.setting_value = backup_path
    else:
        session.add(Setting(setting_key="backup_path", setting_value=backup_path))


# ─────────────────────────────────────────────────────────────
# Helpers for other modules
# ─────────────────────────────────────────────────────────────
def get_setting(key: str, default: str = "") -> str:
    """Quick single-setting fetch."""
    with get_session() as session:
        row = session.query(Setting).filter_by(setting_key=key).first()
        return row.setting_value if row else default


def set_setting(key: str, value: str) -> None:
    """Quick single-setting update."""
    with get_session() as session:
        row = session.query(Setting).filter_by(setting_key=key).first()
        if row:
            row.setting_value = value
        else:
            session.add(Setting(setting_key=key, setting_value=value))
        session.commit()


def compute_audit_hash(prev_hash: str, action_type: str,
                       description: str, action_date: datetime) -> str:
    """SHA-256 chain hash for audit log tamper detection."""
    payload = f"{prev_hash}|{action_type}|{description}|{action_date.isoformat()}"
    return hashlib.sha256(payload.encode()).hexdigest()


def write_audit_log(session: Session, action_type: str,
                    description: str, reference_id: int | None = None) -> AuditLog:
    """Append a tamper-chained audit log entry."""
    last = (
        session.query(AuditLog)
        .order_by(AuditLog.log_id.desc())
        .first()
    )
    prev_hash = last.prev_hash if last else "GENESIS"
    # compute hash of the *last* entry to chain into this one
    now = datetime.utcnow()
    chain_hash = compute_audit_hash(prev_hash, action_type, description, now)

    entry = AuditLog(
        action_type=action_type,
        reference_id=reference_id,
        description=description,
        prev_hash=chain_hash,
        action_date=now,
    )
    session.add(entry)
    return entry
