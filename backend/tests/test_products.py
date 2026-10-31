"""Product and Plan tests."""
import pytest

PRODUCTS_URL = "/api/products"
PLANS_URL = "/api/plans"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_product_happy_path(client, admin_token):
    """POST /api/products — admin creates product → 201."""
    resp = client.post(
        PRODUCTS_URL,
        json={"name": "Business Suite", "product_type": "software", "sales_price": "499.00"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["data"]["name"] == "Business Suite"


def test_create_product_missing_name_returns_422(client, admin_token):
    """POST /api/products — missing name → 422."""
    resp = client.post(
        PRODUCTS_URL,
        json={"product_type": "software"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 422, resp.text


def test_create_plan_happy_path(client, admin_token, db_session):
    """POST /api/plans — admin creates plan linked to product → 201."""
    # Create product first
    from backend.app.models.product import Product
    p = Product(name="Suite", sales_price=499, cost_price=0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    resp = client.post(
        PLANS_URL,
        json={"product_id": p.id, "name": "Monthly Plan", "price": "99.00", "billing_period": "monthly"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["data"]["billing_period"] == "monthly"


def test_create_plan_invalid_billing_period_returns_422(client, admin_token, db_session):
    """POST /api/plans — invalid billing_period → 422."""
    from backend.app.models.product import Product
    p = Product(name="Suite2", sales_price=499, cost_price=0)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    resp = client.post(
        PLANS_URL,
        json={"product_id": p.id, "name": "Bad Plan", "price": "99.00", "billing_period": "quarterly"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 422, resp.text
