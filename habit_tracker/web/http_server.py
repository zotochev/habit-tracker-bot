from fastapi import FastAPI
import uvicorn

from config import API_ENDPOINT_PORT

from .handlers.send_message import router


app = FastAPI()
app.include_router(router)


async def run_http():
    config = uvicorn.Config(app, port=API_ENDPOINT_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
