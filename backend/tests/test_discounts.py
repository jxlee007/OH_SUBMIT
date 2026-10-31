"""Tests for discount rules and invoice discount application."""
from datetime import date, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.models.plan import Plan
from backend.app.models.subscription import Subscription, SubscriptionLine
from backend.app.core.security import create_access_token


@pytest.fixture
def sample_subscription(db_session):
    customer = User(
        email="client@test.com",
        hashed_password="...",
        full_name="Client User",
        role="customer",
    )
    product1 = Product(
        name="CRM License",
        product_type="service",
        sales_price=Decimal("1000.00"),
        cost_price=Decimal("200.00"),
    )
    product2 = Product(
        name="Addon Module",
        product_type="service",
        sales_price=Decimal("500.00"),
        cost_price=Decimal("100.00"),
    )
    db_session.add_all([customer, product1, product2])
    db_session.flush()

    plan = Plan(
        product_id=product1.id,
        name="Annual Growth",
        price=Decimal("1500.00"),
        billing_period="yearly",
        can_pause=True,
        can_renew=True,
    )
    db_session.add(plan)
    db_session.flush()

    sub = Subscription(
        number="SUB-DISC-001",
        customer_id=customer.id,
        plan_id=plan.id,
        start_date=date.today(),
        status="active",
    )
    db_session.add(sub)
    db_session.flush()

    line1 = SubscriptionLine(
        subscription_id=sub.id,
        product_id=product1.id,
        quantity=1,
        unit_price=Decimal("1000.00"),
        tax_rate=Decimal("18.00"),
        amount=Decimal("1180.00"),
    )
    line2 = SubscriptionLine(
        subscription_id=sub.id,
        product_id=product2.id,
        quantity=2,
        unit_price=Decimal("500.00"),
        tax_rate=Decimal("18.00"),
        amount=Decimal("1180.00"),
    )
    db_session.add_all([line1, line2])
    db_session.commit()
    db_session.refresh(sub)
    return sub, product1, product2


def test_create_discount_percent_over_100_returns_422(client: TestClient, admin_token: str):
    res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "OVER100",
            "name": "Invalid 150% discount",
            "rule_type": "percent",
            "discount_value": "150.00",
            "valid_from": str(date.today()),
            "valid_to": str(date.today() + timedelta(days=30)),
        },
    )
    assert res.status_code == 422
    assert "Percentage discount cannot exceed 100%" in res.text


def test_customer_cannot_create_discount_returns_403(client: TestClient, db_session):
    cust = User(email="cust2@test.com", hashed_password="...", full_name="Cust", role="customer")
    db_session.add(cust)
    db_session.commit()
    token = create_access_token({"sub": str(cust.id), "role": cust.role})

    res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": "TRYHACK",
            "name": "Hacked discount",
            "rule_type": "percent",
            "discount_value": "50.00",
            "valid_from": str(date.today()),
            "valid_to": str(date.today() + timedelta(days=30)),
        },
    )
    assert res.status_code == 403


def test_expired_discount_rule_returns_400(client: TestClient, admin_token: str, sample_subscription):
    sub, _, _ = sample_subscription

    # Create expired rule
    res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "EXPIRED10",
            "name": "Old promo",
            "rule_type": "percent",
            "discount_value": "10.00",
            "valid_from": str(date.today() - timedelta(days=60)),
            "valid_to": str(date.today() - timedelta(days=1)),
        },
    )
    assert res.status_code == 201

    # Try applying expired discount to invoice
    inv_res = client.post(
        "/api/invoices/generate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subscription_id": sub.id,
            "billing_period_key": "2026-EXP",
            "discount_code": "EXPIRED10",
        },
    )
    assert inv_res.status_code == 400
    assert "expired" in inv_res.text.lower()


def test_exhausted_usage_limit_returns_409(client: TestClient, admin_token: str, sample_subscription):
    sub, _, _ = sample_subscription

    # Create rule with usage limit = 1
    res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "ONCEONLY",
            "name": "Single Use Voucher",
            "rule_type": "fixed",
            "discount_value": "100.00",
            "valid_from": str(date.today()),
            "valid_to": str(date.today() + timedelta(days=30)),
            "usage_limit": 1,
        },
    )
    assert res.status_code == 201

    # Use it once
    inv1 = client.post(
        "/api/invoices/generate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subscription_id": sub.id,
            "billing_period_key": "2026-USE1",
            "discount_code": "ONCEONLY",
        },
    )
    assert inv1.status_code == 201

    # Second use must return 409 Conflict
    inv2 = client.post(
        "/api/invoices/generate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subscription_id": sub.id,
            "billing_period_key": "2026-USE2",
            "discount_code": "ONCEONLY",
        },
    )
    assert inv2.status_code == 409
    assert "usage limit" in inv2.text.lower()


