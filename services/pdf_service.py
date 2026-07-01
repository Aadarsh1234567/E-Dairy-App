"""
PDF service — A4 reports + thermal receipt generator.
Font: Noto Sans Devanagari bundled at assets/fonts/NotoSansDevanagari.ttf.

IMPORTANT: All _t() calls inside generator functions pass lang= explicitly
so the PDF language matches the requested lang parameter, not the DB setting.
"""
import os
from datetime import date
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FN = "NotoDevanagari"
_FP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "fonts", "NotoSansDevanagari.ttf")
_registered = False


def _font():
    global _registered
    if not _registered:
        pdfmetrics.registerFont(TTFont(_FN, _FP))
        _registered = True


def _t(key, lang="NE", **kw):
    """Translate key to given lang directly (does NOT read from DB setting)."""
    from translations import _ALL
    entry = _ALL.get(key, {})
    text = entry.get(lang, entry.get("NE", key))
    if kw:
        try:
            text = text.format(**kw)
        except Exception:
            pass
    return text


def _org(lang):
    from database.database import get_setting
    if lang == "NE":
        return get_setting("organization_name_nepali", "") or \
               get_setting("organization_name_english", "Santosh Dairy Cooperative")
    return get_setting("organization_name_english", "Santosh Dairy Cooperative")


def _bs(d, lang):
    from utils.bs_calendar import db_date_to_bs_str
    return db_date_to_bs_str(d, lang=lang) if d else _t("all_time", lang=lang)


def _ts():
    return TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), _FN),
        ("FONTSIZE",  (0, 0), (-1, -1), 8),
        ("BACKGROUND",(0, 0), (-1,  0), colors.HexColor("#1A2B4C")),
        ("TEXTCOLOR", (0, 0), (-1,  0), colors.white),
        ("ALIGN",     (2, 0), (-1, -1), "RIGHT"),
        ("ALIGN",     (0, 0), ( 1, -1), "LEFT"),
        ("GRID",      (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ])


def _styles(lang):
    _font()
    title = ParagraphStyle("T",  fontName=_FN, fontSize=16, leading=20,
                           alignment=TA_CENTER, textColor=colors.HexColor("#1A2B4C"))
    sub   = ParagraphStyle("S",  fontName=_FN, fontSize=10, leading=14,
                           alignment=TA_CENTER, textColor=colors.HexColor("#6B7280"))
    sec   = ParagraphStyle("SE", fontName=_FN, fontSize=11, leading=15,
                           alignment=TA_LEFT,   textColor=colors.HexColor("#1A2B4C"),
                           spaceBefore=10, spaceAfter=4)
    norm  = ParagraphStyle("N",  fontName=_FN, fontSize=9, leading=13, alignment=TA_LEFT)
    foot  = ParagraphStyle("F",  fontName=_FN, fontSize=7,
                           textColor=colors.HexColor("#9CA3AF"), spaceBefore=4)
    return title, sub, sec, norm, foot


