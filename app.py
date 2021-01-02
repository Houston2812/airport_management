from flask import Flask
from flask import jsonify
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import  os
import secrets
import json

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'flights.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

admins_file = os.path.join(basedir, 'admins.json')
TOKENS = set()

class Flight(db.Model):
    id = db.Column(db.INTEGER, primary_key = True)
    to_city = db.Column(db.String(100))
    from_city = db.Column(db.String(100))
    date_of_arrival = db.Column(db.DATETIME)
    date_of_departure = db.Column(db.DATETIME)
    airplane_info = db.Column(db.Text)
    pass_num = db.Column(db.Integer)

    def __repr__(self):
        return f'<To {self.to_city}>, <From {self.from_city}>, <Date of arrival {self.date_of_arrival}>, <Date of departure {self.date_of_departure}>, <Airplane Info {self.airplane_info}>, <Pass num {self.pass_num}>'

    def get_dict(self):
        dict_ = {
            'id': self.id,
            'to_city': self.to_city,
            'from_city': self.from_city,
            'date_of_arrival': self.date_of_arrival,
            'date_of_departure': self.date_of_departure,
            'airplane_info': self.airplane_info,
            'pass_num': self.pass_num
        }
        return dict_

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f'<Username {self.username}>'

def add_admins(admins):
    for i in admins['admins']:
        username = i['username']
        if Admin.query.filter_by(username = username).first() == None:
            password = generate_password_hash(i['password'])
            admin = Admin(username=username, password = password)
            db.session.add(admin)
            db.session.commit()

parser = reqparse.RequestParser()
parser.add_argument('id')
parser.add_argument('to_city')
parser.add_argument('from_city')
parser.add_argument('date_of_arrival')
parser.add_argument('date_of_departure')
parser.add_argument('airplane_info')
parser.add_argument('pass_num')
parser.add_argument('token')

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('username')
auth_parser.add_argument('password')

end_parser = reqparse.RequestParser()
end_parser.add_argument('token')

class Flights(Resource):
    def post(self):
        args = parser.parse_args()
        if args['id'] == "0" and args['token'] in TOKENS:
            arrival = datetime.strptime(args['date_of_arrival'], '%Y-%m-%d %H:%M:%S')
            departure = datetime.strptime(args['date_of_departure'], '%Y-%m-%d %H:%M:%S')

            new_flight = Flight(to_city=args['to_city'], from_city=args['from_city'], date_of_arrival=arrival, date_of_departure=departure, airplane_info=args['airplane_info'], pass_num=args['pass_num'])
            db.session.add(new_flight)
            try:
                db.session.commit()
            except Exception as e:
                print(1)
                return jsonify({'status': False})
            return jsonify({'status': True})
        return jsonify({'status': False})

    def put(self):
        args = parser.parse_args()
        if args['token'] in TOKENS:
            arrival = datetime.strptime(args['date_of_arrival'], '%Y-%m-%d %H:%M:%S')
            departure = datetime.strptime(args['date_of_departure'], '%Y-%m-%d %H:%M:%S')

            upd_flight = Flight.query.filter_by(id = args['id']).first()
            upd_flight.to_city = args['to_city']
            upd_flight.from_city = args['from_city']
            upd_flight.date_of_arrival = arrival
            upd_flight.date_of_departure = departure
            upd_flight.airplane_info = args['airplane_info']
            upd_flight.pass_num = args['pass_num']

            try:
                db.session.commit()
            except Exception as e:
                return jsonify({'status': False})

            return jsonify({'status': True})
        return  jsonify({'status': False})
    def delete(self):

        args = parser.parse_args()
        if args['token'] in TOKENS:
            del_flight = Flight.query.filter_by(id = args['id']).delete()
            try:
               db.session.commit()
            except Exception as e:
               return jsonify({'status': False})
            return jsonify({'status': True})
        else:
            return  jsonify({'status': False})

class FlightsFromTo(Resource):
    def get(self, from_, to):
        # print(from_, to)
        if from_ != "0" and to != "0":
            flights = Flight.query.filter_by(from_city = from_, to_city = to).all()
            return jsonify({'flights': list(map(lambda flight: flight.get_dict(), flights))})
        elif from_ == "0":
            flights = Flight.query.filter_by(to_city = to).all()
            return jsonify({'flights': list(map(lambda flight: flight.get_dict(), flights))})
        elif to == "0":
            flights = Flight.query.filter_by(from_city = from_).all()
            return jsonify({'flights': list(map(lambda flight: flight.get_dict(), flights))})

class Auth(Resource):
    def post(self):
        args = auth_parser.parse_args()
        print(args['username'])
        admin = Admin.query.filter_by(username = args['username']).first()
        if check_password_hash(admin.password, args['password']):
            token = secrets.token_hex(16)
            global  TOKENS
            while token in TOKENS:
                token = secrets.token_hex(16)
            TOKENS.add(token)
            return jsonify({'status': token})
        else:
            return jsonify({'status': False})

class End(Resource):
    def post(self):
        args = end_parser.parse_args()
        try:
            TOKENS.remove(args['token'])
        except Exception as e:
            return jsonify({'status': False})
        return jsonify({'status': True})

api.add_resource(Flights, '/flights')
api.add_resource(FlightsFromTo, '/flights/<from_>/<to>')
api.add_resource(Auth, '/authentication_authorization')
api.add_resource(End, '/end_session')

if __name__ == '__main__':
    db.create_all()
    with open(admins_file, 'rb') as f:
        data = json.load(f)
        add_admins(data)

    app.run(debug=  True)
