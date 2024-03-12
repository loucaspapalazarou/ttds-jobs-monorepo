from pydantic import BaseModel


class FeedbackData(BaseModel):
    rating: int
    feedback: str
    email: str
    date: str
