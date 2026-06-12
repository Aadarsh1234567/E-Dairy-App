"""
Shared constants, colour palette, and Qt stylesheet for Santosh E-Dairy.
"""

APP_NAME        = "Santosh E-Dairy"
APP_VERSION     = "1.0.0"
ORG_NAME        = "Santosh Dairy Cooperative"
SCHEMA_VERSION  = 1

# ── Colour palette ─────────────────────────────────────────────────────────────
# Deep navy + warm saffron accent — clean, trustworthy, readable
COLOR_BG            = "#F5F6FA"      # window background
COLOR_SIDEBAR       = "#1B2A4A"      # deep navy sidebar
COLOR_SIDEBAR_HOVER = "#243659"
COLOR_SIDEBAR_SEL   = "#2E4A7A"
COLOR_ACCENT        = "#E8A020"      # saffron/golden accent
COLOR_ACCENT_DARK   = "#C8881A"
COLOR_CARD          = "#FFFFFF"
COLOR_BORDER        = "#DDE1EA"
COLOR_TEXT_PRIMARY  = "#1A1F36"
COLOR_TEXT_SECONDARY= "#6B7280"
COLOR_TEXT_LIGHT    = "#FFFFFF"
COLOR_SUCCESS       = "#2E7D32"
COLOR_WARNING       = "#F59E0B"
COLOR_DANGER        = "#DC2626"
COLOR_DANGER_LIGHT  = "#FEF2F2"

# ── Typography sizes ──────────────────────────────────────────────────────────
FONT_FAMILY   = "Segoe UI, Arial, sans-serif"
FONT_XS       = 9
FONT_SM       = 10
FONT_MD       = 12
FONT_LG       = 14
FONT_XL       = 18
FONT_DISPLAY  = 24

# ── Global Qt stylesheet ───────────────────────────────────────────────────────
STYLESHEET = f"""
/* ── Window & Base ── */
QMainWindow, QDialog, QWidget {{
    background-color: {COLOR_BG};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: {FONT_SM}pt;
    color: {COLOR_TEXT_PRIMARY};
}}

/* ── Sidebar ── */
#sidebar {{
    background-color: {COLOR_SIDEBAR};
    min-width: 220px;
    max-width: 220px;
}}
#app_title_label {{
    color: {COLOR_TEXT_LIGHT};
    font-size: {FONT_LG}pt;
    font-weight: bold;
    padding: 20px 16px 4px 16px;
}}
#app_sub_label {{
    color: {COLOR_ACCENT};
    font-size: {FONT_XS}pt;
    padding: 0px 16px 20px 16px;
}}

/* ── Sidebar nav buttons ── */
#nav_btn {{
    background-color: transparent;
    color: #B8C4D8;
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 0px;
    font-size: {FONT_SM}pt;
}}
#nav_btn:hover {{
    background-color: {COLOR_SIDEBAR_HOVER};
    color: {COLOR_TEXT_LIGHT};
}}
#nav_btn[active="true"] {{
    background-color: {COLOR_SIDEBAR_SEL};
    color: {COLOR_TEXT_LIGHT};
    border-left: 3px solid {COLOR_ACCENT};
    padding-left: 17px;
}}

/* ── Content area ── */
#content_area {{
    background-color: {COLOR_BG};
    padding: 24px;
}}
#page_title {{
    font-size: {FONT_XL}pt;
    font-weight: bold;
    color: {COLOR_TEXT_PRIMARY};
}}
#page_subtitle {{
    font-size: {FONT_SM}pt;
    color: {COLOR_TEXT_SECONDARY};
}}

/* ── Stat cards ── */
#stat_card {{
    background-color: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    padding: 16px;
}}
#stat_card_value {{
    font-size: {FONT_DISPLAY}pt;
    font-weight: bold;
    color: {COLOR_TEXT_PRIMARY};
}}
#stat_card_label {{
    font-size: {FONT_XS}pt;
    color: {COLOR_TEXT_SECONDARY};
    text-transform: uppercase;
    letter-spacing: 1px;
}}
#stat_card_icon {{
    font-size: 22pt;
}}

/* ── Primary button ── */
QPushButton#primary_btn {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_TEXT_LIGHT};
    border: none;
    border-radius: 6px;
    padding: 10px 22px;
    font-size: {FONT_SM}pt;
    font-weight: bold;
}}
QPushButton#primary_btn:hover {{
    background-color: {COLOR_ACCENT_DARK};
}}
QPushButton#primary_btn:pressed {{
    background-color: #A87015;
}}

/* ── Secondary button ── */
QPushButton#secondary_btn {{
    background-color: transparent;
    color: {COLOR_ACCENT};
    border: 2px solid {COLOR_ACCENT};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: {FONT_SM}pt;
    font-weight: bold;
}}
QPushButton#secondary_btn:hover {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_TEXT_LIGHT};
}}

/* ── Danger button ── */
QPushButton#danger_btn {{
    background-color: {COLOR_DANGER};
    color: {COLOR_TEXT_LIGHT};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: {FONT_SM}pt;
    font-weight: bold;
}}
QPushButton#danger_btn:hover {{
    background-color: #B91C1C;
}}

/* ── Quick action buttons on dashboard ── */
QPushButton#quick_btn {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 14px 10px;
    font-size: {FONT_SM}pt;
    text-align: center;
}}
QPushButton#quick_btn:hover {{
    background-color: {COLOR_SIDEBAR};
    color: {COLOR_TEXT_LIGHT};
    border-color: {COLOR_SIDEBAR};
}}

/* ── Tables ── */
QTableWidget {{
    background-color: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    gridline-color: {COLOR_BORDER};
    selection-background-color: #EEF2FF;
    selection-color: {COLOR_TEXT_PRIMARY};
    font-size: {FONT_SM}pt;
}}
QTableWidget::item {{
    padding: 8px;
    border: none;
}}
QHeaderView::section {{
    background-color: {COLOR_SIDEBAR};
    color: {COLOR_TEXT_LIGHT};
    padding: 10px 8px;
    border: none;
    font-size: {FONT_XS}pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Form inputs ── */
QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {COLOR_CARD};
    border: 1.5px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: {FONT_SM}pt;
    color: {COLOR_TEXT_PRIMARY};
    min-height: 20px;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLOR_ACCENT};
    outline: none;
}}
QLineEdit:disabled, QComboBox:disabled {{
    background-color: #F0F2F7;
    color: {COLOR_TEXT_SECONDARY};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    border: 1px solid {COLOR_BORDER};
    selection-background-color: #EEF2FF;
}}

/* ── Labels ── */
QLabel#form_label {{
    font-size: {FONT_XS}pt;
    font-weight: bold;
    color: {COLOR_TEXT_SECONDARY};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QLabel#error_label {{
    color: {COLOR_DANGER};
    font-size: {FONT_XS}pt;
}}
QLabel#success_label {{
    color: {COLOR_SUCCESS};
    font-size: {FONT_XS}pt;
}}

/* ── Status bar ── */
QStatusBar {{
    background-color: {COLOR_SIDEBAR};
    color: #B8C4D8;
    font-size: {FONT_XS}pt;
    padding: 2px 8px;
}}

/* ── Scroll bars ── */
QScrollBar:vertical {{
    background: {COLOR_BG};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_SECONDARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ── Message boxes ── */
QMessageBox {{
    background-color: {COLOR_CARD};
}}
QMessageBox QPushButton {{
    min-width: 80px;
    padding: 6px 16px;
}}

/* ── Separator ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {COLOR_BORDER};
}}
"""
