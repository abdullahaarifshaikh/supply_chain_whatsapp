from dotenv import load_dotenv
import os
from pymongo import MongoClient, ASCENDING
from typing import Any, Dict, List, Optional

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "supply_chain")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Unified collection for all users (retailers and wholesalers)
users_col = db["users"]
orders_col = db["orders"]


def ensure_indexes() -> None:
    # Index for phone numbers (unique)
    users_col.create_index([("phone", ASCENDING)], unique=True)
    # 2dsphere index for location-based queries
    users_col.create_index([("location", "2dsphere")])
    # Index for roles to speed up filtering
    users_col.create_index([("role", ASCENDING)])
    
    orders_col.create_index([("retailer_number", ASCENDING)])
    orders_col.create_index([("created_at", ASCENDING)])


def geojson_point(longitude: float, latitude: float) -> dict:
    return {
        "type": "Point",
        "coordinates": [longitude, latitude],
    }


def normalize_item_name(item_name: str) -> str:
    return item_name.strip().lower()


def serialize_doc(doc: Optional[dict]) -> Optional[dict]:
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc