import os
from typing import Dict, Any

import requests


XERO_BASE_URL = "https://api.xero.com/api.xro/2.0"


def _build_headers() -> Dict[str, str]:
    """
    Returns headers required for Xero API calls using a bearer token.
    Expects XERO_BEARER_TOKEN and XERO_TENANT_ID to be set in the environment.
    """
    token = os.getenv("XERO_BEARER_TOKEN")
    tenant_id = os.getenv("XERO_TENANT_ID")

    if not token or not tenant_id:
        raise RuntimeError(
            "Xero configuration missing: set XERO_BEARER_TOKEN and XERO_TENANT_ID"
        )

    return {
        "Authorization": f"Bearer {token}",
        "Xero-tenant-id": tenant_id,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_profit_and_loss(from_date: str, to_date: str) -> Dict[str, Any]:
    """
    Fetch a Profit and Loss report from Xero between from_date and to_date
    (inclusive). Dates must be ISO formatted strings: YYYY-MM-DD.
    """
    headers = _build_headers()
    params = {
        "fromDate": from_date,
        "toDate": to_date,
    }

    response = requests.get(
        f"{XERO_BASE_URL}/Reports/ProfitAndLoss",
        headers=headers,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

