from typing import Any, Dict

from database.client import (
    wholesalers_col,
    inventory_col,
    normalize_item_name,
    serialize_doc,
)


def update_inventory(
    wholesaler_number: str,
    item_name: str,
    quantity: int,
    price: float,
) -> Dict[str, Any]:
    wholesaler = wholesalers_col.find_one({"phone": wholesaler_number})
    if not wholesaler:
        return {
            "success": False,
            "message": f"Wholesaler with phone {wholesaler_number} not found.",
        }

    normalized_item = normalize_item_name(item_name)

    result = inventory_col.update_one(
        {
            "wholesaler_number": wholesaler_number,
            "item_name": normalized_item,
        },
        {
            "$set": {
                "wholesaler_number": wholesaler_number,
                "wholesaler_name": wholesaler.get("name", "Unknown Wholesaler"),
                "item_name": normalized_item,
                "quantity": int(quantity),
                "price": float(price),
                "location": wholesaler.get("location"),
            }
        },
        upsert=True,
    )

    saved_doc = inventory_col.find_one(
        {
            "wholesaler_number": wholesaler_number,
            "item_name": normalized_item,
        }
    )

    return {
        "success": True,
        "message": "Inventory inserted successfully." if result.upserted_id else "Inventory updated successfully.",
        "inventory": serialize_doc(saved_doc),
    }