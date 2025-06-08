from fastapi import FastAPI
import uvicorn

from .handlers.send_message import router


app = FastAPI()
app.include_router(router)


async def run_http():
    config = uvicorn.Config(app, port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
