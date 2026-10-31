"""Raw SQL Database Engine Constraint & Immutability Tests.

These tests bypass FastAPI and Pydantic schemas entirely, executing raw SQL
directly against the database session to assert that the database engine itself
enforces UNIQUE constraints, CHECK constraints, Foreign Key restrictions, and
paid invoice immutability triggers at the kernel level.
"""
from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.app.models.user import User
from backend.app.models.product import Product
from backend.app.models.plan import Plan
from backend.app.models.subscription import Subscription
from backend.app.models.invoice import Invoice
from backend.app.models.variant import ProductVariant
from backend.app.models.discount import DiscountRule


@pytest.fixture
def base_fixtures(db_session):
    """Seed baseline valid parent records via ORM so all audit and default columns are cleanly set."""
    admin = User(
        email="raw_admin@test.com",
        hashed_password="hashed_password_placeholder",
        full_name="Raw Admin",
        role="admin",
    )
    customer = User(
        email="raw_cust@test.com",
        hashed_password="hashed_password_placeholder",
        full_name="Raw Customer",
        role="customer",
    )
    product = Product(
        name="Raw Enterprise License",
        product_type="service",
        sales_price=Decimal("1200.00"),
        cost_price=Decimal("600.00"),
    )
    db_session.add_all([admin, customer, product])
    db_session.commit()

    plan = Plan(
        product_id=product.id,
        name="Raw Monthly Plan",
        price=Decimal("1200.00"),
        billing_period="monthly",
        min_quantity=1,
        can_pause=True,
        can_renew=True,
        is_active=True,
    )
    db_session.add(plan)
    db_session.commit()

    sub = Subscription(
        number="SUB-RAW-001",
        customer_id=customer.id,
        plan_id=plan.id,
        start_date=date(2026, 10, 1),
        status="active",
    )
    db_session.add(sub)
    db_session.commit()

    invoice = Invoice(
        subscription_id=sub.id,
        customer_id=customer.id,
        billing_period_key="2026-10",
        subtotal=Decimal("1200.00"),
        tax_amount=Decimal("216.00"),
        total=Decimal("1416.00"),
        status="draft",
    )
    db_session.add(invoice)
    db_session.commit()

    return {
        "admin": admin,
        "customer": customer,
        "product": product,
        "plan": plan,
        "subscription": sub,
        "invoice": invoice,
    }


# ── 1. Unique Constraints ─────────────────────────────────────────────────────

def test_raw_unique_user_email_raises_integrity_error(db_session, base_fixtures):
    """Assert DB rejects duplicate email in users table via raw SQL."""
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO users (email, hashed_password, full_name, role, token_version, is_active, created_at, updated_at)
            VALUES ('raw_cust@test.com', 'pwd', 'Imposter', 'customer', 1, 'Y', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """))
        db_session.commit()
    db_session.rollback()


def test_raw_unique_subscription_number_raises_integrity_error(db_session, base_fixtures):
    """Assert DB rejects duplicate subscription number via raw SQL."""
    cust_id = base_fixtures["customer"].id
    plan_id = base_fixtures["plan"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO subscriptions (number, customer_id, plan_id, start_date, status, created_at, updated_at)
            VALUES ('SUB-RAW-001', :cid, :pid, '2026-11-01', 'draft', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"cid": cust_id, "pid": plan_id})
        db_session.commit()
    db_session.rollback()


def test_raw_unique_invoice_period_raises_integrity_error(db_session, base_fixtures):
    """Assert DB rejects duplicate (subscription_id, billing_period_key) double billing via raw SQL."""
    sub_id = base_fixtures["subscription"].id
    cust_id = base_fixtures["customer"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO invoices (subscription_id, customer_id, billing_period_key, subtotal, tax_amount, total, status, created_at, updated_at)
            VALUES (:sid, :cid, '2026-10', 1200.00, 216.00, 1416.00, 'draft', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"sid": sub_id, "cid": cust_id})
        db_session.commit()
    db_session.rollback()


def test_raw_unique_discount_code_raises_integrity_error(db_session):
    """Assert DB rejects duplicate discount rule code via raw SQL."""
    db_session.execute(text("""
        INSERT INTO discount_rules (code, name, rule_type, discount_value, applies_to, min_amount, min_quantity, valid_from, valid_to, usage_limit, times_used, is_active, created_at, updated_at)
        VALUES ('SAVE10', 'Save 10%', 'percent', 10.00, 'subscription', 0.00, 1, '2026-01-01', '2026-12-31', 100, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """))
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO discount_rules (code, name, rule_type, discount_value, applies_to, min_amount, min_quantity, valid_from, valid_to, usage_limit, times_used, is_active, created_at, updated_at)
            VALUES ('SAVE10', 'Duplicate Rule', 'fixed', 50.00, 'subscription', 0.00, 1, '2026-01-01', '2026-12-31', 100, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """))
        db_session.commit()
    db_session.rollback()


def test_raw_unique_variant_sku_raises_integrity_error(db_session, base_fixtures):
    """Assert DB rejects duplicate product variant SKU via raw SQL."""
    prod_id = base_fixtures["product"].id
    db_session.execute(text("""
        INSERT INTO product_variants (product_id, name, sku, price_delta, is_active, created_at, updated_at)
        VALUES (:pid, 'Standard Tier', 'RAW-SKU-01', 50.00, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """), {"pid": prod_id})
    db_session.commit()

    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO product_variants (product_id, name, sku, price_delta, is_active, created_at, updated_at)
            VALUES (:pid, 'Premium Tier', 'RAW-SKU-01', 75.00, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"pid": prod_id})
        db_session.commit()
    db_session.rollback()


