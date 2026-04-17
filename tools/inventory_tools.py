from langchain_core.tools import tool
from database.client import users_col, normalize_item_name
from typing import Any, Dict, List

@tool
def distance_and_price_calculator(retailer_phone_number: str, requested_item: str) -> str:
    """
    Computes distance and finds the best wholesale prices for a requested item.
    
    Args:
        retailer_phone_number (str): The phone number of the retailer making the request.
        requested_item (str): The name of the item they want to buy.
    """
    # 1. Look up the retailer's coordinates
    retailer = users_col.find_one({"phone": retailer_phone_number})
    
    if not retailer or "location" not in retailer:
        return "❌ Error: Your location is missing. Please share your WhatsApp location pin so I can find the nearest wholesalers for you."
    
    retailer_coords = retailer["location"]["coordinates"] # [longitude, latitude]
    normalized_item = normalize_item_name(requested_item)

    # 2. Run MongoDB $geoNear aggregation pipeline
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": retailer_coords
                },
                "distanceField": "distance",
                "maxDistance": 100000, # 100km in meters
                "query": {
                    "role": "wholesaler",
                    "inventory": {
                        "$elemMatch": {
                            "item_name": normalized_item,
                            "in_stock": True
                        }
                    }
                },
                "spherical": True
            }
        },
        # Unwind inventory to filter specific item and sort by its price
        {"$unwind": "$inventory"},
        {
            "$match": {
                "inventory.item_name": normalized_item,
                "inventory.in_stock": True
            }
        },
        # Sort by price first (ascending), then by distance (ascending)
        {
            "$sort": {
                "inventory.price": 1,
                "distance": 1
            }
        },
        {"$limit": 3}
    ]

    results = list(users_col.aggregate(pipeline))

    if not results:
        return f"😔 Sorry, I couldn't find any wholesalers for *{requested_item}* within 100km."

    # 3. Format the output
    response = f"✅ Here are the top 3 best deals for *{requested_item}* near you:\n\n"
    
    for i, doc in enumerate(results, 1):
        name = doc.get("name", "Unknown Wholesaler")
        price = doc["inventory"]["price"]
        unit = doc["inventory"].get("unit", "unit")
        distance_km = round(doc["distance"] / 1000, 1) # convert meters to km
        
        response += f"{i}. *{name}*\n"
        response += f"   💰 Price: ₹{price} per {unit}\n"
        response += f"   📍 Distance: {distance_km} km\n\n"

    return response.strip()
