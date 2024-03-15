from fastapi import Request
from ..models.feedbackModel import FeedbackData


async def save_feedback_to_database(feedback_data: FeedbackData, request: Request):
    insert_statement = (
        "INSERT INTO feedback (rating, feedback, email, date) "
        "VALUES (%s, %s, %s, %s)"
    )

    # Replace None with empty string in the data tuple
    data_tuple = (
        feedback_data.rating if feedback_data.rating is not None else "",
        feedback_data.feedback if feedback_data.feedback is not None else "",
        feedback_data.email if feedback_data.email is not None else "",
        feedback_data.date if feedback_data.date is not None else "",
    )

    await request.app.state.db.execute(insert_statement, *data_tuple)
    return
