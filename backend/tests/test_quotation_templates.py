"""Tests for quotation templates, multi-line instantiation, and quote validity rules."""
from datetime import date, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.models.plan import Plan
from backend.app.models.quotation_template import QuotationTemplate, QuotationTemplateLine
from backend.app.models.subscription import Subscription
from backend.app.core.security import create_access_token


@pytest.fixture
def quote_setup(db_session):
    customer = User(
        email="quote_client@test.com",
        hashed_password="...",
        full_name="Quote Client",
        role="customer",
    )
    product1 = Product(name="Enterprise Server", sales_price=Decimal("5000.00"), cost_price=Decimal("1000.00"))
    product2 = Product(name="Dedicated Support", sales_price=Decimal("1200.00"), cost_price=Decimal("200.00"))
    db_session.add_all([customer, product1, product2])
    db_session.flush()

    plan = Plan(
        product_id=product1.id,
        name="Enterprise Cloud",
        price=Decimal("6200.00"),
        billing_period="monthly",
    )
    db_session.add(plan)
    db_session.flush()

    template = QuotationTemplate(
        name="Enterprise Starter Bundle",
        description="Core Server + Dedicated Support",
        plan_id=plan.id,
        validity_days=14,  # valid for 14 days
    )
    db_session.add(template)
    db_session.flush()

    line1 = QuotationTemplateLine(
        template_id=template.id,
        product_id=product1.id,
        quantity=1,
        unit_price=Decimal("5000.00"),
        tax_rate=Decimal("18.00"),
    )
    line2 = QuotationTemplateLine(
        template_id=template.id,
        product_id=product2.id,
        quantity=3,
        unit_price=Decimal("1200.00"),
        tax_rate=Decimal("18.00"),
    )
    db_session.add_all([line1, line2])
    db_session.commit()
    return customer, plan, template, product1, product2


def test_create_quotation_template_happy_path(client: TestClient, admin_token: str, quote_setup):
    _, plan, _, p1, _ = quote_setup
    res = client.post(
        "/api/quotation-templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Custom Executive Suite",
            "description": "Executive custom offering",
            "plan_id": plan.id,
            "validity_days": 30,
            "lines": [
                {
                    "product_id": p1.id,
                    "quantity": 2,
                    "unit_price": "4500.00",
                    "tax_rate": "18.00",
                }
            ],
        },
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["name"] == "Custom Executive Suite"
    assert len(data["lines"]) == 1
    assert data["lines"][0]["quantity"] == 2


def test_customer_cannot_create_quotation_template_returns_403(client: TestClient, quote_setup):
    customer, _, _, p1, _ = quote_setup
    token = create_access_token({"sub": str(customer.id), "role": customer.role})
    res = client.post(
        "/api/quotation-templates",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Hacked Template",
            "validity_days": 10,
            "lines": [{"product_id": p1.id, "quantity": 1, "unit_price": "100.00"}],
        },
    )
    assert res.status_code == 403


def test_instantiate_quotation_template_copies_lines_and_sets_draft(
    client: TestClient, admin_token: str, quote_setup
):
    customer, _, template, p1, p2 = quote_setup
    res = client.post(
        f"/api/quotation-templates/{template.id}/instantiate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "customer_id": customer.id,
            "start_date": str(date.today()),
            "payment_terms": "Net 15",
        },
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["status"] == "draft"
    assert data["quote_valid_until"] == str(date.today() + timedelta(days=14))
    assert len(data["lines"]) == 2
    # Verify line items copied faithfully
    line_prod_ids = {l["product_id"] for l in data["lines"]}
    assert p1.id in line_prod_ids
    assert p2.id in line_prod_ids


def test_expired_quotation_cannot_be_confirmed_returns_409(client: TestClient, admin_token: str, db_session, quote_setup):
    customer, plan, _, p1, _ = quote_setup

    # Create quotation that expired yesterday
    expired_sub = Subscription(
        number="SUB-EXPIRED-QUOTE",
        customer_id=customer.id,
        plan_id=plan.id,
        start_date=date.today() - timedelta(days=20),
        quote_valid_until=date.today() - timedelta(days=1),  # Expired
        status="quotation",
    )
    db_session.add(expired_sub)
    db_session.commit()

    # Attempt to confirm expired quotation
    res = client.patch(
        f"/api/subscriptions/{expired_sub.id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "confirmed"},
    )
    assert res.status_code == 409
    assert "expired" in res.text.lower()


def test_valid_quotation_confirms_happy_path(client: TestClient, admin_token: str, db_session, quote_setup):
    customer, plan, _, _, _ = quote_setup

    valid_sub = Subscription(
        number="SUB-VALID-QUOTE",
        customer_id=customer.id,
        plan_id=plan.id,
        start_date=date.today(),
        quote_valid_until=date.today() + timedelta(days=14),  # Valid
        status="quotation",
    )
    db_session.add(valid_sub)
    db_session.commit()

    res = client.patch(
        f"/api/subscriptions/{valid_sub.id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "confirmed"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "confirmed"
