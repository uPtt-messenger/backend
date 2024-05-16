import asyncio
import json
import os
import signal
import time
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request

try:
    from src import log
    from src import config
except ImportError:
    import log
    import config

app = FastAPI()

log.init()

message_queue: Dict[str, asyncio.Queue] = {}
push_event: Dict[str, asyncio.Event] = {}
available_channels = [
    'to_ptt_backend',
    'to_login_window',
    'to_chat_window',
    'to_system_tray',
    'to_notification',
    'to_mq_server',
]


@app.post("/push/")
async def push_message(request: Request):
    logger = log.logger

    json_request = await request.json()

    try:
        channel = json_request.get("channel")
        message = json_request.get("message")
    except KeyError:
        logger.warning(f"Invalid request: {request}")
        raise HTTPException(status_code=400, detail="Invalid request")

    if channel not in available_channels:
        logger.warning(f"Invalid channel: {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")

    try:
        dict_message = json.loads(message)
    except json.JSONDecodeError:
        logger.warning(f"Invalid message format: {message}")
        raise HTTPException(status_code=400, detail="Invalid message format")

    logger.info(f"Pushing message to {channel}: {dict_message}")

    if channel not in message_queue:
        message_queue[channel] = asyncio.Queue()
        push_event[channel] = asyncio.Event()

    if channel == 'to_mq_server':
        match dict_message['category']:
            case 'clear':
                for channel in available_channels:
                    if channel in message_queue:
                        message_queue[channel] = asyncio.Queue()
                    if channel in push_event:
                        push_event[channel] = asyncio.Event()
                return {"result": "Message queue cleared"}
            case 'close':
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(5)
            case _:
                logger.warning(f"Invalid category: {dict_message['category']}")

    await message_queue[channel].put(dict_message)
    push_event[channel].set()

    return {"result": "Message pushed"}


@app.get("/pull/")
async def pull_message(request: Request):
    logger = log.logger

    json_request = await request.json()

    try:
        channel = json_request.get("channel")
    except KeyError:
        logger.warning(f"Invalid request: {request}")
        raise HTTPException(status_code=400, detail="Invalid request")

    if channel not in available_channels:
        logger.warning(f"Invalid channel: {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel not in message_queue:
        message_queue[channel] = asyncio.Queue()
        push_event[channel] = asyncio.Event()

    try:
        messages = []
        while True:
            if message_queue[channel].empty():
                await asyncio.wait_for(push_event[channel].wait(), timeout=config.config['long_polling_timeout'])
                push_event[channel].clear()
            while not message_queue[channel].empty():
                message = message_queue[channel].get_nowait()
                messages.append(message)
            if messages:
                break
        return {"messages": messages}
    except asyncio.TimeoutError:
        return {"messages": []}


def init():
    logger = log.logger

    for channel in available_channels:
        message_queue[channel] = asyncio.Queue()
        push_event[channel] = asyncio.Event()

    logger.info('MQ server initialized')


if __name__ == "__main__":
    init()
    uvicorn.run("uptt_mq_server:app", host="127.0.0.1", port=config.config['mq_port'])
