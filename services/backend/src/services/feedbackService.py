from ..models.feedbackModel import FeedbackData


# Define the function to save feedback data to the PostgreSQL database
async def save_feedback_to_database(feedback_data: FeedbackData):
    insert_statement = """
    INSERT INTO feedback (rating, feedback, email, date)
    VALUES (%s, %s, %s, %s);
    """

    data_tuple = (
        feedback_data.rating,
        feedback_data.feedback,
        feedback_data.email,
        feedback_data.date,
    )

    try:
        cur = connection.cursor()
        cur.execute(insert_statement, data_tuple)
        connection.commit()
    except Exception as e:
        logging.error(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        cur.close()
