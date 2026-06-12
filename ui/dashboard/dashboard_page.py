"""
Dashboard page — bilingual (NE default).
"""
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QTimer
from constants import (
    COLOR_ACCENT, COLOR_SIDEBAR, COLOR_TEXT_SECONDARY, COLOR_SUCCESS,
    COLOR_DANGER, COLOR_CARD, COLOR_BORDER, COLOR_TEXT_PRIMARY,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class StatCard(QFrame):
    def __init__(self, icon, label_key, value, accent=COLOR_ACCENT, parent=None):
        super().__init__(parent)
        self._label_key = label_key
        self.setObjectName("stat_card")
        self.setMinimumHeight(110)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:20pt;")
        icon_lbl.setFixedWidth(32)
        self._lbl = QLabel(_t(label_key).upper())
        self._lbl.setStyleSheet(
            f"color:{COLOR_TEXT_SECONDARY}; font-size:8pt; font-weight:bold; letter-spacing:1px;")
        top.addWidget(icon_lbl)
        top.addWidget(self._lbl, 1)
        lay.addLayout(top)

        self._val = QLabel(value)
        self._val.setStyleSheet(f"font-size:20pt; font-weight:bold; color:{accent};")
        lay.addWidget(self._val)

    def set_value(self, v): self._val.setText(v)
    def refresh_label(self):  self._lbl.setText(_t(self._label_key).upper())


class DashboardPage(QWidget):
    QUICK_ACTIONS = [
        ("🥛", "milk_collection",     "milk_collection"),
        ("📦", "product_transaction", "product_transaction"),
        ("💳", "payments",            "payments"),
        ("🏪", "inventory",           "inventory"),
        ("📊", "reports",             "reports"),
        ("👨‍🌾","farmers",             "farmers"),
        ("⚙️", "settings",           "settings"),
    ]

    def __init__(self, navigate_callback=None, parent=None):
        super().__init__(parent)
        self._navigate = navigate_callback
        self._setup_ui()
        self._refresh_data()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_data)
        self._timer.start(60_000)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        self._title_lbl = QLabel(_t("dashboard_title"))
        self._title_lbl.setStyleSheet("font-size:20pt; font-weight:bold;")
        self._date_lbl = QLabel()
        self._date_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        self._update_date()
        col.addWidget(self._title_lbl)
        col.addWidget(self._date_lbl)
        hdr.addLayout(col, 1)

        self._backup_badge = QLabel(_t("backup_ok"))
        self._backup_badge.setStyleSheet(
            f"background:{COLOR_SUCCESS}; color:white; border-radius:4px;"
            f"padding:4px 10px; font-size:8pt; font-weight:bold;")
        hdr.addWidget(self._backup_badge)
        root.addLayout(hdr)

        # Stat cards
        grid = QGridLayout(); grid.setSpacing(14)
        self._c_milk  = StatCard("🥛","today_milk",       "— L",      COLOR_ACCENT)
        self._c_coll  = StatCard("💰","today_collection", "NPR —",    COLOR_SIDEBAR)
        self._c_out   = StatCard("⚖️","outstanding_balance","NPR —",  COLOR_DANGER)
        self._c_inv   = StatCard("🏪","products_in_stock","—",        "#2563EB")
        self._c_txn   = StatCard("📋","transactions_today","—",       COLOR_SUCCESS)
        for i, c in enumerate([self._c_milk,self._c_coll,self._c_out,self._c_inv,self._c_txn]):
            grid.addWidget(c, 0, i)
            grid.setColumnStretch(i, 1)
        root.addLayout(grid)

        # Quick actions label
        self._qa_lbl = QLabel(_t("quick_actions"))
        self._qa_lbl.setStyleSheet(f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(self._qa_lbl)

        qa_row = QHBoxLayout(); qa_row.setSpacing(10)
        for icon, key, page_key in self.QUICK_ACTIONS:
            btn = QPushButton(f"{icon}\n{_t(key)}")
            btn.setObjectName("quick_btn")
            btn.setMinimumSize(120, 80)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            if self._navigate:
                btn.clicked.connect(lambda _, k=page_key: self._navigate(k))
            qa_row.addWidget(btn)
        root.addLayout(qa_row)

        # Recent transactions
        self._recent_lbl = QLabel(_t("recent_transactions"))
        self._recent_lbl.setStyleSheet(f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(self._recent_lbl)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            _t("col_date"), _t("col_farmer"), _t("col_product"),
            _t("col_quantity"), _t("col_amount"),
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setMaximumHeight(220)
        root.addWidget(self._table)
        root.addStretch()

    def _update_date(self):
        self._date_lbl.setText(date.today().strftime("%A, %d %B %Y"))

    def _refresh_data(self):
        self._update_date()
        # refresh translatable labels
        self._title_lbl.setText(_t("dashboard_title"))
        self._qa_lbl.setText(_t("quick_actions"))
        self._recent_lbl.setText(_t("recent_transactions"))
        for c in [self._c_milk,self._c_coll,self._c_out,self._c_inv,self._c_txn]:
            c.refresh_label()
        self._table.setHorizontalHeaderLabels([
            _t("col_date"), _t("col_farmer"), _t("col_product"),
            _t("col_quantity"), _t("col_amount"),
        ])

        try:
            from database.database import get_session
            from database.models import Transaction, Payment, Product, InventoryMovement
            from sqlalchemy import func, and_
            today = date.today()
            s = get_session()

            milk = s.query(Product).filter_by(is_milk=1).first()
            milk_qty = 0.0
            if milk:
                r = s.query(func.sum(Transaction.quantity)).filter(and_(
                    Transaction.transaction_date == today,
                    Transaction.product_id == milk.product_id,
                    Transaction.status == "ACTIVE")).scalar()
                milk_qty = float(r or 0)

            today_rows = s.query(Transaction.quantity, Transaction.rate).filter(and_(
                Transaction.transaction_date == today, Transaction.status == "ACTIVE")).all()
            today_total = sum(float(q)*float(r) for q,r in today_rows)

            all_active = s.query(Transaction.quantity, Transaction.rate).filter_by(status="ACTIVE").all()
            total_owed = sum(float(q)*float(r) for q,r in all_active)
            total_paid = float(s.query(func.sum(Payment.amount_paid)).scalar() or 0)
            outstanding = total_owed - total_paid

            non_milk = s.query(Product).filter_by(is_milk=0).all()
            in_stock = sum(
                1 for p in non_milk
                if float(s.query(func.sum(InventoryMovement.quantity)).filter_by(
                    product_id=p.product_id, movement_type="IN").scalar() or 0)
                 - float(s.query(func.sum(InventoryMovement.quantity)).filter_by(
                    product_id=p.product_id, movement_type="OUT").scalar() or 0) > 0
            )
            txn_today = int(s.query(func.count(Transaction.transaction_id)).filter(and_(
                Transaction.transaction_date == today,
                Transaction.status == "ACTIVE")).scalar() or 0)

            self._c_milk.set_value(f"{milk_qty:,.1f} L")
            self._c_coll.set_value(f"NPR {today_total:,.0f}")
            self._c_out.set_value(f"NPR {outstanding:,.0f}")
            self._c_inv.set_value(str(in_stock))
            self._c_txn.set_value(str(txn_today))

            recent = s.query(Transaction).filter_by(status="ACTIVE")\
                      .order_by(Transaction.transaction_id.desc()).limit(10).all()
            self._table.setRowCount(len(recent))
            for row, txn in enumerate(recent):
                self._table.setItem(row,0,QTableWidgetItem(str(txn.transaction_date)))
                self._table.setItem(row,1,QTableWidgetItem(txn.farmer.display_name if txn.farmer else "—"))
                self._table.setItem(row,2,QTableWidgetItem(txn.product.display_name if txn.product else "—"))
                self._table.setItem(row,3,QTableWidgetItem(
                    f"{float(txn.quantity):,.2f} {txn.product.unit if txn.product else ''}"))
                self._table.setItem(row,4,QTableWidgetItem(f"{txn.amount:,.2f}"))
            s.close()

            # Backup badge
            from database.models import Backup
            s2 = get_session()
            last_bk = s2.query(Backup).filter_by(verified=1)\
                        .order_by(Backup.backup_date.desc()).first()
            s2.close()
            if last_bk:
                from datetime import datetime, timedelta
                age = datetime.utcnow() - last_bk.backup_date
                if age < timedelta(hours=24):
                    self._backup_badge.setText(_t("backup_ok"))
                    self._backup_badge.setStyleSheet(
                        f"background:{COLOR_SUCCESS}; color:white; border-radius:4px;"
                        f"padding:4px 10px; font-size:8pt; font-weight:bold;")
                else:
                    self._backup_badge.setText(_t("backup_warning"))
                    self._backup_badge.setStyleSheet(
                        f"background:#F59E0B; color:white; border-radius:4px;"
                        f"padding:4px 10px; font-size:8pt; font-weight:bold;")
        except Exception:
            pass
