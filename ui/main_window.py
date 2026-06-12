"""
Main application window — bilingual (NE default).
Sidebar navigation + stacked content pages.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QStatusBar,
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont
from constants import (
    APP_NAME, APP_VERSION, COLOR_SIDEBAR, COLOR_SIDEBAR_HOVER,
    COLOR_SIDEBAR_SEL, COLOR_ACCENT, COLOR_TEXT_LIGHT, COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
)
from database.database import get_setting


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, page_key: str, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.setObjectName("nav_btn")
        self.page_key = page_key
        self.setCheckable(False)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(46)
        self.setProperty("active", "false")

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    # (icon, translation_key, page_key)
    NAV_ITEMS = [
        ("🏠", "dashboard",           "dashboard"),
        ("🥛", "milk_collection",     "milk_collection"),
        ("📦", "product_transaction", "product_transaction"),
        ("💳", "payments",            "payments"),
        ("🏪", "inventory",           "inventory"),
        ("📊", "reports",             "reports"),
        ("👨‍🌾","farmers",             "farmers"),
        ("⚙️", "settings",           "settings"),
    ]

    def __init__(self, lock_callback=None, parent=None):
        super().__init__(parent)
        self._nav_buttons: dict[str, NavButton] = {}
        self._pages: dict[str, QWidget] = {}
        self._current_page = ""
        self._lock_callback = lock_callback
        self._setup_window()
        self._setup_ui()
        self._navigate("dashboard")
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _setup_window(self):
        org = get_setting("organization_name_english", "Santosh Dairy Cooperative")
        self.setWindowTitle(f"{APP_NAME}  —  {org}")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())
        self._stack = QStackedWidget()
        self._stack.setObjectName("content_area")
        root.addWidget(self._stack, 1)

        self._status = QStatusBar()
        self._status.setSizeGripEnabled(False)
        self.setStatusBar(self._status)

        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet("color:#B8C4D8; font-size:8pt; padding-right:8px;")
        self._ver_lbl = QLabel(f"Santosh E-Dairy  v{APP_VERSION}")
        self._ver_lbl.setStyleSheet("color:#B8C4D8; font-size:8pt; padding-left:8px;")
        self._db_lbl = QLabel(f"● {_t('db_connected').replace('● ','')}")
        self._db_lbl.setStyleSheet("color:#4ADE80; font-size:8pt;")

        self._status.addWidget(self._ver_lbl)
        self._status.addWidget(self._db_lbl)
        self._status.addPermanentWidget(self._clock_lbl)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Title block
        tf = QFrame()
        tf.setStyleSheet(
            "background-color:rgba(0,0,0,0.15);"
            "border-bottom:1px solid rgba(255,255,255,0.08);")
        tf_lay = QVBoxLayout(tf)
        tf_lay.setContentsMargins(16, 20, 16, 16)
        tf_lay.setSpacing(2)

        app_lbl = QLabel(APP_NAME)
        app_lbl.setStyleSheet("color:white; font-size:14pt; font-weight:bold; background:transparent;")
        org = get_setting("organization_name_nepali", "") or \
              get_setting("organization_name_english", "Santosh Dairy Cooperative")
        sub_lbl = QLabel(org)
        sub_lbl.setStyleSheet(f"color:{COLOR_ACCENT}; font-size:8pt; background:transparent;")
        sub_lbl.setWordWrap(True)
        tf_lay.addWidget(app_lbl)
        tf_lay.addWidget(sub_lbl)
        lay.addWidget(tf)

        sep = QLabel(f"  {_t('navigation')}")
        sep.setStyleSheet(
            "color:rgba(255,255,255,0.3); font-size:7pt; letter-spacing:2px;"
            "padding:14px 16px 4px 16px; background:transparent;")
        lay.addWidget(sep)

        for icon, key, page_key in self.NAV_ITEMS:
            btn = NavButton(icon, _t(key), page_key)
            btn.clicked.connect(lambda _, k=page_key: self._navigate(k))
            lay.addWidget(btn)
            self._nav_buttons[page_key] = btn

        lay.addStretch(1)

        # Lock button
        bf = QFrame()
        bf.setStyleSheet("border-top:1px solid rgba(255,255,255,0.08); background:transparent;")
        bf_lay = QVBoxLayout(bf)
        bf_lay.setContentsMargins(12, 10, 12, 12)
        lock_btn = QPushButton(f"🔒  {_t('lock_screen')}")
        lock_btn.setStyleSheet(
            "background:rgba(255,255,255,0.05); color:#B8C4D8;"
            "border:1px solid rgba(255,255,255,0.1); border-radius:6px;"
            "padding:8px; font-size:9pt; text-align:left;")
        lock_btn.setCursor(Qt.PointingHandCursor)
        lock_btn.clicked.connect(self._lock_screen)
        bf_lay.addWidget(lock_btn)
        lay.addWidget(bf)
        return sidebar

    def _navigate(self, page_key: str):
        if page_key not in self._pages:
            self._pages[page_key] = self._build_page(page_key)
            self._stack.addWidget(self._pages[page_key])
        self._stack.setCurrentWidget(self._pages[page_key])
        self._current_page = page_key
        for key, btn in self._nav_buttons.items():
            btn.set_active(key == page_key)
        if page_key == "dashboard":
            try:
                self._pages["dashboard"]._refresh_data()
            except Exception:
                pass

    def _build_page(self, key: str) -> QWidget:
        if key == "dashboard":
            from ui.dashboard.dashboard_page import DashboardPage
            return DashboardPage(navigate_callback=self._navigate)
        return self._placeholder_page(key)

    def _placeholder_page(self, key: str) -> QWidget:
        icons = {
            "milk_collection":    "🥛",
            "product_transaction":"📦",
            "payments":           "💳",
            "inventory":          "🏪",
            "reports":            "📊",
            "farmers":            "👨‍🌾",
            "settings":           "⚙️",
        }
        icon  = icons.get(key, "📄")
        title = _t(key)
        phase = _t(f"ph_{key}")

        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setAlignment(Qt.AlignCenter)

        il = QLabel(icon); il.setStyleSheet("font-size:48pt;"); il.setAlignment(Qt.AlignCenter)
        tl = QLabel(title); tl.setStyleSheet("font-size:22pt; font-weight:bold; color:#1A1F36;"); tl.setAlignment(Qt.AlignCenter)
        pl = QLabel(phase); pl.setStyleSheet("font-size:11pt; color:#6B7280;"); pl.setAlignment(Qt.AlignCenter)
        hl = QLabel(_t("placeholder_hint"))
        hl.setStyleSheet("font-size:9pt; color:#9CA3AF; margin-top:6px;"); hl.setAlignment(Qt.AlignCenter)

        lay.addWidget(il); lay.addWidget(tl); lay.addWidget(pl); lay.addWidget(hl)
        return page

    def _update_clock(self):
        self._clock_lbl.setText(QDateTime.currentDateTime().toString("ddd dd MMM yyyy   hh:mm:ss"))

    def _lock_screen(self):
        if self._lock_callback:
            self._lock_callback()
