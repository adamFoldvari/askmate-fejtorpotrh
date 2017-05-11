from base64 import b64decode, b64encode
from datetime import datetime
from flask import Markup


def read_raw_data(file_name):
    '''Reads the lines from the csv file without decodeing'''
    with open(file_name) as file:
        data_list = file.readlines()
        data_list = [element.replace("\n", "").split(",") for element in data_list]

    return data_list


def write_raw_data(file_name, table):
    '''Writes the lines from the csv file without decodeing'''
    with open(file_name, 'w') as file:
        for element in table:
            file.write(element + '\n')


def get_questiontable_from_file():
    '''Read the QUESTIONS' file into a @table.

    @file_name: string
    @table: list of lists of strings
    '''
    table = read_raw_data('question.csv')

    for record in table:
        # 2nd data field: convert UNIX timestamp to readable date
        record[1] = datetime.fromtimestamp(int(record[1])).strftime('%Y-%m-%d %H:%M:%S')
        # BASE64 decode of 5th, 6th and 7th data fields
        record[4] = b64decode(record[4]).decode("utf-8")
        record[5] = Markup(b64decode(record[5]).decode("utf-8").replace("\n", "<br>"))
        record[6] = b64decode(record[6]).decode("utf-8")

    return table


def write_questiontable_to_file(row):
    '''Write the QUESTIONS @row into a file.

    @file_name: string
    @row: list of strings
    '''
    with open('question.csv', "a") as file:
        # Convert readable date to UNIX timestamp
        # BASE64 encode of 5th, 6th and 7th data fields:
        row[4] = b64encode(str.encode(row[4])).decode('utf-8')
        row[5] = b64encode(str.encode(row[5])).decode('utf-8')
        row[6] = b64encode(str.encode(row[6])).decode('utf-8')
        new_row = ','.join(row)
        file.write(new_row + "\n")


def get_answertable_from_file():
    '''Read the ANSWERS file into a @table.

    @file_name: string
    @table: list of lists of strings
    '''
    table = read_raw_data('answer.csv')
    #  BASE64 decode of 5th and 6th data fields:
    for record in table:
        record[1] = datetime.fromtimestamp(int(record[1])).strftime('%Y-%m-%d %H:%M:%S')
        record[4] = Markup(b64decode(record[4]).decode("utf-8").replace("\n", "<br>"))
        record[5] = b64decode(record[5]).decode("utf-8")

    return table


def write_answer_to_file(row):
    '''Write the ANSWERS @row into a file.'''
    with open('answer.csv', "a") as file:
        row[4] = b64encode(str.encode(row[4].strip())).decode('utf-8')
        row[5] = b64encode(str.encode(row[5])).decode('utf-8')
        new_row = ','.join(row)
        file.write(new_row + "\n")


def add_view_number(question_id):
    '''Add 1 to the view number for the given question_id.

    You should also give a filename as a database.
    '''
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
    '''Gives the number of answers exists for the question with the given id.'''
    answers = get_answertable_from_file()
    questions = get_questiontable_from_file()
    question = [question for question in questions if question_id == question[0]][0]
    answers_for_question = [answer for answer in answers if answer[3] == question_id]

    return len(answers_for_question)


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
