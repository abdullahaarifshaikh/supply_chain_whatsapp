from fastapi import FastAPI
from api.webhooks import router as whatsapp_router
from database.client import ensure_indexes
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="B2B Supply Chain AI Agent")

# Mount the WhatsApp Webhook router
app.include_router(whatsapp_router, prefix="/api", tags=["WhatsApp"])

@app.on_event("startup")
async def startup_event():
    """Perform startup tasks like ensuring DB indexes."""
    print("🚀 Initializing B2B Supply Chain System...")
    ensure_indexes()
    print("✅ MongoDB Indexes Verified.")

@app.get("/")
async def root():
    return {"status": "online", "message": "B2B Supply Chain AI Agent is running."}

if __name__ == "__main__":
    # In production, use uvicorn main:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
