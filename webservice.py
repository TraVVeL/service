from flask import Flask, request


app = Flask(__name__)


@app.route('/')
def index():
    return 'Start page'

@app.route('/route', methods=['GET', 'POST'])
def route():
    rules = ['No primary parameter', 'No secondary parameter']
    name = request.args.get('name')
    message = request.args.get('message')

    return f"{rules[0] if name == None else 'Hello ' + name + '!'} {rules[1] if message == None else message + '!'}"


@app.errorhandler(404)
def page_not_found(error):
    return 'Bad request'


if __name__ == '__main__':
    app.run(debug=True)
