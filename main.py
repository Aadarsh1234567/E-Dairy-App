"""
Santosh E-Dairy — Application Entry Point
Phase 1 + Phase 2: Foundation & Database Layer
"""

import sys
import os
from pathlib import Path

# Ensure project root is on the path when running as script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap, QPainter, QBrush

from constants import APP_NAME, APP_VERSION, STYLESHEET, COLOR_SIDEBAR, COLOR_ACCENT


def make_splash() -> QSplashScreen:
    """Build a simple branded splash screen."""
    px = QPixmap(480, 280)
    px.fill(QColor(COLOR_SIDEBAR))

    painter = QPainter(px)
    painter.setRenderHint(QPainter.Antialiasing)

    # Accent bar at top
    painter.fillRect(0, 0, 480, 6, QColor(COLOR_ACCENT))

    # App name
    f = QFont("Segoe UI", 26, QFont.Bold)
    painter.setFont(f)
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(px.rect().adjusted(0, 40, 0, 0), Qt.AlignHCenter | Qt.AlignTop, APP_NAME)

    # Subtitle
    f2 = QFont("Segoe UI", 11)
    painter.setFont(f2)
    painter.setPen(QColor(COLOR_ACCENT))
    painter.drawText(px.rect().adjusted(0, 100, 0, 0), Qt.AlignHCenter | Qt.AlignTop,
                     "Dairy Cooperative Management System")

    # Version
    f3 = QFont("Segoe UI", 9)
    painter.setFont(f3)
    painter.setPen(QColor("#6B7280"))
    painter.drawText(px.rect().adjusted(0, 0, -16, -16), Qt.AlignRight | Qt.AlignBottom,
                     f"Version {APP_VERSION}")

    # Loading text
    painter.setPen(QColor("#B8C4D8"))
    painter.drawText(px.rect().adjusted(0, 0, 0, -40), Qt.AlignHCenter | Qt.AlignBottom,
                     "Initialising database...")

    painter.end()

    splash = QSplashScreen(px, Qt.WindowStaysOnTopHint)
    splash.setFont(QFont("Segoe UI", 9))
    return splash


def main():
    # ── Qt application ────────────────────────────────────────
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Santosh Dairy Cooperative")
    app.setStyleSheet(STYLESHEET)

    # Global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # ── Splash screen ─────────────────────────────────────────
    splash = make_splash()
    splash.show()
    app.processEvents()

    # ── Database initialisation ───────────────────────────────
    splash.showMessage("  Connecting to database...",
                       Qt.AlignLeft | Qt.AlignBottom, QColor("#B8C4D8"))
    app.processEvents()

    from database.database import initialize_database
    result = initialize_database()

    if result["errors"]:
        splash.hide()
        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to initialise the database:\n\n{chr(10).join(result['errors'])}\n\n"
            f"Please check that the application has write permission to:\n{result['db_path']}"
        )
        sys.exit(1)

    splash.showMessage("  Loading application...",
                       Qt.AlignLeft | Qt.AlignBottom, QColor("#B8C4D8"))
    app.processEvents()

    # ── Main window ───────────────────────────────────────────
    from ui.main_window import MainWindow
    window = MainWindow()

    # Close splash and show main window after brief delay
    def launch():
        splash.finish(window)
        window.show()
        window.activateWindow()

        if result["is_new_db"]:
            QMessageBox.information(
                window,
                "Welcome to Santosh E-Dairy",
                f"Database created successfully.\n\n"
                f"📁 Location: {result['db_path']}\n"
                f"🗄  Schema Version: {result['schema_version']}\n\n"
                f"Default products (Milk, Butter, Paneer, Ghee, Cheese, Curd) "
                f"have been loaded.\n\n"
                f"You are ready to begin Phase 3 — Authentication."
            )

    QTimer.singleShot(1200, launch)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
