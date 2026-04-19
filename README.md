# B2B Supply Chain WhatsApp AI Agent

A WhatsApp-integrated AI assistant that connects **retailers** with nearby **wholesalers** in real time. Retailers can message the agent to find the best-priced inventory within 100 km, and the agent responds with ranked supplier options — directly in WhatsApp.

Built with **FastAPI**, **LangGraph**, **Google Gemini**, and **MongoDB Atlas**.

---

## How It Works

1. A retailer sends a WhatsApp message like *"I want eggs"*.
2. The webhook receives the message and routes it to the LangGraph AI agent.
3. The agent (powered by Gemini 2.5 Flash) extracts the item name and calls the `distance_and_price_calculator` tool.
4. The tool runs a MongoDB `$geoNear` aggregation to find in-stock wholesalers within 100 km, sorted by price then distance.
5. The top 3 results are formatted with WhatsApp markdown and returned to the retailer.

Location sharing is also handled: when a retailer sends their WhatsApp location pin, it is saved to their profile and used for all subsequent queries — no manual coordinate entry needed.

---

## Project Structure

```
supply_chain_whatsapp/
├── main.py                   # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
│
├── api/
│   └── webhooks.py           # WhatsApp webhook: routes locations and text messages
│
├── core/
│   ├── agent.py              # LangGraph agent graph (model → tool → model loop)
│   ├── state.py              # Session retailer identity helper
│   └── prompts.py            # (reserved for prompt templates)
│
├── tools/
│   ├── inventory_tools.py    # distance_and_price_calculator (primary LangGraph tool)
│   ├── find_nearest_item.py  # Haversine-based nearest item finder (utility)
│   ├── place_regular_order.py# Creates a pending order document in MongoDB
│   └── update_inventory.py   # Upserts a wholesaler's inventory record
│
├── database/
│   ├── client.py             # MongoDB connection, indexes, helpers
│   └── seed_data.py          # Sample retailer / wholesaler / inventory data
│
└── scripts/
    ├── seed_db.py            # Populates the unified `users` collection
    ├── chat_agent.py         # Local chat REPL simulating a retailer session
    └── test_cli.py           # Interactive CLI for testing all tools manually
```

---

## Prerequisites

- Python 3.12+
- MongoDB Atlas cluster (with a `2dsphere` index on the `users.location` field — created automatically on startup)
- A Google AI API key (Gemini 2.5 Flash)
- A WhatsApp Business API provider (Twilio or Meta Graph API) to send replies back to users — the webhook receives messages but outbound sending is out of scope and must be wired up separately

---

## Setup

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd supply_chain_whatsapp
pip install -r requirements.txt
```

**2. Configure environment variables**

Copy `.env` and fill in your own values:

```ini
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
RETAILER_DB_NAME=retailer
WHOLESALER_DB_NAME=wholesalers
GOOGLE_API_KEY=your_google_api_key_here
```

**3. Seed the database**

```bash
python scripts/seed_db.py
```

This populates sample retailers and wholesalers in the Hyderabad area for testing.

**4. Run the server**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at `http://localhost:8000`. MongoDB indexes are created automatically on startup.

---

## Docker

```bash
docker-compose up --build
```

---

## Webhook Endpoint

```
POST /api/whatsapp
```

Expected JSON payload (adapt to your WhatsApp provider's format):

```json
{
  "from": "+919900000001",
  "message": {
    "type": "text",
    "text": { "body": "I want eggs" }
  }
}
```

For location messages:

```json
{
  "from": "+919900000001",
  "message": {
    "type": "location",
    "location": { "latitude": 17.385, "longitude": 78.4867 }
  }
}
```

The webhook handles two flows:
- **Location** → saved to the user's MongoDB document immediately (no AI involved).
- **Text** → passed to the LangGraph agent in a background task.

---

## Local Testing

**Chat REPL** — simulates a retailer conversation with the full AI agent:

```bash
python scripts/chat_agent.py
```

**Tool CLI** — interactively test each tool (find item, place order, update inventory):

```bash
python scripts/test_cli.py
```

---

## Data Model

All users (retailers and wholesalers) live in a single `users` collection:

```json
{
  "phone": "+918800000001",
  "name": "Egg King Traders",
  "role": "wholesaler",
  "location": {
    "type": "Point",
    "coordinates": [78.495, 17.4]
  },
  "inventory": [
    { "item_name": "eggs", "price": 140, "unit": "tray", "in_stock": true }
  ]
}
```

Orders are stored in a separate `orders` collection and linked by `retailer_number`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| AI agent | LangGraph (ReAct loop) |
| LLM | Google Gemini 2.5 Flash |
| Database | MongoDB Atlas (motor + pymongo) |
| Geo queries | MongoDB `$geoNear` / `2dsphere` |
| Containerisation | Docker + docker-compose |
