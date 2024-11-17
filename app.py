from flask import Flask, request
from activity_parser import get_parser

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/activity', methods=['GET'])
def my_form_post():
    url = request.args['activity-url']

    parser = get_parser(url)

    data = parser.get_info()
    return data


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)