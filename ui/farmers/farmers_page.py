"""
Farmer Management page — Phase 4. Bilingual.
Features: list, search, add, edit, deactivate/activate.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QAbstractItemView,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush
from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_SIDEBAR,
    COLOR_CARD, COLOR_BORDER, COLOR_DANGER, COLOR_SUCCESS,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BG,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class FarmersPage(QWidget):
    """Full farmer management screen."""

    # Column indexes
    COL_CODE    = 0
    COL_NAME    = 1
    COL_PHONE   = 2
    COL_ADDRESS = 3
    COL_BALANCE = 4
    COL_STATUS  = 5
    COL_ACTIONS = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._farmers: list = []   # list[FarmerRow]
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._setup_ui()
        self._load_farmers()

    # ── UI ──────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # ── Header ──────────────────────────────────────────────
        hdr = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        self._title = QLabel(_t("farmer_management"))
        self._title.setStyleSheet("font-size:20pt; font-weight:bold;")
        self._sub = QLabel(_t("farmer_list"))
        self._sub.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        col.addWidget(self._title); col.addWidget(self._sub)
        hdr.addLayout(col, 1)

        self._add_btn = QPushButton(f"＋  {_t('add_farmer')}")
        self._add_btn.setObjectName("primary_btn")
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setFixedHeight(40)
        self._add_btn.clicked.connect(self._open_add)
        hdr.addWidget(self._add_btn)
        root.addLayout(hdr)

        # ── Search bar ──────────────────────────────────────────
        search_row = QHBoxLayout(); search_row.setSpacing(10)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(_t("search_placeholder"))
        self._search_input.setFixedHeight(38)
        self._search_input.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self._search_input, 1)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(f"color:{COLOR_TEXT_SECONDARY}; font-size:9pt;")
        search_row.addWidget(self._count_lbl)
        root.addLayout(search_row)

        # ── Table ────────────────────────────────────────────────
        self._table = QTableWidget(0, 7)
        self._refresh_headers()
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_ACTIONS, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_CODE,    QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_STATUS,  QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_BALANCE, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setFocusPolicy(Qt.StrongFocus)
        root.addWidget(self._table, 1)

        # ── Empty state ──────────────────────────────────────────
        self._empty_lbl = QLabel(_t("no_farmers"))
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet(
            f"font-size:12pt; color:{COLOR_TEXT_SECONDARY}; padding:40px;")
        self._empty_lbl.hide()
        root.addWidget(self._empty_lbl)

    def _refresh_headers(self):
        self._table.setHorizontalHeaderLabels([
            _t("col_code"), _t("col_name"), _t("col_phone"),
            _t("col_address"), _t("outstanding_balance"),
            _t("col_status"), _t("col_actions"),
        ])

    # ── Data loading ────────────────────────────────────────────────────────
    def _load_farmers(self, query: str = ""):
        from modules.farmers.farmer_service import get_all_farmers, search_farmers
        if query.strip():
            self._farmers = search_farmers(query.strip(), include_inactive=True)
        else:
            self._farmers = get_all_farmers(include_inactive=True)
        self._render_table()

    def _render_table(self):
        self._table.setRowCount(0)
        if not self._farmers:
            self._table.hide()
            self._empty_lbl.show()
            self._count_lbl.setText("")
            return

        self._empty_lbl.hide()
        self._table.show()
        self._count_lbl.setText(f"{len(self._farmers)} {_t('farmers').lower()}")
        self._table.setRowCount(len(self._farmers))

        for row, f in enumerate(self._farmers):
            # Code
            self._table.setItem(row, self.COL_CODE, QTableWidgetItem(f.farmer_code))

            # Name — prefer Nepali
            display_name = f.name_nepali if f.name_nepali else f.name_english
            self._table.setItem(row, self.COL_NAME, QTableWidgetItem(display_name))
            self._table.setItem(row, self.COL_PHONE,   QTableWidgetItem(f.phone))
            self._table.setItem(row, self.COL_ADDRESS, QTableWidgetItem(f.address))

            # Balance
            bal_item = QTableWidgetItem(f"NPR {f.outstanding:,.2f}")
            bal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if f.outstanding > 0:
                bal_item.setForeground(QBrush(QColor(COLOR_DANGER)))
            elif f.outstanding < 0:
                bal_item.setForeground(QBrush(QColor("#2563EB")))   # blue = advance given
            self._table.setItem(row, self.COL_BALANCE, bal_item)

            # Status badge
            status_text = _t("active") if f.status == "ACTIVE" else _t("inactive")
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            if f.status == "ACTIVE":
                status_item.setForeground(QBrush(QColor(COLOR_SUCCESS)))
            else:
                status_item.setForeground(QBrush(QColor(COLOR_TEXT_SECONDARY)))
            self._table.setItem(row, self.COL_STATUS, status_item)

            # Action buttons
            self._table.setCellWidget(row, self.COL_ACTIONS,
                                      self._action_buttons(f))
            self._table.setRowHeight(row, 48)

    def _action_buttons(self, farmer_row) -> QWidget:
        """Return a widget with Edit + Deactivate/Activate buttons."""
        cell = QWidget()
        cell.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(6)

        edit_btn = QPushButton(_t("edit"))
        edit_btn.setFixedHeight(32)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_ACCENT}; color:white; border:none;
                border-radius:4px; padding:0 12px; font-size:9pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT_DARK}; }}
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda _, f=farmer_row: self._open_edit(f))
        lay.addWidget(edit_btn)

        if farmer_row.status == "ACTIVE":
            tog_btn = QPushButton(_t("deactivate"))
            tog_btn.setStyleSheet(f"""
                QPushButton {{
                    background:transparent; color:{COLOR_DANGER};
                    border:1.5px solid {COLOR_DANGER}; border-radius:4px;
                    padding:0 10px; font-size:9pt;
                }}
                QPushButton:hover {{
                    background:{COLOR_DANGER}; color:white;
                }}
            """)
            tog_btn.clicked.connect(lambda _, f=farmer_row: self._toggle_status(f))
        else:
            tog_btn = QPushButton(_t("activate"))
            tog_btn.setStyleSheet(f"""
                QPushButton {{
                    background:transparent; color:{COLOR_SUCCESS};
                    border:1.5px solid {COLOR_SUCCESS}; border-radius:4px;
                    padding:0 10px; font-size:9pt;
                }}
                QPushButton:hover {{
                    background:{COLOR_SUCCESS}; color:white;
                }}
            """)
            tog_btn.clicked.connect(lambda _, f=farmer_row: self._toggle_status(f))

        tog_btn.setFixedHeight(32)
        tog_btn.setCursor(Qt.PointingHandCursor)
        lay.addWidget(tog_btn)
        lay.addStretch()
        return cell

    # ── Slots ────────────────────────────────────────────────────────────────
    def _on_search_changed(self, text: str):
        self._search_timer.start(300)   # debounce 300ms

    def _do_search(self):
        self._load_farmers(self._search_input.text())

    def _open_add(self):
        from ui.farmers.farmer_form_dialog import FarmerFormDialog
        dlg = FarmerFormDialog(parent=self)
        dlg.saved.connect(lambda _: self._load_farmers(self._search_input.text()))
        dlg.exec()

    def _open_edit(self, farmer_row):
        from ui.farmers.farmer_form_dialog import FarmerFormDialog
        dlg = FarmerFormDialog(farmer_row=farmer_row, parent=self)
        dlg.saved.connect(lambda _: self._load_farmers(self._search_input.text()))
        dlg.exec()

    def _toggle_status(self, farmer_row):
        from modules.farmers.farmer_service import (
            deactivate_farmer, activate_farmer, FarmerError
        )
        if farmer_row.status == "ACTIVE":
            # Confirm deactivation
            reply = QMessageBox.question(
                self, _t("confirm"),
                _t("confirm_deactivate"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            try:
                deactivate_farmer(farmer_row.farmer_id)
                self._load_farmers(self._search_input.text())
            except FarmerError as e:
                QMessageBox.warning(self, _t("warning"), str(e))
        else:
            try:
                activate_farmer(farmer_row.farmer_id)
                self._load_farmers(self._search_input.text())
            except FarmerError as e:
                QMessageBox.warning(self, _t("warning"), str(e))

    def showEvent(self, event):
        """Refresh data every time the page becomes visible."""
        super().showEvent(event)
        self._load_farmers(self._search_input.text())
        self._refresh_headers()
