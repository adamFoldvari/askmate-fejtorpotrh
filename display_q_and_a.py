from flask import Flask
from flask import render_template, request, redirect, url_for
import time
import data_manager

app = Flask(__name__)


@app.route('/question/<question_id>')
@app.route('/question/<question_id>/new_answer', methods=["GET", "POST"])
def display_q_and_a(question_id, new_answer=None):
    if request.method == "POST":
        new_answer = request.form("new_answer")
        time_now = int(time.time())
        print(time_now)
        answer_data = [answert_id, time, votes, question_id, new_answer, image]
        return redirect(url_for('display_q_and_a', question_id=question_id))
    questions = data_manager.get_questiontable_from_file('question.csv')
    answers = data_manager.get_answertable_from_file('answer.csv')
    question = [question for question in questions if question[0] == question_id][0]
    answers_for_question = [answer for answer in answers if answer[3] == question_id]
    return render_template("display_question_answers.html", question=question, answers=answers_for_question,
                           new_answer=new_answer)


if __name__ == '__main__':
    app.debug = True
    app.run()
