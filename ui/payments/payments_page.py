"""
Payment Entry page — Phase 8. Bilingual.
Supports advance payments (negative balance) per product decision:
  - Same form as regular payments
  - No block when amount exceeds balance
  - Clear warning shown when payment creates/extends an advance
"""

from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QDoubleSpinBox, QTableWidget,
    QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt

from constants import (
    COLOR_ACCENT, COLOR_CARD, COLOR_BORDER,
    COLOR_DANGER, COLOR_SUCCESS, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
)

ADVANCE_BLUE = "#2563EB"


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class PaymentsPage(QWidget):
    """Payment entry and history screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._farmer = None
        self._last_payment = None
        self._last_balance_after = 0.0
        self._setup_ui()
        self._load_recent()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        self._title = QLabel(_t("payment_entry"))
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

        row1 = QHBoxLayout(); row1.setSpacing(16)
        code_col = QVBoxLayout(); code_col.setSpacing(4)
        code_col.addWidget(self._field_label("farmer_code"))
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

        bal_row = QHBoxLayout(); bal_row.setSpacing(16)
        bal_col = QVBoxLayout(); bal_col.setSpacing(4)
        bal_col.addWidget(self._field_label("outstanding"))
        self._balance_display = QLabel("NPR 0.00")
        self._balance_display.setStyleSheet(
            f"font-size:16pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY}; "
            f"background:#F0F2F7; border-radius:6px; padding:10px 16px;")
        bal_col.addWidget(self._balance_display)
        bal_row.addLayout(bal_col)
        bal_row.addStretch()
        card_lay.addLayout(bal_row)

        row3 = QHBoxLayout(); row3.setSpacing(16)
        date_col = QVBoxLayout(); date_col.setSpacing(4)
        date_col.addWidget(self._field_label("payment_date"))
        self._date_display = QLabel("")
        self._date_display.setStyleSheet(
            f"font-size:11pt; color:{COLOR_TEXT_PRIMARY}; "
            f"background:white; border:1.5px solid {COLOR_BORDER}; "
            f"border-radius:6px; padding:9px 14px;")
        self._update_date_display()
        date_col.addWidget(self._date_display)
        row3.addLayout(date_col)

        amt_col = QVBoxLayout(); amt_col.setSpacing(4)
        amt_col.addWidget(self._field_label("amount_paid"))
        self._amount_spin = QDoubleSpinBox()
        self._amount_spin.setRange(0, 99999999.99)
        self._amount_spin.setDecimals(2)
        self._amount_spin.setStyleSheet(self._input_style())
        self._amount_spin.setFixedHeight(42)
        self._amount_spin.setFixedWidth(200)
        self._amount_spin.valueChanged.connect(self._update_preview)
        amt_col.addWidget(self._amount_spin)
        row3.addLayout(amt_col)
        row3.addStretch()
        card_lay.addLayout(row3)

        rem_col = QVBoxLayout(); rem_col.setSpacing(4)
        rem_col.addWidget(self._field_label("payment_remarks"))
        self._remarks_input = QLineEdit()
        self._remarks_input.setStyleSheet(self._input_style())
        self._remarks_input.setFixedHeight(40)
        rem_col.addWidget(self._remarks_input)
        card_lay.addLayout(rem_col)

        self._preview_banner = QLabel("")
        self._preview_banner.setWordWrap(True)
        self._preview_banner.setStyleSheet("font-size:9pt; padding:4px 0;")
        self._preview_banner.hide()
        card_lay.addWidget(self._preview_banner)

        self._msg = QLabel("")
        self._msg.setWordWrap(True)
        self._msg.setMinimumHeight(26)
        self._msg.setStyleSheet(f"font-size:10pt; color:{COLOR_DANGER};")
        card_lay.addWidget(self._msg)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        self._clear_btn = QPushButton(_t("clear"))
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

        self._print_btn = QPushButton(f"🖨  {_t('print_receipt')}")
        self._print_btn.setEnabled(False)
        self._print_btn.setStyleSheet("""
            QPushButton {background:#7C3AED;color:white;border:none;
                border-radius:6px;padding:10px 18px;font-size:10pt;font-weight:bold;}
            QPushButton:hover{background:#6D28D9;}
            QPushButton:disabled{background:#D1D5DB;color:#9CA3AF;}
        """)
        self._print_btn.setCursor(Qt.PointingHandCursor)
        self._print_btn.clicked.connect(self._print_receipt)
        btn_row.addWidget(self._print_btn)
        btn_row.addStretch()

        self._save_btn = QPushButton(f"💾  {_t('save')}")
        self._save_btn.setObjectName("primary_btn")
        self._save_btn.setFixedHeight(44)
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.clicked.connect(self._save_payment)
        btn_row.addWidget(self._save_btn)
        card_lay.addLayout(btn_row)

        root.addWidget(card)

        self._recent_lbl = QLabel(_t("payment_list"))
        self._recent_lbl.setStyleSheet(
            f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(self._recent_lbl)

        self._table = QTableWidget(0, 5)
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
            QLineEdit, QDoubleSpinBox {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:8px 12px; font-size:11pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QDoubleSpinBox:focus {{ border-color:{COLOR_ACCENT}; }}
        """

    def _refresh_table_headers(self):
        self._table.setHorizontalHeaderLabels([
            _t("col_payment_date"), _t("col_farmer"), _t("col_amount_paid"),
            _t("col_receipt"), _t("col_remarks"),
        ])

    def _update_date_display(self):
        from utils.bs_calendar import db_date_to_bs_str
        from database.database import get_setting
        lang = get_setting("default_language", "NE")
        self._date_display.setText(db_date_to_bs_str(date.today(), lang=lang))

    def _on_code_entered(self):
        from modules.transactions.milk_service import lookup_farmer, MilkError
        from modules.payments.payment_service import get_outstanding_balance

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

            balance = get_outstanding_balance(farmer.farmer_id)
            self._render_balance(balance)
            self._amount_spin.setFocus()

        except MilkError as e:
            self._farmer = None
            self._farmer_info_lbl.setText("—")
            self._farmer_info_lbl.setStyleSheet(
                f"font-size:11pt; color:{COLOR_TEXT_SECONDARY}; padding-top:8px;")
            self._render_balance(None)
            self._error(str(e))

    def _render_balance(self, balance):
        if balance is None:
            self._balance_display.setText("NPR 0.00")
            self._balance_display.setStyleSheet(
                f"font-size:16pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY}; "
                f"background:#F0F2F7; border-radius:6px; padding:10px 16px;")
            return

        if balance > 0:
            color, bg = COLOR_DANGER, "#FEF2F2"
        elif balance < 0:
            color, bg = ADVANCE_BLUE, "#EFF6FF"
        else:
            color, bg = COLOR_SUCCESS, "#ECFDF5"

        self._balance_display.setText(f"NPR {balance:,.2f}")
        self._balance_display.setStyleSheet(
            f"font-size:16pt; font-weight:bold; color:{color}; "
            f"background:{bg}; border-radius:6px; padding:10px 16px;")

    def _update_preview(self):
        if not self._farmer:
            self._preview_banner.hide()
            return

        from modules.payments.payment_service import get_outstanding_balance
        balance = get_outstanding_balance(self._farmer.farmer_id)
        amount = self._amount_spin.value()

        if amount <= 0:
            self._preview_banner.hide()
            return

        balance_after = balance - amount

        if balance_after < 0:
            advance_amount = abs(balance_after)
            self._preview_banner.setText(
                _t("advance_warning", amount=f"{advance_amount:,.2f}")
            )
            self._preview_banner.setStyleSheet(
                f"font-size:9pt; color:{ADVANCE_BLUE}; background:#EFF6FF; "
                f"border:1px solid #BFDBFE; border-radius:6px; padding:8px 12px;")
            self._preview_banner.show()
        else:
            self._preview_banner.hide()

    def _save_payment(self):
        from modules.payments.payment_service import record_payment, get_outstanding_balance, PaymentError

        self._msg.setText("")
        if not self._farmer:
            self._error(_t("select_farmer_first"))
            self._code_input.setFocus()
            return

        amount = self._amount_spin.value()
        remarks = self._remarks_input.text().strip()

        try:
            row = record_payment(
                farmer_id     = self._farmer.farmer_id,
                payment_date   = date.today(),
                amount_paid     = amount,
                remarks          = remarks,
            )
            self._last_payment = row
            self._last_balance_after = get_outstanding_balance(self._farmer.farmer_id)
            self._print_btn.setEnabled(True)
            self._success(_t("payment_saved"))
            self._clear_form()
            self._load_recent()
        except PaymentError as e:
            self._error(str(e))
        except Exception as e:
            self._error(_t("unexpected_error", err=str(e)))

    def _clear_form(self):
        self._code_input.clear()
        self._farmer = None
        self._farmer_info_lbl.setText("—")
        self._farmer_info_lbl.setStyleSheet(
            f"font-size:11pt; color:{COLOR_TEXT_SECONDARY}; padding-top:8px;")
        self._render_balance(None)
        self._amount_spin.setValue(0)
        self._remarks_input.clear()
        self._preview_banner.hide()
        self._msg.setText("")
        self._print_btn.setEnabled(False)
        self._update_date_display()
        self._code_input.setFocus()

    def _error(self, msg):
        self._msg.setStyleSheet(f"font-size:10pt; color:{COLOR_DANGER};")
        self._msg.setText(msg)

    def _success(self, msg):
        self._msg.setStyleSheet(f"font-size:10pt; color:{COLOR_SUCCESS}; font-weight:bold;")
        self._msg.setText(msg)

    def _load_recent(self):
        from modules.payments.payment_service import get_recent_payments
        from utils.bs_calendar import db_date_to_bs_str
        from database.database import get_setting

        lang = get_setting("default_language", "NE")
        payments = get_recent_payments(limit=15)
        self._table.setRowCount(len(payments))

        for row, p in enumerate(payments):
            bs_date = db_date_to_bs_str(p.payment_date, lang=lang)
            self._table.setItem(row, 0, QTableWidgetItem(bs_date))
            self._table.setItem(row, 1, QTableWidgetItem(f"{p.farmer_code} — {p.farmer_name}"))

            amt_item = QTableWidgetItem(f"{p.amount_paid:,.2f}")
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(row, 2, amt_item)

            self._table.setItem(row, 3, QTableWidgetItem(p.receipt_number or "—"))
            self._table.setItem(row, 4, QTableWidgetItem(p.remarks or "—"))
            self._table.setRowHeight(row, 34)

    def _print_receipt(self):
        if not self._last_payment:
            return
        from services.pdf_service import generate_payment_receipt_pdf
        from database.database import get_setting
        from PySide6.QtWidgets import QFileDialog
        lang = get_setting("default_language", "NE")
        width_mm = int(get_setting("receipt_width_mm", "80"))
        name = f"receipt_{self._last_payment.receipt_number or 'payment'}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, _t("print_receipt"), name, "PDF (*.pdf)")
        if not path:
            return
        try:
            generate_payment_receipt_pdf(
                payment_row=self._last_payment,
                balance_after=self._last_balance_after,
                output_path=path, lang=lang, width_mm=width_mm,
            )
            self._success(_t("receipt_printed"))
        except Exception as e:
            self._error(_t("unexpected_error", err=str(e)))

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_table_headers()
        self._title.setText(_t("payment_entry"))
        self._recent_lbl.setText(_t("payment_list"))
        self._update_date_display()
        self._load_recent()
        self._code_input.setFocus()
