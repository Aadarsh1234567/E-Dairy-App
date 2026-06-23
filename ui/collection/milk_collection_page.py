"""
Milk Collection page — Phase 6. CRITICAL PHASE.
Most used screen. Optimized for speed per UI/UX blueprint.

Workflow: Farmer Code -> auto-load -> Session -> Milk Type -> Quantity
          -> FAT -> SNF -> Rate (auto) -> Amount (auto) -> Save
Keyboard: Enter moves to next field, F2 saves, Esc clears.
"""

from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QBrush

from constants import (
    COLOR_ACCENT, COLOR_CARD, COLOR_BORDER,
    COLOR_DANGER, COLOR_SUCCESS, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_SIDEBAR,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class MilkCollectionPage(QWidget):
    """The most important screen in the application."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._farmer = None    # currently loaded FarmerLookup
        self._setup_ui()
        self._setup_shortcuts()
        self._load_recent()

    # ── UI ──────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        self._title = QLabel(_t("milk_collection"))
        self._title.setStyleSheet("font-size:20pt; font-weight:bold;")
        root.addWidget(self._title)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLOR_CARD}; border:1px solid {COLOR_BORDER};
                border-radius:10px;
            }}
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 20, 24, 20)
        card_lay.setSpacing(14)

        # Row 1: Farmer code + auto-loaded info
        row1 = QHBoxLayout(); row1.setSpacing(16)
        code_col = QVBoxLayout(); code_col.setSpacing(4)
        self._code_lbl = self._field_label("farmer_id_prompt")
        code_col.addWidget(self._code_lbl)
        self._code_input = QLineEdit()
        self._code_input.setStyleSheet(self._input_style())
        self._code_input.setFixedHeight(42)
        self._code_input.setFixedWidth(160)
        self._code_input.returnPressed.connect(self._on_code_entered)
        code_col.addWidget(self._code_input)
        row1.addLayout(code_col)

        info_col = QVBoxLayout(); info_col.setSpacing(4)
        info_col.addWidget(QLabel(""))
        self._farmer_info_lbl = QLabel("—")
        self._farmer_info_lbl.setStyleSheet(
            f"font-size:11pt; color:{COLOR_TEXT_SECONDARY}; padding-top:8px;")
        self._farmer_info_lbl.setWordWrap(True)
        info_col.addWidget(self._farmer_info_lbl)
        row1.addLayout(info_col, 1)
        card_lay.addLayout(row1)

        div1 = QFrame(); div1.setFrameShape(QFrame.HLine)
        div1.setStyleSheet(f"color:{COLOR_BORDER};")
        card_lay.addWidget(div1)

        # Row 2: Session + Milk Type
        row2 = QHBoxLayout(); row2.setSpacing(16)
        sess_col = QVBoxLayout(); sess_col.setSpacing(4)
        sess_col.addWidget(self._field_label("session"))
        self._session_combo = QComboBox()
        self._session_combo.addItem(_t("morning"), "MORNING")
        self._session_combo.addItem(_t("evening"), "EVENING")
        self._session_combo.setStyleSheet(self._input_style())
        self._session_combo.setFixedHeight(40)
        sess_col.addWidget(self._session_combo)
        row2.addLayout(sess_col)

        type_col = QVBoxLayout(); type_col.setSpacing(4)
        type_col.addWidget(self._field_label("milk_type"))
        self._type_combo = QComboBox()
        self._type_combo.addItem(_t("cow"), "COW")
        self._type_combo.addItem(_t("buffalo"), "BUFFALO")
        self._type_combo.setStyleSheet(self._input_style())
        self._type_combo.setFixedHeight(40)
        type_col.addWidget(self._type_combo)
        row2.addLayout(type_col)
        row2.addStretch()
        card_lay.addLayout(row2)

        # Row 3: Quantity, FAT, SNF, Rate, Amount
        row3 = QHBoxLayout(); row3.setSpacing(16)
        self._qty_spin = self._spin_field(row3, "quantity", 0, 10000, 2)
        self._fat_spin = self._spin_field(row3, "fat",      0, 100,   2)
        self._snf_spin = self._spin_field(row3, "snf",      0, 100,   2)

        rate_col = QVBoxLayout(); rate_col.setSpacing(4)
        rate_col.addWidget(self._field_label("rate"))
        self._rate_display = QLabel("NPR 0.00")
        self._rate_display.setStyleSheet(
            f"font-size:13pt; font-weight:bold; color:{COLOR_SIDEBAR}; "
            f"background:#F0F2F7; border-radius:6px; padding:9px 14px;")
        self._rate_display.setFixedHeight(40)
        rate_col.addWidget(self._rate_display)
        row3.addLayout(rate_col)

        amount_col = QVBoxLayout(); amount_col.setSpacing(4)
        amount_col.addWidget(self._field_label("amount"))
        self._amount_display = QLabel("NPR 0.00")
        self._amount_display.setStyleSheet(
            f"font-size:13pt; font-weight:bold; color:{COLOR_SUCCESS}; "
            f"background:#ECFDF5; border-radius:6px; padding:9px 14px;")
        self._amount_display.setFixedHeight(40)
        amount_col.addWidget(self._amount_display)
        row3.addLayout(amount_col)
        card_lay.addLayout(row3)

        self._qty_spin.valueChanged.connect(self._update_preview)
        self._fat_spin.valueChanged.connect(self._update_preview)
        self._snf_spin.valueChanged.connect(self._update_preview)

        self._msg = QLabel("")
        self._msg.setWordWrap(True)
        self._msg.setMinimumHeight(28)
        self._msg.setStyleSheet(f"font-size:10pt; color:{COLOR_DANGER};")
        card_lay.addWidget(self._msg)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        self._clear_btn = QPushButton(f"{_t('clear')}  (Esc)")
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{COLOR_TEXT_SECONDARY};
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:10px 20px; font-size:10pt;
            }}
            QPushButton:hover {{ border-color:{COLOR_ACCENT}; color:{COLOR_ACCENT}; }}
        """)
        self._clear_btn.clicked.connect(self._clear_form)
        btn_row.addWidget(self._clear_btn)
        btn_row.addStretch()

        self._save_btn = QPushButton(f"💾  {_t('save')}  (F2)")
        self._save_btn.setObjectName("primary_btn")
        self._save_btn.setFixedHeight(44)
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.clicked.connect(self._save_entry)
        btn_row.addWidget(self._save_btn)
        card_lay.addLayout(btn_row)

        root.addWidget(card)

        self._recent_lbl = QLabel(_t("recent_transactions"))
        self._recent_lbl.setStyleSheet(
            f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(self._recent_lbl)

        self._table = QTableWidget(0, 8)
        self._refresh_table_headers()
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        root.addWidget(self._table, 1)

        self._code_input.setFocus()

    def _field_label(self, key: str) -> QLabel:
        lbl = QLabel(_t(key).upper())
        lbl.setStyleSheet(
            f"font-size:8pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY};"
            f"letter-spacing:0.8px;")
        return lbl

    def _input_style(self) -> str:
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:8px 12px; font-size:11pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
                border-color:{COLOR_ACCENT};
            }}
        """

    def _spin_field(self, parent_layout, key: str, lo, hi, decimals) -> QDoubleSpinBox:
        col = QVBoxLayout(); col.setSpacing(4)
        col.addWidget(self._field_label(key))
        spin = QDoubleSpinBox()
        spin.setRange(lo, hi)
        spin.setDecimals(decimals)
        spin.setStyleSheet(self._input_style())
        spin.setFixedHeight(40)
        spin.setFixedWidth(130)
        col.addWidget(spin)
        parent_layout.addLayout(col)
        return spin

    def _refresh_table_headers(self):
        self._table.setHorizontalHeaderLabels([
            _t("col_date"), _t("col_farmer"), _t("col_session"),
            _t("col_type"), _t("col_quantity"), _t("col_fat"),
            _t("col_snf"), _t("col_amount"),
        ])

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("F2"), self, activated=self._save_entry)
        QShortcut(QKeySequence("Esc"), self, activated=self._clear_form)

    def _on_code_entered(self):
        from modules.transactions.milk_service import lookup_farmer, MilkError
        code = self._code_input.text().strip()
        if not code:
            return
        self._msg.setText("")
        try:
            farmer = lookup_farmer(code)
            self._farmer = farmer
            self._farmer_info_lbl.setText(
                f"✓  {farmer.display_name}   •   {farmer.phone or '—'}   •   {farmer.address or '—'}"
            )
            self._farmer_info_lbl.setStyleSheet(
                f"font-size:11pt; color:{COLOR_SUCCESS}; font-weight:bold; padding-top:8px;")
            self._qty_spin.setFocus()
        except MilkError as e:
            self._farmer = None
            self._farmer_info_lbl.setText("—")
            self._farmer_info_lbl.setStyleSheet(
                f"font-size:11pt; color:{COLOR_TEXT_SECONDARY}; padding-top:8px;")
            self._error(str(e))

    def _update_preview(self):
        from modules.transactions.milk_service import preview_rate, MilkError
        fat = self._fat_spin.value()
        snf = self._snf_spin.value()
        qty = self._qty_spin.value()
        if fat <= 0 and snf <= 0:
            self._rate_display.setText("NPR 0.00")
            self._amount_display.setText("NPR 0.00")
            return
        try:
            rate = preview_rate(fat, snf)
            amount = round(qty * rate, 2)
            self._rate_display.setText(f"NPR {rate:,.2f}")
            self._amount_display.setText(f"NPR {amount:,.2f}")
        except MilkError:
            self._rate_display.setText("—")
            self._amount_display.setText("—")

    def _save_entry(self):
        from modules.transactions.milk_service import (
            save_milk_collection, check_duplicate, MilkError
        )
        self._msg.setText("")
        if not self._farmer:
            self._error(_t("farmer_not_found"))
            self._code_input.setFocus()
            return

        session_value = self._session_combo.currentData()
        milk_type      = self._type_combo.currentData()
        quantity       = self._qty_spin.value()
        fat            = self._fat_spin.value()
        snf            = self._snf_spin.value()
        today          = date.today()

        if check_duplicate(self._farmer.farmer_id, today, session_value):
            self._error(_t("duplicate_entry"))
            return

        try:
            save_milk_collection(
                farmer_code      = self._farmer.farmer_code,
                transaction_date = today,
                session_value    = session_value,
                milk_type        = milk_type,
                quantity         = quantity,
                fat              = fat,
                snf              = snf,
            )
            self._success(_t("milk_saved"))
            self._reset_for_next_entry()
            self._load_recent()
        except MilkError as e:
            self._error(str(e))
        except Exception as e:
            self._error(_t("unexpected_error", err=str(e)))

    def _clear_form(self):
        self._code_input.clear()
        self._farmer = None
        self._farmer_info_lbl.setText("—")
        self._farmer_info_lbl.setStyleSheet(
            f"font-size:11pt; color:{COLOR_TEXT_SECONDARY}; padding-top:8px;")
        self._qty_spin.setValue(0)
        self._fat_spin.setValue(0)
        self._snf_spin.setValue(0)
        self._rate_display.setText("NPR 0.00")
        self._amount_display.setText("NPR 0.00")
        self._msg.setText("")
        self._code_input.setFocus()

    def _reset_for_next_entry(self):
        self._clear_form()

    def _error(self, msg):
        self._msg.setStyleSheet(f"font-size:10pt; color:{COLOR_DANGER};")
        self._msg.setText(msg)

    def _success(self, msg):
        self._msg.setStyleSheet(f"font-size:10pt; color:{COLOR_SUCCESS}; font-weight:bold;")
        self._msg.setText(msg)

    def _load_recent(self):
        from modules.transactions.milk_service import get_recent_milk_entries
        from utils.bs_calendar import db_date_to_bs_str
        from database.database import get_setting

        lang = get_setting("default_language", "NE")
        entries = get_recent_milk_entries(limit=10)
        self._table.setRowCount(len(entries))

        for row, e in enumerate(entries):
            bs_date = db_date_to_bs_str(e.transaction_date, lang=lang)
            self._table.setItem(row, 0, QTableWidgetItem(bs_date))
            self._table.setItem(row, 1, QTableWidgetItem(f"{e.farmer_code} — {e.farmer_name}"))

            sess_text = _t("morning") if e.session == "MORNING" else _t("evening")
            self._table.setItem(row, 2, QTableWidgetItem(sess_text))

            type_text = _t("cow") if e.milk_type == "COW" else _t("buffalo")
            self._table.setItem(row, 3, QTableWidgetItem(type_text))

            self._table.setItem(row, 4, QTableWidgetItem(f"{e.quantity:,.2f} L"))
            self._table.setItem(row, 5, QTableWidgetItem(f"{e.fat:.2f}"))
            self._table.setItem(row, 6, QTableWidgetItem(f"{e.snf:.2f}"))

            amt_item = QTableWidgetItem(f"{e.amount:,.2f}")
            if e.status == "CANCELLED":
                amt_item.setForeground(QBrush(QColor(COLOR_DANGER)))
                for col in range(8):
                    item = self._table.item(row, col)
                    if item:
                        item.setForeground(QBrush(QColor(COLOR_TEXT_SECONDARY)))
            self._table.setItem(row, 7, amt_item)
            self._table.setRowHeight(row, 36)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_table_headers()
        self._title.setText(_t("milk_collection"))
        self._recent_lbl.setText(_t("recent_transactions"))
        self._load_recent()
        self._code_input.setFocus()
