"""
Farmer form dialog — Add / Edit farmer. Bilingual.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from PySide6.QtCore import Qt, Signal
from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_CARD, COLOR_BORDER,
    COLOR_DANGER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_SUCCESS,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class FarmerFormDialog(QDialog):
    """
    Modal dialog for adding or editing a farmer.
    saved(farmer_code) emitted on success.
    """
    saved = Signal(str)   # emits farmer_code

    def __init__(self, farmer_row=None, parent=None):
        """
        farmer_row=None  → Add mode
        farmer_row=FarmerRow → Edit mode
        """
        super().__init__(parent)
        self._edit_mode = farmer_row is not None
        self._farmer_row = farmer_row
        self.setModal(True)
        self.setFixedWidth(480)
        self.setWindowTitle(
            _t("edit_farmer") if self._edit_mode else _t("add_farmer")
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
        title_text = _t("edit_farmer") if self._edit_mode else _t("add_farmer")
        title = QLabel(f"{icon}  {title_text}")
        title.setStyleSheet(
            f"font-size:15pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        lay.addWidget(title)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{COLOR_BORDER};")
        lay.addWidget(div)

        # Fields
        self._code_input   = self._field(lay, "farmer_code",    required=True)
        self._name_en_input= self._field(lay, "farmer_name_en", required=True)
        self._name_ne_input= self._field(lay, "farmer_name_ne", required=False)
        self._phone_input  = self._field(lay, "phone",           required=False)
        self._address_input= self._field(lay, "address",         required=False)

        # Message
        self._msg = QLabel("")
        self._msg.setWordWrap(True)
        self._msg.setMinimumHeight(28)
        self._msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
        lay.addWidget(self._msg)

        # Buttons
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

        self._code_input.setFocus()
        # Enter on any field triggers save
        for f in [self._code_input, self._name_en_input,
                  self._name_ne_input, self._phone_input, self._address_input]:
            f.returnPressed.connect(self._save)

    def _field(self, parent_layout, key: str, required: bool) -> QLineEdit:
        label_text = _t(key) + (" *" if required else "")
        lbl = QLabel(label_text.upper())
        lbl.setStyleSheet(
            f"font-size:8pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY};"
            f"letter-spacing:0.8px;")
        parent_layout.addWidget(lbl)
        inp = QLineEdit()
        inp.setStyleSheet(f"""
            QLineEdit {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:9px 12px; font-size:10pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus {{ border-color:{COLOR_ACCENT}; }}
        """)
        parent_layout.addWidget(inp)
        return inp

    def _populate(self):
        r = self._farmer_row
        self._code_input.setText(r.farmer_code)
        self._name_en_input.setText(r.name_english)
        self._name_ne_input.setText(r.name_nepali)
        self._phone_input.setText(r.phone)
        self._address_input.setText(r.address)

    # ── Save ────────────────────────────────────────────────────────────────
    def _save(self):
        from modules.farmers.farmer_service import add_farmer, edit_farmer, FarmerError

        self._save_btn.setEnabled(False)
        self._msg.setText("")
        try:
            if self._edit_mode:
                row = edit_farmer(
                    farmer_id    = self._farmer_row.farmer_id,
                    farmer_code  = self._code_input.text(),
                    name_english = self._name_en_input.text(),
                    name_nepali  = self._name_ne_input.text(),
                    phone        = self._phone_input.text(),
                    address      = self._address_input.text(),
                )
                self._ok(_t("farmer_updated"))
            else:
                row = add_farmer(
                    farmer_code  = self._code_input.text(),
                    name_english = self._name_en_input.text(),
                    name_nepali  = self._name_ne_input.text(),
                    phone        = self._phone_input.text(),
                    address      = self._address_input.text(),
                )
                self._ok(_t("farmer_saved"))
            self.saved.emit(row.farmer_code)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(700, self.accept)

        except FarmerError as e:
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
