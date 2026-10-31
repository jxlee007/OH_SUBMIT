"""In-process scheduler service for automated daily billing and renewal enforcement via APScheduler."""
import logging
from datetime import date, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.subscription import Subscription
from backend.app.models.invoice import Invoice
from backend.app.schemas.invoice import GenerateInvoiceRequest
from backend.app.services.invoice_service import generate_invoice

logger = logging.getLogger(__name__)

# Global BackgroundScheduler instance
scheduler = BackgroundScheduler(daemon=True)


def compute_billing_period_key(billing_period: str, target_date: date) -> str:
    """Computes standard billing period key (e.g. 2026-10 for monthly)."""
    if billing_period == "daily":
        return target_date.strftime("%Y-%m-%d")
    elif billing_period == "weekly":
        return f"{target_date.year}-W{target_date.isocalendar()[1]:02d}"
    elif billing_period == "yearly":
        return target_date.strftime("%Y")
    else:  # default monthly
        return target_date.strftime("%Y-%m")


def run_billing_cycle(db: Session, target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Executes automated billing and renewal cycle.
    - Scans active subscriptions where plan.can_renew == True.
    - Explicitly skips paused subscriptions.
    - Automatically closes expired non-renewable subscriptions.
    - Generates invoices for current period without double-billing.
    """
    target_date = target_date or date.today()
    due_date = target_date + timedelta(days=15)

    # 1. Count skipped paused subscriptions
    paused_count = db.query(Subscription).filter(Subscription.status == "paused").count()

    # 2. Query active subscriptions
    active_subs = db.query(Subscription).filter(Subscription.status == "active").all()

    invoices_generated = 0
    closed_expired = 0

    for sub in active_subs:
        plan = sub.plan
        can_renew = getattr(plan, "can_renew", True) if plan else True

        # Check for expiry on non-renewable subscriptions
        if not can_renew and sub.expiry_date and sub.expiry_date <= target_date:
            sub.status = "closed"
            closed_expired += 1
            continue

        billing_period = getattr(plan, "billing_period", "monthly") if plan else "monthly"
        period_key = compute_billing_period_key(billing_period, target_date)

        # Check if invoice already generated for this period
        existing_invoice = db.query(Invoice).filter(
            Invoice.subscription_id == sub.id,
            Invoice.billing_period_key == period_key,
        ).first()

        if not existing_invoice:
            try:
                req = GenerateInvoiceRequest(
                    subscription_id=sub.id,
                    billing_period_key=period_key,
                    due_date=due_date,
                )
                generate_invoice(req, db)
                invoices_generated += 1
            except Exception as exc:
                logger.warning(f"Could not auto-generate invoice for sub {sub.id}: {exc}")

    db.commit()

    return {
        "target_date": str(target_date),
        "active_processed": len(active_subs),
        "invoices_generated": invoices_generated,
        "paused_skipped": paused_count,
        "closed_expired": closed_expired,
    }


def _scheduled_billing_job():
    """Scheduled task executed by APScheduler."""
    logger.info("APScheduler executing daily billing and renewal cycle...")
    db = SessionLocal()
    try:
        run_billing_cycle(db)
    except Exception as exc:
        logger.error(f"Error in APScheduler daily billing execution: {exc}")
    finally:
        db.close()


def start_scheduler():
    """Start APScheduler in-process background worker."""
    if not scheduler.running:
        scheduler.add_job(
            _scheduled_billing_job,
            IntervalTrigger(hours=1),
            id="daily_billing_renewal_job",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("APScheduler started successfully.")


def stop_scheduler():
    """Gracefully shutdown APScheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
