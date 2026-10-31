"""Database Initialization and Seeding Script for Demo Data."""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.app.core.database import SessionLocal, create_tables
from backend.app.core.security import hash_password
from backend.app.models.user import User
from backend.app.models.product import Product, Plan
from backend.app.models.subscription import Subscription, SubscriptionLine
from backend.app.models.invoice import Invoice, InvoiceLine
from backend.app.models.payment import Payment
from backend.app.models.discount import DiscountRule
from backend.app.models.quotation_template import QuotationTemplate, QuotationTemplateLine


def seed_demo_data():
    """Seeds initial clean demo records into PostgreSQL."""
    create_tables()
    db = SessionLocal()
    try:
        # 1. Users
        admin = db.query(User).filter(User.email == "admin@brightloop.com").first()
        if not admin:
            admin = User(
                email="admin@brightloop.com",
                hashed_password=hash_password("Admin@1234"),
                full_name="Admin Director",
                role="admin",
            )
            db.add(admin)

        staff = db.query(User).filter(User.email == "staff@brightloop.com").first()
        if not staff:
            staff = User(
                email="staff@brightloop.com",
                hashed_password=hash_password("Staff@1234"),
                full_name="Staff Specialist",
                role="staff",
            )
            db.add(staff)

        customer = db.query(User).filter(User.email == "customer@brightloop.com").first()
        if not customer:
            customer = User(
                email="customer@brightloop.com",
                hashed_password=hash_password("Customer@1234"),
                full_name="Acme Enterprise (Customer)",
                role="customer",
            )
            db.add(customer)

        db.commit()
        db.refresh(admin)
        db.refresh(staff)
        db.refresh(customer)
        print("[OK] Users verified: admin, staff, customer.")

        # 2. Products
        suite = db.query(Product).filter(Product.name == "Brightloop Business Suite").first()
        if not suite:
            suite = Product(
                name="Brightloop Business Suite",
                product_type="software",
                sales_price=Decimal("1200.00"),
                cost_price=Decimal("400.00"),
                notes="Primary ERP and SaaS core platform",
            )
            db.add(suite)

        addon = db.query(Product).filter(Product.name == "Team Collab Add-on").first()
        if not addon:
            addon = Product(
                name="Team Collab Add-on",
                product_type="addon",
                sales_price=Decimal("250.00"),
                cost_price=Decimal("50.00"),
                notes="Unlimited workspace seats and chat integrations",
            )
            db.add(addon)

        analytics = db.query(Product).filter(Product.name == "Analytics Pro").first()
        if not analytics:
            analytics = Product(
                name="Analytics Pro",
                product_type="service",
                sales_price=Decimal("450.00"),
                cost_price=Decimal("120.00"),
                notes="Predictive metrics and export reporting",
            )
            db.add(analytics)

        db.commit()
        db.refresh(suite)
        db.refresh(addon)
        db.refresh(analytics)
        print("[OK] Products verified: 3 items.")

        # 3. Plans
        monthly_plan = db.query(Plan).filter(Plan.name == "Business Suite Monthly").first()
        if not monthly_plan:
            monthly_plan = Plan(
                product_id=suite.id,
                name="Business Suite Monthly",
                price=Decimal("1200.00"),
                billing_period="monthly",
                min_quantity=1,
                auto_close=False,
                can_pause=True,
                can_renew=True,
            )
            db.add(monthly_plan)

        yearly_plan = db.query(Plan).filter(Plan.name == "Business Suite Yearly").first()
        if not yearly_plan:
            yearly_plan = Plan(
                product_id=suite.id,
                name="Business Suite Yearly",
                price=Decimal("12000.00"),
                billing_period="yearly",
                min_quantity=1,
                auto_close=False,
                can_pause=False,
                can_renew=True,
            )
            db.add(yearly_plan)

        analytics_plan = db.query(Plan).filter(Plan.name == "Analytics Pro Monthly").first()
        if not analytics_plan:
            analytics_plan = Plan(
                product_id=analytics.id,
                name="Analytics Pro Monthly",
                price=Decimal("450.00"),
                billing_period="monthly",
                min_quantity=1,
            )
            db.add(analytics_plan)

        db.commit()
        db.refresh(monthly_plan)
        print("[OK] Plans verified: 3 plans.")

        # 4. Subscription
        sub1 = db.query(Subscription).filter(Subscription.number == "SUB-BL001").first()
        if not sub1:
            sub1 = Subscription(
                number="SUB-BL001",
                customer_id=customer.id,
                plan_id=monthly_plan.id,
                start_date=date(2026, 10, 1),
                expiry_date=date(2027, 10, 1),
                payment_terms="Net 15",
                status="active",
                notes="Standard enterprise monthly subscription",
            )
            db.add(sub1)
            db.flush()

            line1 = SubscriptionLine(
                subscription_id=sub1.id,
                product_id=suite.id,
                description="Brightloop Business Suite - Core Seat",
                quantity=1,
                unit_price=Decimal("1200.00"),
                tax_rate=Decimal("18.00"),
                amount=Decimal("1200.00"),
            )
            line2 = SubscriptionLine(
                subscription_id=sub1.id,
                product_id=addon.id,
                description="Team Collab Add-on Pack",
                quantity=2,
                unit_price=Decimal("250.00"),
                tax_rate=Decimal("18.00"),
                amount=Decimal("500.00"),
            )
            db.add_all([line1, line2])
            db.commit()
            db.refresh(sub1)

        print(f"[OK] Subscription verified: {sub1.number} (status={sub1.status}).")

        # 5. Invoice
        inv1 = db.query(Invoice).filter(
            Invoice.subscription_id == sub1.id,
            Invoice.billing_period_key == "2026-10",
        ).first()
        if not inv1:
            subtotal = Decimal("1700.00")
            tax = Decimal("306.00")  # 18% of 1700
            total = subtotal + tax
            inv1 = Invoice(
                subscription_id=sub1.id,
                customer_id=customer.id,
                billing_period_key="2026-10",
                subtotal=subtotal,
                tax_amount=tax,
                total=total,
                due_date=date(2026, 10, 15),
                status="confirmed",
                notes="October 2026 Billing Period",
            )
            db.add(inv1)
            db.flush()

            inv_line1 = InvoiceLine(
                invoice_id=inv1.id,
                product_id=suite.id,
                description="Brightloop Business Suite - Core Seat",
                quantity=1,
                unit_price=Decimal("1200.00"),
                tax_rate=Decimal("18.00"),
                net_amount=Decimal("1200.00"),
                tax_amount=Decimal("216.00"),
                amount=Decimal("1416.00"),
            )
            inv_line2 = InvoiceLine(
                invoice_id=inv1.id,
                product_id=addon.id,
                description="Team Collab Add-on Pack",
                quantity=2,
                unit_price=Decimal("250.00"),
                tax_rate=Decimal("18.00"),
                net_amount=Decimal("500.00"),
                tax_amount=Decimal("90.00"),
                amount=Decimal("590.00"),
            )
            db.add_all([inv_line1, inv_line2])
            db.commit()
            db.refresh(inv1)

        print(f"[OK] Invoice verified: ID={inv1.id} (Period={inv1.billing_period_key}, Total={inv1.total}).")

        # 6. Payment
        pay1 = db.query(Payment).filter(Payment.invoice_id == inv1.id).first()
        if not pay1:
            pay1 = Payment(
                invoice_id=inv1.id,
                amount=Decimal("2006.00"),
                method="bank_transfer",
                payment_date=date(2026, 10, 10),
                reference="TXN-20261010-001",
                notes="Full payment via NEFT",
            )
            db.add(pay1)
            inv1.status = "paid"
            db.commit()
            print(f"[OK] Payment verified: ID={pay1.id} on Invoice {inv1.id}.")

        # 7. Discount Rules
        d1 = db.query(DiscountRule).filter(DiscountRule.code == "WELCOME10").first()
        if not d1:
            d1 = DiscountRule(
                code="WELCOME10",
                name="10% Welcome Discount",
                rule_type="percent",
                discount_value=Decimal("10.00"),
                applies_to="subscription",
                valid_from=date(2026, 1, 1),
                valid_to=date(2026, 12, 31),
                usage_limit=100,
                is_active=True,
            )
            db.add(d1)
            db.commit()
            print("[OK] Discount rule verified: WELCOME10 (10% off).")

        # 8. Quotation Templates
        qt1 = db.query(QuotationTemplate).filter(QuotationTemplate.name == "Enterprise Starter Bundle").first()
        if not qt1:
            qt1 = QuotationTemplate(
                name="Enterprise Starter Bundle",
                description="Pre-packaged standard enterprise subscription with core seat and analytics",
                plan_id=monthly_plan.id,
                validity_days=30,
            )
            db.add(qt1)
            db.flush()

            qt_line1 = QuotationTemplateLine(
                template_id=qt1.id,
                product_id=suite.id,
                quantity=5,
                unit_price=Decimal("1200.00"),
            )
            qt_line2 = QuotationTemplateLine(
                template_id=qt1.id,
                product_id=analytics.id,
                quantity=1,
                unit_price=Decimal("450.00"),
            )
            db.add_all([qt_line1, qt_line2])
            db.commit()
            print("[OK] Quotation template verified: Enterprise Starter Bundle (30 days validity).")

        print("\nAll database seeds successfully established in local PostgreSQL (oh_db)!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
