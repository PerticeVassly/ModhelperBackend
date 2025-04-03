from pydantic import BaseModel

class AskRequest(BaseModel):
    ask: str