def test_valid_discount_rule_applied_to_invoice_happy_path(client: TestClient, admin_token: str, sample_subscription):
    sub, _, _ = sample_subscription

    # Create 20% discount on subscription
    res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "SAVE20",
            "name": "20% Off Everything",
            "rule_type": "percent",
            "discount_value": "20.00",
            "valid_from": str(date.today()),
            "valid_to": str(date.today() + timedelta(days=30)),
        },
    )
    assert res.status_code == 201

    # Generate invoice with discount
    inv_res = client.post(
        "/api/invoices/generate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subscription_id": sub.id,
            "billing_period_key": "2026-SAVE20",
            "discount_code": "SAVE20",
        },
    )
    assert inv_res.status_code == 201
    data = inv_res.json()["data"]

    # Line 1: 1000 gross - 200 discount = 800 net + 144 tax (18%) = 944 total
    # Line 2: 1000 gross - 200 discount = 800 net + 144 tax (18%) = 944 total
    # Subtotal = 1600, Tax = 288, Total = 1888
    assert Decimal(str(data["subtotal"])) == Decimal("1600.00")
    assert Decimal(str(data["tax_amount"])) == Decimal("288.00")
    assert Decimal(str(data["total"])) == Decimal("1888.00")


def test_product_scoped_discount_applied_only_to_matching_product(client: TestClient, admin_token: str, sample_subscription):
    sub, p1, p2 = sample_subscription

    # Create 50% discount restricted only to Product 2 (Addon Module)
    res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "ADDON50",
            "name": "50% off Addon Module only",
            "rule_type": "percent",
            "discount_value": "50.00",
            "applies_to": "product",
            "product_id": p2.id,
            "valid_from": str(date.today()),
            "valid_to": str(date.today() + timedelta(days=30)),
        },
    )
    assert res.status_code == 201

    inv_res = client.post(
        "/api/invoices/generate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "subscription_id": sub.id,
            "billing_period_key": "2026-ADDON50",
            "discount_code": "ADDON50",
        },
    )
    assert inv_res.status_code == 201
    data = inv_res.json()["data"]

    # Line 1 (P1): 1000 gross, 0 discount, 180 tax = 1180
    # Line 2 (P2): 1000 gross, 500 discount = 500 net, 90 tax = 590
    # Subtotal = 1500, Tax = 270, Total = 1770
    assert Decimal(str(data["subtotal"])) == Decimal("1500.00")
    assert Decimal(str(data["tax_amount"])) == Decimal("270.00")
    assert Decimal(str(data["total"])) == Decimal("1770.00")


def test_concurrent_invoice_generation_enforces_discount_usage_limit(client: TestClient, admin_token: str, sample_subscription, db_engine):
    """Verifies concurrency locking (SELECT ... FOR UPDATE): only 1 request consumes usage_limit=1."""
    import concurrent.futures
    from sqlalchemy.orm import sessionmaker
    from backend.app.core.database import get_db
    from backend.app.main import app

    sub, p1, p2 = sample_subscription

    # Create discount with usage_limit = 1
    create_res = client.post(
        "/api/discounts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "CONCURRENT1",
            "name": "One-Time Limited Flash Sale",
            "rule_type": "percent",
            "discount_value": "20.00",
            "applies_to": "subscription",
            "usage_limit": 1,
            "valid_from": str(date.today()),
            "valid_to": str(date.today() + timedelta(days=10)),
        },
    )
    assert create_res.status_code == 201

    # Provide per-request session factory for multi-threaded test execution
    SessionMaker = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    def thread_safe_get_db():
        db = SessionMaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = thread_safe_get_db

    try:
        def try_generate(period_key: str):
            with TestClient(app) as local_client:
                return local_client.post(
                    "/api/invoices/generate",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={
                        "subscription_id": sub.id,
                        "billing_period_key": period_key,
                        "discount_code": "CONCURRENT1",
                    },
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(try_generate, "2026-CONC-A")
            f2 = executor.submit(try_generate, "2026-CONC-B")
            r1 = f1.result()
            r2 = f2.result()

        status_codes = sorted([r1.status_code, r2.status_code])
        # Exactly one succeeded with 201 and one was rejected with 409
        assert status_codes == [201, 409], f"Unexpected status codes: {status_codes}"
        error_res = r1 if r1.status_code == 409 else r2
        assert "usage limit" in error_res.text.lower() and "exhausted" in error_res.text.lower()
    finally:
        app.dependency_overrides.clear()
