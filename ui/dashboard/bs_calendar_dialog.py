"""
BS Calendar Picker — Phase 6 add-on.
A visually attractive month-grid calendar rendered entirely in Bikram Sambat,
navigable from 2083 BS (current) to 2100 BS (library hard limit).

Opened by clicking the date on the dashboard's BSDateTimeWidget.
"""

import nepali_datetime as nd
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QComboBox, QWidget,
)
from PySide6.QtCore import Qt, Signal

from constants import (
    COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_SIDEBAR, COLOR_CARD,
    COLOR_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BG,
)

MIN_YEAR = 2083   # current BS year — no dairy records exist before this
MAX_YEAR = 2100   # nepali_datetime hard limit


def _t(key, **kw):
    from translations import t
    return t(key, **kw)


class BSCalendarDialog(QDialog):
    """
    Modal calendar picker. Shows one BS month at a time in a 7-column grid.
    Year/month navigation clamped to [MIN_YEAR, MAX_YEAR].
    """

    date_selected = Signal(object)   # emits nepali_datetime.date

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumWidth(440)

        today = nd.date.today()
        self._view_year  = today.year
        self._view_month = today.month
        self._today       = today
        self._selected    = today

        from database.database import get_setting
        self._lang = get_setting("default_language", "NE")

        self.setWindowTitle(_t("bs_calendar_label"))
        self._setup_ui()
        self._render_month()

    # ── UI scaffold ───────────────────────────────────────────────────────────
    def _setup_ui(self):
        self.setStyleSheet(f"QDialog {{ background:{COLOR_BG}; }}")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header band (navy gradient like dashboard hero) ──────
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLOR_SIDEBAR}, stop:1 #2E4A7A
                );
                border-radius: 0px;
            }}
        """)
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(24, 18, 24, 16)
        h_lay.setSpacing(10)

        title = QLabel(f"📅  {_t('bs_calendar_label')}")
        title.setStyleSheet("color:white; font-size:13pt; font-weight:bold; background:transparent;")
        h_lay.addWidget(title)

        # Nav row: prev | Month Year dropdown(s) | next
        nav_row = QHBoxLayout(); nav_row.setSpacing(8)

        self._prev_btn = QPushButton("‹")
        self._next_btn = QPushButton("›")
        for btn in (self._prev_btn, self._next_btn):
            btn.setFixedSize(36, 36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.12); color:white;
                    border:none; border-radius:18px; font-size:16pt; font-weight:bold;
                }
                QPushButton:hover { background: rgba(255,255,255,0.22); }
                QPushButton:disabled { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); }
            """)
        self._prev_btn.clicked.connect(self._go_prev_month)
        self._next_btn.clicked.connect(self._go_next_month)

        self._month_combo = QComboBox()
        self._month_combo.setStyleSheet(self._combo_style())
        self._populate_months()
        self._month_combo.currentIndexChanged.connect(self._on_month_combo_changed)

        self._year_combo = QComboBox()
        self._year_combo.setStyleSheet(self._combo_style())
        for y in range(MIN_YEAR, MAX_YEAR + 1):
            label = self._np_year(y) if self._lang == "NE" else str(y)
            self._year_combo.addItem(label, y)
        self._year_combo.currentIndexChanged.connect(self._on_year_combo_changed)

        nav_row.addWidget(self._prev_btn)
        nav_row.addWidget(self._month_combo, 1)
        nav_row.addWidget(self._year_combo, 1)
        nav_row.addWidget(self._next_btn)
        h_lay.addLayout(nav_row)
        root.addWidget(header)

        # ── Weekday header row ────────────────────────────────────
        wd_frame = QFrame()
        wd_frame.setStyleSheet(f"background:{COLOR_CARD}; border-bottom:1px solid {COLOR_BORDER};")
        wd_lay = QHBoxLayout(wd_frame)
        wd_lay.setContentsMargins(16, 10, 16, 10)
        wd_lay.setSpacing(4)
        weekday_labels_ne = ["आइत","सोम","मंगल","बुध","बिहि","शुक्र","शनि"]
        weekday_labels_en = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
        labels = weekday_labels_ne if self._lang == "NE" else weekday_labels_en
        for i, wd in enumerate(labels):
            lbl = QLabel(wd)
            lbl.setAlignment(Qt.AlignCenter)
            color = "#DC2626" if i == 0 else COLOR_TEXT_SECONDARY  # Sunday red-ish accent
            lbl.setStyleSheet(f"font-size:8pt; font-weight:bold; color:{color};")
            wd_lay.addWidget(lbl, 1)
        root.addWidget(wd_frame)

        # ── Calendar grid ─────────────────────────────────────────
        grid_container = QFrame()
        grid_container.setStyleSheet(f"background:{COLOR_CARD};")
        self._grid_layout = QGridLayout(grid_container)
        self._grid_layout.setContentsMargins(16, 12, 16, 12)
        self._grid_layout.setSpacing(6)
        root.addWidget(grid_container)

        # ── Footer: selected date + Today button + Close ───────────
        footer = QFrame()
        footer.setStyleSheet(f"background:{COLOR_CARD}; border-top:1px solid {COLOR_BORDER};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 14, 20, 16)

        self._selected_lbl = QLabel("")
        self._selected_lbl.setStyleSheet(
            f"font-size:9pt; color:{COLOR_TEXT_SECONDARY};")
        f_lay.addWidget(self._selected_lbl, 1)

        today_btn = QPushButton(self._today_label())
        today_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{COLOR_ACCENT};
                border:1.5px solid {COLOR_ACCENT}; border-radius:6px;
                padding:7px 16px; font-size:9pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT}; color:white; }}
        """)
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.clicked.connect(self._go_today)
        f_lay.addWidget(today_btn)

        close_btn = QPushButton(_t("close"))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_ACCENT}; color:white; border:none;
                border-radius:6px; padding:7px 20px; font-size:9pt; font-weight:bold;
            }}
            QPushButton:hover {{ background:{COLOR_ACCENT_DARK}; }}
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        f_lay.addWidget(close_btn)

        root.addWidget(footer)

    def _combo_style(self) -> str:
        return """
            QComboBox {
                background: rgba(255,255,255,0.12); color:white;
                border:1px solid rgba(255,255,255,0.2); border-radius:6px;
                padding:6px 10px; font-size:10pt; font-weight:bold;
            }
            QComboBox::drop-down { border:none; width:20px; }
            QComboBox QAbstractItemView {
                background:white; color:black; selection-background-color:#EEF2FF;
            }
        """

    def _today_label(self) -> str:
        return "आज" if self._lang == "NE" else "Today"

    # ── Month/year dropdown population ──────────────────────────────────────
    def _populate_months(self):
        from utils.bs_calendar import MONTH_NAMES_NE, MONTH_NAMES_EN
        names = MONTH_NAMES_NE if self._lang == "NE" else MONTH_NAMES_EN
        self._month_combo.blockSignals(True)
        self._month_combo.clear()
        for m in range(1, 13):
            self._month_combo.addItem(names[m], m)
        self._month_combo.blockSignals(False)

    def _np_year(self, y: int) -> str:
        from utils.bs_calendar import to_np_digits
        return to_np_digits(y)

    # ── Navigation ────────────────────────────────────────────────────────────
    def _go_prev_month(self):
        y, m = self._view_year, self._view_month
        if m == 1:
            y, m = y - 1, 12
        else:
            m -= 1
        if y < MIN_YEAR:
            return
        self._view_year, self._view_month = y, m
        self._sync_combos()
        self._render_month()

    def _go_next_month(self):
        y, m = self._view_year, self._view_month
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
        if y > MAX_YEAR:
            return
        self._view_year, self._view_month = y, m
        self._sync_combos()
        self._render_month()

    def _go_today(self):
        self._view_year  = self._today.year
        self._view_month = self._today.month
        self._selected    = self._today
        self._sync_combos()
        self._render_month()

    def _on_month_combo_changed(self, idx):
        m = self._month_combo.currentData()
        if m is None:
            return
        self._view_month = m
        self._render_month()

    def _on_year_combo_changed(self, idx):
        y = self._year_combo.currentData()
        if y is None:
            return
        self._view_year = y
        self._render_month()

    def _sync_combos(self):
        self._month_combo.blockSignals(True)
        self._year_combo.blockSignals(True)
        self._month_combo.setCurrentIndex(self._view_month - 1)
        self._year_combo.setCurrentIndex(self._view_year - MIN_YEAR)
        self._month_combo.blockSignals(False)
        self._year_combo.blockSignals(False)

    # ── Rendering ────────────────────────────────────────────────────────────
    def _render_month(self):
        from utils.bs_calendar import days_in_bs_month, to_np_digits

        # Clear existing grid widgets
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Update nav button enabled state at boundaries
        self._prev_btn.setEnabled(not (self._view_year == MIN_YEAR and self._view_month == 1))
        self._next_btn.setEnabled(not (self._view_year == MAX_YEAR and self._view_month == 12))

        first_day = nd.date(self._view_year, self._view_month, 1)
        offset = first_day.weekday()   # 0=Sunday per our verified mapping
        total_days = days_in_bs_month(self._view_year, self._view_month)

        row, col = 0, offset
        for day in range(1, total_days + 1):
            cell = self._day_cell(day)
            self._grid_layout.addWidget(cell, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

        for c in range(7):
            self._grid_layout.setColumnStretch(c, 1)

        self._update_selected_label()

    def _day_cell(self, day: int) -> QWidget:
        from utils.bs_calendar import to_np_digits

        is_today    = (self._view_year == self._today.year and
                       self._view_month == self._today.month and
                       day == self._today.day)
        is_selected = (self._view_year == self._selected.year and
                       self._view_month == self._selected.month and
                       day == self._selected.day)

        label_text = to_np_digits(day) if self._lang == "NE" else str(day)
        btn = QPushButton(label_text)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)

        if is_today and is_selected:
            style = f"""
                QPushButton {{
                    background:{COLOR_ACCENT}; color:white; border:2px solid {COLOR_ACCENT_DARK};
                    border-radius:8px; font-size:10pt; font-weight:bold;
                }}
            """
        elif is_today:
            style = f"""
                QPushButton {{
                    background:white; color:{COLOR_ACCENT}; border:2px solid {COLOR_ACCENT};
                    border-radius:8px; font-size:10pt; font-weight:bold;
                }}
                QPushButton:hover {{ background:#FFF8E1; }}
            """
        elif is_selected:
            style = f"""
                QPushButton {{
                    background:{COLOR_SIDEBAR}; color:white; border:none;
                    border-radius:8px; font-size:10pt; font-weight:bold;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background:transparent; color:{COLOR_TEXT_PRIMARY}; border:none;
                    border-radius:8px; font-size:10pt;
                }}
                QPushButton:hover {{ background:#F0F2F7; }}
            """
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda _, d=day: self._on_day_clicked(d))
        return btn

    def _on_day_clicked(self, day: int):
        self._selected = nd.date(self._view_year, self._view_month, day)
        self._render_month()
        self.date_selected.emit(self._selected)

    def _update_selected_label(self):
        from utils.bs_calendar import format_bs_date, bs_to_ad
        bs_str = format_bs_date(self._selected, lang=self._lang, include_weekday=True)
        ad_date = bs_to_ad(self._selected)
        self._selected_lbl.setText(f"{bs_str}   ({ad_date.strftime('%Y-%m-%d')} AD)")
