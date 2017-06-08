from flask import Flask, render_template, request, redirect, url_for
import data_manager
import os
import datetime


app = Flask(__name__)


# Listing
@app.route('/', methods=['POST', 'GET'])
def list_lates_five_question():
    ordered_questions = data_manager.get_questions(first_five_only=True)
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
        ordered_questions = data_manager.get_questions()
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
    tags = data_manager.get_tags_for_question(question_id)
    comments = data_manager.get_comments_for_question(question_id)
    users = []
    if request.method == "POST":
        answer_id = None
        time_now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        votes = "0"
        new_answer_message = request.form["new_answer"].replace("\r\n", "\n")
        image = None
        user_id = request.form['user']
        new_answer_data = [answer_id, time_now, votes, question_id, new_answer_message, image, user_id]
        data_manager.write_answer_to_db(new_answer_data)
        return redirect(url_for('display_q_and_a', question_id=question_id))
    if request.url.endswith("new_answer"):
        new_answer = True
        users = data_manager.get_existing_users()
    return render_template("display_question_answers.html", question=question, answers=answers_for_question,
                           new_answer=new_answer, answer_count=answer_count, tags=tags, comments=comments,
                           users=users)


@app.route('/question/<question_id>/viewcount')
def view_counter(question_id):
    data_manager.add_view_number(question_id)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question_and_answers(question_id)
    return redirect('/')


@app.route('/question/<question_id>/new-tag/')
def add_tag_form(question_id):
    existing_tags = data_manager.get_existing_tags()
    return render_template('new_tag.html', question_id=question_id, existing_tags=existing_tags)


@app.route('/question/<question_id>/existing-tag/<existing_tag_id>')
def add_existing_tag_to_question(question_id, existing_tag_id):
    data_manager.add_existing_tag_to_question(question_id, existing_tag_id)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/question/<question_id>/new-tag/add', methods=['POST'])
def add_new_tag_to_question(question_id):
    existing_tags = data_manager.get_existing_tags()
    existing_tag_names = [tag[1] for tag in existing_tags]
    new_tag_name = request.form['name']
    if new_tag_name in existing_tag_names:
        return render_template('new_tag.html', question_id=question_id, existing_tags=existing_tags,
                               new_tag_error_message="This tag already exists! Please, type here another one!")
    data_manager.add_new_tag_to_question(question_id, new_tag_name)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_tag(question_id, tag_id):
    data_manager.delete_tag(question_id, tag_id)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/question/<question_id>/new-comment')
def add_comment_form(question_id):
    users = data_manager.get_existing_users()
    return render_template('new_question.html', question_id=question_id, users=users)


@app.route('/question/<question_id>/new-comment/add', methods=['POST'])
def add_comment_to_question(question_id):
    submission_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = request.form['comment']
    user_id = request.form['user_id']
    data_manager.add_comment_to_db(question_id, message, submission_time, user_id)
    return redirect(url_for('display_q_and_a', question_id=question_id))


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_phrase = str(request.query_string)
    search_text = search_phrase[search_phrase.index('=') + 1:-1]
    questions = data_manager.search(search_text)
    answer_count_list = data_manager.answer_count

    return render_template("questionlist.html",
                           questions=questions, answer_count_list=answer_count_list, create_link=True,
                           search_text=search_text)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        user_name = request.form['username']
        time_now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        row = [user_name, time_now]
        try:
            data_manager.register_user(row)
            return redirect('/')
        except Exception as e:
            return render_template('new_question.html', registration=True, user_exists=True)
    return render_template('new_question.html', registration=True)


@app.route('/list_users', methods=['GET', 'POST'])
def list_users():
    if request.method == "POST":
        parameters = request.args.to_dict()
        key = list(parameters.keys())
        value = list(parameters.values())
        users = data_manager.get_existing_users(key[0], value[0])
    else:
        users = data_manager.get_existing_users()
    return render_template("list_users.html", users=users)


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_page(user_id):
    if request.method == "POST":
        parameters = request.args.to_dict()
        key = list(parameters.keys())
        value = list(parameters.values())
        user_name, questions, answers, comments = data_manager.user_data(user_id, key[0], value[0])
    else:
        user_name, questions, answers, comments = data_manager.user_data(user_id)
    answer_count_list = data_manager.answer_count

    return render_template("user_page.html", user_id=user_id, user_name=user_name, questions=questions,
                           answer_count_list=answer_count_list, answers=answers, comments=comments)


if __name__ == '__main__':
    app.debug = True
    app.run()
