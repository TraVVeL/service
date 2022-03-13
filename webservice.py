from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Start page'

@app.route('/route', methods=['GET', 'POST'])
def login():
    name = request.args.get('name')
    message = request.args.get('message')

    if name != None and message != None:
        return f"Hello {name}! {message}!"

    elif name == None and message != None:
        return f"{message}"

    elif name != None and message == None:
        return f"Hello {name}!"

    else:
        return "There is no parameters"


if __name__ == '__main__':
    app.run(debug=True)


