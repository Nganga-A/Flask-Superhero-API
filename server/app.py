#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate

from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h2>Welcome To Flask-Superhero-API</>'


# Route to get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    hero_list = []
    for hero in heroes:
        hero_data = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name
        }
        hero_list.append(hero_data)
    return jsonify(hero_list)


# Route to get a specific hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({'error': 'Hero not found'}), 404

    hero_data = {
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name,
        'powers': [{'id': power.id, 'name': power.name, 'description': power.description} for power in hero.powers]
    }
    return jsonify(hero_data)


# Route to get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    power_list = []
    for power in powers:
        power_data = {
            'id': power.id,
            'name': power.name,
            'description': power.description
        }
        power_list.append(power_data)
    return jsonify(power_list)



# Route to get a specific power by ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404

    power_data = {
        'id': power.id,
        'name': power.name,
        'description': power.description
    }
    return jsonify(power_data)

# Route to update an existing power by ID
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json()
    new_description = data.get('description')

    if new_description:
        power.description = new_description

    try:
        db.session.commit()
        return jsonify({'id': power.id, 'name': power.name, 'description': power.description})
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': ['Validation errors']}), 400

# Route to create a new HeroPower
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')

    # Validate strength (you can reuse the HeroPower validation)

    # Check if the Hero and Power exist
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return jsonify({'error': 'Hero or Power not found'}), 404

    # Create the HeroPower
    hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)

    try:
        db.session.add(hero_power)
        db.session.commit()
        # Return hero data with associated powers
        hero_data = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'powers': [{'id': power.id, 'name': power.name, 'description': power.description} for power in hero.powers]
        }
        return jsonify(hero_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': ['Validation errors']}), 400

















if __name__ == '__main__':
    app.run(port=5555)
