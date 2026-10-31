"""Invoice tests — generation, double-billing guard, status transitions."""
from datetime import date

INVOICES_URL = "/api/invoices"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _seed_active_subscription(db_session):
    from backend.app.models.user import User
    from backend.app.models.product import Product, Plan
    from backend.app.models.subscription import Subscription, SubscriptionLine
    from backend.app.core.security import hash_password
    customer = User(email="inv_c@test.com", hashed_password=hash_password("X@1aaaaa"), full_name="Inv C", role="customer")
    db_session.add(customer)
    product = Product(name="InvProd", sales_price=200, cost_price=0)
    db_session.add(product)
    db_session.flush()
    plan = Plan(product_id=product.id, name="InvPlan", price=200, billing_period="monthly")
    db_session.add(plan)
    db_session.flush()
    sub = Subscription(
        number="SUB-TEST01",
        customer_id=customer.id,
        plan_id=plan.id,
        start_date=date.today(),
        status="active",
    )
    db_session.add(sub)
    db_session.flush()
    line = SubscriptionLine(
        subscription_id=sub.id,
        product_id=product.id,
        description="Monthly service",
        quantity=1,
        unit_price=200,
        tax_rate=10,
        amount=200,
    )
    db_session.add(line)
    db_session.commit()
    db_session.refresh(sub)
    return sub.id, customer.id


def test_generate_invoice_happy_path(client, admin_token, db_session):
    """POST /api/invoices — generate invoice for active subscription → 201."""
    sub_id, _ = _seed_active_subscription(db_session)
    resp = client.post(
        INVOICES_URL,
        json={"subscription_id": sub_id, "billing_period_key": "2026-10", "due_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    assert data["subscription_id"] == sub_id
    assert float(data["tax_amount"]) > 0  # 10% tax


def test_double_billing_returns_409(client, admin_token, db_session):
    """POST /api/invoices — same period twice → 409."""
    sub_id, _ = _seed_active_subscription(db_session)
    payload = {"subscription_id": sub_id, "billing_period_key": "2026-11"}
    client.post(INVOICES_URL, json=payload, headers=auth_header(admin_token))
    resp = client.post(INVOICES_URL, json=payload, headers=auth_header(admin_token))
    assert resp.status_code == 409, resp.text


def test_invoice_status_draft_to_confirmed(client, admin_token, db_session):
    """PATCH invoice status: draft → confirmed → 200."""
    sub_id, _ = _seed_active_subscription(db_session)
    inv_resp = client.post(
        INVOICES_URL,
        json={"subscription_id": sub_id, "billing_period_key": "2026-12"},
        headers=auth_header(admin_token),
    )
    inv_id = inv_resp.json()["data"]["id"]
    r = client.patch(f"{INVOICES_URL}/{inv_id}/status", json={"status": "confirmed"}, headers=auth_header(admin_token))
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "confirmed"


def test_invalid_invoice_status_transition_returns_400(client, admin_token, db_session):
    """PATCH invoice status: draft → paid (skip confirmed) → 400."""
    sub_id, _ = _seed_active_subscription(db_session)
    inv_resp = client.post(
        INVOICES_URL,
        json={"subscription_id": sub_id, "billing_period_key": "2027-01"},
        headers=auth_header(admin_token),
    )
    inv_id = inv_resp.json()["data"]["id"]
    r = client.patch(f"{INVOICES_URL}/{inv_id}/status", json={"status": "paid"}, headers=auth_header(admin_token))
    assert r.status_code == 400, r.text
