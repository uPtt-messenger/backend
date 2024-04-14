import json

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

message_queue = {}
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
        message_queue[channel] = []
    message_queue[channel].append(message)

    return {"message": "Message pushed"}


@app.get("/pull/")
async def pull_message(channel: str):
    logger = log.logger

    if channel not in available_channels:
        logger.warning(f"Invalid channel: {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel not in message_queue:
        logger.warning(f"No message in {channel}")
        raise HTTPException(status_code=404, detail=f"No message found in {channel}")

    if not message_queue[channel]:
        logger.info(f"No message in {channel}")
        raise HTTPException(status_code=404, detail=f"No message found in {channel}")

    message = message_queue[channel].pop(0)
    logger.info(f"Pulling message from {channel}: {message}")

    logger.info(f"len(message_queue[channel]): {len(message_queue[channel])}")

    return {"content": message}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=config.config['mq_port'])
