"""
Product Management page — Phase 5. Bilingual.
Features: list all products, add new product, edit existing product.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_PRIMARY, COLOR_SUCCESS, COLOR_WARNING,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class ProductsPage(QWidget):
    """Product management screen."""

    COL_NAME     = 0
    COL_NEPALI   = 1
    COL_UNIT     = 2
    COL_TYPE     = 3
    COL_RATE     = 4
    COL_ACTIONS  = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._products = []
        self._setup_ui()
        self._load_products()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # ── Header ──────────────────────────────────────────────
        hdr = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        self._title = QLabel(_t("product_management"))
        self._title.setStyleSheet("font-size:20pt; font-weight:bold;")
        self._sub = QLabel(_t("product_list"))
        self._sub.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        col.addWidget(self._title); col.addWidget(self._sub)
        hdr.addLayout(col, 1)

        self._add_btn = QPushButton(f"＋  {_t('add_product')}")
        self._add_btn.setObjectName("primary_btn")
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setFixedHeight(40)
        self._add_btn.clicked.connect(self._open_add)
        hdr.addWidget(self._add_btn)
        root.addLayout(hdr)

        # ── Table ────────────────────────────────────────────────
        self._table = QTableWidget(0, 6)
        self._refresh_headers()
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_UNIT,    QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_TYPE,    QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_RATE,    QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_ACTIONS, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        root.addWidget(self._table, 1)

        # ── Empty state ──────────────────────────────────────────
        self._empty_lbl = QLabel(_t("no_products"))
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet(
            f"font-size:12pt; color:{COLOR_TEXT_SECONDARY}; padding:40px;")
        self._empty_lbl.hide()
        root.addWidget(self._empty_lbl)

    def _refresh_headers(self):
        self._table.setHorizontalHeaderLabels([
            _t("col_product_name"), _t("product_name_ne"),
            _t("unit_label"), _t("col_is_milk"),
            _t("col_default_rate"), _t("col_actions"),
        ])

    def _load_products(self):
        from modules.products.product_service import get_all_products
        self._products = get_all_products()
        self._render_table()

    def _render_table(self):
        self._table.setRowCount(0)
        if not self._products:
            self._table.hide(); self._empty_lbl.show(); return
        self._empty_lbl.hide(); self._table.show()
        self._table.setRowCount(len(self._products))

        for row, p in enumerate(self._products):
            # English name
            self._table.setItem(row, self.COL_NAME,
                                QTableWidgetItem(p.product_name_english))
            # Nepali name
            self._table.setItem(row, self.COL_NEPALI,
                                QTableWidgetItem(p.product_name_nepali))
            # Unit
            unit_text = _t("unit_liter") if p.unit == "LITER" else _t("unit_kg")
            self._table.setItem(row, self.COL_UNIT,
                                QTableWidgetItem(unit_text))
            # Type (milk / other)
            type_text = _t("milk_type_label") if p.is_milk == 1 else _t("other_type_label")
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)
            if p.is_milk == 1:
                type_item.setForeground(QBrush(QColor("#1D4ED8")))
            else:
                type_item.setForeground(QBrush(QColor(COLOR_TEXT_SECONDARY)))
            self._table.setItem(row, self.COL_TYPE, type_item)

            # Default rate
            if p.default_rate is not None:
                rate_text = f"NPR {p.default_rate:,.2f}"
            else:
                rate_text = "—"
            rate_item = QTableWidgetItem(rate_text)
            rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(row, self.COL_RATE, rate_item)

            # Edit button
            self._table.setCellWidget(row, self.COL_ACTIONS,
                                      self._action_widget(p))
            self._table.setRowHeight(row, 46)

    def _action_widget(self, product_row) -> QWidget:
        cell = QWidget()
        cell.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(6)

        edit_btn = QPushButton(_t("edit"))
        edit_btn.setFixedHeight(30)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_ACCENT}; color:white; border:none;
                border-radius:4px; padding:0 14px; font-size:9pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT_DARK}; }}
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda _, p=product_row: self._open_edit(p))
        lay.addWidget(edit_btn)
        lay.addStretch()
        return cell

    def _open_add(self):
        from ui.products.product_form_dialog import ProductFormDialog
        dlg = ProductFormDialog(parent=self)
        dlg.saved.connect(lambda _: self._load_products())
        dlg.exec()

    def _open_edit(self, product_row):
        from ui.products.product_form_dialog import ProductFormDialog
        dlg = ProductFormDialog(product_row=product_row, parent=self)
        dlg.saved.connect(lambda _: self._load_products())
        dlg.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_products()
        self._refresh_headers()
        self._title.setText(_t("product_management"))
        self._sub.setText(_t("product_list"))
        self._add_btn.setText(f"＋  {_t('add_product')}")
