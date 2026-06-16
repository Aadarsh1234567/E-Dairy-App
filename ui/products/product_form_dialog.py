"""
Product form dialog — Add / Edit product. Bilingual.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QComboBox,
    QDoubleSpinBox, QRadioButton, QButtonGroup, QWidget,
)
from PySide6.QtCore import Qt, Signal
from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_BORDER,
    COLOR_DANGER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_SUCCESS,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class ProductFormDialog(QDialog):
    """
    Modal dialog for adding or editing a product.
    saved emitted on success with the product_id.
    """
    saved = Signal(int)

    def __init__(self, product_row=None, parent=None):
        super().__init__(parent)
        self._edit_mode   = product_row is not None
        self._product_row = product_row
        self.setModal(True)
        self.setFixedWidth(460)
        self.setWindowTitle(
            _t("edit_product") if self._edit_mode else _t("add_product")
        )
        self._setup_ui()
        if self._edit_mode:
            self._populate()

    # ── UI ──────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(14)

        # Title
        icon = "✏️" if self._edit_mode else "➕"
        title = QLabel(f"{icon}  {_t('edit_product') if self._edit_mode else _t('add_product')}")
        title.setStyleSheet(
            f"font-size:14pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        lay.addWidget(title)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{COLOR_BORDER};")
        lay.addWidget(div)

        # ── Product type (only shown on Add) ────────────────────
        if not self._edit_mode:
            lay.addWidget(self._section_label("is_milk_label"))
            type_row = QHBoxLayout(); type_row.setSpacing(20)
            self._rb_other = QRadioButton(_t("is_milk_no"))
            self._rb_milk  = QRadioButton(_t("is_milk_yes"))
            self._rb_other.setChecked(True)
            self._rb_group = QButtonGroup()
            self._rb_group.addButton(self._rb_other, 0)
            self._rb_group.addButton(self._rb_milk,  1)
            self._rb_other.toggled.connect(self._on_type_changed)
            self._rb_milk.toggled.connect(self._on_type_changed)
            type_row.addWidget(self._rb_other)
            type_row.addWidget(self._rb_milk)
            type_row.addStretch()
            lay.addLayout(type_row)
        else:
            # In edit mode show type as read-only info
            self._rb_group = None
            type_text = _t("is_milk_yes") if self._product_row.is_milk == 1 else _t("is_milk_no")
            unit_info = QLabel(f"{_t('is_milk_label')}: {type_text}  |  {_t('unit_label')}: {self._product_row.unit}")
            unit_info.setStyleSheet(
                f"font-size:9pt; color:{COLOR_TEXT_SECONDARY}; "
                f"background:#F0F2F7; border-radius:4px; padding:6px 10px;")
            lay.addWidget(unit_info)
            if self._product_row.is_milk == 1:
                milk_note = QLabel(f"ℹ  {_t('milk_unit_fixed')}")
                milk_note.setWordWrap(True)
                milk_note.setStyleSheet(f"font-size:8pt; color:{COLOR_TEXT_SECONDARY};")
                lay.addWidget(milk_note)

        # ── Name (English) ───────────────────────────────────────
        lay.addWidget(self._section_label("product_name_en", required=True))
        self._name_en = QLineEdit()
        self._name_en.setStyleSheet(self._input_style())
        lay.addWidget(self._name_en)

        # ── Name (Nepali) ────────────────────────────────────────
        lay.addWidget(self._section_label("product_name_ne"))
        self._name_ne = QLineEdit()
        self._name_ne.setStyleSheet(self._input_style())
        lay.addWidget(self._name_ne)

        # ── Default rate ─────────────────────────────────────────
        lay.addWidget(self._section_label("default_rate_label"))
        self._rate_spin = QDoubleSpinBox()
        self._rate_spin.setRange(0, 999999.99)
        self._rate_spin.setDecimals(2)
        self._rate_spin.setValue(0.00)
        self._rate_spin.setSpecialValueText(_t("default_rate_hint"))
        self._rate_spin.setStyleSheet(self._input_style())
        lay.addWidget(self._rate_spin)

        hint = QLabel(_t("default_rate_hint"))
        hint.setStyleSheet(f"font-size:8pt; color:{COLOR_TEXT_SECONDARY};")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        # ── Message ──────────────────────────────────────────────
        self._msg = QLabel("")
        self._msg.setWordWrap(True)
        self._msg.setMinimumHeight(28)
        self._msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
        lay.addWidget(self._msg)

        # ── Buttons ──────────────────────────────────────────────
        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        cancel = QPushButton(_t("cancel"))
        cancel.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{COLOR_TEXT_SECONDARY};
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:9px 20px; font-size:10pt;
            }}
            QPushButton:hover {{ border-color:{COLOR_ACCENT}; color:{COLOR_ACCENT}; }}
        """)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        self._save_btn = QPushButton(_t("save"))
        self._save_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_ACCENT}; color:white; border:none;
                border-radius:6px; padding:9px 24px;
                font-size:10pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT_DARK}; }}
            QPushButton:disabled {{ background:#D1D5DB; color:#9CA3AF; }}
        """)
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.clicked.connect(self._save)
        btn_row.addWidget(self._save_btn)
        lay.addLayout(btn_row)

        self._name_en.setFocus()
        self._name_en.returnPressed.connect(self._save)
        self._name_ne.returnPressed.connect(self._save)

    def _section_label(self, key: str, required: bool = False) -> QLabel:
        text = _t(key) + (" *" if required else "")
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            f"font-size:8pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY};"
            f"letter-spacing:0.8px;")
        return lbl

    def _input_style(self) -> str:
        return f"""
            QLineEdit, QDoubleSpinBox {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:9px 12px; font-size:10pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QDoubleSpinBox:focus {{ border-color:{COLOR_ACCENT}; }}
        """

    def _on_type_changed(self):
        """When milk type selected, show info about fixed unit."""
        pass  # Unit handled transparently in service

    def _populate(self):
        self._name_en.setText(self._product_row.product_name_english)
        self._name_ne.setText(self._product_row.product_name_nepali)
        rate = self._product_row.default_rate
        self._rate_spin.setValue(rate if rate is not None else 0.00)

    # ── Save ────────────────────────────────────────────────────────────────
    def _save(self):
        from modules.products.product_service import (
            add_product, edit_product, ProductError
        )
        self._save_btn.setEnabled(False)
        self._msg.setText("")

        name_en  = self._name_en.text().strip()
        name_ne  = self._name_ne.text().strip()
        rate_val = self._rate_spin.value()
        rate     = rate_val if rate_val > 0 else None

        try:
            if self._edit_mode:
                row = edit_product(
                    product_id   = self._product_row.product_id,
                    name_english = name_en,
                    name_nepali  = name_ne,
                    default_rate = rate,
                )
                self._ok(_t("product_updated"))
            else:
                is_milk = 1 if (self._rb_group and self._rb_group.checkedId() == 1) else 0
                row = add_product(
                    name_english = name_en,
                    name_nepali  = name_ne,
                    is_milk      = is_milk,
                    default_rate = rate,
                )
                self._ok(_t("product_saved"))

            self.saved.emit(row.product_id)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(700, self.accept)

        except ProductError as e:
            self._error(str(e))
        except Exception as e:
            self._error(_t("unexpected_error", err=str(e)))
        finally:
            self._save_btn.setEnabled(True)

    def _ok(self, msg):
        self._msg.setStyleSheet(f"font-size:9pt; color:{COLOR_SUCCESS};")
        self._msg.setText(msg)

    def _error(self, msg):
        self._msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
        self._msg.setText(msg)
