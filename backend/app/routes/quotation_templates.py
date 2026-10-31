"""Quotation template routes — template management and 1-click instantiation."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.auth_service import require_roles
from backend.app.models.user import User
from backend.app.schemas.common import StandardResponse, ok
from backend.app.schemas.quotation_template import (
    QuotationTemplateCreate, QuotationTemplateRead, InstantiateTemplateRequest,
)
from backend.app.schemas.subscription import SubscriptionRead
from backend.app.services.quotation_service import (
    list_quotation_templates,
    get_quotation_template,
    create_quotation_template,
    instantiate_template_to_subscription,
)

router = APIRouter(prefix="/quotation-templates", tags=["Quotation Templates"])


@router.get("", response_model=StandardResponse[list[QuotationTemplateRead]])
def list_templates(
    current_user: User = Depends(require_roles("admin", "staff")),
    db: Session = Depends(get_db),
):
    tmpls = list_quotation_templates(db)
    return ok([QuotationTemplateRead.model_validate(t) for t in tmpls])


@router.get("/{template_id}", response_model=StandardResponse[QuotationTemplateRead])
def get_template(
    template_id: int,
    current_user: User = Depends(require_roles("admin", "staff")),
    db: Session = Depends(get_db),
):
    tmpl = get_quotation_template(template_id, db)
    return ok(QuotationTemplateRead.model_validate(tmpl))


@router.post("", response_model=StandardResponse[QuotationTemplateRead], status_code=status.HTTP_201_CREATED)
def create_template(
    payload: QuotationTemplateCreate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    tmpl = create_quotation_template(payload, db)
    return ok(QuotationTemplateRead.model_validate(tmpl), "Quotation template created successfully.")


@router.post("/{template_id}/instantiate", response_model=StandardResponse[SubscriptionRead], status_code=status.HTTP_201_CREATED)
def instantiate_template(
    template_id: int,
    payload: InstantiateTemplateRequest,
    current_user: User = Depends(require_roles("admin", "staff")),
    db: Session = Depends(get_db),
):
    sub = instantiate_template_to_subscription(template_id, payload, db)
    return ok(SubscriptionRead.model_validate(sub), "Subscription instantiated from template in Draft status.")
