"""
Dashboard page — home screen shown after login.
Phase 1: placeholder stat cards and quick action buttons.
Real data will be wired in as each module is built.
"""

from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from constants import (
    COLOR_ACCENT, COLOR_SIDEBAR, COLOR_TEXT_SECONDARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_CARD, COLOR_BORDER, COLOR_TEXT_PRIMARY,
)


class StatCard(QFrame):
    """A single summary stat card shown on the dashboard."""

    def __init__(self, icon: str, label: str, value: str,
                 accent: str = COLOR_ACCENT, parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        # Top row: icon + label
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("stat_card_icon")
        icon_lbl.setFixedWidth(32)
        lbl = QLabel(label.upper())
        lbl.setObjectName("stat_card_label")
        lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 8pt; font-weight: bold; letter-spacing: 1px;")
        top.addWidget(icon_lbl)
        top.addWidget(lbl, 1)
        layout.addLayout(top)

        # Value
        self._value_lbl = QLabel(value)
        self._value_lbl.setObjectName("stat_card_value")
        self._value_lbl.setStyleSheet(f"font-size: 22pt; font-weight: bold; color: {accent};")
        layout.addWidget(self._value_lbl)

    def set_value(self, v: str):
        self._value_lbl.setText(v)


class QuickActionButton(QPushButton):
    """Large quick-action button for the dashboard."""

    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("quick_btn")
        self.setText(f"{icon}\n{label}")
        self.setMinimumSize(120, 80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setCursor(Qt.PointingHandCursor)


class DashboardPage(QWidget):
    """Main dashboard / home page."""

    # Signal mapping for quick action buttons: (label, page_key)
    QUICK_ACTIONS = [
        ("🥛", "Milk Collection",      "milk_collection"),
        ("📦", "Product Transaction",  "product_transaction"),
        ("💳", "Record Payment",       "payments"),
        ("🏪", "Inventory",            "inventory"),
        ("📊", "Reports",              "reports"),
        ("👨‍🌾", "Farmers",             "farmers"),
        ("⚙️", "Settings",            "settings"),
    ]

    def __init__(self, navigate_callback=None, parent=None):
        super().__init__(parent)
        self._navigate = navigate_callback
        self._setup_ui()
        self._refresh_data()

        # Auto-refresh every 60 seconds
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_data)
        self._timer.start(60_000)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # ── Header ────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Dashboard")
        page_title.setObjectName("page_title")
        page_title.setStyleSheet("font-size: 20pt; font-weight: bold;")

        self._date_lbl = QLabel()
        self._date_lbl.setObjectName("page_subtitle")
        self._update_date_label()

        title_col.addWidget(page_title)
        title_col.addWidget(self._date_lbl)
        header.addLayout(title_col, 1)

        # Backup status badge
        self._backup_badge = QLabel("✓ Backup OK")
        self._backup_badge.setStyleSheet(
            f"background:{COLOR_SUCCESS}; color:white; border-radius:4px; "
            f"padding:4px 10px; font-size:8pt; font-weight:bold;"
        )
        header.addWidget(self._backup_badge)
        root.addLayout(header)

        # ── Stat cards ────────────────────────────────────────────
        cards_grid = QGridLayout()
        cards_grid.setSpacing(14)

        self._card_milk_qty   = StatCard("🥛", "Today's Milk",         "— L",    COLOR_ACCENT)
        self._card_collection = StatCard("💰", "Today's Collection",   "NPR —",  COLOR_SIDEBAR)
        self._card_outstanding= StatCard("⚖️", "Outstanding Balance",  "NPR —",  COLOR_DANGER)
        self._card_inventory  = StatCard("🏪", "Products in Stock",    "—",      "#2563EB")
        self._card_txn_today  = StatCard("📋", "Transactions Today",   "—",      COLOR_SUCCESS)

        cards_grid.addWidget(self._card_milk_qty,    0, 0)
        cards_grid.addWidget(self._card_collection,  0, 1)
        cards_grid.addWidget(self._card_outstanding, 0, 2)
        cards_grid.addWidget(self._card_inventory,   0, 3)
        cards_grid.addWidget(self._card_txn_today,   0, 4)

        for col in range(5):
            cards_grid.setColumnStretch(col, 1)

        root.addLayout(cards_grid)

        # ── Quick actions ─────────────────────────────────────────
        qa_label = QLabel("Quick Actions")
        qa_label.setStyleSheet(f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(qa_label)

        qa_row = QHBoxLayout()
        qa_row.setSpacing(10)
        for icon, label, page_key in self.QUICK_ACTIONS:
            btn = QuickActionButton(icon, label)
            if self._navigate:
                btn.clicked.connect(lambda _, k=page_key: self._navigate(k))
            qa_row.addWidget(btn)
        root.addLayout(qa_row)

        # ── Recent activity ───────────────────────────────────────
        recent_label = QLabel("Recent Transactions")
        recent_label.setStyleSheet(f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(recent_label)

        self._recent_table = QTableWidget(0, 5)
        self._recent_table.setHorizontalHeaderLabels(
            ["Date", "Farmer", "Product", "Quantity", "Amount (NPR)"]
        )
        self._recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._recent_table.setAlternatingRowColors(True)
        self._recent_table.verticalHeader().setVisible(False)
        self._recent_table.setMaximumHeight(220)
        root.addWidget(self._recent_table)

        root.addStretch()

    def _update_date_label(self):
        today = date.today()
        self._date_lbl.setText(
            f"{today.strftime('%A, %d %B %Y')}"
        )

    def _refresh_data(self):
        """Pull live stats from the database."""
        self._update_date_label()
        try:
            from database.database import get_session
            from database.models import Transaction, Payment, Product, InventoryMovement
            from sqlalchemy import func, and_
            import datetime

            today = date.today()
            session = get_session()

            # Today's milk quantity
            milk_product = session.query(Product).filter_by(is_milk=1).first()
            milk_qty = 0.0
            if milk_product:
                result = session.query(func.sum(Transaction.quantity)).filter(
                    and_(
                        Transaction.transaction_date == today,
                        Transaction.product_id == milk_product.product_id,
                        Transaction.status == "ACTIVE",
                    )
                ).scalar()
                milk_qty = float(result or 0)

            # Today's collection amount
            today_amounts = session.query(
                Transaction.quantity, Transaction.rate
            ).filter(
                and_(Transaction.transaction_date == today, Transaction.status == "ACTIVE")
            ).all()
            today_total = sum(float(q) * float(r) for q, r in today_amounts)

            # Outstanding balance
            all_active = session.query(Transaction.quantity, Transaction.rate).filter_by(
                status="ACTIVE"
            ).all()
            total_owed = sum(float(q) * float(r) for q, r in all_active)
            total_paid_row = session.query(func.sum(Payment.amount_paid)).scalar()
            total_paid = float(total_paid_row or 0)
            outstanding = total_owed - total_paid

            # Products in stock count
            non_milk = session.query(Product).filter_by(is_milk=0).all()
            in_stock = 0
            for p in non_milk:
                stock_in = session.query(func.sum(InventoryMovement.quantity)).filter_by(
                    product_id=p.product_id, movement_type="IN"
                ).scalar() or 0
                stock_out = session.query(func.sum(InventoryMovement.quantity)).filter_by(
                    product_id=p.product_id, movement_type="OUT"
                ).scalar() or 0
                if float(stock_in) - float(stock_out) > 0:
                    in_stock += 1

            # Transactions today
            txn_today = session.query(func.count(Transaction.transaction_id)).filter(
                and_(Transaction.transaction_date == today, Transaction.status == "ACTIVE")
            ).scalar() or 0

            # Update cards
            self._card_milk_qty.set_value(f"{milk_qty:,.1f} L")
            self._card_collection.set_value(f"NPR {today_total:,.0f}")
            self._card_outstanding.set_value(f"NPR {outstanding:,.0f}")
            self._card_inventory.set_value(str(in_stock))
            self._card_txn_today.set_value(str(txn_today))

            # Recent transactions (last 10)
            recent = session.query(Transaction).filter_by(
                status="ACTIVE"
            ).order_by(Transaction.transaction_id.desc()).limit(10).all()

            self._recent_table.setRowCount(len(recent))
            for row, txn in enumerate(recent):
                self._recent_table.setItem(row, 0, QTableWidgetItem(str(txn.transaction_date)))
                self._recent_table.setItem(row, 1, QTableWidgetItem(
                    txn.farmer.display_name if txn.farmer else "—"
                ))
                self._recent_table.setItem(row, 2, QTableWidgetItem(
                    txn.product.display_name if txn.product else "—"
                ))
                self._recent_table.setItem(row, 3, QTableWidgetItem(
                    f"{float(txn.quantity):,.2f} {txn.product.unit if txn.product else ''}"
                ))
                self._recent_table.setItem(row, 4, QTableWidgetItem(
                    f"{txn.amount:,.2f}"
                ))

            session.close()

        except Exception:
            # Database not yet populated — show dashes (Phase 1 is fine)
            pass
