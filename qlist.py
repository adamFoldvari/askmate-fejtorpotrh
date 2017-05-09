# WARNING: after creating main.py these import section must be reviewed
# and "if __name__ == '__main__'" etc. must be deleted!
from flask import Flask
from flask import render_template
import data_manager
import os


current_file_path = os.path.dirname(os.path.abspath(__file__))
file_name = current_file_path + '/question.csv'
app = Flask(__name__)


# Listing
@app.route('/', methods=['POST', 'GET'])
@app.route('/list', methods=['POST', 'GET'])
def listing():
    questions = data_manager.get_questiontable_from_file(file_name)
    return render_template("questionlist.html", questions=questions)


if __name__ == '__main__':
    app.debug = True
    app.run()