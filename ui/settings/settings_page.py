"""
Settings page — Phase 10.
Sections: Organization, System, Pricing Formula, Security.
All saves go to the 'settings' DB table via get_setting/set_setting.
Language change takes effect immediately across the app on next navigation.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QSpinBox, QScrollArea,
)
from PySide6.QtCore import Qt
from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_CARD, COLOR_BORDER,
    COLOR_DANGER, COLOR_SUCCESS, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_SIDEBAR,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load()

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # Title + Save button (sticky header)
        hdr = QHBoxLayout()
        self._title = QLabel(_t("settings"))
        self._title.setStyleSheet("font-size:20pt; font-weight:bold;")
        hdr.addWidget(self._title, 1)

        self._save_btn = QPushButton(f"💾  {_t('save_settings')}")
        self._save_btn.setObjectName("primary_btn")
        self._save_btn.setFixedHeight(42)
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.clicked.connect(self._save)
        hdr.addWidget(self._save_btn)
        root.addLayout(hdr)
        root.addSpacing(4)

        # Global message label
        self._msg = QLabel("")
        self._msg.setWordWrap(True)
        self._msg.setMinimumHeight(24)
        self._msg.setStyleSheet(f"font-size:9pt; color:{COLOR_SUCCESS};")
        root.addWidget(self._msg)
        root.addSpacing(12)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 8, 0)
        cl.setSpacing(16)

        # ── Section 1: Organization ──────────────────────────────
        cl.addWidget(self._section_header("organization_settings", "🏢"))
        org_card = self._card()
        ol = QVBoxLayout(org_card); ol.setSpacing(12)

        self._org_name_en  = self._field_row(ol, "organization_name_en",  required=True)
        self._org_name_ne  = self._field_row(ol, "organization_name_ne")
        self._org_addr_en  = self._field_row(ol, "organization_address_en")
        self._org_addr_ne  = self._field_row(ol, "organization_address_ne")
        self._org_phone    = self._field_row(ol, "organization_phone")
        cl.addWidget(org_card)

        # ── Section 2: System ────────────────────────────────────
        cl.addWidget(self._section_header("system_settings", "⚙️"))
        sys_card = self._card()
        sl = QVBoxLayout(sys_card); sl.setSpacing(16)

        # Language
        lang_row = QHBoxLayout(); lang_row.setSpacing(16)
        lang_lbl = self._lbl("language_setting")
        lang_lbl.setFixedWidth(200)
        lang_row.addWidget(lang_lbl)
        self._lang_combo = QComboBox()
        self._lang_combo.addItem("नेपाली", "NE")
        self._lang_combo.addItem("English", "EN")
        self._lang_combo.setStyleSheet(self._combo_style())
        self._lang_combo.setFixedWidth(180)
        lang_row.addWidget(self._lang_combo)
        lang_row.addStretch()
        sl.addLayout(lang_row)

        # Idle lock
        lock_row = QHBoxLayout(); lock_row.setSpacing(16)
        lock_lbl = self._lbl("idle_lock_setting")
        lock_lbl.setFixedWidth(200)
        lock_row.addWidget(lock_lbl)
        self._idle_spin = QSpinBox()
        self._idle_spin.setRange(1, 120)
        self._idle_spin.setSuffix(f"  {_t('minutes_label')}")
        self._idle_spin.setStyleSheet(self._spin_style())
        self._idle_spin.setFixedWidth(140)
        lock_row.addWidget(self._idle_spin)
        lock_row.addStretch()
        sl.addLayout(lock_row)

        # Receipt width
        rcpt_row = QHBoxLayout(); rcpt_row.setSpacing(16)
        rcpt_lbl = self._lbl("receipt_width_setting")
        rcpt_lbl.setFixedWidth(200)
        rcpt_row.addWidget(rcpt_lbl)
        self._rcpt_combo = QComboBox()
        self._rcpt_combo.addItem("80mm", "80")
        self._rcpt_combo.addItem("58mm", "58")
        self._rcpt_combo.setStyleSheet(self._combo_style())
        self._rcpt_combo.setFixedWidth(120)
        rcpt_row.addWidget(self._rcpt_combo)
        rcpt_row.addStretch()
        sl.addLayout(rcpt_row)

        # Auto-backup hour
        bk_row = QHBoxLayout(); bk_row.setSpacing(16)
        bk_lbl = self._lbl("backup_hour_setting")
        bk_lbl.setFixedWidth(200)
        bk_row.addWidget(bk_lbl)
        self._backup_spin = QSpinBox()
        self._backup_spin.setRange(0, 23)
        self._backup_spin.setSuffix(f"  {_t('hour_label')} (0–23)")
        self._backup_spin.setStyleSheet(self._spin_style())
        self._backup_spin.setFixedWidth(160)
        bk_row.addWidget(self._backup_spin)
        bk_row.addStretch()
        sl.addLayout(bk_row)

        cl.addWidget(sys_card)

        # ── Section 3: Pricing formula ───────────────────────────
        cl.addWidget(self._section_header("pricing_formula_setting", "📐"))
        formula_card = self._card()
        fl = QVBoxLayout(formula_card); fl.setSpacing(12)

        # Current formula + test result
        cur_row = QHBoxLayout(); cur_row.setSpacing(16)
        self._cur_formula_lbl = QLabel("")
        self._cur_formula_lbl.setStyleSheet(
            f"font-size:10pt; color:{COLOR_SIDEBAR}; font-weight:bold; "
            f"background:#EEF2FF; border-radius:4px; padding:6px 10px;")
        cur_row.addWidget(QLabel(f"{_t('current_formula')}:"))
        cur_row.addWidget(self._cur_formula_lbl)
        cur_row.addStretch()
        fl.addLayout(cur_row)

        self._test_lbl = QLabel("")
        self._test_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        fl.addWidget(self._test_lbl)

        # New formula input + validate
        inp_row = QHBoxLayout(); inp_row.setSpacing(10)
        inp_row.addWidget(self._lbl("pricing_formula_setting"))
        self._formula_input = QLineEdit()
        self._formula_input.setStyleSheet(self._input_style())
        self._formula_input.setPlaceholderText("(fat*8)+(snf*4)")
        self._formula_input.setFixedHeight(38)
        inp_row.addWidget(self._formula_input, 1)
        val_btn = QPushButton(f"✓  {_t('validate_formula')}")
        val_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_SIDEBAR}; color:white; border:none;
                border-radius:6px; padding:7px 16px; font-size:9pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:#2E4A7A; }}
        """)
        val_btn.setCursor(Qt.PointingHandCursor)
        val_btn.clicked.connect(self._validate_formula)
        inp_row.addWidget(val_btn)
        fl.addLayout(inp_row)

        hint = QLabel(f"ℹ  {_t('formula_variables')}  •  {_t('formula_hint')}")
        hint.setStyleSheet(f"font-size:8pt; color:{COLOR_TEXT_SECONDARY};")
        hint.setWordWrap(True)
        fl.addWidget(hint)

        self._formula_msg = QLabel("")
        self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
        fl.addWidget(self._formula_msg)

        save_formula_btn = QPushButton(_t("save_settings"))
        save_formula_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_ACCENT}; color:white; border:none;
                border-radius:6px; padding:8px 20px; font-size:9pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT_DARK}; }}
        """)
        save_formula_btn.setCursor(Qt.PointingHandCursor)
        save_formula_btn.clicked.connect(self._save_formula)
        save_formula_btn.setFixedWidth(160)
        fl.addWidget(save_formula_btn)
        cl.addWidget(formula_card)

        # ── Section 4: Security ──────────────────────────────────
        cl.addWidget(self._section_header("security_settings", "🔒"))
        sec_card = self._card()
        secl = QVBoxLayout(sec_card); secl.setSpacing(10)

        sec_desc = QLabel(_t("change_password"))
        sec_desc.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        secl.addWidget(sec_desc)

        chpw_btn = QPushButton(f"🔑  {_t('change_password')}")
        chpw_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{COLOR_ACCENT};
                border:1.5px solid {COLOR_ACCENT}; border-radius:6px;
                padding:9px 20px; font-size:10pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT}; color:white; }}
        """)
        chpw_btn.setCursor(Qt.PointingHandCursor)
        chpw_btn.setFixedWidth(240)
        chpw_btn.clicked.connect(self._change_password)
        secl.addWidget(chpw_btn)
        cl.addWidget(sec_card)

        cl.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    # ── Helper widget builders ────────────────────────────────────────────────
    def _section_header(self, key: str, icon: str) -> QLabel:
        lbl = QLabel(f"{icon}  {_t(key)}")
        lbl.setStyleSheet(
            f"font-size:11pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};"
            f"padding-bottom:2px; border-bottom:2px solid {COLOR_ACCENT};"
            f"margin-top:4px;")
        return lbl

    def _card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{COLOR_CARD}; border:1px solid {COLOR_BORDER};
                border-radius:10px;
            }}
        """)
        card.setContentsMargins(0, 0, 0, 0)
        return card

    def _lbl(self, key: str) -> QLabel:
        lbl = QLabel(_t(key))
        lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        return lbl

    def _field_row(self, parent_layout, key: str, required: bool = False) -> QLineEdit:
        row = QHBoxLayout(); row.setSpacing(16)
        lbl_text = _t(key) + (" *" if required else "")
        lbl = QLabel(lbl_text)
        lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        lbl.setFixedWidth(200)
        row.addWidget(lbl)
        inp = QLineEdit()
        inp.setStyleSheet(self._input_style())
        inp.setFixedHeight(36)
        row.addWidget(inp, 1)
        parent_layout.addLayout(row)
        return inp

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:7px 12px; font-size:10pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QLineEdit:focus {{ border-color:{COLOR_ACCENT}; }}
        """

    def _combo_style(self) -> str:
        return f"""
            QComboBox {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:6px 12px; font-size:10pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QComboBox:focus {{ border-color:{COLOR_ACCENT}; }}
        """

    def _spin_style(self) -> str:
        return f"""
            QSpinBox {{
                border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                padding:6px 10px; font-size:10pt;
                background:white; color:{COLOR_TEXT_PRIMARY};
            }}
            QSpinBox:focus {{ border-color:{COLOR_ACCENT}; }}
        """

    # ── Load from DB ─────────────────────────────────────────────────────────
    def _load(self):
        from database.database import get_setting
        from services.pricing_service import get_active_formula, calculate_rate

        self._org_name_en.setText(get_setting("organization_name_english", ""))
        self._org_name_ne.setText(get_setting("organization_name_nepali",  ""))
        self._org_addr_en.setText(get_setting("organization_address_english", ""))
        self._org_addr_ne.setText(get_setting("organization_address_nepali",  ""))
        self._org_phone.setText(  get_setting("organization_phone", ""))

        # Language
        lang = get_setting("default_language", "NE")
        idx = self._lang_combo.findData(lang)
        self._lang_combo.setCurrentIndex(idx if idx >= 0 else 0)

        # Idle lock
        try:
            self._idle_spin.setValue(int(get_setting("idle_lock_minutes", "15")))
        except ValueError:
            self._idle_spin.setValue(15)

        # Receipt width
        rw = get_setting("receipt_width_mm", "80")
        ri = self._rcpt_combo.findData(rw)
        self._rcpt_combo.setCurrentIndex(ri if ri >= 0 else 0)

        # Backup hour
        try:
            self._backup_spin.setValue(int(get_setting("auto_backup_hour", "18")))
        except ValueError:
            self._backup_spin.setValue(18)

        # Formula
        formula = get_active_formula()
        self._cur_formula_lbl.setText(formula)
        self._formula_input.setText(formula)
        try:
            test_rate = calculate_rate(4, 8, formula=formula)
            self._test_lbl.setText(f"{_t('formula_test_result')}: NPR {test_rate:,.2f}")
        except Exception:
            self._test_lbl.setText("")

        self._msg.setText("")

    # ── Save all non-formula settings ─────────────────────────────────────────
    def _save(self):
        from database.database import set_setting, write_audit_log, get_session

        name_en = self._org_name_en.text().strip()
        if not name_en:
            self._show_msg(_t("name_required"), error=True)
            return

        settings_to_save = {
            "organization_name_english":    name_en,
            "organization_name_nepali":     self._org_name_ne.text().strip(),
            "organization_address_english": self._org_addr_en.text().strip(),
            "organization_address_nepali":  self._org_addr_ne.text().strip(),
            "organization_phone":           self._org_phone.text().strip(),
            "default_language":             self._lang_combo.currentData(),
            "idle_lock_minutes":            str(self._idle_spin.value()),
            "receipt_width_mm":             self._rcpt_combo.currentData(),
            "auto_backup_hour":             str(self._backup_spin.value()),
        }

        try:
            for key, value in settings_to_save.items():
                set_setting(key, value)
            with get_session() as session:
                write_audit_log(session, "SETTINGS_CHANGED",
                                f"Settings updated by operator")
                session.commit()
            self._show_msg(_t("settings_saved_ok"), error=False)
        except Exception as e:
            self._show_msg(_t("unexpected_error", err=str(e)), error=True)

    # ── Validate formula ──────────────────────────────────────────────────────
    def _validate_formula(self):
        from services.pricing_service import validate_formula, calculate_rate, PricingError
        formula = self._formula_input.text().strip()
        if not formula:
            self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
            self._formula_msg.setText(_t("formula_invalid"))
            return
        try:
            validate_formula(formula)
            test_rate = calculate_rate(4, 8, formula=formula)
            self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_SUCCESS};")
            self._formula_msg.setText(
                f"✓ {_t('formula_validated')}  |  "
                f"{_t('formula_test_result')}: NPR {test_rate:,.2f}"
            )
        except PricingError as e:
            self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
            self._formula_msg.setText(str(e))

    # ── Save formula ──────────────────────────────────────────────────────────
    def _save_formula(self):
        from services.pricing_service import set_new_formula, validate_formula, PricingError
        formula = self._formula_input.text().strip()
        if not formula:
            self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
            self._formula_msg.setText(_t("formula_invalid"))
            return
        try:
            validate_formula(formula)
            set_new_formula(formula)
            self._cur_formula_lbl.setText(formula)
            self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_SUCCESS};")
            self._formula_msg.setText(f"✓ {_t('settings_saved_ok')}")
            # Update test result
            from services.pricing_service import calculate_rate
            test_rate = calculate_rate(4, 8, formula=formula)
            self._test_lbl.setText(f"{_t('formula_test_result')}: NPR {test_rate:,.2f}")
        except PricingError as e:
            self._formula_msg.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
            self._formula_msg.setText(str(e))

    # ── Change password ───────────────────────────────────────────────────────
    def _change_password(self):
        from ui.login.change_password_dialog import ChangePasswordDialog
        dlg = ChangePasswordDialog(forced=False, parent=self)
        dlg.exec()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _show_msg(self, text: str, error: bool = False):
        color = COLOR_DANGER if error else COLOR_SUCCESS
        self._msg.setStyleSheet(f"font-size:9pt; color:{color};")
        self._msg.setText(text)

    def showEvent(self, event):
        super().showEvent(event)
        self._title.setText(_t("settings"))
        self._save_btn.setText(f"💾  {_t('save_settings')}")
        self._load()
