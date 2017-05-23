from base64 import b64decode, b64encode
from datetime import datetime
from flask import Markup
import psycopg2


SORTING_REVERSE = [0, 0, 0]


def connect_database():
    try:
        # setup connection string
        connect_str = "dbname='gergo' user='gergo' host='localhost'"
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
    try:
        cursor, conn = connect_database()
        cursor.execute(*query)
        rows = cursor.fetchall()
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


def read_raw_data(file_name):
    '''Read the lines from the csv file without decoding'''
    with open(file_name) as file:
        data_list = file.readlines()
        data_list = [element.replace("\n", "").split(",") for element in data_list]

    return data_list


def write_raw_data(file_name, table):
    '''Write the lines from the csv file without decoding'''
    with open(file_name, 'w') as file:
        for element in table:
            file.write(element + '\n')


def get_questiontable_from_file():
    '''Read the QUESTIONS' file into a @table.

    @file_name: string
    @table: list of lists of strings
    '''
    table = query_result("""SELECT * FROM question;""")

    for i in range(len(table)):
        table[i] = list(table[i])
        table[i][5] = Markup(table[i][5].replace("\n", "<br>"))

    return table


def write_questiontable_to_file(row):
    '''Write the QUESTION @row into a file.

    @file_name: string
    @row: list of strings
    '''

    query_result("""INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                    VALUES(%s, %s, %s, %s, %s, %s);""", (row[1], row[2], row[3], row[4], row[5], row[6]))


def get_answertable_from_file():
    '''Read the ANSWERS file into a @table.

    @file_name: string
    @table: list of lists of strings
    '''
    table = read_raw_data('answer.csv')
    for record in table:
        record[4] = Markup(record[4].replace("\n", "<br>"))

    return table


def write_answer_to_file(row):
    '''Write the ANSWER @row into a file.'''
    with open('answer.csv', "a") as file:
        row[4] = b64encode(str.encode(row[4].strip())).decode('utf-8')
        row[5] = b64encode(str.encode(row[5])).decode('utf-8')
        new_row = ','.join(row)
        file.write(new_row + "\n")


def add_view_number(question_id):
    '''Increase the view number of the question with the given question_id by 1.'''
    file_name = 'question.csv'
    questions = read_raw_data(file_name)
    new_questions = []

    for question in questions:
        if question[0] == str(question_id):
            question[2] = str(int(question[2]) + 1)
        question = ','.join(question)
        new_questions.append(question)

    write_raw_data(file_name, new_questions)


def answer_count(question_id):
    '''Give back the number of the answers to the question with the given id.'''
    answers = get_answertable_from_file()
    answers_to_question = [answer for answer in answers if answer[3] == question_id]

    return len(answers_to_question)


def delete_question_and_answers(question_id):
    '''Delete the question with the given id and all existing answers.'''
    questions = read_raw_data('question.csv')
    new_questions = []
    for question in questions:
        if question[0] != question_id:
            question = ','.join(question)
            new_questions.append(question)

    write_raw_data('question.csv', new_questions)

    answers = read_raw_data('answer.csv')
    new_answers = []
    for answer in answers:
        if answer[3] != question_id:
            answer = ','.join(answer)
            new_answers.append(answer)

    write_raw_data('answer.csv', new_answers)


def print_table(rows):
    table = []

    for row in rows:
        row = str(row).strip("()").split(", ")
        table.append(row)

    for row in table:
        print(", ".join(row))
