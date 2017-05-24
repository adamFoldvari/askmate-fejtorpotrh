from flask import Flask, render_template, request, redirect, url_for
import data_manager
import os
import datetime

 
app = Flask(__name__)


# Listing
@app.route('/', methods=['POST', 'GET'])
def list_lates_five_question():
    ordered_questions = data_manager.get_questions('submisson_time', 'DESC', first_five_only=True)
    answer_count_list = data_manager.answer_count
    return render_template("questionlist.html",
                           questions=ordered_questions, answer_count_list=answer_count_list, create_link=True)


@app.route('/list', methods=['POST', 'GET'])
def listing():
    if request.method == "POST":
        parameters = request.args.to_dict()
        key = list(parameters.keys())
        value = list(parameters.values())
        ordered_questions = data_manager.get_questions(key[0], value[0])
    else:
        ordered_questions = data_manager.get_questions('submission_time', 'DESC')
    answer_count_list = data_manager.answer_count
    return render_template("questionlist.html",
                           questions=ordered_questions, answer_count_list=answer_count_list)


@app.route('/new_question')
def question_sheet():
    return render_template('new_question.html')


@app.route('/new_question/add', methods=['POST'])
def add_question():
    table = data_manager.get_questions()
    new_row = []
    new_row.append(None)
    time_now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    new_row.append(time_now)
    for _ in range(2):
        new_row.append(str(0))
    new_row.append(request.form['question_title'])
    new_row.append(request.form['question'].replace("\r\n", "\n"))
    new_row.append(None)
    data_manager.write_question_to_db(new_row)
    [[question_id]] = data_manager.query_result(
        """SELECT id FROM question WHERE submission_time = %s""", (time_now,))
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/question/<question_id>/new_answer', methods=["GET", "POST"])
@app.route('/question/<question_id>', methods=["GET", "POST"])
def display_q_and_a(question_id, new_answer=False):
    questions = data_manager.get_questions()
    [question] = [question for question in questions if question[0] == int(question_id)]
    answers_for_question = data_manager.answers_for_question(int(question_id))
    answer_count = data_manager.answer_count(question_id)
    comments = data_manager.get_comments_for_question(question_id)
    if request.method == "POST":
        answer_id = None
        time_now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        votes = "0"
        new_answer_message = request.form["new_answer"].replace("\r\n", "\n")
        image = None
        new_answer_data = [answer_id, time_now, votes, question_id, new_answer_message, image]
        data_manager.write_answer_to_db(new_answer_data)
        return redirect(url_for('display_q_and_a', question_id=question_id))
    if request.url.endswith("new_answer"):
        new_answer = True
    return render_template("display_question_answers.html", question=question, answers=answers_for_question,
                           new_answer=new_answer, answer_count=answer_count, comments=comments)


@app.route('/question/<question_id>/viewcount')
def view_counter(question_id):
    data_manager.add_view_number(question_id)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question_and_answers(question_id)
    return redirect('/')


@app.route('/question/<question_id>/new-comment')
def add_comment_form(question_id):
    return render_template('new_question.html', question_id=question_id)


@app.route('/question/<question_id>/new-comment/add', methods=['POST'])
def add_comment_to_question(question_id):
    submission_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = request.form['comment']
    data_manager.add_comment_to_db(question_id, message, submission_time)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_phrase = str(request.query_string)
    search_text = search_phrase[search_phrase.index('=') + 1:-1]
    print('search text:', search_text)
    questions = data_manager.search(search_text)
    if request.method == "POST":
        ordered_questions = data_manager.get_questions(questions, request.form['field_name'])
    else:
        ordered_questions = sorted(questions, key=lambda q: q[1], reverse=True)
    answer_count_list = data_manager.answer_count

    return render_template("questionlist.html",
                           questions=ordered_questions, answer_count_list=answer_count_list, create_link=True)


if __name__ == '__main__':
    app.debug = True
    app.run()
