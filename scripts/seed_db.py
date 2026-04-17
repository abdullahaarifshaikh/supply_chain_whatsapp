import sys
import os
sys.path.append(os.getcwd())

from database.client import users_col, ensure_indexes

def populate_test_data():
    ensure_indexes()
    
    users = [
        # RETAILER
        {
            "phone": "+919900000001",
            "name": "Fresh Mart",
            "role": "retailer",
            "location": {
                "type": "Point",
                "coordinates": [78.4867, 17.3850] # Hyderabad
            }
        },
        # WHOLESALERS
        {
            "phone": "+918800000001",
            "name": "Egg King Traders",
            "role": "wholesaler",
            "location": {
                "type": "Point",
                "coordinates": [78.4900, 17.3900]
            },
            "inventory": [
                {"item_name": "eggs", "price": 140, "unit": "tray", "in_stock": True},
                {"item_name": "milk", "price": 30, "unit": "liter", "in_stock": True}
            ]
        },
        {
            "phone": "+918800000002",
            "name": "General Foods Supply",
            "role": "wholesaler",
            "location": {
                "type": "Point",
                "coordinates": [78.5000, 17.4000]
            },
            "inventory": [
                {"item_name": "eggs", "price": 135, "unit": "tray", "in_stock": True},
                {"item_name": "rice", "price": 50, "unit": "kg", "in_stock": True}
            ]
        },
        {
            "phone": "+918800000003",
            "name": "Organic Greens",
            "role": "wholesaler",
            "location": {
                "type": "Point",
                "coordinates": [78.4700, 17.3700]
            },
            "inventory": [
                {"item_name": "rice", "price": 60, "unit": "kg", "in_stock": True},
                {"item_name": "eggs", "price": 150, "unit": "tray", "in_stock": True}
            ]
        }
    ]
    
    users_col.delete_many({}) # Clear existing
    users_col.insert_many(users)
    print("✅ Test data populated successfully.")

if __name__ == "__main__":
    populate_test_data()
