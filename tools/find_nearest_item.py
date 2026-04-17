import math
from typing import Any, Dict, List

from database.client import inventory_col, normalize_item_name


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees) using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    # Convert latitude and longitude from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def find_nearest_item(item_name: str, retailer_location: dict) -> List[Dict[str, Any]]:
    """
    retailer_location format:
    {
        "latitude": 17.3850,
        "longitude": 78.4867
    }
    """
    normalized_item = normalize_item_name(item_name)

    lat1 = retailer_location["latitude"]
    lon1 = retailer_location["longitude"]

    # 1. Fetch ALL inventory matching the item name where quantity > 0
    all_matching_items = list(
        inventory_col.find(
            {
                "item_name": normalized_item,
                "quantity": {"$gt": 0},
            }
        )
    )

    valid_items = []
    
    # 2. Calculate distance for each wholesaler using Haversine
    for doc in all_matching_items:
        loc = doc.get("location", {})
        coords = loc.get("coordinates", [])
        
        # Ensure coordinates exist [longitude, latitude]
        if len(coords) == 2:
            lon2, lat2 = coords[0], coords[1]
            
            distance_km = haversine(lat1, lon1, lat2, lon2)
            
            # 3. Filter distance d <= 100 km
            if distance_km <= 100.0:
                doc["distance_km"] = round(distance_km, 2)
                valid_items.append(doc)

    # 4. Sort primarily by least distance, then by lowest price
    ranked = sorted(
        valid_items,
        key=lambda x: (x["distance_km"], x.get("price", float("inf")))
    )

    # Get top 3 options
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
                "distance_km": doc.get("distance_km"),  # Passing distance back to AI
                "location": doc.get("location"),
            }
        )

    return results