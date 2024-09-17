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
from models import db, User, People, Planet, Favorites
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

#USER
#POST A USER
@app.route('/user', methods=['POST'])
def creat_user():
    req_body = request.get_json()
    user_email = req_body['email']
    user_password = req_body['password']
    user_active = req_body['is_active']
    new_user = User(email=user_email, password=user_password, is_active=user_active)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Added a new user to the database'}), 200

#GET ALL USERS
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized_users = []
    for user in users: 
        serialized_users.append(user.serialize())
    if len(serialized_users) > 0:
        return jsonify(serialized_users), 200
    return jsonify({'Message': 'No users in database'}), 404



#PEOPLE
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

#GET PERSON
@app.route('/person/<int:person_id>', methods=['GET'])
def get_single_person(person_id):
    person = People.query.get(person_id)
    if person:
        return jsonify(person.serialize()), 200
    return jsonify({'message': 'Person not found'}), 404

#GET ALL PEOPLE
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    serialized_people = []
    for peps in people: 
        serialized_people.append(peps.serialize())
    if len(serialized_people) > 0:
        return jsonify(serialized_people), 200
    return jsonify({'Message': 'No people in database'}), 404



# PLANET
#CREATE NEW PLANET
@app.route('/planet', methods=['POST'])
def create_planet():
    req_body = request.get_json()
    planet_name = req_body['name']
    planet_about = req_body['about']
    new_planet = Planet(name=planet_name, about=planet_about)

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({'message': 'Added a new planet to the database'}), 200

#GET ALL PLANETS
@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    serialized_planet = []
    for planet in planets: 
        serialized_planet.append(planet.serialize())

    if len(serialized_planet) > 0:
        return jsonify(serialized_planet), 200

    return jsonify({'message': 'No planets in database'}), 404



#FAVORITES

#CREATE FAVORITE PERSON
@app.route('/favorite/person/<int:person_id>', methods=['POST'])
def create_favorite_person(person_id):
    user_id = 1
    current_user = User.query.get(user_id)
    if current_user:
        person = People.query.get(person_id)
        favorites = Favorites()
        favorites.user = current_user
        favorites.person = person
        current_user.favorites.append(favorites)
        db.session.commit()
        return jsonify({'message': 'Successfully added person to favorites'})
    
    return jsonify({'message': 'Error adding person to favorites'})

#DELETE FAVORITE PERSON
@app.route('/favorite/person/<int:person_id>', methods=['DELETE'])
def delete_favorite_person(person_id):
    user_id = 1 #request.arg.get('user_id')
    person = People.query.get(person_id)
    if person:
        user = User.query.get(user_id)
        user_favorite = user.favorites()
    favorite = Favorites.query.filter_by(user_id=user_id, people_id = person_id).first()
    db.session.delete(favorite)
    db.session.commit()

#CREATE FAVORITE PLANET
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_favorite_planet(planet_id):
    user_id = 1
    current_user = User.query.get(user_id)
    if current_user:
        planet = Planet.query.get(planet_id)
        favorites = Favorites()
        favorites.user = current_user
        favorites.planet = planet
        current_user.favorites.append(favorites)
        db.session.commit()
        return jsonify({'message': 'Successfully added planet to favorites'})
    
    return jsonify({'message': 'Error adding planet to favorites'})


#GET ALL FAVORITES FOR USER
@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    serialized_favorites = []
    for favorites in user.favorites: 
        serialized_favorites.append(favorites.serialize())

    if len(serialized_favorites) > 0:
        return jsonify(serialized_favorites), 200

    return jsonify({'message': 'No favorites in database'}), 404

# get each favorite


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