# ── 2. Check Constraints ──────────────────────────────────────────────────────

def test_raw_check_payment_positive_raises_integrity_error(db_session, base_fixtures):
    """Assert ck_payment_positive rejects payment amount <= 0 via raw SQL."""
    inv_id = base_fixtures["invoice"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO payments (invoice_id, amount, method, payment_date, created_at, updated_at)
            VALUES (:inv_id, 0.00, 'bank_transfer', '2026-10-31', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"inv_id": inv_id})
        db_session.commit()
    db_session.rollback()

    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO payments (invoice_id, amount, method, payment_date, created_at, updated_at)
            VALUES (:inv_id, -150.00, 'bank_transfer', '2026-10-31', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"inv_id": inv_id})
        db_session.commit()
    db_session.rollback()


def test_raw_check_user_role_raises_integrity_error(db_session):
    """Assert ck_user_role rejects non-whitelisted roles via raw SQL."""
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO users (email, hashed_password, full_name, role, token_version, is_active, created_at, updated_at)
            VALUES ('super@test.com', 'pw', 'Super User', 'superadmin', 1, 'Y', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """))
        db_session.commit()
    db_session.rollback()


def test_raw_check_plan_billing_period_raises_integrity_error(db_session, base_fixtures):
    """Assert ck_plan_billing_period rejects non-whitelisted periods via raw SQL."""
    prod_id = base_fixtures["product"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO plans (product_id, name, price, billing_period, min_quantity, can_pause, can_renew, is_active, created_at, updated_at)
            VALUES (:pid, 'Hourly Plan', 10.00, 'hourly', 1, 0, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"pid": prod_id})
        db_session.commit()
    db_session.rollback()


def test_raw_check_subscription_status_raises_integrity_error(db_session, base_fixtures):
    """Assert ck_subscription_status rejects non-whitelisted statuses via raw SQL."""
    cust_id = base_fixtures["customer"].id
    plan_id = base_fixtures["plan"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO subscriptions (number, customer_id, plan_id, start_date, status, created_at, updated_at)
            VALUES ('SUB-ILLEGAL', :cid, :pid, '2026-10-01', 'terminated', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"cid": cust_id, "pid": plan_id})
        db_session.commit()
    db_session.rollback()


def test_raw_check_invoice_status_raises_integrity_error(db_session, base_fixtures):
    """Assert ck_invoice_status rejects non-whitelisted statuses via raw SQL."""
    sub_id = base_fixtures["subscription"].id
    cust_id = base_fixtures["customer"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO invoices (subscription_id, customer_id, billing_period_key, subtotal, tax_amount, total, status, created_at, updated_at)
            VALUES (:sid, :cid, '2026-12', 100.00, 18.00, 118.00, 'refunded', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"sid": sub_id, "cid": cust_id})
        db_session.commit()
    db_session.rollback()


# ── 3. Foreign Key & ON DELETE RESTRICT ────────────────────────────────────────

def test_raw_fk_restrict_delete_user_with_subscription(db_session, base_fixtures):
    """Assert DB restricts deleting a user who has active subscriptions."""
    cust_id = base_fixtures["customer"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("DELETE FROM users WHERE id = :cid"), {"cid": cust_id})
        db_session.commit()
    db_session.rollback()


def test_raw_fk_restrict_delete_plan_with_subscription(db_session, base_fixtures):
    """Assert DB restricts deleting a plan referenced by subscriptions."""
    plan_id = base_fixtures["plan"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("DELETE FROM plans WHERE id = :pid"), {"pid": plan_id})
        db_session.commit()
    db_session.rollback()


def test_raw_fk_insert_invalid_customer_id(db_session, base_fixtures):
    """Assert DB rejects inserting a subscription for a non-existent customer."""
    plan_id = base_fixtures["plan"].id
    with pytest.raises(IntegrityError):
        db_session.execute(text("""
            INSERT INTO subscriptions (number, customer_id, plan_id, start_date, status, created_at, updated_at)
            VALUES ('SUB-NONEXISTENT', 99999, :pid, '2026-10-01', 'draft', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"pid": plan_id})
        db_session.commit()
    db_session.rollback()


# ── 4. Paid Invoice Immutability Trigger ───────────────────────────────────────

def test_raw_paid_invoice_immutable_update_raises_integrity_error(db_session, base_fixtures):
    """Assert database kernel trigger rejects direct SQL update on paid invoice."""
    inv_id = base_fixtures["invoice"].id
    # Move invoice to paid
    db_session.execute(text("UPDATE invoices SET status = 'paid' WHERE id = :iid"), {"iid": inv_id})
    db_session.commit()

    # Now attempt a raw SQL update tampering with financial amounts
    with pytest.raises(IntegrityError):
        db_session.execute(text("UPDATE invoices SET total = 0.00 WHERE id = :iid"), {"iid": inv_id})
        db_session.commit()
    db_session.rollback()


def test_raw_paid_invoice_immutable_delete_raises_integrity_error(db_session, base_fixtures):
    """Assert database kernel trigger rejects direct SQL deletion of paid invoice."""
    inv_id = base_fixtures["invoice"].id
    # Move invoice to paid
    db_session.execute(text("UPDATE invoices SET status = 'paid' WHERE id = :iid"), {"iid": inv_id})
    db_session.commit()

    # Attempt raw SQL deletion
    with pytest.raises(IntegrityError):
        db_session.execute(text("DELETE FROM invoices WHERE id = :iid"), {"iid": inv_id})
        db_session.commit()
    db_session.rollback()
