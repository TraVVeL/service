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



'''
from flask import Flask, jsonify, request
app = Flask(__name__)

studentBD = [
    {
        'rollNo': '11',
        'name': 'John Dennis',
        'section': 'A'
    },
    {
        'rollNo': '12',
        'name': 'Phil Coulson',
        'section': 'B'
    }
]

@app.route('/', methods=['GET'])
def welcome():
    return 'Hello to the web-service'

@app.route('/students/getStudents', methods=['GET'])
def getStudents():
    return jsonify({'stud': studentBD})

@app.route('/student/getStudent/<rollNo>', methods=['GET'])
def getStudentDetails(rollNo):
    student = [stud for stud in studentBD if(stud['rollNo'] == rollNo)]
    print(student)
    return jsonify({'stud': student})

@app.route('/student/updateStudent/<rollNo>', methods=['PUT'])
def updateStudentsDetail(rollNo):
    student = [stud for stud in studentBD if (stud['rollNo'] == rollNo)]

    if 'rollNo' in request.json:
        print('Student Available')
    if 'name' in request.json:
        student[0]['name'] = request.json['name']
    return jsonify({'stud': student[0]})

if __name__ == '__main__':
    app.run(debug=True)'''

'''from flask import Flask, jsonify

app = Flask(__name__)

collect = [
    {
        'name' : 'Rekruto',
        'message' : 'Давай дружить!'
    }

]


@app.route('/', methods=['GET'])
def welcome():
    return 'Hello'

@app.route('/id', methods=["GET"])
def getid():
    return jsonify({'id':collect})

@app.route('/id/ip/<name>', methods=['GET'])
def getidip(name):
    student = [stud for stud in collect if (stud['name']==name)]
    return jsonify({"stud":student})


if __name__ == '__main__':
    app.run()
'''
