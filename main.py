from flask import Flask, render_template, request, redirect, url_for
import data_manager
import os
import time


current_file_path = os.path.dirname(os.path.abspath(__file__))
file_name = current_file_path + '/question.csv'
app = Flask(__name__)


# Listing
@app.route('/', methods=['POST', 'GET'])
@app.route('/list', methods=['POST', 'GET'])
def listing():
    questions = data_manager.get_questiontable_from_file(file_name)
    return render_template("questionlist.html", questions=questions)


@app.route('/new_question')
def question_sheet():
    return render_template('new_question.html')


@app.route('/new_question/add', methods=['POST'])
def add_question():
    table = data_manager.get_questiontable_from_file('question.csv')
    new_row = []
    last_id = int(table[-1][0])
    new_row.append(str(last_id + 1))
    new_row.append(str(int(time.time())))
    for _ in range(2):
        new_row.append(str(0))
    new_row.append(request.form['question_title'])
    new_row.append(request.form['question'])
    new_row.append('')
    data_manager.write_questiontable_to_file('question.csv', new_row)
    return redirect(url_for('display_q_and_a', question_id=new_row[0]))


@app.route('/question/<question_id>/new_answer', methods=["GET", "POST"])
@app.route('/question/<question_id>', methods=["GET", "POST"])
def display_q_and_a(question_id, new_answer=False):
    questions = data_manager.get_questiontable_from_file('question.csv')
    answers = data_manager.get_answertable_from_file('answer.csv')
    question = [question for question in questions if question[0] == question_id][0]
    answers_for_question = [answer for answer in answers if answer[3] == question_id]
    if request.method == "POST":
        answer_id = str(int(answers[-1][0]) + 1)
        time_now = str(int(time.time()))
        votes = "0"
        new_answer_message = request.form["new_answer"]
        image = ""
        new_answer_data = [answer_id, time_now, votes, question_id, new_answer_message, image]
        print(new_answer_data)
        data_manager.write_answer_to_file('answer.csv', new_answer_data)
        return redirect(url_for('display_q_and_a', question_id=question_id))
    if request.url.endswith("new_answer"):
        new_answer = True
    return render_template("display_question_answers.html", question=question, answers=answers_for_question,
                           new_answer=new_answer)

if __name__ == '__main__':
    app.debug = True
    app.run()