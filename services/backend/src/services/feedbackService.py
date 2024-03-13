from fastapi import Request

from ..models.feedbackModel import FeedbackData


async def save_feedback_to_database(feedback_data: FeedbackData, request: Request):
    insert_statement = (f"INSERT INTO feedback (rating, feedback, email, date) "
                        f"VALUES ({feedback_data.rating}, {feedback_data.feedback}, "
                        f"{feedback_data.email}, {feedback_data.date});")

    await request.app.state.db.fetch_rows(insert_statement)
    return
