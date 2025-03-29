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
from models import db, User, People, Planets, Favoritos
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


# METODOS GET

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all() 
    users_serialized = [user.serialize() for user in users]
    return jsonify(users_serialized),200

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all() 
    people_serialized = [character.serialize() for character in people]
    return jsonify(people_serialized),200

@app.route('/people/<:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    return jsonify(person.serialize()),200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all() 
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify(planets_serialized),200

@app.route('/planets/<:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    return jsonify(planet.serialize()),200

@app.route('/users/favorites', methods=['GET'])
def get_all_users_with_favorites():
    users = User.query.all()  
    data = []
    for user in users:
        user_data = user.serialize()  
        user_data["favoritos"] = [fav.serialize() for fav in user.favoritos]
        data.append(user_data)
    return jsonify(data)

# METODOS POST

@app.route('/favorite/planet/<:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()  
    user_id = data.get("user_id")  

    exist = Favoritos.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    
    if not exist:
        new_favorito = Favoritos(
            planet_id=planet_id,
            user_id=user_id
        )
        db.session.add(new_favorito)
        db.session.commit()

    return jsonify({"msg": "Planeta añadido a favoritos"}), 201


@app.route('/favorite/people/<:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()  
    user_id = data.get("user_id")  

    exist = Favoritos.query.filter_by(user_id=user_id, people_id=people_id).first()
    
    if not exist:
        new_favorito = Favoritos(
            people_id=people_id,
            user_id=user_id
        )
        db.session.add(new_favorito)
        db.session.commit()

    return jsonify({"msg": "Personaje añadido a favoritos"}), 201

#METODOS DELETE

@app.route('/favorite/planet/<:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")

    favorito = Favoritos.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()

    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200

@app.route('/favorite/people/<:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get("user_id")

    favorito = Favoritos.query.filter_by(user_id=user_id, people_id=people_id).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()

    return jsonify({"msg": "Personaje eliminado de favoritos"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
