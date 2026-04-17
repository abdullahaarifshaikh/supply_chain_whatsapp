from dotenv import load_dotenv
import os
from pymongo import MongoClient, ASCENDING

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
RETAILER_DB_NAME = os.getenv("RETAILER_DB_NAME", "retailer")
WHOLESALER_DB_NAME = os.getenv("WHOLESALER_DB_NAME", "wholesalers")

client = MongoClient(MONGO_URI)

retailer_db = client[RETAILER_DB_NAME]
wholesaler_db = client[WHOLESALER_DB_NAME]

retailers_col = retailer_db["retailers"]
orders_col = retailer_db["orders"]

wholesalers_col = wholesaler_db["wholesalers"]
inventory_col = wholesaler_db["inventory"]


def ensure_indexes() -> None:
    retailers_col.create_index([("phone", ASCENDING)], unique=True)
    retailers_col.create_index([("location", "2dsphere")])

    wholesalers_col.create_index([("phone", ASCENDING)], unique=True)
    wholesalers_col.create_index([("location", "2dsphere")])

    inventory_col.create_index(
        [("wholesaler_number", ASCENDING), ("item_name", ASCENDING)],
        unique=True,
    )
    inventory_col.create_index([("location", "2dsphere")])
    inventory_col.create_index([("item_name", ASCENDING)])
    inventory_col.create_index([("price", ASCENDING)])

    orders_col.create_index([("retailer_number", ASCENDING)])
    orders_col.create_index([("created_at", ASCENDING)])


def geojson_point(longitude: float, latitude: float) -> dict:
    return {
        "type": "Point",
        "coordinates": [longitude, latitude],
    }


def normalize_item_name(item_name: str) -> str:
    return item_name.strip().lower()


def serialize_doc(doc: dict | None) -> dict | None:
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc