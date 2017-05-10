from base64 import b64decode, b64encode
from datetime import datetime
from flask import Markup


#
def get_questiontable_from_file(file_name):
    '''Read the QUESTIONS' file into a @table.

    @file_name: string
    @table: list of lists of strings'''
    with open(file_name, "r") as file:
        lines = file.readlines()
    table = [element.replace("\n", "").split(",") for element in lines]
    for record in table:
        # 2nd data field: convert UNIX timestamp to readable date
        record[1] = datetime.fromtimestamp(int(record[1])).strftime('%Y-%m-%d %H:%M:%S')
        # BASE64 decode of 5th, 6th and 7th data fields
        record[4] = b64decode(record[4]).decode("utf-8")
        record[5] = Markup(b64decode(record[5]).decode("utf-8").replace("\n", "<br>"))
        record[6] = b64decode(record[6]).decode("utf-8")
    return table


def write_questiontable_to_file(file_name, row):
    '''Write the QUESTIONS @table into a file.

    @file_name: string
    @table: list of lists of strings'''
    with open(file_name, "a") as file:
        # Convert readable date to UNIX timestamp
        # record[1] = SOMETHING :)
        # BASE64 encode of 5th, 6th and 7th data fields:
        row[4] = b64encode(str.encode(row[4])).decode('utf-8')
        row[5] = b64encode(str.encode(row[5])).decode('utf-8')
        row[6] = b64encode(str.encode(row[6])).decode('utf-8')
        new_row = ','.join(row)
        file.write(new_row + "\n")


def get_answertable_from_file(file_name):
    '''Read the ANSWERS file into a @table.

    @file_name: string
    @table: list of lists of strings'''
    with open(file_name, "r") as file:
        lines = file.readlines()
    table = [element.replace("\n", "").split(",") for element in lines]

    #  BASE64 decode of 5th and 6th data fields:
    for record in table:
        record[1] = datetime.fromtimestamp(int(record[1])).strftime('%Y-%m-%d %H:%M:%S')
        record[4] = b64decode(record[4]).decode("utf-8")
        record[5] = b64decode(record[5]).decode("utf-8")

    return table


def write_answer_to_file(file_name, row):
    '''Write the ANSWERS @table into a file.'''
    with open(file_name, "a") as file:
        row[4] = b64encode(str.encode(row[4])).decode('utf-8')
        row[5] = b64encode(str.encode(row[5])).decode('utf-8')
        new_row = ','.join(row)
        file.write(new_row + "\n")
