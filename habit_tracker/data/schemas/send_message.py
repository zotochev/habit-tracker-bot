from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    user_id: int
    message: str
