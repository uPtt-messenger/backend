import json
import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from src import log
except ImportError:
    import log

app = FastAPI()

log.init()

message_queue = {}


@app.post("/push/")
async def push_message(channel: str, message: str):
    logger = log.logger

    logger.info(f"Pushing message to {channel}: {message}")

    try:
        message = json.loads(message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid message format")

    logger.info(f"Pushing message to {channel}: {message}")

    if channel not in message_queue:
        message_queue[channel] = []
    message_queue[channel].append(message)

    return {"message": "Message pushed"}


@app.get("/pull/")
async def pull_message(channel: str):
    logger = log.logger

    if channel not in message_queue:
        logger.warning(f"No message in {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")

    if not message_queue[channel]:
        logger.info(f"No message in {channel}")
        return {"message": "No message"}

    message = message_queue[channel].pop(0)
    logger.info(f"Pulling message from {channel}: {message}")

    return {"content": message}