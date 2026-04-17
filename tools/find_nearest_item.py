from typing import Any, Dict, List

from database.client import inventory_col, geojson_point, normalize_item_name


def find_nearest_item(item_name: str, retailer_location: dict) -> List[Dict[str, Any]]:
    """
    retailer_location format:
    {
        "latitude": 17.3850,
        "longitude": 78.4867
    }
    """
    normalized_item = normalize_item_name(item_name)

    latitude = retailer_location["latitude"]
    longitude = retailer_location["longitude"]

    nearby_items = list(
        inventory_col.find(
            {
                "item_name": normalized_item,
                "quantity": {"$gt": 0},
                "location": {
                    "$near": {
                        "$geometry": geojson_point(longitude, latitude),
                        "$maxDistance": 30000
                    }
                },
            },
            {
                "wholesaler_number": 1,
                "wholesaler_name": 1,
                "item_name": 1,
                "price": 1,
                "quantity": 1,
                "location": 1,
            },
        ).limit(15)
    )

    ranked = sorted(
        nearby_items,
        key=lambda x: (x.get("price", float("inf")))
    )

    top_3 = ranked[:3]

    results = []
    for doc in top_3:
        results.append(
            {
                "wholesaler_number": doc.get("wholesaler_number"),
                "wholesaler_name": doc.get("wholesaler_name", "Unknown Wholesaler"),
                "item_name": doc.get("item_name"),
                "price": doc.get("price"),
                "available_quantity": doc.get("quantity"),
                "location": doc.get("location"),
            }
        )

    return results