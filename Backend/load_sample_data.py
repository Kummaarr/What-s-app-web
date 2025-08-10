import os, asyncio, json
import motor.motor_asyncio

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "whatsapp"
COL_NAME = "processed_messages"

SAMPLE_PAYLOADS = [
    {
        "messages": [
            {"id": "msg-1", "from": "919900000001", "text": {"body": "Hello from user 1"}, "timestamp": "2025-08-01T08:00:00Z", "status":"received"},
            {"id": "msg-2", "from": "919900000002", "text": {"body": "Hi, this is user 2"}, "timestamp": "2025-08-01T08:01:00Z", "status":"received"}
        ]
    },
    {
        "statuses": [
            {"id": "msg-1", "status": "delivered"},
            {"id": "msg-2", "status": "read"}
        ]
    }
]

async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    coll = client[DB_NAME][COL_NAME]
    for payload in SAMPLE_PAYLOADS:
        if "messages" in payload:
            for m in payload["messages"]:
                await coll.replace_one({"_id": m["id"]}, {
                    "_id": m["id"],
                    "wa_id": m["from"],
                    "text": m["text"]["body"],
                    "timestamp": m["timestamp"],
                    "status": m["status"],
                    "outgoing": False
                }, upsert=True)
        if "statuses" in payload:
            for s in payload["statuses"]:
                await coll.update_one({"_id": s["id"]}, {"$set": {"status": s["status"]}})
    print("Sample data loaded.")

if __name__ == "__main__":
    asyncio.run(main())
