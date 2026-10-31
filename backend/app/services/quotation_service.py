"""Quotation template service — bundle templates and subscription instantiation."""
from datetime import date, timedelta
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.quotation_template import QuotationTemplate, QuotationTemplateLine
from backend.app.models.subscription import Subscription, SubscriptionLine
from backend.app.models.user import User
from backend.app.models.plan import Plan
from backend.app.schemas.quotation_template import QuotationTemplateCreate, InstantiateTemplateRequest
from backend.app.services.subscription_service import _generate_number, _compute_line_amount


def list_quotation_templates(db: Session) -> list[QuotationTemplate]:
    return db.query(QuotationTemplate).all()


def get_quotation_template(template_id: int, db: Session) -> QuotationTemplate:
    tmpl = db.query(QuotationTemplate).filter(QuotationTemplate.id == template_id).first()
    if not tmpl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quotation template with ID {template_id} not found.",
        )
    return tmpl


def create_quotation_template(payload: QuotationTemplateCreate, db: Session) -> QuotationTemplate:
    existing = db.query(QuotationTemplate).filter(QuotationTemplate.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Quotation template '{payload.name}' already exists.",
        )

    tmpl = QuotationTemplate(
        name=payload.name,
        description=payload.description,
        plan_id=payload.plan_id,
        validity_days=payload.validity_days,
    )
    db.add(tmpl)
    db.flush()

    for line_data in payload.lines:
        tmpl_line = QuotationTemplateLine(
            template_id=tmpl.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            tax_rate=line_data.tax_rate,
        )
        db.add(tmpl_line)

    db.commit()
    db.refresh(tmpl)
    return tmpl


def instantiate_template_to_subscription(
    template_id: int,
    payload: InstantiateTemplateRequest,
    db: Session,
) -> Subscription:
    """Instantiates a quotation template into a new Draft subscription, copying all lines
    and configuring the quotation validity date."""
    tmpl = get_quotation_template(template_id, db)

    customer = db.query(User).filter(User.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {payload.customer_id} not found.",
        )

    # Determine plan (use template plan or first plan)
    plan_id = tmpl.plan_id
    if not plan_id:
        first_plan = db.query(Plan).first()
        if not first_plan:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active plan found to associate.")
        plan_id = first_plan.id

    start = payload.start_date or date.today()
    quote_valid_until = start + timedelta(days=tmpl.validity_days)

    sub = Subscription(
        number=_generate_number(),
        customer_id=customer.id,
        plan_id=plan_id,
        start_date=start,
        quote_valid_until=quote_valid_until,
        payment_terms=payload.payment_terms,
        notes=f"Created from template: {tmpl.name}",
        status="draft",
    )
    db.add(sub)
    db.flush()

    for tmpl_line in tmpl.lines:
        line_amt = _compute_line_amount(tmpl_line.quantity, tmpl_line.unit_price)
        sub_line = SubscriptionLine(
            subscription_id=sub.id,
            product_id=tmpl_line.product_id,
            description=tmpl_line.product.name if tmpl_line.product else "Service Item",
            quantity=tmpl_line.quantity,
            unit_price=tmpl_line.unit_price,
            tax_rate=tmpl_line.tax_rate,
            amount=line_amt,
        )
        db.add(sub_line)

    db.commit()
    db.refresh(sub)
    return sub
