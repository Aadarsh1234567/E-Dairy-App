"""
Login screen — bilingual (NE default).
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from constants import (
    COLOR_SIDEBAR, COLOR_ACCENT, COLOR_ACCENT_DARK,
    COLOR_CARD, COLOR_BORDER, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, APP_NAME, APP_VERSION,
)


class LoginScreen(QWidget):
    login_successful         = Signal()
    change_password_required = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lockout_timer = QTimer(self)
        self._lockout_timer.timeout.connect(self._tick_lockout)
        self._setup_ui()

    def _t(self, key, **kw):
        from translations import t
        return t(key, **kw)

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {COLOR_SIDEBAR};")
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD};
                border-radius: 14px;
                border: 1px solid {COLOR_BORDER};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40); shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 36, 40, 36)
        lay.setSpacing(0)

        # Icon
        icon_lbl = QLabel("🥛")
        icon_lbl.setStyleSheet("font-size:36pt; background:transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(icon_lbl)

        # App name
        title_lbl = QLabel(APP_NAME)
        title_lbl.setStyleSheet(
            f"font-size:18pt; font-weight:bold; color:{COLOR_TEXT_PRIMARY};"
            f"background:transparent; margin-top:4px;")
        title_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(title_lbl)

        sub_lbl = QLabel("Dairy Cooperative Management System")
        sub_lbl.setStyleSheet(
            f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};"
            f"background:transparent; margin-bottom:24px;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub_lbl)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color:{COLOR_BORDER}; background:{COLOR_BORDER}; max-height:1px;")
        lay.addWidget(div)
        lay.addSpacing(22)

        # Password label
        self._pw_label = QLabel(self._t("password"))
        self._pw_label.setStyleSheet(
            f"font-size:8pt; font-weight:bold; color:{COLOR_TEXT_SECONDARY};"
            f"letter-spacing:1px; background:transparent; margin-bottom:4px;")
        lay.addWidget(self._pw_label)

        # Password row
        pw_row = QHBoxLayout(); pw_row.setSpacing(0)
        self._pw_input = QLineEdit()
        self._pw_input.setEchoMode(QLineEdit.Password)
        self._pw_input.setPlaceholderText(self._t("enter_password"))
        self._pw_input.setStyleSheet(f"""
            QLineEdit {{
                border:1.5px solid {COLOR_BORDER}; border-right:none;
                border-radius:6px 0 0 6px; padding:10px 14px;
                font-size:11pt; color:{COLOR_TEXT_PRIMARY}; background:white;
            }}
            QLineEdit:focus {{ border-color:{COLOR_ACCENT}; }}
        """)
        self._pw_input.returnPressed.connect(self._attempt_login)

        self._toggle_btn = QPushButton("👁")
        self._toggle_btn.setFixedSize(44, 44)
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background:white; border:1.5px solid {COLOR_BORDER};
                border-left:none; border-radius:0 6px 6px 0;
                font-size:14pt; color:{COLOR_TEXT_SECONDARY};
            }}
            QPushButton:checked {{ color:{COLOR_ACCENT}; border-color:{COLOR_ACCENT}; }}
        """)
        self._toggle_btn.clicked.connect(
            lambda chk: self._pw_input.setEchoMode(
                QLineEdit.Normal if chk else QLineEdit.Password))
        pw_row.addWidget(self._pw_input, 1)
        pw_row.addWidget(self._toggle_btn)
        lay.addLayout(pw_row)
        lay.addSpacing(6)

        # Message
        self._msg_lbl = QLabel("")
        self._msg_lbl.setWordWrap(True)
        self._msg_lbl.setAlignment(Qt.AlignCenter)
        self._msg_lbl.setMinimumHeight(36)
        self._msg_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER}; background:transparent;")
        lay.addWidget(self._msg_lbl)

        # Login button
        self._login_btn = QPushButton(self._t("login_btn"))
        self._login_btn.setFixedHeight(46)
        self._login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color:{COLOR_ACCENT}; color:white; border:none;
                border-radius:8px; font-size:12pt; font-weight:bold;
            }}
            QPushButton:hover {{ background-color:{COLOR_ACCENT_DARK}; }}
            QPushButton:disabled {{ background-color:#D1D5DB; color:#9CA3AF; }}
        """)
        self._login_btn.setCursor(Qt.PointingHandCursor)
        self._login_btn.clicked.connect(self._attempt_login)
        lay.addWidget(self._login_btn)
        lay.addSpacing(16)

        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet(f"font-size:8pt; color:{COLOR_TEXT_SECONDARY}; background:transparent;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(ver_lbl)

        outer.addWidget(card, 0, Qt.AlignCenter)
        self._pw_input.setFocus()

    def _attempt_login(self):
        from modules.auth.auth_service import (
            verify_password, is_first_login,
            AccountLockedError, WrongPasswordError,
        )
        plain = self._pw_input.text()
        if not plain:
            self._show_error(self._t("enter_password_first"))
            return

        self._login_btn.setEnabled(False)
        self._pw_input.setEnabled(False)
        try:
            verify_password(plain)
            self._pw_input.clear()
            self._msg_lbl.setText("")
            if is_first_login():
                self.change_password_required.emit()
            else:
                self.login_successful.emit()
        except AccountLockedError as e:
            self._show_error(str(e))
            self._start_lockout_countdown()
        except WrongPasswordError as e:
            self._show_error(str(e))
            self._pw_input.clear()
            self._pw_input.setEnabled(True)
            self._login_btn.setEnabled(True)
            self._pw_input.setFocus()
        except Exception as e:
            self._show_error(self._t("unexpected_error", err=str(e)))
            self._pw_input.setEnabled(True)
            self._login_btn.setEnabled(True)

    def _start_lockout_countdown(self):
        self._lockout_timer.start(1000)
        self._login_btn.setEnabled(False)
        self._pw_input.setEnabled(False)

    def _tick_lockout(self):
        from modules.auth.auth_service import is_locked
        locked, until = is_locked()
        if locked and until:
            remaining = max(0, int((until - datetime.utcnow()).total_seconds()))
            m, s = divmod(remaining, 60)
            self._show_error(self._t("locked_countdown", m=m, s=s))
        else:
            self._lockout_timer.stop()
            self._show_success(self._t("account_unlocked"))
            self._pw_input.setEnabled(True)
            self._login_btn.setEnabled(True)
            self._pw_input.setFocus()

    def _show_error(self, msg):
        self._msg_lbl.setStyleSheet(f"font-size:9pt; color:{COLOR_DANGER}; background:transparent;")
        self._msg_lbl.setText(msg)

    def _show_success(self, msg):
        self._msg_lbl.setStyleSheet("font-size:9pt; color:#2E7D32; background:transparent;")
        self._msg_lbl.setText(msg)

    def reset(self):
        self._pw_input.clear()
        self._pw_input.setEnabled(True)
        self._login_btn.setEnabled(True)
        self._msg_lbl.setText("")
        self._lockout_timer.stop()
        # Refresh labels in case language changed
        self._pw_label.setText(self._t("password"))
        self._pw_input.setPlaceholderText(self._t("enter_password"))
        self._login_btn.setText(self._t("login_btn"))
        from modules.auth.auth_service import is_locked
        locked, until = is_locked()
        if locked and until:
            self._pw_input.setEnabled(False)
            self._login_btn.setEnabled(False)
            self._start_lockout_countdown()
        self._pw_input.setFocus()
