"""Payment tests — happy path, validation failures, and 403 RBAC."""
from datetime import date

PAYMENTS_URL = "/api/payments"
INVOICES_URL = "/api/invoices"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _seed_confirmed_invoice(db_session):
    from backend.app.models.user import User
    from backend.app.models.product import Product
    from backend.app.models.plan import Plan
    from backend.app.models.subscription import Subscription, SubscriptionLine
    from backend.app.models.invoice import Invoice
    from backend.app.core.security import hash_password
    customer = User(email="pay_c@test.com", hashed_password=hash_password("X@1aaaaa"), full_name="Pay C", role="customer")
    db_session.add(customer)
    product = Product(name="PayProd", sales_price=300, cost_price=0)
    db_session.add(product)
    db_session.flush()
    plan = Plan(product_id=product.id, name="PayPlan", price=300, billing_period="monthly")
    db_session.add(plan)
    db_session.flush()
    sub = Subscription(
        number="SUB-PAY01",
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
        quantity=1,
        unit_price=300,
        tax_rate=0,
        amount=300,
    )
    db_session.add(line)
    db_session.flush()
    invoice = Invoice(
        subscription_id=sub.id,
        customer_id=customer.id,
        billing_period_key="2026-10",
        subtotal=300,
        tax_amount=0,
        total=300,
        due_date=date.today(),
        status="confirmed",
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice.id


def test_record_payment_happy_path(client, admin_token, db_session):
    """POST /api/payments — valid payment against confirmed invoice → 201."""
    inv_id = _seed_confirmed_invoice(db_session)
    resp = client.post(
        PAYMENTS_URL,
        json={"invoice_id": inv_id, "amount": "300.00", "method": "bank_transfer", "payment_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 201, resp.text
    assert float(resp.json()["data"]["amount"]) == 300.0


def test_payment_zero_amount_returns_422(client, admin_token, db_session):
    """POST /api/payments — amount = 0 → 422."""
    inv_id = _seed_confirmed_invoice(db_session)
    resp = client.post(
        PAYMENTS_URL,
        json={"invoice_id": inv_id, "amount": "0", "method": "cash", "payment_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 422, resp.text


def test_payment_negative_amount_returns_422(client, admin_token, db_session):
    """POST /api/payments — amount = -50 → 422."""
    inv_id = _seed_confirmed_invoice(db_session)
    resp = client.post(
        PAYMENTS_URL,
        json={"invoice_id": inv_id, "amount": "-50", "method": "cash", "payment_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 422, resp.text


def test_payment_unknown_invoice_returns_404(client, admin_token, db_session):
    """POST /api/payments — non-existent invoice → 404."""
    resp = client.post(
        PAYMENTS_URL,
        json={"invoice_id": 99999, "amount": "100", "method": "cash", "payment_date": str(date.today())},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 404, resp.text


def test_customer_cannot_record_payment_returns_403(client, customer_token, db_session):
    """POST /api/payments — customer role attempting to record payment → 403 Forbidden."""
    inv_id = _seed_confirmed_invoice(db_session)
    resp = client.post(
        PAYMENTS_URL,
        json={"invoice_id": inv_id, "amount": "100", "method": "cash", "payment_date": str(date.today())},
        headers=auth_header(customer_token),
    )
    assert resp.status_code == 403, resp.text