def generate_farmer_statement_pdf(statement, output_path, lang="NE"):
    """Generate A4 PDF for a single farmer's statement."""
    _font()
    title, sub, sec, norm, foot = _styles(lang)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=18*mm, bottomMargin=18*mm,
                            leftMargin=16*mm, rightMargin=16*mm)
    E = []

    E.append(Paragraph(_org(lang), title))
    E.append(Paragraph(_t("farmer_statement", lang=lang), sub))
    E.append(Spacer(1, 4*mm))
    E.append(HRFlowable(width="100%", color=colors.HexColor("#D1D5DB"), thickness=1))
    E.append(Spacer(1, 4*mm))

    E.append(Paragraph(
        f"{_t('col_farmer', lang=lang)}: {statement.farmer_code} — {statement.farmer_name}", norm))
    if statement.bank_account:
        E.append(Paragraph(
            f"{_t('bank_account_label', lang=lang)}: {statement.bank_account}", norm))
    dr_label = _t("date_range", lang=lang)
    df_str = _bs(statement.date_from, lang)
    dt_str = _bs(statement.date_to, lang)
    E.append(Paragraph(f"{dr_label}: {df_str} — {dt_str}", norm))
    E.append(Spacer(1, 3*mm))

    # Summary balance table
    bal_data = [
        [_t("opening_balance", lang=lang),
         f"NPR {statement.opening_balance:,.2f}"],
        [_t("grand_total", lang=lang) + " (" + _t("milk_collection", lang=lang) + ")",
         f"NPR {statement.total_transaction_amount:,.2f}"],
        [_t("total_paid", lang=lang),
         f"NPR {statement.total_paid:,.2f}"],
        [_t("closing_balance", lang=lang),
         f"NPR {statement.closing_balance:,.2f}"],
    ]
    bt = Table(bal_data, colWidths=[90*mm, 60*mm])
    bt.setStyle(TableStyle([
        ("FONTNAME",     (0, 0), (-1, -1), _FN),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ALIGN",        (1, 0), ( 1, -1), "RIGHT"),
        ("LINEBELOW",    (0, 0), (-1, -2), 0.5, colors.HexColor("#E5E7EB")),
        ("LINEABOVE",    (0,-1), (-1, -1), 1,   colors.HexColor("#1A2B4C")),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    E.append(bt)
    E.append(Spacer(1, 6*mm))

    # Transactions table
    if statement.transactions:
        E.append(Paragraph(_t("milk_collection", lang=lang), sec))
        rows = [[_t("col_date", lang=lang), _t("col_quantity", lang=lang),
                 _t("rate", lang=lang),     _t("col_amount", lang=lang)]]
        for ln in statement.transactions:
            rows.append([
                _bs(ln.transaction_date, lang),
                f"{ln.quantity:,.2f}",
                f"{ln.rate:,.2f}",
                f"{ln.amount:,.2f}",
            ])
        t2 = Table(rows, colWidths=[45*mm, 35*mm, 35*mm, 35*mm], repeatRows=1)
        t2.setStyle(_ts())
        E.append(t2)
        E.append(Spacer(1, 6*mm))
    else:
        E.append(Paragraph(_t("no_data", lang=lang), norm))
        E.append(Spacer(1, 4*mm))

    # Payments table
    if statement.payments:
        E.append(Paragraph(_t("payment_entry", lang=lang), sec))
        rows = [[_t("col_date", lang=lang), _t("receipt_number", lang=lang),
                 _t("amount_paid", lang=lang)]]
        for ln in statement.payments:
            rows.append([
                _bs(ln.payment_date, lang),
                ln.receipt_number or "—",
                f"{ln.amount_paid:,.2f}",
            ])
        t3 = Table(rows, colWidths=[45*mm, 55*mm, 50*mm], repeatRows=1)
        t3.setStyle(_ts())
        E.append(t3)

    E.append(Spacer(1, 8*mm))
    E.append(HRFlowable(width="100%", color=colors.HexColor("#D1D5DB"), thickness=1))
    E.append(Paragraph(
        f"{_t('bs_calendar_label', lang=lang)}: {_bs(date.today(), lang)}", foot))

    doc.build(E)
    return output_path


def generate_collection_summary_pdf(summary, output_path, lang="NE"):
    """Generate A4 PDF for the all-farmers collection summary."""
    _font()
    title, sub, sec, norm, foot = _styles(lang)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=18*mm, bottomMargin=18*mm,
                            leftMargin=14*mm, rightMargin=14*mm)
    E = []

    E.append(Paragraph(_org(lang), title))
    E.append(Paragraph(_t("monthly_summary", lang=lang), sub))
    E.append(Spacer(1, 4*mm))
    E.append(HRFlowable(width="100%", color=colors.HexColor("#D1D5DB"), thickness=1))
    E.append(Spacer(1, 4*mm))

    df_str = _bs(summary.date_from, lang)
    dt_str = _bs(summary.date_to, lang)
    E.append(Paragraph(
        f"{_t('date_range', lang=lang)}: {df_str} — {dt_str}", norm))
    E.append(Spacer(1, 4*mm))

    if summary.rows:
        rows = [[
            _t("col_code",     lang=lang),
            _t("col_name",     lang=lang),
            _t("col_quantity", lang=lang),
            _t("col_amount",   lang=lang),
            _t("total_paid",   lang=lang),
            _t("col_balance",  lang=lang),
        ]]
        for r in summary.rows:
            rows.append([
                r.farmer_code, r.farmer_name,
                f"{r.total_quantity:,.2f}",
                f"{r.total_amount:,.2f}",
                f"{r.total_paid:,.2f}",
                f"{r.balance:,.2f}",
            ])
        rows.append([
            "",
            _t("grand_total", lang=lang),
            f"{summary.grand_total_quantity:,.2f}",
            f"{summary.grand_total_amount:,.2f}",
            f"{summary.grand_total_paid:,.2f}",
            f"{summary.grand_total_balance:,.2f}",
        ])
        st = _ts()
        st.add("LINEABOVE",    (0, -1), (-1, -1), 1, colors.HexColor("#1A2B4C"))
        st.add("TOPPADDING",   (0, -1), (-1, -1), 6)
        t = Table(rows, colWidths=[20*mm, 45*mm, 28*mm, 30*mm, 28*mm, 28*mm], repeatRows=1)
        t.setStyle(st)
        E.append(t)
    else:
        E.append(Paragraph(_t("no_data", lang=lang), norm))

    E.append(Spacer(1, 8*mm))
    E.append(HRFlowable(width="100%", color=colors.HexColor("#D1D5DB"), thickness=1))
    E.append(Paragraph(
        f"{_t('bs_calendar_label', lang=lang)}: {_bs(date.today(), lang)}", foot))

    doc.build(E)
    return output_path


def generate_payment_receipt_pdf(payment_row, balance_after, output_path, lang="NE", width_mm=80):
    """
    Generate a thermal receipt PDF for a single payment.
    width_mm: 58 or 80. Height auto-sizes based on content.
    """
    _font()
    pw  = width_mm * mm
    ph  = 150 * mm
    mg  = 4*mm if width_mm == 58 else 5*mm
    cw  = pw - (2 * mg)
    bs  = 8 if width_mm == 58 else 9

    doc = SimpleDocTemplate(output_path, pagesize=(pw, ph),
                            topMargin=4*mm, bottomMargin=4*mm,
                            leftMargin=mg, rightMargin=mg)
    E = []

    tit = ParagraphStyle("RT", fontName=_FN, fontSize=bs+2, leading=bs+5, alignment=TA_CENTER)
    cen = ParagraphStyle("RC", fontName=_FN, fontSize=bs-1, leading=bs+2, alignment=TA_CENTER,
                         textColor=colors.HexColor("#374151"))
    lbl = ParagraphStyle("RL", fontName=_FN, fontSize=bs,   leading=bs+4, alignment=TA_LEFT)
    amt = ParagraphStyle("RA", fontName=_FN, fontSize=bs+3, leading=bs+6, alignment=TA_CENTER)

    from utils.bs_calendar import db_date_to_bs_str

    E.append(Paragraph(_org(lang), tit))
    E.append(Paragraph(_t("payment_entry", lang=lang), cen))
    E.append(Spacer(1, 2*mm))
    E.append(HRFlowable(width="100%", color=colors.black, thickness=0.75, dash=(2, 2)))
    E.append(Spacer(1, 2*mm))

    ir = [
        [_t("receipt_number", lang=lang), payment_row.receipt_number or "—"],
        [_t("payment_date",   lang=lang), db_date_to_bs_str(payment_row.payment_date, lang=lang)],
        [_t("col_farmer",     lang=lang), payment_row.farmer_code],
        ["", payment_row.farmer_name],
    ]
    it = Table(ir, colWidths=[cw*0.42, cw*0.58])
    it.setStyle(TableStyle([
        ("FONTNAME",     (0, 0), (-1, -1), _FN),
        ("FONTSIZE",     (0, 0), (-1, -1), bs-1),
        ("ALIGN",        (1, 0), ( 1, -1), "RIGHT"),
        ("TOPPADDING",   (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1.5),
    ]))
    E.append(it)
    E.append(Spacer(1, 2*mm))
    E.append(HRFlowable(width="100%", color=colors.black, thickness=0.75, dash=(2, 2)))
    E.append(Spacer(1, 2*mm))

    E.append(Paragraph(_t("amount_paid", lang=lang), cen))
    E.append(Paragraph(f"NPR {payment_row.amount_paid:,.2f}", amt))
    E.append(Spacer(1, 2*mm))

    if balance_after < 0:
        bal_label = _t("you_owe_farmer", lang=lang)
    elif balance_after > 0:
        bal_label = _t("farmer_owes_dairy", lang=lang)
    else:
        bal_label = _t("balance_after_payment", lang=lang)

    bt = Table([[bal_label, f"NPR {abs(balance_after):,.2f}"]],
               colWidths=[cw*0.6, cw*0.4])
    bt.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _FN),
        ("FONTSIZE", (0, 0), (-1, -1), bs-1),
        ("ALIGN",    (1, 0), ( 1, -1), "RIGHT"),
    ]))
    E.append(bt)

    if payment_row.remarks:
        E.append(Spacer(1, 2*mm))
        E.append(Paragraph(
            f"{_t('payment_remarks', lang=lang)}: {payment_row.remarks}", lbl))

    E.append(Spacer(1, 3*mm))
    E.append(HRFlowable(width="100%", color=colors.black, thickness=0.75, dash=(2, 2)))
    E.append(Spacer(1, 2*mm))

    from utils.bs_calendar import format_bs_datetime
    E.append(Paragraph(format_bs_datetime(lang=lang), cen))
    E.append(Spacer(1, 6*mm))

    doc.build(E)
    return output_path
