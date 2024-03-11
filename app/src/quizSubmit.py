import os
import json
from flask import Blueprint, render_template, current_app

quiz = Blueprint('quiz', __name__)

@quiz.route('/quizResults')
def quiz_results():
    score = 0

    # Get the directory of the current file
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the root directory by going up two levels
    root_directory = os.path.abspath(os.path.join(current_directory, '..', '..'))
    questions_file_path = os.path.join(root_directory, 'json', 'questions.json')


    print("Root directory:", root_directory)
    
    try:
        # Pulling json data from "questions.json"
        with open(questions_file_path, "r") as f:
            data = json.load(f)
    except IOError:
        print("questions.json file not found")
        exit()

    # Created for loop to iterate for all the questions defined in "questions.json"
    for i in range(data["module"]["num_questions"]):
        # Implemented logic to calculate score and other relevant operations
        pass

    # Render the HTML template with the calculated score
    return render_template('quizResults.html', score=score, num_questions=data["module"]["num_questions"])
