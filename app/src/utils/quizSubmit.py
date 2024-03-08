import json
from flask import render_template
from flask import Blueprint, jsonify
from datetime import datetime

quiz_api = Blueprint("quiz_api", __name__)

try:
    # Pulling json data from "questions.json"
    with open("../json/questions.json", "r") as f:
         data = json.load(f)
         
except IOError:
    print("questions.json file not found")
    exit()

try:
    # Pulling json data from "responses.json"
    with open("../json/responses.json") as f:
        listObj = json.load(f)

except IOError:
    print("responses.json file not found")
    exit()

@quiz_api.route("/submit")
def SubmitQuiz():
    # Initializing new submission with timestamp
    timestamp = str(datetime.now())
    score = 0
    # individual question data stored as list
    listObj[timestamp] = {"data":[]}
    listObj[timestamp]["module"] = str(data["module"]["number"])

    # Created for loop to iterate for all the questions defined in "questions.json"
    for i in range(data["module"]["num_questions"]):
        # Initialized response variable with dummy data (Should hold user's selection)
        response = "0.018"
        # Pulling expected value from "questions.json" file
        correct_resp = str(data["module"]["questions"][i]["correct_answer"])

        try:
            # Appending user response to "responses.json"
            listObj[timestamp]["data"].append({
                "number": str(data["module"]["questions"][i]["number"]),
                "question": str(data["module"]["questions"][i]["question"]),
                "answers": str(data["module"]["questions"][i]["answers"]),
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
            listObj[timestamp]["score"] = "{}/{}".format(score, i + 1)
            with open("json/responses.json", 'w') as f:
                json.dump(listObj, f, indent = 4, separators=(',',': '))
        except IOError:
            print("responses.json file not found")
            exit()

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

