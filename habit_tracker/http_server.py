from fastapi import FastAPI, Header
from pydantic import BaseModel
import uvicorn

from bot import bot


app = FastAPI()


class NotifyRequest(BaseModel):
    user_id: int
    message: str


@app.post("/notify/")
async def notify_user(req: NotifyRequest, x_secret: str = Header(None)):
    await bot.send_message(req.user_id, req.message)


async def run_http():
    config = uvicorn.Config(app, port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
