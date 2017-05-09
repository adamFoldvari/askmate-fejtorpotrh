from base64 import b64decode, b64encode
from datetime import datetime


# read the QUESTIONS' file into a @table
#
# @file_name: string
# @table: list of lists of strings
def get_questiontable_from_file(file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
    table = [element.replace("\n", "").split(",") for element in lines]
    for record in table:
        # Convert UNIX timestamp to readable date
        record[1] = datetime.fromtimestamp(int(record[1])).strftime('%Y-%m-%d %H:%M:%S')
        # BASE64 decode of 2nd, 5th, 6th and 7th data fields
        record[4] = b64decode(record[4])
        record[5] = b64decode(record[5])
        record[6] = b64decode(record[6])
        print(table)
    return table


# write the QUESTIONS @table into a file
#
# @file_name: string
# @table: list of lists of strings
def write_questiontable_to_file(file_name, table):
    with open(file_name, "w") as file:
        for record in table:
            for record in table:
                # Convert readable date to UNIX timestamp

                # BASE64 encode of 5th, 6th and 7th data fields:
                record[4] = base64.b64encode(record[4])
                record[5] = base64.b64encode(record[5])
                record[6] = base64.b64encode(record[6])

            row = ','.join(record)
            file.write(row + "\n")


# read the ANSWERS file into a @table
#
# @file_name: string
# @table: list of lists of strings
def get_answertable_from_file(file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
    table = [element.replace("\n", "").split(",") for element in lines]

    #  BASE64 decode of 5th, 6th and 7th data fields:
    for record in table:
        record[4] = base64.b64decode(record[4])
        record[5] = base64.b64decode(record[5])

    return table


# write the ANSWERS @table into a file
#
# @file_name: string
# @table: list of lists of strings
