"""Tests for list endpoint ordering and nullability resilience.

Verifies:
1. Deterministic reverse-chronological order (id DESC) on list endpoints.
2. Graceful serialization when optional fields (notes, dates, references, cost_price) are NULL.
"""
from datetime import date
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.models.plan import Plan
from backend.app.models.subscription import Subscription, SubscriptionLine
from backend.app.models.invoice import Invoice, InvoiceLine
from backend.app.models.payment import Payment


@pytest.fixture
def populated_dataset(db_session):
    """Seed multiple records with mixed populated and null fields."""
    customer = User(
        email="ordering_cust@test.com",
        hashed_password="pw",
        full_name="Ordering Cust",
        role="customer",
    )
    db_session.add(customer)
    db_session.commit()

    # Products: one full, one with NULLs
    p1 = Product(name="Alpha Product", product_type="service", sales_price=Decimal("100.00"), cost_price=Decimal("50.00"), notes="Alpha notes")
    p2 = Product(name="Beta Product", product_type="service", sales_price=Decimal("200.00"), cost_price=None, notes=None)
    db_session.add_all([p1, p2])
    db_session.commit()

    # Plans: one with dates, one with NULL dates
    plan1 = Plan(product_id=p1.id, name="Plan 1", price=Decimal("100.00"), billing_period="monthly", available_from=date(2026, 1, 1), available_until=date(2026, 12, 31))
    plan2 = Plan(product_id=p2.id, name="Plan 2", price=Decimal("200.00"), billing_period="yearly", available_from=None, available_until=None)
    db_session.add_all([plan1, plan2])
    db_session.commit()

    # Subscriptions: multiple to test ordering and nulls
    s1 = Subscription(number="SUB-ORD-1", customer_id=customer.id, plan_id=plan1.id, start_date=date(2026, 1, 1), expiry_date=date(2026, 6, 1), quote_valid_until=date(2026, 1, 15), payment_terms="Net 30", notes="Some notes", status="active")
    s2 = Subscription(number="SUB-ORD-2", customer_id=customer.id, plan_id=plan2.id, start_date=date(2026, 2, 1), expiry_date=None, quote_valid_until=None, payment_terms=None, notes=None, status="draft")
    s3 = Subscription(number="SUB-ORD-3", customer_id=customer.id, plan_id=plan1.id, start_date=date(2026, 3, 1), expiry_date=None, quote_valid_until=None, payment_terms=None, notes=None, status="confirmed")
    db_session.add_all([s1, s2, s3])
    db_session.commit()

    # Invoices: multiple with and without due_date / notes
    inv1 = Invoice(subscription_id=s1.id, customer_id=customer.id, billing_period_key="2026-01", subtotal=Decimal("100.00"), tax_amount=Decimal("18.00"), total=Decimal("118.00"), due_date=date(2026, 1, 31), notes="Invoice 1 note", status="confirmed")
    inv2 = Invoice(subscription_id=s3.id, customer_id=customer.id, billing_period_key="2026-03", subtotal=Decimal("200.00"), tax_amount=Decimal("36.00"), total=Decimal("236.00"), due_date=None, notes=None, status="confirmed")
    db_session.add_all([inv1, inv2])
    db_session.commit()

    # Payments: with and without reference/notes
    pay1 = Payment(invoice_id=inv1.id, amount=Decimal("118.00"), method="bank_transfer", payment_date=date(2026, 2, 1), reference="REF-12345", notes="Paid in full")
    pay2 = Payment(invoice_id=inv2.id, amount=Decimal("100.00"), method="cash", payment_date=date(2026, 3, 5), reference=None, notes=None)
    db_session.add_all([pay1, pay2])
    db_session.commit()

    return {
        "customer": customer,
        "products": [p1, p2],
        "plans": [plan1, plan2],
        "subscriptions": [s1, s2, s3],
        "invoices": [inv1, inv2],
        "payments": [pay1, pay2],
    }


def test_subscriptions_list_ordering_and_null_tolerance(client: TestClient, admin_token: str, populated_dataset):
    """Verify subscriptions are returned in descending ID order and handle NULL attributes cleanly."""
    res = client.get("/api/subscriptions", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    items = res.json()["data"]
    assert len(items) >= 3

    # 1. Ordering check (newest first)
    ids = [item["id"] for item in items]
    assert ids == sorted(ids, reverse=True), f"Expected descending order, got: {ids}"

    # 2. Nullability check: find the subscription with null fields
    sub_null = next((item for item in items if item["number"] == "SUB-ORD-2"), None)
    assert sub_null is not None
    assert sub_null["expiry_date"] is None
    assert sub_null["quote_valid_until"] is None
    assert sub_null["payment_terms"] is None
    assert sub_null["notes"] is None


def test_invoices_list_ordering_and_null_tolerance(client: TestClient, admin_token: str, populated_dataset):
    """Verify invoices are returned in descending ID order and handle NULL notes/due_date."""
    res = client.get("/api/invoices", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    items = res.json()["data"]
    assert len(items) >= 2

    # 1. Ordering check
    ids = [item["id"] for item in items]
    assert ids == sorted(ids, reverse=True), f"Expected descending order, got: {ids}"

    # 2. Nullability check
    inv_null = next((item for item in items if item["billing_period_key"] == "2026-03"), None)
    assert inv_null is not None
    assert inv_null["due_date"] is None
    assert inv_null["notes"] is None


def test_products_and_plans_ordering_and_null_tolerance(client: TestClient, admin_token: str, populated_dataset):
    """Verify products and plans list endpoints return descending order and serialize NULL values."""
    # Products
    res_p = client.get("/api/products", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_p.status_code == 200
    prods = res_p.json()["data"]
    p_ids = [p["id"] for p in prods]
    assert p_ids == sorted(p_ids, reverse=True)
    p_null = next((p for p in prods if p["name"] == "Beta Product"), None)
    assert p_null is not None
    assert p_null["notes"] is None
    assert Decimal(str(p_null["cost_price"])) == Decimal("0.00")

    # Plans
    res_pl = client.get("/api/plans", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_pl.status_code == 200
    plans = res_pl.json()["data"]
    pl_ids = [pl["id"] for pl in plans]
    assert pl_ids == sorted(pl_ids, reverse=True)
    pl_null = next((pl for pl in plans if pl["name"] == "Plan 2"), None)
    assert pl_null is not None
    assert pl_null["available_from"] is None
    assert pl_null["available_until"] is None


def test_payments_list_ordering_and_null_tolerance(client: TestClient, admin_token: str, populated_dataset):
    """Verify payments list returns descending order and serializes NULL reference/notes."""
    res = client.get("/api/payments", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    payments = res.json()["data"]
    assert len(payments) >= 2

    # 1. Ordering check
    pay_ids = [p["id"] for p in payments]
    assert pay_ids == sorted(pay_ids, reverse=True)

    # 2. Nullability check
    pay_null = next((p for p in payments if p["method"] == "cash"), None)
    assert pay_null is not None
    assert pay_null["reference"] is None
    assert pay_null["notes"] is None
