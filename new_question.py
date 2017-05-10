from flask import Flask, render_template, request, redirect, url_for
import time
import data_manager

app = Flask(__name__)


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
