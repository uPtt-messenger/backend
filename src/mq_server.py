import json
import asyncio
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException

try:
    from src import log
    from src import config
except ImportError:
    import log
    import config

app = FastAPI()

log.init()

message_queue: Dict[str, asyncio.Queue] = {}
available_channels = [
    'to_backend',
    'to_ui',
    'to_system_tray',
    'to_notification',
]


@app.post("/push/")
async def push_message(channel: str, message: str):
    logger = log.logger

    if channel not in available_channels:
        logger.warning(f"Invalid channel: {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")

    try:
        message = json.loads(message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid message format")

    logger.info(f"Pushing message to {channel}: {message}")

    if channel not in message_queue:
        message_queue[channel] = asyncio.Queue()

    await message_queue[channel].put(message)

    return {"result": "Message pushed"}


@app.get("/pull/")
async def pull_message(channel: str):
    logger = log.logger

    if channel not in available_channels:
        logger.warning(f"Invalid channel: {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel not in message_queue:
        message_queue[channel] = asyncio.Queue()

    try:
        message = await asyncio.wait_for(message_queue[channel].get(), timeout=config.config['long_polling_timeout'])
        return {"messages": [message]}
    except asyncio.TimeoutError:
        return {"messages": []}


def init():
    logger = log.logger

    for channel in available_channels:
        message_queue[channel] = asyncio.Queue()

    logger.info('MQ server initialized')


if __name__ == "__main__":
    init()
    uvicorn.run(app, host="127.0.0.1", port=config.config['mq_port'])