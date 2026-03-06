"""
Mock tool implementations for StayIntel intents.
Used when real MCP servers or integrations are not yet connected.
PRD: Week 1-2 - Implement mock tools for each intent.
"""
from datetime import date, timedelta
from typing import Any, Dict


def _parse_period(period: str) -> tuple[str, str]:
    """Convert period string to from_date, to_date (YYYY-MM-DD)."""
    today = date.today()
    if period in ("next_week", "next week"):
        start = today + timedelta(days=1)
        end = today + timedelta(days=7)
    elif period in ("last_week", "last week"):
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
    elif period in ("this_week", "this week"):
        start = today - timedelta(days=today.weekday())
        end = today + timedelta(days=6 - today.weekday())
    elif period in ("last_month", "last month"):
        start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        end = today.replace(day=1) - timedelta(days=1)
    else:
        start = today - timedelta(days=7)
        end = today
    return start.isoformat(), end.isoformat()


def get_occupancy_report(period: str = "this_week") -> Dict[str, Any]:
    """Mock occupancy report. Replace with PMS MCP when available."""
    from_d, to_d = _parse_period(period)
    return {
        "success": True,
        "data": {
            "period": {"from": from_d, "to": to_d},
            "occupancy_pct": 71.3,
            "rooms_available": 94,
            "rooms_sold": 67,
            "rooms_remaining": 27,
            "note": "Demo data. Connect PMS for real occupancy.",
        },
    }


def get_revenue_report(period: str = "last_month") -> Dict[str, Any]:
    """Mock revenue report. Replace with Xero/PMS when available."""
    from_d, to_d = _parse_period(period)
    return {
        "success": True,
        "data": {
            "period": {"from": from_d, "to": to_d},
            "room_revenue": 28450.00,
            "other_revenue": 3200.00,
            "total_revenue": 31650.00,
            "adr": 142.50,
            "revpar": 101.60,
            "note": "Demo data. Connect Xero for real revenue.",
        },
    }


def get_revenue_forecast(period: str = "next_week") -> Dict[str, Any]:
    """Mock revenue forecast. Replace with Revenue MCP when available."""
    from_d, to_d = _parse_period(period)
    return {
        "success": True,
        "data": {
            "period": {"from": from_d, "to": to_d},
            "projected_revenue": 34280.00,
            "projected_occupancy_pct": 68.0,
            "confidence": 0.75,
            "note": "Demo forecast. Connect PMS/Xero for real forecasts.",
        },
    }


def check_availability(check_in: str = "", check_out: str = "") -> Dict[str, Any]:
    """Mock availability check. Replace with PMS MCP when available."""
    today = date.today()
    ci = check_in or (today + timedelta(days=1)).isoformat()
    co = check_out or (today + timedelta(days=3)).isoformat()
    return {
        "success": True,
        "data": {
            "check_in": ci,
            "check_out": co,
            "rooms_available": 12,
            "room_types": [
                {"type": "Standard Double", "available": 5, "rate": 98.00},
                {"type": "Deluxe", "available": 4, "rate": 128.00},
                {"type": "Suite", "available": 3, "rate": 189.00},
            ],
            "note": "Demo data. Connect PMS for real availability.",
        },
    }


def get_cost_analysis(period: str = "last_month") -> Dict[str, Any]:
    """Mock cost analysis. Replace with Xero when available."""
    from_d, to_d = _parse_period(period)
    return {
        "success": True,
        "data": {
            "period": {"from": from_d, "to": to_d},
            "total_costs": 18500.00,
            "breakdown": {
                "staff": 9200.00,
                "utilities": 2100.00,
                "housekeeping": 3400.00,
                "other": 3800.00,
            },
            "note": "Demo data. Connect Xero for real cost analysis.",
        },
    }


def get_guest_lookup(query: str) -> Dict[str, Any]:
    """Mock guest lookup. Replace with PMS MCP when available."""
    return {
        "success": True,
        "data": {
            "query": query,
            "guests": [
                {
                    "name": "John Smith",
                    "email": "john@example.com",
                    "check_in": "2026-03-05",
                    "check_out": "2026-03-08",
                },
            ],
            "note": "Demo data. Connect PMS for real guest lookup.",
        },
    }


def get_housekeeping_status(date_str: str | None = None) -> Dict[str, Any]:
    """Mock housekeeping status. Replace with Housekeeping MCP when available."""
    d = date_str or date.today().isoformat()
    return {
        "success": True,
        "data": {
            "date": d,
            "total_rooms": 94,
            "cleaned": 67,
            "in_progress": 8,
            "pending": 19,
            "note": "Demo data. Connect Housekeeping MCP for real status.",
        },
    }
