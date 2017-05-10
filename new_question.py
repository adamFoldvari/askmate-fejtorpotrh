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
    print(table)
    return redirect('/question/<question_id>')

if __name__ == '__main__':
    app.debug = True
    app.run()
