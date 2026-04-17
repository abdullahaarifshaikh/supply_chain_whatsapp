from fastapi import APIRouter, Request, BackgroundTasks
from database.client import users_col, geojson_point
from core.agent import run_agent_workflow
import logging

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handles incoming WhatsApp payloads.
    - Intercepts locations and saves them to the database.
    - Forwards text messages to the LangGraph AI Agent.
    """
    payload = await request.json()
    
    # Extracting standard WhatsApp payload fields (example structure)
    # Note: Payload structure depends on the specific WhatsApp provider (Twilio, Meta, etc.)
    sender_number = payload.get("from")
    message = payload.get("message", {})
    msg_type = message.get("type")

    if not sender_number:
        return {"status": "error", "message": "No sender number found"}

    # --- WORKFLOW 1: Webhook Intercept (No AI) ---
    if msg_type == "location":
        lat = message["location"]["latitude"]
        lng = message["location"]["longitude"]
        
        # Save/Upsert directly to user's document
        users_col.update_one(
            {"phone": sender_number},
            {
                "$set": {
                    "location": geojson_point(lng, lat)
                },
                "$setOnInsert": {
                    "role": "retailer", # Default role for new users sharing location
                    "name": "New Retailer"
                }
            },
            upsert=True
        )
        logging.info(f"Location updated for {sender_number}")
        return {"status": "success", "message": "Location saved"}

    # --- WORKFLOW 2: Pass Text to AI Agent ---
    elif msg_type == "text":
        text_body = message.get("text", {}).get("body", "")
        
        # Run AI workflow in background to respond via WhatsApp API (out of scope for this file)
        # Here we just trigger the logic
        background_tasks.add_task(run_agent_workflow, sender_number, text_body)
        
        return {"status": "success", "message": "Agent triggered"}

    return {"status": "ignored", "message": "Message type not handled"}
