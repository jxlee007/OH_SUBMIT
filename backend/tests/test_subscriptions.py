"""Subscription tests."""
from datetime import date

SUBS_URL = "/api/subscriptions"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _seed_customer_and_plan(db_session):
    from backend.app.models.user import User
    from backend.app.models.product import Product, Plan
    from backend.app.core.security import hash_password
    customer = User(email="c@test.com", hashed_password=hash_password("X@1aaaaa"), full_name="C", role="customer")
    db_session.add(customer)
    product = Product(name="Prod", sales_price=100, cost_price=0)
    db_session.add(product)
    db_session.flush()
    plan = Plan(product_id=product.id, name="Monthly", price=100, billing_period="monthly")
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(customer)
    db_session.refresh(plan)
    return customer.id, plan.id


def test_create_subscription_happy_path(client, admin_token, db_session):
    """POST /api/subscriptions — admin creates subscription in Draft → 201."""
    cid, pid = _seed_customer_and_plan(db_session)
    resp = client.post(
        SUBS_URL,
        json={"customer_id": cid, "plan_id": pid, "start_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["data"]["status"] == "draft"


def test_subscription_status_lifecycle(client, admin_token, db_session):
    """PATCH status: draft → confirmed → active → closed."""
    cid, pid = _seed_customer_and_plan(db_session)
    create_resp = client.post(
        SUBS_URL,
        json={"customer_id": cid, "plan_id": pid, "start_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    sub_id = create_resp.json()["data"]["id"]

    for target_status in ("confirmed", "active", "closed"):
        r = client.patch(
            f"{SUBS_URL}/{sub_id}/status",
            json={"status": target_status},
            headers=auth_header(admin_token),
        )
        assert r.status_code == 200, r.text
        assert r.json()["data"]["status"] == target_status


def test_invalid_status_transition_returns_400(client, admin_token, db_session):
    """PATCH status: draft → paid → 400 (invalid transition)."""
    cid, pid = _seed_customer_and_plan(db_session)
    create_resp = client.post(
        SUBS_URL,
        json={"customer_id": cid, "plan_id": pid, "start_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    sub_id = create_resp.json()["data"]["id"]
    r = client.patch(
        f"{SUBS_URL}/{sub_id}/status",
        json={"status": "active"},  # draft can't skip to active
        headers=auth_header(admin_token),
    )
    assert r.status_code == 400, r.text


def test_create_subscription_unknown_customer_returns_422(client, admin_token, db_session):
    """POST /api/subscriptions — non-existent customer → 422."""
    from backend.app.models.product import Product, Plan
    product = Product(name="P2", sales_price=50, cost_price=0)
    db_session.add(product)
    db_session.flush()
    plan = Plan(product_id=product.id, name="P2 Plan", price=50, billing_period="monthly")
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    r = client.post(
        SUBS_URL,
        json={"customer_id": 99999, "plan_id": plan.id, "start_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 422, r.text
