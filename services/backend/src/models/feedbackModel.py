from pydantic import BaseModel


class FeedbackData(BaseModel):
    rating: int
    feedback: str
    date: str
