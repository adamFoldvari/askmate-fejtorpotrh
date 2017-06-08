from base64 import b64decode, b64encode
from datetime import datetime
from flask import Markup
import psycopg2

from database_connection_data import db_con_data


def connect_database():
    try:
        # setup connection string
        connect_str = "dbname={} user={} host='localhost'".format(
            db_con_data()['dbname'], db_con_data()['user'])
        # use our connection values to establish a connection
        conn = psycopg2.connect(connect_str)
        # set autocommit option, to do every query when we call it
        conn.autocommit = True
        # create a psycopg2 cursor that can execute queries
        cursor = conn.cursor()
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)

    return cursor, conn


def query_result(*query):
    """Execute SQL query and return the result if it exists.

    Close the connection after execution.
    """
    try:
        cursor, conn = connect_database()
        cursor.execute(*query)
        rows = cursor.fetchall()
        rows = [list(row) for row in rows]
    except psycopg2.OperationalError as e:
        print(e)
    except psycopg2.ProgrammingError as e:
        print(e)
        print("Nothing to print")
        rows = ""
    except psycopg2.IntegrityError as e:
        print(e)
        rows = ""
    finally:
        if conn:
            conn.close()

    return rows


def get_questions(field_name='submission_time', sorting_direction='DESC', first_five_only=False):
    '''Read the QUESTIONS into a @table.
        first_five_only gets only tha latest 5 questions
    @table: list of lists of strings
    '''
    if first_five_only:
        questions = query_result("""SELECT * FROM question ORDER BY submission_time DESC LIMIT 5;""")
    else:
        questions = query_result("SELECT * FROM question ORDER BY " +
                                 field_name + " " + sorting_direction)
    MESSAGE = 5
    for question in questions:
        question[MESSAGE] = Markup(question[MESSAGE].replace("\n", "<br>"))

    return questions


def write_question_to_db(row):
    '''Write the QUESTION @row into a file.

    @row: list of strings
    '''
    query_result("""INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                    VALUES(%s, %s, %s, %s, %s, %s);""", (row[1], row[2], row[3], row[4], row[5], row[6]))


def answers_for_question(question_id):
    answers = query_result("""SELECT * FROM answer WHERE question_id = %s;""", (question_id,))
    MESSAGE = 4
    for answer in answers:
        answer[MESSAGE] = Markup(answer[MESSAGE].replace("\n", "<br>"))

    return answers


def write_answer_to_db(row):
    '''Write the ANSWER @row into the database.'''
    query_result("""INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                    VALUES(%s, %s, %s, %s, %s, %s);""", (row[1], row[2], row[3], row[4], row[5], row[6]))


def add_view_number(question_id):
    '''Increase the view number of the question with the given question_id by 1.'''
    query_result("""UPDATE question SET view_number = view_number + 1 WHERE id = %s;""", (question_id,))


def answer_count(question_id):
    '''Give back the number of the answers to the question with the given id.'''
    [[count]] = query_result("""SELECT COUNT(*) FROM answer WHERE question_id = %s;""", (question_id,))

    return count


def delete_question_and_answers(question_id):
    '''Delete the question with the given id and all existing answers.'''
    query_result("""DELETE FROM question WHERE id = %s;""", (question_id,))


def add_comment_to_db(question_id, message, submission_time, user_id):
    query_result("""INSERT INTO comment (question_id, message, submission_time, user_id)
                    VALUES (%s, %s, %s, %s);""", (question_id, message, submission_time, user_id))


def get_tags_for_question(question_id):
    tags = query_result("SELECT * FROM tag WHERE id IN (SELECT tag_id FROM question_tag WHERE question_id = %s);",
                        (question_id,))
    return tags


def get_existing_tags():
    existing_tags = query_result("""SELECT * FROM tag;""")
    return existing_tags


def add_existing_tag_to_question(question_id, existing_tag_id):
    query_result("""INSERT INTO question_tag (question_id, tag_id)
                    VALUES (%s, %s);""", (int(question_id), int(existing_tag_id)))


def add_new_tag_to_question(question_id, new_tag_name):
    query_result("""INSERT INTO tag (name) VALUES (%s);""", (new_tag_name, ))
    tag_id = query_result("SELECT id FROM tag WHERE name = " + "'" + new_tag_name + "'")
    query_result("""INSERT INTO question_tag (question_id, tag_id)
                    VALUES (%s, %s);""", (int(question_id), tag_id[0][0]))


def delete_tag(question_id, tag_id):
    query_result("DELETE FROM question_tag WHERE question_id=" + question_id + " AND tag_id=" + tag_id + ";")


def get_comments_for_question(question_id):
    comments = query_result("""SELECT * FROM comment WHERE question_id = %s;""", (question_id,))
    return comments


def search(search_text):
    search_text = '%{}%'.format(search_text.lower())
    answer_q_ids = query_result("""SELECT question_id FROM answer WHERE LOWER(message) LIKE %s;""", (search_text,))
    questions = query_result("""SELECT * FROM question WHERE LOWER(title) LIKE %s;""", (search_text,))
    if answer_q_ids:
        for answer_q_id in answer_q_ids:
            if answer_q_id:
                [answer_q_id] = answer_q_id
                [question_to_answer] = query_result("""SELECT * FROM question WHERE id = %s;""", (answer_q_id,))
                questions.append(question_to_answer)
    # Convert list to set to delete duplicates
    questions = set(map(tuple, questions))
    questions = list(map(list, questions))

    MESSAGE = 5
    for question in questions:
        question[MESSAGE] = Markup(question[MESSAGE].replace("\n", "<br>"))

    return questions


def register_user(row):
    query_result("""INSERT INTO users (name, register_date)
                    VALUES (%s, %s);""", (row[0], row[1]))


def get_existing_users(field_name='name', sorting_direction='ASC'):
    users = query_result("SELECT * FROM users ORDER BY " + field_name + " " + sorting_direction + ";")
    return users


def get_tags(field_name='name', sorting_direction='ASC'):
    if field_name == 'count':
        tags = query_result("""SELECT t.id, t.name, COUNT(qt.tag_id) AS count FROM tag AS t
                        LEFT JOIN question_tag AS qt ON t.id=qt.tag_id
                        GROUP BY t.id, t.name
                        ORDER BY """ + field_name + " " + sorting_direction + ", t.name ASC;")
    else:
        tags = query_result("""SELECT t.id, t.name, COUNT(qt.tag_id) AS count FROM tag AS t
                            LEFT JOIN question_tag AS qt ON t.id=qt.tag_id
                            GROUP BY t.id, t.name
                            ORDER BY """ + field_name + " " + sorting_direction + ";")
    return tags
