"""Tests for product variants and attributes."""
from decimal import Decimal
import pytest
from backend.app.models.product import Product, Plan
from backend.app.models.user import User


@pytest.fixture
def sample_product_and_plan(db_session):
    prod = Product(
        name="Enterprise Cloud Platform",
        product_type="service",
        sales_price=Decimal("1000.00"),
        cost_price=Decimal("200.00"),
        notes="Base cloud tier",
        is_active=True,
    )
    db_session.add(prod)
    db_session.flush()

    plan = Plan(
        product_id=prod.id,
        name="Monthly Pro",
        price=Decimal("1000.00"),
        billing_period="monthly",
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(prod)
    db_session.refresh(plan)
    return prod, plan


def test_create_variant_duplicate_sku_returns_409(client, admin_token, sample_product_and_plan):
    prod, _ = sample_product_and_plan
    headers = {"Authorization": f"Bearer {admin_token}"}

    payload = {
        "product_id": prod.id,
        "sku": "ECP-US-EAST",
        "name": "US-East Dedicated",
        "price_delta": "250.00",
    }
    r1 = client.post("/api/products/variants", json=payload, headers=headers)
    assert r1.status_code == 201
    assert r1.json()["sku"] == "ECP-US-EAST"

    # Duplicate SKU
    r2 = client.post("/api/products/variants", json=payload, headers=headers)
    assert r2.status_code == 409
    assert "already exists" in r2.text.lower()


def test_create_variant_unknown_product_returns_404(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "product_id": 99999,
        "sku": "UNKNOWN-001",
        "name": "Phantom Variant",
        "price_delta": "50.00",
    }
    resp = client.post("/api/products/variants", json=payload, headers=headers)
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()


def test_effective_price_calculation_base_plus_delta(client, admin_token, sample_product_and_plan):
    prod, _ = sample_product_and_plan
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Add variant with positive delta
    v1 = client.post(
        "/api/products/variants",
        json={"product_id": prod.id, "sku": "ECP-HIGH-MEM", "name": "High Memory", "price_delta": "350.00"},
        headers=headers,
    )
    assert v1.status_code == 201
    assert Decimal(str(v1.json()["effective_price"])) == Decimal("1350.00")

    # Add variant with negative delta (discounted tier)
    v2 = client.post(
        "/api/products/variants",
        json={"product_id": prod.id, "sku": "ECP-DEV-TIER", "name": "Dev Tier", "price_delta": "-200.00"},
        headers=headers,
    )
    assert v2.status_code == 201
    assert Decimal(str(v2.json()["effective_price"])) == Decimal("800.00")

    # Verify listing calculates effective_price
    list_resp = client.get(f"/api/products/{prod.id}/variants", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 2


def test_subscription_with_variant_line_item(client, admin_token, sample_product_and_plan):
    prod, plan = sample_product_and_plan
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create variant
    v_resp = client.post(
        "/api/products/variants",
        json={"product_id": prod.id, "sku": "ECP-ENTERPRISE", "name": "Enterprise Cluster", "price_delta": "500.00"},
        headers=headers,
    )
    assert v_resp.status_code == 201
    variant_id = v_resp.json()["id"]

    # Create customer
    reg = client.post(
        "/api/auth/register",
        json={"email": "subscriber@test.com", "password": "Password@123", "full_name": "Subscriber User"},
    )
    assert reg.status_code == 201
    customer_id = reg.json()["data"]["id"]

    # Create subscription referencing variant without explicit unit_price (should auto-compute 1000 + 500 = 1500)
    sub_payload = {
        "customer_id": customer_id,
        "plan_id": plan.id,
        "start_date": "2026-11-01",
        "lines": [
            {
                "product_id": prod.id,
                "variant_id": variant_id,
                "quantity": 2,
                "tax_rate": "18.00",
            }
        ],
    }
    sub_resp = client.post("/api/subscriptions/", json=sub_payload, headers=headers)
    assert sub_resp.status_code == 201
    sub_data = sub_resp.json()["data"]
    assert len(sub_data["lines"]) == 1
    line = sub_data["lines"][0]
    assert line["variant_id"] == variant_id
    assert Decimal(str(line["unit_price"])) == Decimal("1500.00")
    assert Decimal(str(line["amount"])) == Decimal("3000.00")


def test_customer_cannot_create_variant_returns_403(client, customer_token, sample_product_and_plan):
    prod, _ = sample_product_and_plan
    headers = {"Authorization": f"Bearer {customer_token}"}
    payload = {
        "product_id": prod.id,
        "sku": "HACK-SKU",
        "name": "Unauthorized Variant",
        "price_delta": "0.00",
    }
    resp = client.post("/api/products/variants", json=payload, headers=headers)
    assert resp.status_code == 403


def test_attribute_creation_and_duplicate_check(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    attr_payload = {
        "name": "Hosting Region",
        "values": ["US-East", "EU-West", "AP-South"],
    }
    resp = client.post("/api/products/attributes", json=attr_payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Hosting Region"
    assert len(data["values"]) == 3

    # Duplicate attribute name returns 409
    dup = client.post("/api/products/attributes", json=attr_payload, headers=headers)
    assert dup.status_code == 409
