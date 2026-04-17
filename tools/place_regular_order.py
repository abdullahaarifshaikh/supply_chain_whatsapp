from datetime import datetime, timezone
from typing import Any, Dict, List

from database.client import (
    retailers_col,
    inventory_col,
    orders_col,
    normalize_item_name,
    serialize_doc,
)


def place_regular_order(retailer_number: str, item_list: List[dict]) -> Dict[str, Any]:
    """
    item_list format:
    [
        {"item_name": "eggs", "quantity": 50},
        {"item_name": "rice", "quantity": 10}
    ]
    """
    retailer = retailers_col.find_one({"phone": retailer_number})
    if not retailer:
        return {
            "success": False,
            "message": f"Retailer with phone {retailer_number} not found.",
        }

    processed_items: List[Dict[str, Any]] = []
    total_estimated_amount = 0.0

    for item in item_list:
        item_name = normalize_item_name(item["item_name"])
        quantity = int(item["quantity"])

        cheapest_inventory = inventory_col.find_one(
            {
                "item_name": item_name,
                "quantity": {"$gt": 0},
            },
            sort=[("price", 1)],
        )

        estimated_unit_price = float(cheapest_inventory["price"]) if cheapest_inventory else 0.0
        estimated_line_total = estimated_unit_price * quantity
        total_estimated_amount += estimated_line_total

        processed_items.append(
            {
                "item_name": item_name,
                "quantity": quantity,
                "estimated_unit_price": estimated_unit_price,
                "estimated_line_total": estimated_line_total,
                "matched_wholesaler_number": (
                    cheapest_inventory.get("wholesaler_number") if cheapest_inventory else None
                ),
            }
        )

    order_doc = {
        "retailer_number": retailer_number,
        "retailer_name": retailer.get("name"),
        "items": processed_items,
        "total_estimated_amount": round(total_estimated_amount, 2),
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
        "source": "whatsapp_regular_order",
    }

    result = orders_col.insert_one(order_doc)
    order_doc["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Regular order created successfully.",
        "order": serialize_doc(order_doc),
    }