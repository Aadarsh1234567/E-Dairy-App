"""Report service — data layer for Farmer Statement and Collection Summary."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from sqlalchemy import and_
from database.database import get_session
from database.models import Farmer, Transaction, Payment

class ReportError(Exception): pass

def _t(key, **kw):
    from translations import t
    return t(key, **kw)

@dataclass
class TransactionLine:
    transaction_id: int
    transaction_date: date
    farmer_code: str; farmer_name: str
    quantity: float; rate: float; amount: float

@dataclass
class PaymentLine:
    payment_date: date
    farmer_code: str; farmer_name: str
    amount_paid: float; receipt_number: str

@dataclass
class FarmerStatement:
    farmer_id: int; farmer_code: str; farmer_name: str
    bank_account: str
    date_from: Optional[date]; date_to: Optional[date]
    opening_balance: float; closing_balance: float
    transactions: list = field(default_factory=list)
    payments: list = field(default_factory=list)
    total_quantity: float = 0.0
    total_transaction_amount: float = 0.0
    total_paid: float = 0.0

@dataclass
class FarmerSummaryRow:
    farmer_id: int; farmer_code: str; farmer_name: str
    total_quantity: float; total_amount: float
    total_paid: float; balance: float

@dataclass
class CollectionSummary:
    date_from: Optional[date]; date_to: Optional[date]
    rows: list = field(default_factory=list)
    grand_total_quantity: float = 0.0
    grand_total_amount: float = 0.0
    grand_total_paid: float = 0.0
    grand_total_balance: float = 0.0

def _dcond(col, df, dt):
    conds = []
    if df: conds.append(col >= df)
    if dt: conds.append(col <= dt)
    return and_(*conds) if conds else None

def _opening_balance(session, farmer_id, date_from):
    if not date_from: return 0.0
    txns = session.query(Transaction.quantity, Transaction.rate, Transaction.bonus_amount).filter(
        Transaction.farmer_id==farmer_id, Transaction.status=="ACTIVE",
        Transaction.transaction_date < date_from).all()
    pays = session.query(Payment.amount_paid).filter(
        Payment.farmer_id==farmer_id, Payment.payment_date < date_from).all()
    return round(sum(float(q)*float(r)+float(b or 0) for q,r,b in txns) - sum(float(a) for (a,) in pays), 2)

def get_farmer_statement(farmer_id, date_from=None, date_to=None):
    with get_session() as session:
        farmer = session.query(Farmer).filter_by(farmer_id=farmer_id).first()
        if not farmer: raise ReportError(_t("farmer_not_found"))
        opening = _opening_balance(session, farmer_id, date_from)
        tf = [Transaction.farmer_id==farmer_id, Transaction.status=="ACTIVE"]
        dc = _dcond(Transaction.transaction_date, date_from, date_to)
        if dc is not None: tf.append(dc)
        txns = session.query(Transaction).filter(and_(*tf))\
                      .order_by(Transaction.transaction_date, Transaction.transaction_id).all()
        pf = [Payment.farmer_id==farmer_id]
        pc = _dcond(Payment.payment_date, date_from, date_to)
        if pc is not None: pf.append(pc)
        pays = session.query(Payment).filter(and_(*pf))\
                      .order_by(Payment.payment_date, Payment.payment_id).all()
        tlines = [TransactionLine(
            transaction_id=t.transaction_id,
            transaction_date=t.transaction_date,
            farmer_code=farmer.farmer_code, farmer_name=farmer.display_name,
            quantity=float(t.quantity), rate=float(t.rate),
            amount=round(float(t.quantity)*float(t.rate)+float(t.bonus_amount or 0),2)) for t in txns]
        plines = [PaymentLine(
            payment_date=p.payment_date,
            farmer_code=farmer.farmer_code, farmer_name=farmer.display_name,
            amount_paid=float(p.amount_paid), receipt_number=p.receipt_number or "") for p in pays]
        tot_q = sum(l.quantity for l in tlines)
        tot_a = sum(l.amount for l in tlines)
        tot_p = sum(l.amount_paid for l in plines)
        return FarmerStatement(
            farmer_id=farmer_id, farmer_code=farmer.farmer_code,
            farmer_name=farmer.display_name, bank_account=farmer.bank_account or "",
            date_from=date_from, date_to=date_to,
            opening_balance=opening, closing_balance=round(opening+tot_a-tot_p,2),
            transactions=tlines, payments=plines,
            total_quantity=round(tot_q,2),
            total_transaction_amount=round(tot_a,2), total_paid=round(tot_p,2))

def get_collection_summary(date_from=None, date_to=None):
    with get_session() as session:
        farmers = session.query(Farmer).order_by(Farmer.farmer_code).all()
        rows=[]; gq=ga=gp=gb=0.0
        for farmer in farmers:
            tf=[Transaction.farmer_id==farmer.farmer_id, Transaction.status=="ACTIVE"]
            dc=_dcond(Transaction.transaction_date, date_from, date_to)
            if dc is not None: tf.append(dc)
            txns=session.query(Transaction.quantity,Transaction.rate,Transaction.bonus_amount).filter(and_(*tf)).all()
            pf=[Payment.farmer_id==farmer.farmer_id]
            pc=_dcond(Payment.payment_date, date_from, date_to)
            if pc is not None: pf.append(pc)
            pays=session.query(Payment.amount_paid).filter(and_(*pf)).all()
            q=sum(float(x) for x,_,_ in txns)
            a=round(sum(float(x)*float(y)+float(z or 0) for x,y,z in txns),2)
            p=round(sum(float(x) for (x,) in pays),2)
            b=round(a-p,2)
            if q==0 and a==0 and p==0: continue
            rows.append(FarmerSummaryRow(
                farmer_id=farmer.farmer_id, farmer_code=farmer.farmer_code,
                farmer_name=farmer.display_name,
                total_quantity=round(q,2), total_amount=a, total_paid=p, balance=b))
            gq+=q; ga+=a; gp+=p; gb+=b
        return CollectionSummary(
            date_from=date_from, date_to=date_to, rows=rows,
            grand_total_quantity=round(gq,2), grand_total_amount=round(ga,2),
            grand_total_paid=round(gp,2), grand_total_balance=round(gb,2))
