from fastapi import Request

from ..models.feedbackModel import FeedbackData


async def save_feedback_to_database(feedback_data: FeedbackData, request: Request):
    insert_statement = "INSERT INTO feedback (rating, feedback) " "VALUES ($1, $2)"

    data_tuple = (
        feedback_data.rating,
        feedback_data.feedback,
    )

    await request.app.state.db.insert_feedback(insert_statement, data_tuple)
    return
