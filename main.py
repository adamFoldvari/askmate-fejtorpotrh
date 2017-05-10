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
    new_row.append(str(last_id+1))
    new_row.append(str(int(time.time())))
    for _ in range(2):
        new_row.append(str(0))
    new_row.append(request.form['question_title'])
    new_row.append(request.form['question'])
    new_row.append('')
    data_manager.write_questiontable_to_file('question.csv', new_row)
    return redirect('/question/<question_id>')


if __name__ == '__main__':
    app.debug = True
    app.run()