from typing import Any, Dict

from llm import xero_client
from llm.mock_tools import (
    check_availability,
    get_cost_analysis,
    get_guest_lookup,
    get_housekeeping_status,
    get_occupancy_report,
    get_revenue_forecast,
    get_revenue_report,
)


def run_tool(tool_name: str, tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches tool calls from Claude to concrete implementations.
    Uses mock tools when real MCP/integrations are not connected.
    """
    args = tool_arguments or {}
    period = args.get("period", "this_week")

    # Xero (real when credentials set, else handled below)
    if tool_name == "xero_profit_and_loss":
        from_date = args.get("from_date")
        to_date = args.get("to_date")
        if not from_date or not to_date:
            return {"success": False, "error": "from_date and to_date required"}
        try:
            data = xero_client.get_profit_and_loss(from_date, to_date)
            return {"success": True, "data": data}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    # Mock tools (PRD Week 1-2)
    if tool_name == "get_occupancy_report":
        return get_occupancy_report(period)
    if tool_name == "get_revenue_report":
        return get_revenue_report(period)
    if tool_name == "get_revenue_forecast":
        return get_revenue_forecast(period)
    if tool_name == "check_availability":
        return check_availability(
            args.get("check_in", ""),
            args.get("check_out", ""),
        )
    if tool_name == "get_cost_analysis":
        return get_cost_analysis(period)
    if tool_name == "get_guest_lookup":
        return get_guest_lookup(args.get("query", ""))
    if tool_name == "get_housekeeping_status":
        return get_housekeeping_status(args.get("date"))

    # create_booking: mock for demo
    if tool_name == "create_booking":
        return {
            "success": True,
            "data": {
                "status": "booking_created",
                "confirmation": "DEMO-001",
                "note": "Demo mode. Connect PMS to create real bookings.",
            },
        }

    return {"success": False, "error": f"Unknown tool_name '{tool_name}'"}

