import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.client import (
    ensure_indexes,
    retailers_col,
    wholesalers_col,
    inventory_col,
    orders_col,
)

# Clear old data
retailers_col.delete_many({})
orders_col.delete_many({})
wholesalers_col.delete_many({})
inventory_col.delete_many({})

ensure_indexes()

retailers = [
    {
        "phone": "+919900000001",
        "name": "Fresh Mart",
        "location": {
            "type": "Point",
            "coordinates": [78.4867, 17.3850]
        }
    },
    {
        "phone": "+919900000002",
        "name": "Daily Needs Store",
        "location": {
            "type": "Point",
            "coordinates": [78.4900, 17.3900]
        }
    }
]

wholesalers = [
    {
        "phone": "+918800000001",
        "name": "Egg King Traders",
        "location": {
            "type": "Point",
            "coordinates": [78.4950, 17.4000]
        }
    },
    {
        "phone": "+918800000002",
        "name": "Rice Hub Wholesale",
        "location": {
            "type": "Point",
            "coordinates": [78.4700, 17.3700]
        }
    },
    {
        "phone": "+918800000003",
        "name": "General Foods Supply",
        "location": {
            "type": "Point",
            "coordinates": [78.5000, 17.3800]
        }
    }
]

inventory = [
    {
        "wholesaler_number": "+918800000001",
        "wholesaler_name": "Egg King Traders",
        "item_name": "eggs",
        "quantity": 500,
        "price": 5,
        "location": {
            "type": "Point",
            "coordinates": [78.4950, 17.4000]
        }
    },
    {
        "wholesaler_number": "+918800000003",
        "wholesaler_name": "General Foods Supply",
        "item_name": "eggs",
        "quantity": 300,
        "price": 4.5,
        "location": {
            "type": "Point",
            "coordinates": [78.5000, 17.3800]
        }
    },
    {
        "wholesaler_number": "+918800000002",
        "wholesaler_name": "Rice Hub Wholesale",
        "item_name": "rice",
        "quantity": 1000,
        "price": 42,
        "location": {
            "type": "Point",
            "coordinates": [78.4700, 17.3700]
        }
    },
    {
        "wholesaler_number": "+918800000003",
        "wholesaler_name": "General Foods Supply",
        "item_name": "sugar",
        "quantity": 700,
        "price": 48,
        "location": {
            "type": "Point",
            "coordinates": [78.5000, 17.3800]
        }
    }
]

retailers_col.insert_many(retailers)
wholesalers_col.insert_many(wholesalers)
inventory_col.insert_many(inventory)

print("Dummy data inserted into retailer and wholesalers databases successfully.")