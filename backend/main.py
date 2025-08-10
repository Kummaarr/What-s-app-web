import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
from pydantic import BaseModel
from datetime import datetime
import uuid
import socketio

# Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "whatsapp"
COL_NAME = "processed_messages"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
coll = db[COL_NAME]

# Socket.IO mount
socket_app = socketio.ASGIApp(sio, app)

class OutgoingMessage(BaseModel):
    wa_id: str
    name: str | None = None
    text: str

@app.post("/webhook")
async def webhook(payload: dict):
    if "messages" in payload:
        for m in payload["messages"]:
            msg = {
                "_id": m.get("id", str(uuid.uuid4())),
                "wa_id": m.get("from"),
                "name": m.get("profile", {}).get("name") if m.get("profile") else None,
                "text": m.get("text", {}).get("body"),
                "timestamp": m.get("timestamp", datetime.utcnow().isoformat()),
                "status": m.get("status", "received"),
                "outgoing": False
            }
            await coll.replace_one({"_id": msg["_id"]}, msg, upsert=True)
            await sio.emit("new_message", msg)
    if "statuses" in payload:
        for s in payload["statuses"]:
            ref = s.get("id")
            if ref:
                await coll.update_one({"_id": ref}, {"$set": {"status": s.get("status")}})
                await sio.emit("status_update", {"id": ref, "status": s.get("status")})
    return {"ok": True}

@app.post("/send")
async def send(msg: OutgoingMessage):
    doc_id = str(uuid.uuid4())
    doc = {
        "_id": doc_id,
        "wa_id": msg.wa_id,
        "name": msg.name,
        "text": msg.text,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "sent",
        "outgoing": True
    }
    await coll.insert_one(doc)
    await sio.emit("new_message", doc)
    return {"ok": True, "id": doc_id}

@app.get("/conversations")
async def conversations():
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$wa_id", "last": {"$first": "$$ROOT"}, "count": {"$sum": 1}}}
    ]
    data = []
    async for doc in coll.aggregate(pipeline):
        data.append(doc)
    return data

@app.get("/messages/{wa_id}")
async def messages(wa_id: str):
    msgs = []
    async for m in coll.find({"wa_id": wa_id}).sort("timestamp", 1):
        msgs.append(m)
    return msgs

# Serve static frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
