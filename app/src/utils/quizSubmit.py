import json, re
from flask import render_template
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime
from app.src.main import returnLoggedInData

quiz_api = Blueprint("quiz_api", __name__)

try:
    # Pulling json data from "questions.json"
    with open("../json/questions.json", "r") as f:
         data = json.load(f)
         
except IOError:
    print("questions.json file not found")
    with open("../json/questions.json", "x") as f:
        json.dump({}, f)
    exit()

try:
    # Pulling json data from "responses.json"
    with open("../json/responses.json") as f:
        listObj = json.load(f)

except IOError:
    print("responses.json file not found")
    with open("../json/responses.json", "x") as f:
        json.dump({}, f)
    # exit()

@quiz_api.route("/submit")
@login_required
def SubmitQuiz():
    queryStr = request.query_string.decode()
    print(queryStr)
    
    # Currently hardcoded to choose quiz #2 (Prime Factorization) every single time for the demo; 
    # we would change this to be dynamic in the future (send through query string of what quiz number)
    moduleNum = 1
    topicNum = 2
    userAnswers = {
        (int(re.findall("\d+", answer)[0]) - 1) : (int(re.findall("\d+", answer)[2])) for answer in queryStr.split("&")
    }
    chosenQuiz = [
        quiz for quiz in data["module"] if quiz["number"] == moduleNum and quiz["topic"] == topicNum
    ][0]
    totalNumQs = chosenQuiz["num_questions"]

    # Initializing new submission with timestamp
    timestamp = str(datetime.now())
    score = 0
    # individual question data stored as list
    listObj[timestamp] = {"data":[]}
    listObj[timestamp]["module"] = str(chosenQuiz["number"])
    listObj[timestamp]["topic"] = str(chosenQuiz["topic"])
    listObj[timestamp]["user_id"] = current_user.id

    # Created for loop to iterate for all the questions defined in "questions.json"
    for i in range(totalNumQs):
        # Initialized response variable with user's response
        response = chosenQuiz["questions"][i]["answers"][userAnswers[i]]
        # Pulling expected value from "questions.json" file
        correct_resp = str(chosenQuiz["questions"][i]["correct_answer"])

        try:
            # Appending user response to "responses.json"
            listObj[timestamp]["data"].append({
                "number": str(chosenQuiz["questions"][i]["number"]),
                "question": str(chosenQuiz["questions"][i]["question"]),
                "answers": str(chosenQuiz["questions"][i]["answers"]),
                "user_answer": response,
                "correct" : response == correct_resp
            })
            if (response == correct_resp):
            # Implement logic for the case where user enters the correct response
                score += 1
            else:
            # Implement logic for the case where user enters the wrong response
                pass
            listObj[timestamp]["points"] = score 
            listObj[timestamp]["score"] = "{}/{}".format(score, totalNumQs)
            with open("../json/responses.json", 'w') as f:
                json.dump(listObj, f, indent = 4, separators=(',',': '))
        except IOError:
            print("responses.json file not found")
            exit()

    loggedInUser: dict = returnLoggedInData()
    return render_template("quizResults.html", score=score, num_questions=totalNumQs, **loggedInUser)

@quiz_api.route("/submissions", methods=["GET"])
def GetSubmissions():
    return jsonify(listObj)

# with open("/app/src/templates/results.html", "w+") as f:
#     f.write(
#     """<html>
#     <head></head>
#     <body><p>""" + score +
#     """</p></body>
#     </html>""")

# render_template("results.html")

