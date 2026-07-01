"""Reports page — Farmer Statement + Collection Summary. Bilingual."""
import os
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QButtonGroup, QRadioButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from constants import (
    COLOR_ACCENT, COLOR_CARD, COLOR_BORDER,
    COLOR_DANGER, COLOR_SUCCESS, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
)

def _t(k,**kw):
    from translations import t; return t(k,**kw)
def _lang():
    from database.database import get_setting
    return get_setting("default_language","NE")

class ReportsPage(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self._statement=None; self._summary=None
        self._date_from=None; self._date_to=None
        self._setup_ui(); self._load_farmers()

    def _setup_ui(self):
        root=QVBoxLayout(self); root.setContentsMargins(28,24,28,24); root.setSpacing(16)
        self._title=QLabel(_t("reports")); self._title.setStyleSheet("font-size:20pt;font-weight:bold;")
        root.addWidget(self._title)

        card=QFrame()
        card.setStyleSheet(f"QFrame{{background:{COLOR_CARD};border:1px solid {COLOR_BORDER};border-radius:10px;}}")
        cl=QVBoxLayout(card); cl.setContentsMargins(20,16,20,16); cl.setSpacing(14)

        # Report type
        tr=QHBoxLayout(); tr.setSpacing(20)
        tr.addWidget(self._lbl("report_type"))
        self._rb_group=QButtonGroup()
        self._rb_stmt=QRadioButton(_t("farmer_statement"))
        self._rb_sum=QRadioButton(_t("monthly_summary"))
        self._rb_stmt.setChecked(True)
        self._rb_group.addButton(self._rb_stmt,0); self._rb_group.addButton(self._rb_sum,1)
        self._rb_stmt.toggled.connect(self._on_type)
        tr.addWidget(self._rb_stmt); tr.addWidget(self._rb_sum); tr.addStretch()
        cl.addLayout(tr)

        # Farmer selector
        fr=QHBoxLayout(); fr.setSpacing(12)
        fr.addWidget(self._lbl("select_farmer"))
        self._farmer_combo=QComboBox()
        self._farmer_combo.setStyleSheet(self._inp())
        self._farmer_combo.setFixedHeight(38); self._farmer_combo.setMinimumWidth(260)
        fr.addWidget(self._farmer_combo); fr.addStretch()
        cl.addLayout(fr)

        # Date range
        dr=QHBoxLayout(); dr.setSpacing(12)
        dr.addWidget(self._lbl("date_range"))
        self._from_btn=QPushButton(f"{_t('from_date')}: {_t('select_date_range')}")
        self._from_btn.setStyleSheet(self._dbtn()); self._from_btn.setCursor(Qt.PointingHandCursor)
        self._from_btn.clicked.connect(lambda: self._pick("from"))
        dr.addWidget(self._from_btn)
        dr.addWidget(QLabel("—"))
        self._to_btn=QPushButton(f"{_t('to_date')}: {_t('select_date_range')}")
        self._to_btn.setStyleSheet(self._dbtn()); self._to_btn.setCursor(Qt.PointingHandCursor)
        self._to_btn.clicked.connect(lambda: self._pick("to"))
        dr.addWidget(self._to_btn)
        clr_btn=QPushButton(_t("all_time"))
        clr_btn.setStyleSheet(f"QPushButton{{background:transparent;color:{COLOR_TEXT_SECONDARY};border:1.5px solid {COLOR_BORDER};border-radius:6px;padding:6px 14px;font-size:9pt;}}QPushButton:hover{{border-color:{COLOR_ACCENT};color:{COLOR_ACCENT};}}")
        clr_btn.clicked.connect(self._clr_dates)
        dr.addWidget(clr_btn); dr.addStretch()
        cl.addLayout(dr)

        self._msg=QLabel(""); self._msg.setStyleSheet(f"font-size:9pt;color:{COLOR_DANGER};")
        cl.addWidget(self._msg)

        br=QHBoxLayout(); br.setSpacing(10); br.addStretch()
        self._excel_btn=QPushButton(f"📊  {_t('export_excel')}")
        self._excel_btn.setStyleSheet("QPushButton{background:#059669;color:white;border:none;border-radius:6px;padding:9px 18px;font-size:10pt;font-weight:bold;}QPushButton:hover{background:#047857;}QPushButton:disabled{background:#D1D5DB;color:#9CA3AF;}")
        self._excel_btn.setCursor(Qt.PointingHandCursor); self._excel_btn.setEnabled(False)
        self._excel_btn.clicked.connect(self._export_excel); br.addWidget(self._excel_btn)
        self._pdf_btn=QPushButton(f"📄  {_t('export_pdf')}")
        self._pdf_btn.setStyleSheet("QPushButton{background:#DC2626;color:white;border:none;border-radius:6px;padding:9px 18px;font-size:10pt;font-weight:bold;}QPushButton:hover{background:#B91C1C;}QPushButton:disabled{background:#D1D5DB;color:#9CA3AF;}")
        self._pdf_btn.setCursor(Qt.PointingHandCursor); self._pdf_btn.setEnabled(False)
        self._pdf_btn.clicked.connect(self._export_pdf); br.addWidget(self._pdf_btn)
        self._gen_btn=QPushButton(f"🔍  {_t('generate_report')}")
        self._gen_btn.setObjectName("primary_btn"); self._gen_btn.setFixedHeight(42)
        self._gen_btn.setCursor(Qt.PointingHandCursor); self._gen_btn.clicked.connect(self._gen)
        br.addWidget(self._gen_btn); cl.addLayout(br)
        root.addWidget(card)

        self._rtitle=QLabel("")
        self._rtitle.setStyleSheet(f"font-size:11pt;font-weight:bold;color:{COLOR_TEXT_PRIMARY};")
        root.addWidget(self._rtitle)
        self._table=QTableWidget(0,4)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        root.addWidget(self._table,1)

    def _lbl(self,k):
        l=QLabel(_t(k).upper())
        l.setStyleSheet(f"font-size:8pt;font-weight:bold;color:{COLOR_TEXT_SECONDARY};letter-spacing:0.8px;")
        return l
    def _inp(self):
        return f"QComboBox{{border:1.5px solid {COLOR_BORDER};border-radius:6px;padding:7px 12px;font-size:10pt;background:white;color:{COLOR_TEXT_PRIMARY};}}"
    def _dbtn(self):
        return f"QPushButton{{background:white;color:{COLOR_TEXT_PRIMARY};border:1.5px solid {COLOR_BORDER};border-radius:6px;padding:7px 14px;font-size:9pt;text-align:left;}}QPushButton:hover{{border-color:{COLOR_ACCENT};}}"

    def _load_farmers(self):
        from modules.farmers.farmer_service import get_all_farmers
        self._farmer_combo.clear()
        for f in get_all_farmers(include_inactive=True):
            self._farmer_combo.addItem(f"{f.farmer_code} — {f.name_nepali or f.name_english}", f.farmer_id)

    def _pick(self,which):
        from ui.dashboard.bs_calendar_dialog import BSCalendarDialog
        from utils.bs_calendar import bs_to_ad, format_bs_date
        dlg=BSCalendarDialog(parent=self); sel=[]
        dlg.date_selected.connect(lambda d: sel.append(d))
        if dlg.exec() and sel:
            bs_d=sel[-1]; ad_d=bs_to_ad(bs_d)
            bs_str=format_bs_date(bs_d,lang=_lang())
            if which=="from":
                self._date_from=ad_d
                self._from_btn.setText(f"{_t('from_date')}: {bs_str}")
                self._from_btn.setStyleSheet(self._dbtn().replace(COLOR_BORDER,COLOR_ACCENT))
            else:
                self._date_to=ad_d
                self._to_btn.setText(f"{_t('to_date')}: {bs_str}")
                self._to_btn.setStyleSheet(self._dbtn().replace(COLOR_BORDER,COLOR_ACCENT))

    def _clr_dates(self):
        self._date_from=self._date_to=None
        self._from_btn.setText(f"{_t('from_date')}: {_t('select_date_range')}"); self._from_btn.setStyleSheet(self._dbtn())
        self._to_btn.setText(f"{_t('to_date')}: {_t('select_date_range')}"); self._to_btn.setStyleSheet(self._dbtn())

    def _on_type(self):
        self._statement=self._summary=None
        self._table.setRowCount(0); self._rtitle.setText("")
        self._pdf_btn.setEnabled(False); self._excel_btn.setEnabled(False)

    def _item(self,text,align=Qt.AlignLeft|Qt.AlignVCenter,bold=False,color=None):
        item=QTableWidgetItem(str(text)); item.setTextAlignment(align)
        if bold: f=item.font(); f.setBold(True); item.setFont(f)
        if color: item.setForeground(QBrush(QColor(color)))
        return item

    def _gen(self):
        from services.report_service import get_farmer_statement, get_collection_summary, ReportError
        self._msg.setText(""); self._pdf_btn.setEnabled(False); self._excel_btn.setEnabled(False)
        self._statement=self._summary=None
        if self._date_from and self._date_to and self._date_from>self._date_to:
            self._msg.setText(f"{_t('from_date')} > {_t('to_date')}"); return
        try:
            if self._rb_stmt.isChecked():
                if self._farmer_combo.count()==0:
                    self._msg.setText(_t("no_farmers")); return
                self._statement=get_farmer_statement(self._farmer_combo.currentData(),self._date_from,self._date_to)
                self._show_stmt()
            else:
                self._summary=get_collection_summary(self._date_from,self._date_to)
                self._show_sum()
            self._pdf_btn.setEnabled(True); self._excel_btn.setEnabled(True)
        except ReportError as e: self._msg.setText(str(e))
        except Exception as e: self._msg.setText(_t("unexpected_error",err=str(e)))

    def _show_stmt(self):
        from utils.bs_calendar import db_date_to_bs_str
        s=self._statement; lang=_lang()
        self._rtitle.setText(f"{_t('farmer_statement')}: {s.farmer_code} — {s.farmer_name}")
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels([_t("col_date"),_t("col_quantity"),_t("rate"),_t("col_amount")])
        R=Qt.AlignRight|Qt.AlignVCenter
        rows=[]
        for lbl,val in [(_t("opening_balance"),f"NPR {s.opening_balance:,.2f}"),
                        (_t("grand_total"),f"NPR {s.total_transaction_amount:,.2f}"),
                        (_t("total_paid"),f"NPR {s.total_paid:,.2f}"),
                        (_t("closing_balance"),f"NPR {s.closing_balance:,.2f}")]:
            rows.append(("summary",lbl,val))
        for ln in s.transactions:
            rows.append(("txn",db_date_to_bs_str(ln.transaction_date,lang),
                         f"{ln.quantity:,.2f}",f"{ln.rate:,.2f}",f"{ln.amount:,.2f}"))
        if not s.transactions and not s.payments:
            self._table.setRowCount(1)
            self._table.setItem(0,0,QTableWidgetItem(_t("no_data"))); return
        self._table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            if row[0]=="summary":
                self._table.setItem(i,0,self._item(row[1],bold=True))
                self._table.setSpan(i,1,1,2)
                self._table.setItem(i,3,self._item(row[2],R,bold=True))
            else:
                for col,val in enumerate(row[1:]):
                    align=R if col>0 else Qt.AlignLeft|Qt.AlignVCenter
                    self._table.setItem(i,col,self._item(val,align))

    def _show_sum(self):
        s=self._summary
        self._rtitle.setText(_t("monthly_summary"))
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels([
            _t("col_code"),_t("col_name"),_t("col_quantity"),
            _t("col_amount"),_t("total_paid"),_t("col_balance")])
        if not s.rows:
            self._table.setRowCount(1)
            self._table.setItem(0,0,QTableWidgetItem(_t("no_report_data"))); return
        self._table.setRowCount(len(s.rows)+1)
        R=Qt.AlignRight|Qt.AlignVCenter
        for i,r in enumerate(s.rows):
            self._table.setItem(i,0,self._item(r.farmer_code))
            self._table.setItem(i,1,self._item(r.farmer_name))
            self._table.setItem(i,2,self._item(f"{r.total_quantity:,.2f}",R))
            self._table.setItem(i,3,self._item(f"{r.total_amount:,.2f}",R))
            self._table.setItem(i,4,self._item(f"{r.total_paid:,.2f}",R))
            c="#2563EB" if r.balance<0 else ("#DC2626" if r.balance>0 else None)
            self._table.setItem(i,5,self._item(f"{r.balance:,.2f}",R,color=c))
        g=len(s.rows)
        self._table.setItem(g,1,self._item(_t("grand_total"),bold=True))
        self._table.setItem(g,2,self._item(f"{s.grand_total_quantity:,.2f}",R,bold=True))
        self._table.setItem(g,3,self._item(f"{s.grand_total_amount:,.2f}",R,bold=True))
        self._table.setItem(g,4,self._item(f"{s.grand_total_paid:,.2f}",R,bold=True))
        self._table.setItem(g,5,self._item(f"{s.grand_total_balance:,.2f}",R,bold=True))

    def _export_pdf(self):
        from services.pdf_service import generate_farmer_statement_pdf, generate_collection_summary_pdf
        is_s=self._rb_stmt.isChecked(); lang=_lang()
        name=f"farmer_statement.pdf" if is_s else "collection_summary.pdf"
        path,_=QFileDialog.getSaveFileName(self,_t("export_pdf"),name,"PDF (*.pdf)")
        if not path: return
        try:
            (generate_farmer_statement_pdf(self._statement,path,lang) if is_s
             else generate_collection_summary_pdf(self._summary,path,lang))
            self._msg.setStyleSheet(f"font-size:9pt;color:{COLOR_SUCCESS};")
            self._msg.setText(f"✓ {os.path.basename(path)}")
        except Exception as e:
            self._msg.setStyleSheet(f"font-size:9pt;color:{COLOR_DANGER};")
            self._msg.setText(_t("unexpected_error",err=str(e)))

    def _export_excel(self):
        from services.excel_service import generate_farmer_statement_excel, generate_collection_summary_excel
        is_s=self._rb_stmt.isChecked(); lang=_lang()
        name="farmer_statement.xlsx" if is_s else "collection_summary.xlsx"
        path,_=QFileDialog.getSaveFileName(self,_t("export_excel"),name,"Excel (*.xlsx)")
        if not path: return
        try:
            (generate_farmer_statement_excel(self._statement,path,lang) if is_s
             else generate_collection_summary_excel(self._summary,path,lang))
            self._msg.setStyleSheet(f"font-size:9pt;color:{COLOR_SUCCESS};")
            self._msg.setText(f"✓ {os.path.basename(path)}")
        except Exception as e:
            self._msg.setStyleSheet(f"font-size:9pt;color:{COLOR_DANGER};")
            self._msg.setText(_t("unexpected_error",err=str(e)))

    def showEvent(self,event):
        super().showEvent(event); self._title.setText(_t("reports")); self._load_farmers()
