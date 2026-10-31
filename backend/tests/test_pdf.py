"""Invoice PDF generation tests using ReportLab and pypdf verification."""
import io
from datetime import date
from decimal import Decimal
from pypdf import PdfReader
from starlette.testclient import TestClient

from backend.app.models.user import User
from backend.app.models.product import Product, Plan
from backend.app.models.subscription import Subscription, SubscriptionLine
from backend.app.models.invoice import Invoice, InvoiceLine
from backend.app.core.security import hash_password, create_access_token


def _seed_test_invoice(db_session, num_lines: int = 2):
    customer = User(
        email="pdf_customer@brightloop.com",
        hashed_password=hash_password("PdfPass@123"),
        full_name="PDF Test Enterprise",
        role="customer",
    )
    db_session.add(customer)
    product = Product(name="Enterprise Cloud Service", sales_price=1000, cost_price=200)
    db_session.add(product)
    db_session.flush()

    plan = Plan(product_id=product.id, name="Cloud Scale Plan", price=1000, billing_period="monthly")
    db_session.add(plan)
    db_session.flush()

    sub = Subscription(
        number="SUB-PDF-001",
        customer_id=customer.id,
        plan_id=plan.id,
        start_date=date.today(),
        status="active",
    )
    db_session.add(sub)
    db_session.flush()

    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")
    inv_lines = []

    for i in range(1, num_lines + 1):
        line_gross = Decimal("1000.00")
        line_discount = Decimal("100.00") if i == 1 else Decimal("0.00")
        line_net = line_gross - line_discount
        line_tax = (line_net * Decimal("18.00") / Decimal("100.00")).quantize(Decimal("0.01"))
        line_amount = line_net + line_tax
        subtotal += line_net
        tax_total += line_tax

        inv_lines.append(
            InvoiceLine(
                product_id=product.id,
                description=f"Module Service Tier #{i}",
                quantity=1,
                unit_price=Decimal("1000.00"),
                tax_rate=Decimal("18.00"),
                discount_amount=line_discount,
                net_amount=line_net,
                tax_amount=line_tax,
                amount=line_amount,
            )
        )

    invoice = Invoice(
        subscription_id=sub.id,
        customer_id=customer.id,
        billing_period_key="2026-PDF-01",
        subtotal=subtotal,
        tax_amount=tax_total,
        total=subtotal + tax_total,
        due_date=date.today(),
        status="confirmed",
        lines=inv_lines,
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice, customer


def test_pdf_download_happy_path(client: TestClient, admin_token: str, db_session):
    """1. Happy path: response 200, body starts with b'%PDF', content type correct."""
    invoice, customer = _seed_test_invoice(db_session, num_lines=2)

    resp = client.get(
        f"/api/invoices/{invoice.id}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"
    assert f"attachment; filename=invoice-{invoice.id}.pdf" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF")


def test_pdf_extracted_text_contains_invoice_number_and_grand_total(client: TestClient, admin_token: str, db_session):
    """2. Extracted text (pypdf) contains the invoice number and the grand total string."""
    invoice, _ = _seed_test_invoice(db_session, num_lines=2)

    resp = client.get(
        f"/api/invoices/{invoice.id}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    reader = PdfReader(io.BytesIO(resp.content))
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()

    # Invoice number verification
    assert f"INV-{invoice.id}" in extracted_text
    # Grand total verification
    total_str = f"{Decimal(str(invoice.total)):.2f}"
    assert total_str in extracted_text
    # Company branding verification
    assert "Brightloop" in extracted_text


def test_pdf_page_count_is_one_for_five_line_invoice(client: TestClient, admin_token: str, db_session):
    """3. Page count is exactly 1 for a 5-line invoice."""
    invoice, _ = _seed_test_invoice(db_session, num_lines=5)

    resp = client.get(
        f"/api/invoices/{invoice.id}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    reader = PdfReader(io.BytesIO(resp.content))
    assert len(reader.pages) == 1, f"Expected 1 page, got {len(reader.pages)}"


def test_customer_cannot_download_another_customers_invoice_returns_403(client: TestClient, db_session):
    """4. Customer downloads another customer's invoice -> 403 Forbidden."""
    invoice, owner = _seed_test_invoice(db_session, num_lines=1)

    other_user = User(
        email="stranger@other.com",
        hashed_password=hash_password("Str@ng3rPass"),
        full_name="Stranger Inc",
        role="customer",
    )
    db_session.add(other_user)
    db_session.commit()

    owner_token = create_access_token({"sub": str(owner.id), "role": "customer"})
    stranger_token = create_access_token({"sub": str(other_user.id), "role": "customer"})

    # Owner can download their own invoice
    owner_resp = client.get(
        f"/api/invoices/{invoice.id}/pdf",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_resp.status_code == 200
    assert owner_resp.content.startswith(b"%PDF")

    # Stranger receives 403 Forbidden
    stranger_resp = client.get(
        f"/api/invoices/{invoice.id}/pdf",
        headers={"Authorization": f"Bearer {stranger_token}"},
    )
    assert stranger_resp.status_code == 403
    assert "Access denied" in stranger_resp.text


def test_pdf_unknown_invoice_id_returns_404(client: TestClient, admin_token: str):
    """5. Unknown invoice id -> 404 Not Found."""
    resp = client.get(
        "/api/invoices/999999/pdf",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()
