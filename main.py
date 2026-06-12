"""
Santosh E-Dairy — Application Entry Point
Phase 1+2+3 — Bilingual (NE default)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QStackedWidget
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QFontDatabase

from constants import APP_NAME, APP_VERSION, STYLESHEET, COLOR_SIDEBAR, COLOR_ACCENT, FONT_FAMILY


def load_font() -> QFont:
    """Load Noto Sans Devanagari and return it as the app font."""
    font_path = str(Path(__file__).resolve().parent / "assets" / "fonts" / "NotoSansDevanagari.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    families = QFontDatabase.applicationFontFamilies(font_id)
    family = families[0] if families else FONT_FAMILY
    return QFont(family, 10)


def make_splash(app_font: QFont) -> QSplashScreen:
    px = QPixmap(480, 280)
    px.fill(QColor(COLOR_SIDEBAR))
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.fillRect(0, 0, 480, 6, QColor(COLOR_ACCENT))

    f = QFont(app_font.family(), 24, QFont.Bold)
    p.setFont(f); p.setPen(QColor("#FFFFFF"))
    p.drawText(px.rect().adjusted(0, 40, 0, 0), Qt.AlignHCenter | Qt.AlignTop, APP_NAME)

    p.setFont(QFont(app_font.family(), 11))
    p.setPen(QColor(COLOR_ACCENT))
    p.drawText(px.rect().adjusted(0, 100, 0, 0), Qt.AlignHCenter | Qt.AlignTop,
               "Dairy Cooperative Management System")

    p.setFont(QFont(app_font.family(), 9))
    p.setPen(QColor("#6B7280"))
    p.drawText(px.rect().adjusted(0, 0, -16, -16), Qt.AlignRight | Qt.AlignBottom,
               f"v{APP_VERSION}")
    p.setPen(QColor("#B8C4D8"))
    p.drawText(px.rect().adjusted(0, 0, 0, -40), Qt.AlignHCenter | Qt.AlignBottom,
               "Initialising database...")
    p.end()

    splash = QSplashScreen(px, Qt.WindowStaysOnTopHint)
    splash.setFont(app_font)
    return splash


class AppController(QStackedWidget):
    PAGE_LOGIN = 0
    PAGE_MAIN  = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)

        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._lock_due_to_idle)

        self._build_pages()
        self._show_login()

        QApplication.instance().installEventFilter(self)

    def _build_pages(self):
        from ui.login.login_screen import LoginScreen
        from ui.main_window import MainWindow

        self._login_screen = LoginScreen()
        self._main_window  = MainWindow(lock_callback=self._show_login)

        self.addWidget(self._login_screen)
        self.addWidget(self._main_window)

        self._login_screen.login_successful.connect(self._on_login_success)
        self._login_screen.change_password_required.connect(self._on_change_password_required)

    def _show_login(self):
        self._idle_timer.stop()
        self._login_screen.reset()
        self.setCurrentIndex(self.PAGE_LOGIN)
        self.setWindowTitle(APP_NAME)

    def _on_login_success(self):
        self._start_idle_timer()
        self.setCurrentIndex(self.PAGE_MAIN)
        from database.database import get_setting
        org = get_setting("organization_name_english", "Santosh Dairy Cooperative")
        self.setWindowTitle(f"{APP_NAME}  —  {org}")

    def _on_change_password_required(self):
        from ui.login.change_password_dialog import ChangePasswordDialog
        dlg = ChangePasswordDialog(forced=True, parent=self)
        dlg.password_changed.connect(self._on_login_success)
        dlg.exec()

    def _lock_due_to_idle(self):
        self._idle_timer.stop()
        self._show_login()

    def _start_idle_timer(self):
        from modules.auth.auth_service import get_idle_lock_minutes
        self._idle_timer.start(get_idle_lock_minutes() * 60 * 1000)

    def _reset_idle_timer(self):
        if self.currentIndex() == self.PAGE_MAIN and self._idle_timer.isActive():
            self._idle_timer.start()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseMove, QEvent.MouseButtonPress,
                             QEvent.KeyPress, QEvent.Wheel):
            self._reset_idle_timer()
        return super().eventFilter(obj, event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Santosh Dairy Cooperative")

    # Load Noto Sans Devanagari FIRST, before stylesheet
    app_font = load_font()
    app.setFont(app_font)
    app.setStyleSheet(STYLESHEET)

    splash = make_splash(app_font)
    splash.show()
    app.processEvents()

    splash.showMessage("  Connecting to database...",
                       Qt.AlignLeft | Qt.AlignBottom, QColor("#B8C4D8"))
    app.processEvents()

    from database.database import initialize_database
    result = initialize_database()

    if result["errors"]:
        splash.hide()
        QMessageBox.critical(None, "Database Error",
            f"Failed to initialise the database:\n\n"
            f"{chr(10).join(result['errors'])}\n\nLocation: {result['db_path']}")
        sys.exit(1)

    splash.showMessage("  Loading application...",
                       Qt.AlignLeft | Qt.AlignBottom, QColor("#B8C4D8"))
    app.processEvents()

    controller = AppController()

    def launch():
        splash.finish(controller)
        controller.show()
        controller.activateWindow()
        if result["is_new_db"]:
            from translations import t
            QMessageBox.information(controller, t("welcome"),
                f"{t('db_created')}\n\n"
                f"📁 {result['db_path']}\n"
                f"🗄  Schema v{result['schema_version']}\n\n"
                f"Default password: admin123\n"
                f"You will be asked to change it on first login.")

    QTimer.singleShot(1200, launch)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
