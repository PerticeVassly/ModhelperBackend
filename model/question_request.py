from pydantic import BaseModel
from pydantic import Field

class QuestionRequest(BaseModel):

    question: str = Field(
        default=None,
        title="question",
        description="question the user input",
    )