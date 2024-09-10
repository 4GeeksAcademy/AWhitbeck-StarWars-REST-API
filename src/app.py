"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#CREATE NEW PERSON
@app.route('/person', methods=['POST'])
def create_person():
    req_body = request.get_json()
    person_name = req_body['name']
    person_about = req_body['about']
    new_person = People(name=person_name, about=person_about)

    db.session.add(new_person)
    db.session.commit()

    return jsonify({'message': 'Added a new person to the database'}), 200

#GET ALL PEOPLE
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    serialized_people = []
    for person in people: 
        serialized_people.append(person.serialize())

    if len(serialized_people) > 0:
        return jsonify(serialized_people), 200

    return jsonify({'message': 'No people in database'}), 404

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
