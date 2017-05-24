from base64 import b64decode, b64encode
from datetime import datetime
from flask import Markup
import psycopg2

from database_connection_data import db_con_data

SORTING_REVERSE = [0, 0, 0]


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
    finally:
        if conn:
            conn.close()

    return rows


def table_sort(unordered_q, field_num):
    '''Sort the table by the given field number.'''
    field_number = int(field_num)

    if SORTING_REVERSE[field_number - 1] == 0:
        rev = False
        SORTING_REVERSE[field_number - 1] = 1
    elif SORTING_REVERSE[field_number - 1] == 1:
        rev = True
        SORTING_REVERSE[field_number - 1] = 0

    if field_number == 2 or field_number == 3:
        ordered_q = sorted(unordered_q, key=lambda q: int(q[field_number]), reverse=rev)
    elif field_number == 1:
        ordered_q = sorted(unordered_q, key=lambda q: q[field_number], reverse=rev)
    return ordered_q


def get_questions(first_five_only=False):
    '''Read the QUESTIONS into a @table.
        first_five_only gets only tha latest 5 questions
    @table: list of lists of strings
    '''
    if first_five_only:
        questions = query_result("""SELECT * FROM question ORDER BY submission_time DESC LIMIT 5;""")
    else:
        questions = query_result("""SELECT * FROM question;""")
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
    query_result("""INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                    VALUES(%s, %s, %s, %s, %s);""", (row[1], row[2], row[3], row[4], row[5]))


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
