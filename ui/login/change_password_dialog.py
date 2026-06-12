"""
Change Password dialog — bilingual (NE default).
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor
from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_CARD, COLOR_BORDER,
    COLOR_DANGER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_SUCCESS,
)


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


def _pw_row(placeholder: str):
    field = QLineEdit()
    field.setEchoMode(QLineEdit.Password)
    field.setPlaceholderText(placeholder)
    field.setStyleSheet(f"""
        QLineEdit {{
            border:1.5px solid {COLOR_BORDER}; border-right:none;
            border-radius:6px 0 0 6px; padding:9px 12px;
            font-size:10pt; background:white; color:{COLOR_TEXT_PRIMARY};
        }}
        QLineEdit:focus {{ border-color:{COLOR_ACCENT}; }}
    """)
    toggle = QPushButton("👁")
    toggle.setFixedSize(40, 40)
    toggle.setCheckable(True)
    toggle.setStyleSheet(f"""
        QPushButton {{
            background:white; border:1.5px solid {COLOR_BORDER};
            border-left:none; border-radius:0 6px 6px 0;
            font-size:12pt; color:{COLOR_TEXT_SECONDARY};
        }}
        QPushButton:checked {{ color:{COLOR_ACCENT}; border-color:{COLOR_ACCENT}; }}
    """)
    toggle.clicked.connect(
        lambda chk, f=field: f.setEchoMode(
            QLineEdit.Normal if chk else QLineEdit.Password))
    return field, toggle


class ChangePasswordDialog(QDialog):
    password_changed = Signal()

    def __init__(self, forced: bool = False, parent=None):
        super().__init__(parent)
        self._forced = forced
        self.setWindowTitle(_t("change_password"))
        self.setModal(True)
        self.setFixedWidth(440)
        if forced:
            self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(12)

        if self._forced:
            icon, title = "🔐", _t("set_password")
            intro, intro_color = _t("forced_intro"), COLOR_DANGER
        else:
            icon, title = "🔒", _t("change_password")
            intro, intro_color = _t("voluntary_intro"), COLOR_TEXT_SECONDARY

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:28pt;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size:15pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};")
        title_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(title_lbl)

        intro_lbl = QLabel(intro)
        intro_lbl.setWordWrap(True)
        intro_lbl.setStyleSheet(f"font-size:9pt; color:{intro_color};")
        intro_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(intro_lbl)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{COLOR_BORDER};")
        lay.addWidget(div)

        def lbl(key):
            l = QLabel(_t(key))
            l.setStyleSheet(
                f"font-size:8pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY}; letter-spacing:0.8px;")
            return l

        lay.addWidget(lbl("current_password"))
        r1 = QHBoxLayout(); r1.setSpacing(0)
        self._old_pw, t1 = _pw_row(_t("enter_current_pw"))
        r1.addWidget(self._old_pw, 1); r1.addWidget(t1)
        lay.addLayout(r1)

        lay.addWidget(lbl("new_password"))
        r2 = QHBoxLayout(); r2.setSpacing(0)
        self._new_pw, t2 = _pw_row(_t("min_6_chars"))
        r2.addWidget(self._new_pw, 1); r2.addWidget(t2)
        lay.addLayout(r2)

        lay.addWidget(lbl("confirm_password"))
        r3 = QHBoxLayout(); r3.setSpacing(0)
        self._confirm_pw, t3 = _pw_row(_t("repeat_new_pw"))
        r3.addWidget(self._confirm_pw, 1); r3.addWidget(t3)
        lay.addLayout(r3)

        self._msg_lbl = QLabel("")
        self._msg_lbl.setWordWrap(True)
        self._msg_lbl.setAlignment(Qt.AlignCenter)
        self._msg_lbl.setMinimumHeight(30)
        self._msg_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
        lay.addWidget(self._msg_lbl)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        if not self._forced:
            cancel_btn = QPushButton(_t("cancel"))
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background:transparent; color:{COLOR_TEXT_SECONDARY};
                    border:1.5px solid {COLOR_BORDER}; border-radius:6px;
                    padding:9px 20px; font-size:10pt;
                }}
                QPushButton:hover {{ border-color:{COLOR_ACCENT}; color:{COLOR_ACCENT}; }}
            """)
            cancel_btn.clicked.connect(self.reject)
            btn_row.addWidget(cancel_btn)

        btn_label = _t("set_password_btn") if self._forced else _t("change_password_btn")
        self._save_btn = QPushButton(btn_label)
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

        for f in (self._old_pw, self._new_pw, self._confirm_pw):
            f.returnPressed.connect(self._save)
        self._old_pw.setFocus()

    def _save(self):
        from modules.auth.auth_service import (
            change_password, AuthError, AccountLockedError, WrongPasswordError,
        )
        old = self._old_pw.text()
        new = self._new_pw.text()
        conf = self._confirm_pw.text()

        if not old or not new or not conf:
            self._error(_t("all_fields_required")); return

        self._save_btn.setEnabled(False)
        try:
            change_password(old, new, conf)
            self._msg_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_SUCCESS};")
            self._msg_lbl.setText(_t("pw_changed_ok"))
            self.password_changed.emit()
            QTimer.singleShot(900, self.accept)
        except (AccountLockedError, WrongPasswordError, AuthError) as e:
            self._error(str(e))
            if isinstance(e, WrongPasswordError):
                self._old_pw.clear(); self._old_pw.setFocus()
        finally:
            self._save_btn.setEnabled(True)

    def _error(self, msg):
        self._msg_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER};")
        self._msg_lbl.setText(msg)
