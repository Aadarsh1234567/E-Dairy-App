"""
Dashboard page — Phase 5+BS. Bilingual with Nepali BS calendar.
"""
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush
from constants import (
    COLOR_ACCENT, COLOR_SIDEBAR, COLOR_TEXT_SECONDARY,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_CARD, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_BG,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


# ── BS Date/Time hero widget ───────────────────────────────────────────────────
class BSDateTimeWidget(QFrame):
    """
    Attractive hero widget showing the current Nepali date and time.
    Updates every second. Switches language with the app setting.
    Clickable — opens the full BS calendar picker dialog.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bs_datetime_card")
        self.setStyleSheet(f"""
            QFrame#bs_datetime_card {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLOR_SIDEBAR},
                    stop:1 #2E4A7A
                );
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.08);
            }}
            QFrame#bs_datetime_card:hover {{
                border: 1px solid rgba(255,255,255,0.25);
            }}
        """)
        self.setMinimumHeight(110)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(_t("open_calendar_hint"))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(4)

        # Top row: calendar label + org name
        top_row = QHBoxLayout()
        cal_badge = QLabel("📅  विक्रम सम्वत्")
        cal_badge.setStyleSheet(
            "color: rgba(255,255,255,0.55); font-size:8pt; background:transparent;"
        )
        top_row.addWidget(cal_badge, 1)

        self._org_lbl = QLabel("")
        self._org_lbl.setStyleSheet(
            f"color:{COLOR_ACCENT}; font-size:8pt; font-weight:bold; background:transparent;"
        )
        self._org_lbl.setAlignment(Qt.AlignRight)
        top_row.addWidget(self._org_lbl)
        lay.addLayout(top_row)

        # Date (large)
        self._date_lbl = QLabel("")
        self._date_lbl.setStyleSheet(
            "color:white; font-size:18pt; font-weight:bold; background:transparent;"
        )
        lay.addWidget(self._date_lbl)

        # Time row
        time_row = QHBoxLayout()
        self._time_lbl = QLabel("")
        self._time_lbl.setStyleSheet(
            f"color:{COLOR_ACCENT}; font-size:13pt; font-weight:bold; background:transparent;"
        )
        self._tod_lbl = QLabel("")
        self._tod_lbl.setStyleSheet(
            "color:rgba(255,255,255,0.6); font-size:9pt; background:transparent;"
        )
        time_row.addWidget(self._time_lbl)
        time_row.addWidget(self._tod_lbl)
        time_row.addStretch()
        lay.addLayout(time_row)

        self._refresh()

    def _refresh(self):
        from utils.bs_calendar import bs_now, format_bs_date, format_bs_time, to_np_digits
        from database.database import get_setting
        lang = get_setting("default_language", "NE")

        now = bs_now()
        d   = now.date()

        # Date line
        self._date_lbl.setText(format_bs_date(d, lang=lang, include_weekday=True))

        # Time
        h   = now.hour
        m   = now.minute
        s   = now.second

        if lang == "NE":
            h12   = h % 12 or 12
            tod   = self._tod_ne(h)
            h_str = to_np_digits(str(h12).zfill(2))
            m_str = to_np_digits(str(m).zfill(2))
            s_str = to_np_digits(str(s).zfill(2))
            self._time_lbl.setText(f"{h_str}:{m_str}:{s_str}")
            self._tod_lbl.setText(f"  {tod}")
        else:
            h12   = h % 12 or 12
            ampm  = "AM" if h < 12 else "PM"
            self._time_lbl.setText(f"{h12:02d}:{m:02d}:{s:02d}")
            self._tod_lbl.setText(f"  {ampm}")

        # Org name
        if lang == "NE":
            org = get_setting("organization_name_nepali", "") or \
                  get_setting("organization_name_english", "Santosh Dairy Cooperative")
        else:
            org = get_setting("organization_name_english", "Santosh Dairy Cooperative")
        self._org_lbl.setText(org)

    def _tod_ne(self, hour: int) -> str:
        if 4 <= hour < 12:   return "बिहान"
        elif 12 <= hour < 16: return "दिउँसो"
        elif 16 <= hour < 20: return "साँझ"
        else:                 return "राति"

    def tick(self):
        self._refresh()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            from ui.dashboard.bs_calendar_dialog import BSCalendarDialog
            dlg = BSCalendarDialog(parent=self.window())
            dlg.exec()
        super().mousePressEvent(event)


# ── Stat card ─────────────────────────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, icon, label_key, value, accent=COLOR_ACCENT, parent=None):
        super().__init__(parent)
        self._label_key = label_key
        self.setObjectName("stat_card")
        self.setMinimumHeight(100)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:18pt; background:transparent;")
        icon_lbl.setFixedWidth(30)
        self._lbl = QLabel(_t(label_key).upper())
        self._lbl.setStyleSheet(
            f"color:{COLOR_TEXT_SECONDARY}; font-size:7pt; font-weight:bold; letter-spacing:1px; background:transparent;"
        )
        top.addWidget(icon_lbl)
        top.addWidget(self._lbl, 1)
        lay.addLayout(top)

        self._val = QLabel(value)
        self._val.setStyleSheet(
            f"font-size:18pt; font-weight:bold; color:{accent}; background:transparent;"
        )
        lay.addWidget(self._val)

    def set_value(self, v): self._val.setText(v)
    def refresh_label(self): self._lbl.setText(_t(self._label_key).upper())

    def set_value_with_color(self, v: str, color: str):
        """Update value text and font color together (used for balance cards that can flip sign)."""
        self._val.setText(v)
        self._val.setStyleSheet(
            f"font-size:18pt; font-weight:bold; color:{color}; background:transparent;"
        )


# ── Dashboard page ────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    QUICK_ACTIONS = [
        ("🥛", "milk_collection",     "milk_collection"),
        ("💳", "payments",            "payments"),
        ("📊", "reports",             "reports"),
        ("👨‍🌾","farmers",             "farmers"),
        ("⚙️", "settings",           "settings"),
    ]

    def __init__(self, navigate_callback=None, parent=None):
        super().__init__(parent)
        self._navigate = navigate_callback
        self._setup_ui()
        self._refresh_data()

        # 1-second clock timer
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._bs_widget.tick)
        self._clock_timer.start(1000)

        # Data refresh every 60 seconds
        self._data_timer = QTimer(self)
        self._data_timer.timeout.connect(self._refresh_data)
        self._data_timer.start(60_000)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        # ── Top row: BS date hero + backup badge ────────────────
        top_row = QHBoxLayout(); top_row.setSpacing(16)

        self._bs_widget = BSDateTimeWidget()
        top_row.addWidget(self._bs_widget, 3)

        # Backup status card
        self._backup_card = QFrame()
        self._backup_card.setStyleSheet(f"""
            QFrame {{
                background:{COLOR_CARD};
                border:1px solid {COLOR_BORDER};
                border-radius:12px;
            }}
        """)
        bk_lay = QVBoxLayout(self._backup_card)
        bk_lay.setContentsMargins(16, 14, 16, 14)
        bk_lay.setSpacing(4)
        bk_icon = QLabel("💾")
        bk_icon.setStyleSheet("font-size:22pt; background:transparent;")
        self._backup_lbl = QLabel(_t("backup_ok"))
        self._backup_lbl.setStyleSheet(
            f"font-size:9pt; font-weight:bold; color:{COLOR_SUCCESS}; background:transparent;"
        )
        self._backup_sub = QLabel("—")
        self._backup_sub.setStyleSheet(
            f"font-size:8pt; color:{COLOR_TEXT_SECONDARY}; background:transparent;"
        )
        bk_lay.addWidget(bk_icon)
        bk_lay.addWidget(self._backup_lbl)
        bk_lay.addWidget(self._backup_sub)
        top_row.addWidget(self._backup_card, 1)
        root.addLayout(top_row)

        # ── Stat cards ──────────────────────────────────────────
        grid = QGridLayout(); grid.setSpacing(12)
        self._c_milk  = StatCard("🥛", "today_milk",         "— L",     COLOR_ACCENT)
        self._c_coll  = StatCard("💰", "today_collection",   "NPR —",   COLOR_SIDEBAR)
        self._c_out   = StatCard("⚖️", "outstanding_balance","NPR —",   COLOR_DANGER)
        self._c_farmers = StatCard("👨‍🌾", "active_farmers_count", "—",  "#2563EB")
        self._c_txn   = StatCard("📋", "transactions_today", "—",       COLOR_SUCCESS)
        for i, c in enumerate([self._c_milk,self._c_coll,self._c_out,self._c_farmers,self._c_txn]):
            grid.addWidget(c, 0, i)
            grid.setColumnStretch(i, 1)
        root.addLayout(grid)

        # ── Quick actions ───────────────────────────────────────
        self._qa_lbl = QLabel(_t("quick_actions"))
        self._qa_lbl.setStyleSheet(
            f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};"
        )
        root.addWidget(self._qa_lbl)

        qa_row = QHBoxLayout(); qa_row.setSpacing(10)
        for icon, key, page_key in self.QUICK_ACTIONS:
            btn = QPushButton(f"{icon}\n{_t(key)}")
            btn.setObjectName("quick_btn")
            btn.setMinimumSize(100, 76)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            if self._navigate:
                btn.clicked.connect(lambda _, k=page_key: self._navigate(k))
            qa_row.addWidget(btn)
        root.addLayout(qa_row)

        # ── Recent transactions ─────────────────────────────────
        self._recent_lbl = QLabel(_t("recent_transactions"))
        self._recent_lbl.setStyleSheet(
            f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};"
        )
        root.addWidget(self._recent_lbl)

        self._table = QTableWidget(0, 5)
        self._refresh_table_headers()
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setMaximumHeight(200)
        root.addWidget(self._table)
        root.addStretch()

    def _refresh_table_headers(self):
        self._table.setHorizontalHeaderLabels([
            _t("col_date"), _t("col_farmer"), _t("col_product"),
            _t("col_quantity"), _t("col_amount"),
        ])

    def _refresh_data(self):
        # Refresh translatable labels
        self._qa_lbl.setText(_t("quick_actions"))
        self._recent_lbl.setText(_t("recent_transactions"))
        self._refresh_table_headers()
        for c in [self._c_milk,self._c_coll,self._c_out,self._c_farmers,self._c_txn]:
            c.refresh_label()

        try:
            from database.database import get_session, get_setting
            from database.models import Transaction, Payment, Product, Farmer, Backup
            from utils.bs_calendar import ad_to_bs, format_bs_date, db_date_to_bs_str
            from sqlalchemy import func, and_
            import datetime

            lang  = get_setting("default_language", "NE")
            today = datetime.date.today()
            s     = get_session()

            # Today milk qty
            milk = s.query(Product).filter_by(is_milk=1).first()
            milk_qty = 0.0
            if milk:
                r = s.query(func.sum(Transaction.quantity)).filter(and_(
                    Transaction.transaction_date == today,
                    Transaction.product_id == milk.product_id,
                    Transaction.status == "ACTIVE",
                )).scalar()
                milk_qty = float(r or 0)

            # Today collection
            today_rows = s.query(Transaction.quantity, Transaction.rate, Transaction.bonus_amount).filter(and_(
                Transaction.transaction_date == today,
                Transaction.status == "ACTIVE",
            )).all()
            today_total = sum(float(q) * float(r) + float(b or 0) for q, r, b in today_rows)

            # Outstanding
            all_active = s.query(Transaction.quantity, Transaction.rate, Transaction.bonus_amount).filter_by(
                status="ACTIVE"
            ).all()
            total_owed = sum(float(q) * float(r) + float(b or 0) for q, r, b in all_active)
            total_paid = float(s.query(func.sum(Payment.amount_paid)).scalar() or 0)
            outstanding = total_owed - total_paid

            # Active farmers count
            active_farmers = int(s.query(func.count(Farmer.farmer_id)).filter_by(
                status="ACTIVE"
            ).scalar() or 0)

            # Txn today
            txn_today = int(s.query(func.count(Transaction.transaction_id)).filter(and_(
                Transaction.transaction_date == today,
                Transaction.status == "ACTIVE",
            )).scalar() or 0)

            self._c_milk.set_value(f"{milk_qty:,.1f} L")
            self._c_coll.set_value(f"NPR {today_total:,.0f}")
            out_color = "#2563EB" if outstanding < 0 else COLOR_DANGER
            self._c_out.set_value_with_color(f"NPR {outstanding:,.0f}", out_color)
            self._c_farmers.set_value(str(active_farmers))
            self._c_txn.set_value(str(txn_today))

            # Recent transactions — date in BS
            recent = s.query(Transaction).filter_by(status="ACTIVE") \
                      .order_by(Transaction.transaction_id.desc()).limit(10).all()
            self._table.setRowCount(len(recent))
            for row, txn in enumerate(recent):
                # Date shown in BS
                bs_date_str = db_date_to_bs_str(txn.transaction_date, lang=lang)
                self._table.setItem(row, 0, QTableWidgetItem(bs_date_str))
                self._table.setItem(row, 1, QTableWidgetItem(
                    txn.farmer.display_name if txn.farmer else "—"))
                self._table.setItem(row, 2, QTableWidgetItem(
                    txn.product.display_name if txn.product else "—"))
                self._table.setItem(row, 3, QTableWidgetItem(
                    f"{float(txn.quantity):,.2f} {txn.product.unit if txn.product else ''}"))
                amt = QTableWidgetItem(f"{txn.amount:,.2f}")
                amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._table.setItem(row, 4, amt)

            # Backup status — date shown in BS
            last_bk = s.query(Backup).filter_by(verified=1) \
                       .order_by(Backup.backup_date.desc()).first()
            if last_bk:
                from datetime import timedelta, datetime as dt
                age = dt.utcnow() - last_bk.backup_date
                bs_bk_date = db_date_to_bs_str(last_bk.backup_date.date(), lang=lang)
                if age < timedelta(hours=24):
                    self._backup_lbl.setText(_t("backup_ok"))
                    self._backup_lbl.setStyleSheet(
                        f"font-size:9pt; font-weight:bold; color:{COLOR_SUCCESS}; background:transparent;")
                else:
                    self._backup_lbl.setText(_t("backup_warning"))
                    self._backup_lbl.setStyleSheet(
                        f"font-size:9pt; font-weight:bold; color:#F59E0B; background:transparent;")
                self._backup_sub.setText(bs_bk_date)
            else:
                self._backup_lbl.setText(_t("backup_warning"))
                self._backup_sub.setText("—")

            s.close()
        except Exception:
            pass
