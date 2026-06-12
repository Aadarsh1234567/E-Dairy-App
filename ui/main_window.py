"""
Main application window.
Sidebar navigation + content area.
Pages are loaded lazily as the user navigates.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QStatusBar, QSizePolicy, QSpacerItem,
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QIcon

from constants import (
    APP_NAME, APP_VERSION, COLOR_SIDEBAR,
    COLOR_ACCENT, COLOR_TEXT_LIGHT, COLOR_TEXT_SECONDARY,
    COLOR_SUCCESS, COLOR_WARNING,
)
from database.database import get_setting


class NavButton(QPushButton):
    """Sidebar navigation button."""

    def __init__(self, icon: str, label: str, page_key: str, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.setObjectName("nav_btn")
        self.page_key = page_key
        self.setCheckable(False)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(44)
        self.setProperty("active", "false")

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    """
    Main application window.
    Sidebar + stacked content pages.
    """

    NAV_ITEMS = [
        ("🏠", "Dashboard",          "dashboard"),
        ("🥛", "Milk Collection",    "milk_collection"),
        ("📦", "Product Transaction","product_transaction"),
        ("💳", "Payments",           "payments"),
        ("🏪", "Inventory",          "inventory"),
        ("📊", "Reports",            "reports"),
        ("👨‍🌾", "Farmers",           "farmers"),
        ("⚙️", "Settings",          "settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nav_buttons: dict[str, NavButton] = {}
        self._pages: dict[str, QWidget] = {}
        self._current_page = ""

        self._setup_window()
        self._setup_ui()
        self._navigate("dashboard")

        # Clock in status bar
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    # ── Window setup ──────────────────────────────────────────
    def _setup_window(self):
        org = get_setting("organization_name_english", "Santosh Dairy Cooperative")
        self.setWindowTitle(f"{APP_NAME}  —  {org}")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)

    # ── UI construction ───────────────────────────────────────
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        root.addWidget(self._build_sidebar())

        # Content
        self._stack = QStackedWidget()
        self._stack.setObjectName("content_area")
        root.addWidget(self._stack, 1)

        # Status bar
        self._status = QStatusBar()
        self._status.setSizeGripEnabled(False)
        self.setStatusBar(self._status)

        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet(f"color: #B8C4D8; font-size:8pt; padding-right:8px;")
        self._version_lbl = QLabel(f"Santosh E-Dairy  v{APP_VERSION}")
        self._version_lbl.setStyleSheet(f"color: #B8C4D8; font-size:8pt; padding-left:8px;")
        self._db_lbl = QLabel("● Database Connected")
        self._db_lbl.setStyleSheet(f"color: #4ADE80; font-size:8pt;")

        self._status.addWidget(self._version_lbl)
        self._status.addWidget(self._db_lbl)
        self._status.addPermanentWidget(self._clock_lbl)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # App title block
        title_frame = QFrame()
        title_frame.setStyleSheet(
            f"background-color: rgba(0,0,0,0.15); border-bottom: 1px solid rgba(255,255,255,0.08);"
        )
        tf_layout = QVBoxLayout(title_frame)
        tf_layout.setContentsMargins(16, 20, 16, 16)
        tf_layout.setSpacing(2)

        app_lbl = QLabel(APP_NAME)
        app_lbl.setStyleSheet(
            f"color: white; font-size: 14pt; font-weight: bold; background: transparent;"
        )
        sub_lbl = QLabel(get_setting("organization_name_english", "Santosh Dairy Cooperative"))
        sub_lbl.setStyleSheet(
            f"color: {COLOR_ACCENT}; font-size: 8pt; background: transparent;"
        )
        sub_lbl.setWordWrap(True)
        tf_layout.addWidget(app_lbl)
        tf_layout.addWidget(sub_lbl)
        layout.addWidget(title_frame)

        # Nav separator label
        sep_lbl = QLabel("  NAVIGATION")
        sep_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.3); font-size:7pt; "
            "letter-spacing:2px; padding: 14px 16px 4px 16px; background:transparent;"
        )
        layout.addWidget(sep_lbl)

        # Nav buttons
        for icon, label, key in self.NAV_ITEMS:
            btn = NavButton(icon, label, key)
            btn.clicked.connect(lambda _, k=key: self._navigate(k))
            layout.addWidget(btn)
            self._nav_buttons[key] = btn

        layout.addStretch(1)

        # Bottom: version + logout
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet(
            "border-top: 1px solid rgba(255,255,255,0.08); background:transparent;"
        )
        bf_layout = QVBoxLayout(bottom_frame)
        bf_layout.setContentsMargins(12, 10, 12, 12)
        bf_layout.setSpacing(6)

        logout_btn = QPushButton("🔒  Lock Screen")
        logout_btn.setStyleSheet(
            f"background: rgba(255,255,255,0.05); color:#B8C4D8; "
            f"border:1px solid rgba(255,255,255,0.1); border-radius:6px; "
            f"padding:8px; font-size:9pt; text-align:left;"
        )
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self._lock_screen)
        bf_layout.addWidget(logout_btn)

        layout.addWidget(bottom_frame)
        return sidebar

    # ── Navigation ────────────────────────────────────────────
    def _navigate(self, page_key: str):
        if page_key not in self._pages:
            self._pages[page_key] = self._build_page(page_key)
            self._stack.addWidget(self._pages[page_key])

        self._stack.setCurrentWidget(self._pages[page_key])
        self._current_page = page_key

        # Update active state on nav buttons
        for key, btn in self._nav_buttons.items():
            btn.set_active(key == page_key)

        # Refresh dashboard data when navigating to it
        if page_key == "dashboard":
            try:
                self._pages["dashboard"]._refresh_data()
            except Exception:
                pass

    def _build_page(self, key: str) -> QWidget:
        """Lazy-load each page widget."""
        if key == "dashboard":
            from ui.dashboard.dashboard_page import DashboardPage
            return DashboardPage(navigate_callback=self._navigate)

        # Placeholder for future modules
        return self._placeholder_page(key)

    def _placeholder_page(self, key: str) -> QWidget:
        """Temporary placeholder for modules not yet built."""
        labels = {
            "milk_collection":    ("🥛", "Milk Collection",     "Phase 6 — Coming Soon"),
            "product_transaction":("📦", "Product Transaction", "Phase 7 — Coming Soon"),
            "payments":           ("💳", "Payments",            "Phase 8 — Coming Soon"),
            "inventory":          ("🏪", "Inventory",           "Phase 9 — Coming Soon"),
            "reports":            ("📊", "Reports",             "Phase 12 — Coming Soon"),
            "farmers":            ("👨‍🌾", "Farmers",            "Phase 4 — Coming Soon"),
            "settings":           ("⚙️", "Settings",           "Phase 10 — Coming Soon"),
        }
        icon, title, subtitle = labels.get(key, ("📄", key.title(), "Coming Soon"))

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:48pt;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size:22pt; font-weight:bold; color:#1A1F36;")
        title_lbl.setAlignment(Qt.AlignCenter)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("font-size:11pt; color:#6B7280;")
        sub_lbl.setAlignment(Qt.AlignCenter)

        hint_lbl = QLabel("This module will be built in the next development phase.")
        hint_lbl.setStyleSheet("font-size:9pt; color:#9CA3AF; margin-top:6px;")
        hint_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)
        layout.addWidget(hint_lbl)

        return page

    # ── Clock ─────────────────────────────────────────────────
    def _update_clock(self):
        now = QDateTime.currentDateTime()
        self._clock_lbl.setText(now.toString("ddd dd MMM yyyy   hh:mm:ss"))

    # ── Lock screen ───────────────────────────────────────────
    def _lock_screen(self):
        """Show login window and hide main window — Phase 3 will wire this fully."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Lock Screen",
            "Screen locking will be active from Phase 3 (Authentication Module).\n\n"
            "Close the application to exit."
        )
