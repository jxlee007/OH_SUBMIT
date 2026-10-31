"""Dashboard summary tests."""

SUMMARY_URL = "/api/dashboard/summary"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_summary_empty_db(client, admin_token):
    """GET /api/dashboard/summary — empty DB → 200 with zero counts."""
    resp = client.get(SUMMARY_URL, headers=auth_header(admin_token))
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["active_subscriptions"] == 0
    assert float(data["total_revenue"]) == 0.0


def test_summary_customer_forbidden(client, customer_token):
    """GET /api/dashboard/summary — customer role → 403."""
    resp = client.get(SUMMARY_URL, headers=auth_header(customer_token))
    assert resp.status_code == 403, resp.text
