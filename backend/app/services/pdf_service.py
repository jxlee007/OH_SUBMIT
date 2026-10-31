"""Invoice PDF generation service using ReportLab.
Pure presentation function that renders stored invoice data to PDF bytes without database access.
"""
import io
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def render_invoice_pdf(invoice) -> bytes:
    """Renders invoice data to PDF bytes. Pure function with zero DB access.
    All figures are taken verbatim from stored invoice attributes without recalculation.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
    )
    subtitle_style = ParagraphStyle(
        "InvoiceSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b"),
    )
    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
    )
    cell_right_style = ParagraphStyle(
        "TableCellRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=2,
        textColor=colors.HexColor("#1e293b"),
    )
    total_label_style = ParagraphStyle(
        "TotalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=2,
        textColor=colors.HexColor("#334155"),
    )
    grand_total_style = ParagraphStyle(
        "GrandTotal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=2,
        textColor=colors.HexColor("#4338ca"),
    )

    story = []

    # 1. Company Header & Invoice Details
    customer_name = "Customer"
    customer_email = ""
    if hasattr(invoice, "customer") and invoice.customer:
        customer_name = getattr(invoice.customer, "full_name", "") or getattr(invoice.customer, "email", "Customer")
        customer_email = getattr(invoice.customer, "email", "")
    elif hasattr(invoice, "customer_id"):
        customer_name = f"Customer #{invoice.customer_id}"

    inv_number = f"INV-{invoice.id}"
    inv_status = getattr(invoice, "status", "DRAFT").upper()
    billing_period = getattr(invoice, "billing_period_key", "N/A")
    due_date = str(getattr(invoice, "due_date", "Upon Receipt"))

    header_data = [
        [
            Paragraph("<b>Brightloop Subscriptions</b>", title_style),
            Paragraph(f"<b>INVOICE: {inv_number}</b>", ParagraphStyle("InvNum", parent=title_style, alignment=2, fontSize=16, leading=20)),
        ],
        [
            Paragraph("Brightloop Inc. • 100 Innovation Park, Tech Hub<br/>support@brightloop.com • GSTIN: 09AAACB1234F1Z5", subtitle_style),
            Paragraph(f"Status: <b>{inv_status}</b><br/>Period: <b>{billing_period}</b><br/>Due: <b>{due_date}</b>", ParagraphStyle("Meta", parent=subtitle_style, alignment=2)),
        ],
        [
            Paragraph(f"<b>Billed To:</b><br/>{customer_name}<br/>{customer_email}", subtitle_style),
            Paragraph("Currency: <b>INR (₹)</b>", ParagraphStyle("Curr", parent=subtitle_style, alignment=2)),
        ],
    ]

    header_table = Table(header_data, colWidths=[3.8 * inch, 3.8 * inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # 2. Line Items Table
    table_data = [
        [
            Paragraph("Item Description", header_style),
            Paragraph("Qty", ParagraphStyle("ThCenter", parent=header_style, alignment=1)),
            Paragraph("Unit Price (₹)", ParagraphStyle("ThRight", parent=header_style, alignment=2)),
            Paragraph("Discount (₹)", ParagraphStyle("ThRight", parent=header_style, alignment=2)),
            Paragraph("Tax Rate", ParagraphStyle("ThRight", parent=header_style, alignment=2)),
            Paragraph("Line Total (₹)", ParagraphStyle("ThRight", parent=header_style, alignment=2)),
        ]
    ]

    lines = getattr(invoice, "lines", [])
    for line in lines:
        desc = getattr(line, "description", "") or "Subscription Service"
        qty = str(getattr(line, "quantity", 1))
        unit_price = f"{Decimal(str(getattr(line, 'unit_price', 0))):.2f}"
        discount = f"{Decimal(str(getattr(line, 'discount_amount', 0))):.2f}"
        tax_rate = f"{Decimal(str(getattr(line, 'tax_rate', 0)))}%"
        amount = f"{Decimal(str(getattr(line, 'amount', 0))):.2f}"

        table_data.append([
            Paragraph(desc, cell_style),
            Paragraph(qty, ParagraphStyle("TdCenter", parent=cell_style, alignment=1)),
            Paragraph(unit_price, cell_right_style),
            Paragraph(discount, cell_right_style),
            Paragraph(tax_rate, cell_right_style),
            Paragraph(amount, cell_right_style),
        ])

    lines_table = Table(table_data, colWidths=[2.6 * inch, 0.6 * inch, 1.1 * inch, 1.0 * inch, 0.9 * inch, 1.4 * inch])
    lines_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338ca")),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(lines_table)
    story.append(Spacer(1, 12))

    # 3. Summary & Grand Total (Stored invoice values, strictly never recalculated)
    subtotal_val = f"{Decimal(str(getattr(invoice, 'subtotal', 0))):.2f}"
    tax_val = f"{Decimal(str(getattr(invoice, 'tax_amount', 0))):.2f}"
    total_val = f"{Decimal(str(getattr(invoice, 'total', 0))):.2f}"

    totals_data = [
        [Paragraph("Subtotal:", total_label_style), Paragraph(f"₹ {subtotal_val}", cell_right_style)],
        [Paragraph("Taxes (GST):", total_label_style), Paragraph(f"₹ {tax_val}", cell_right_style)],
        [Paragraph("<b>Grand Total:</b>", grand_total_style), Paragraph(f"<b>₹ {total_val}</b>", grand_total_style)],
    ]
    totals_table = Table(totals_data, colWidths=[6.2 * inch, 1.4 * inch])
    totals_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEABOVE", (0, 2), (-1, 2), 1, colors.HexColor("#4338ca")),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 20))

    # 4. Footer notes
    footer_text = Paragraph(
        "Thank you for choosing Brightloop. Invoices are subject to terms of service.<br/>"
        "Official Odoo x FLUX Lucknow Hackathon '26 Subscription Platform • Powered by PostgreSQL.",
        subtitle_style,
    )
    story.append(footer_text)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
