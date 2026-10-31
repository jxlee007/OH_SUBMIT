"""Tests for pause/resume capabilities and automated renewal/billing scheduler."""
from datetime import date, timedelta
from decimal import Decimal
import pytest
from backend.app.models.product import Product, Plan
from backend.app.models.subscription import Subscription, SubscriptionLine
from backend.app.models.user import User
from backend.app.models.invoice import Invoice
from backend.app.services.scheduler_service import run_billing_cycle


@pytest.fixture
def pauseable_setup(db_session):
    customer = User(
        email="client.pause@example.com",
        hashed_password="hash",
        full_name="Client Pause",
        role="customer",
    )
    product = Product(
        name="Modular SaaS Suite",
        product_type="service",
        sales_price=Decimal("500.00"),
        cost_price=Decimal("100.00"),
        is_active=True,
    )
    db_session.add_all([customer, product])
    db_session.flush()

    plan_no_pause = Plan(
        product_id=product.id,
        name="Strict Fixed Plan",
        price=Decimal("500.00"),
        billing_period="monthly",
        can_pause=False,
        can_renew=True,
    )
    plan_with_pause = Plan(
        product_id=product.id,
        name="Flexible Pro Plan",
        price=Decimal("700.00"),
        billing_period="monthly",
        can_pause=True,
        can_renew=True,
    )
    plan_no_renew = Plan(
        product_id=product.id,
        name="One-Time Term Plan",
        price=Decimal("300.00"),
        billing_period="monthly",
        can_pause=True,
        can_renew=False,
    )
    db_session.add_all([plan_no_pause, plan_with_pause, plan_no_renew])
    db_session.commit()
    db_session.refresh(customer)
    db_session.refresh(product)
    db_session.refresh(plan_no_pause)
    db_session.refresh(plan_with_pause)
    db_session.refresh(plan_no_renew)
    return customer, product, plan_no_pause, plan_with_pause, plan_no_renew


def test_pause_subscription_with_can_pause_false_returns_409(client, staff_token, pauseable_setup, db_session):
    customer, product, plan_no_pause, _, _ = pauseable_setup
    headers = {"Authorization": f"Bearer {staff_token}"}

    sub = Subscription(
        number="SUB-STRICT-01",
        customer_id=customer.id,
        plan_id=plan_no_pause.id,
        start_date=date(2026, 1, 1),
        status="active",
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)

    resp = client.post(f"/api/subscriptions/{sub.id}/pause", headers=headers)
    assert resp.status_code == 409
    assert "does not allow pausing" in resp.text.lower()


def test_pause_and_resume_happy_path(client, staff_token, pauseable_setup, db_session):
    customer, product, _, plan_with_pause, _ = pauseable_setup
    headers = {"Authorization": f"Bearer {staff_token}"}

    sub = Subscription(
        number="SUB-FLEX-01",
        customer_id=customer.id,
        plan_id=plan_with_pause.id,
        start_date=date(2026, 1, 1),
        status="active",
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)

    # Pause
    r_pause = client.post(f"/api/subscriptions/{sub.id}/pause", headers=headers)
    assert r_pause.status_code == 200
    assert r_pause.json()["data"]["status"] == "paused"

    # Resume
    r_resume = client.post(f"/api/subscriptions/{sub.id}/resume", headers=headers)
    assert r_resume.status_code == 200
    assert r_resume.json()["data"]["status"] == "active"


def test_billing_run_skips_paused_subscriptions(pauseable_setup, db_session):
    customer, product, _, plan_with_pause, _ = pauseable_setup

    # Active sub
    sub_active = Subscription(
        number="SUB-ACTIVE-01",
        customer_id=customer.id,
        plan_id=plan_with_pause.id,
        start_date=date(2026, 10, 1),
        status="active",
    )
    line1 = SubscriptionLine(
        subscription=sub_active,
        product_id=product.id,
        quantity=1,
        unit_price=Decimal("700.00"),
        amount=Decimal("700.00"),
    )

    # Paused sub
    sub_paused = Subscription(
        number="SUB-PAUSED-01",
        customer_id=customer.id,
        plan_id=plan_with_pause.id,
        start_date=date(2026, 10, 1),
        status="paused",
    )
    line2 = SubscriptionLine(
        subscription=sub_paused,
        product_id=product.id,
        quantity=1,
        unit_price=Decimal("700.00"),
        amount=Decimal("700.00"),
    )
    db_session.add_all([sub_active, line1, sub_paused, line2])
    db_session.commit()

    # Execute billing run for October 2026
    target_dt = date(2026, 10, 15)
    summary = run_billing_cycle(db_session, target_date=target_dt)

    assert summary["invoices_generated"] == 1
    assert summary["paused_skipped"] == 1

    # Check that paused sub has NO invoices generated
    paused_invoices = db_session.query(Invoice).filter(Invoice.subscription_id == sub_paused.id).all()
    assert len(paused_invoices) == 0

    # Check active sub HAS invoice
    active_invoices = db_session.query(Invoice).filter(Invoice.subscription_id == sub_active.id).all()
    assert len(active_invoices) == 1
    assert active_invoices[0].billing_period_key == "2026-10"


def test_billing_run_closes_expired_non_renewable_subscription(pauseable_setup, db_session):
    customer, product, _, _, plan_no_renew = pauseable_setup

    sub_expired = Subscription(
        number="SUB-EXPIRED-TERM",
        customer_id=customer.id,
        plan_id=plan_no_renew.id,
        start_date=date(2026, 8, 1),
        expiry_date=date(2026, 9, 30),
        status="active",
    )
    db_session.add(sub_expired)
    db_session.commit()

    # Target date is October 1, after expiry date
    summary = run_billing_cycle(db_session, target_date=date(2026, 10, 1))
    assert summary["closed_expired"] == 1

    db_session.refresh(sub_expired)
    assert sub_expired.status == "closed"


def test_customer_cannot_trigger_billing_run_returns_403(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    resp = client.post("/api/subscriptions/billing-run", headers=headers)
    assert resp.status_code == 403


def test_admin_manual_billing_run_api_happy_path(client, admin_token, pauseable_setup, db_session):
    customer, product, plan_no_pause, _, _ = pauseable_setup
    headers = {"Authorization": f"Bearer {admin_token}"}

    sub = Subscription(
        number="SUB-ADMIN-BILL-01",
        customer_id=customer.id,
        plan_id=plan_no_pause.id,
        start_date=date(2026, 11, 1),
        status="active",
    )
    line = SubscriptionLine(
        subscription=sub,
        product_id=product.id,
        quantity=1,
        unit_price=Decimal("500.00"),
        amount=Decimal("500.00"),
    )
    db_session.add_all([sub, line])
    db_session.commit()

    resp = client.post("/api/subscriptions/billing-run?target_date=2026-11-05", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["target_date"] == "2026-11-05"
    assert data["invoices_generated"] >= 1


def test_apscheduler_job_registration_and_execution():
    """Verifies that APScheduler registers the billing job and manages lifecycle."""
    from backend.app.services.scheduler_service import scheduler, start_scheduler, stop_scheduler

    try:
        start_scheduler()
        assert scheduler.running is True
        job = scheduler.get_job("daily_billing_renewal_job")
        assert job is not None
        assert "billing" in job.id
    finally:
        stop_scheduler()
        assert scheduler.running is False
