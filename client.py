from flask import Flask
from flask import render_template, request, redirect, url_for
import requests

app = Flask(__name__)
token = None
USERNAME = None
data = ""

@app.route('/', methods = ['GET'])
def home():
    return render_template("from_to.html", is_data = data, login=USERNAME)

@app.route('/', methods=['POST'])
def fromTo():
    from_ = request.form.get('from')
    to = request.form.get('to')
    URL = f"http://127.0.0.1:5000/flights/{from_}/{to}"
    r = requests.get(url = URL)
    global data
    data = r.json()
    for i in data['flights']:
        i['id'] = str(i['id'])

    print(USERNAME)
    return redirect(url_for('home'))

    # return render_template("from_to.html", is_data = r.json(), login = USERNAME)

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    print('hiiiiiii')
    username = request.form.get('username')
    global USERNAME
    USERNAME = username
    password = request.form.get('password')
    URL = f"http://127.0.0.1:5000/authentication_authorization"
    data = {
        'username': username,
        'password': password
    }
    r = requests.post(url=URL, data = data)
    global token
    token = r.json()['status']
    print(token)
    return redirect(url_for('home'))
    # return render_template('from_to.html', is_data = None, login=USERNAME)

@app.route('/sign_out')
def end_session():
    global  token
    token = None
    global USERNAME
    USERNAME = None
    return  redirect(url_for("home"))

@app.route('/add_flight')
def add_new():
    return render_template('add.html')

@app.route('/add_new', methods=['POST'])
def add_new_post():
    from_ = request.form.get('from')
    to = request.form.get('to')
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    airplane_info = request.form.get('airplane_info')
    pass_num = request.form.get('pass_num')

    URL = f"http://127.0.0.1:5000/flights"
    data = {
        'from': from_,
        'to': to,
        'from_date': from_date,
        'to_date': to_date,
        'airplane_info': airplane_info,
        'pass_num': pass_num,
        'token': token
    }
    r = requests.post(url=URL, data=data)
    print(r.json())
    if (r.json()['status'] == True):
        return redirect(url_for('home'))
    else:
        return "<h1>ERROR</h1>"

@app.route('/delete/<id>', methods=['post'])
def delete(id):
    id_ = int(id)
    data = {
        'id' : id_,
        'token': token
    }
    URL = f"http://127.0.0.1:5000/flights"
    r = requests.delete(URL, data=data)
    print(r.json())
    if (r.json()['status'] == True):
        return redirect(url_for('home'))
    else:
        return "<h1>ERROR</h1>"
if __name__ == '__main__':
    app.run(debug=True, port = 5001)