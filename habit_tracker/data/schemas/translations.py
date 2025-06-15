from pydantic import BaseModel


class Translations(BaseModel):
    start: str = '<START>'
