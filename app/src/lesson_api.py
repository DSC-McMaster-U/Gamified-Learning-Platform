from flask import Blueprint, jsonify, abort
from .models import Lesson, db

# Create a Blueprint for the API
api = Blueprint("api", __name__)

# Define an API endpoint for retrieving lesson information
@api.route("/api/lesson/<int:lesson_id>", methods=["GET"])
def get_lesson(lesson_id):
    # Attempt to retrieve the lesson with the given ID
    lesson = Lesson.query.get(lesson_id)

    # Check if the lesson was found
    if lesson:
        # If the lesson exists, create a dictionary with relevant information
        lesson_data = {
            "id": lesson.id,
            "level": lesson.level,
            "active": lesson.active,
            "summary": lesson.summary,
            "learning_objective": lesson.learning_objective,
            "content": lesson.lesson_content
        }
        # Return the lesson data as a JSON response
        return jsonify(lesson_data)
    else:
        # If the lesson was not found, return a 404 error with a description
        abort(404, description="Not found")

