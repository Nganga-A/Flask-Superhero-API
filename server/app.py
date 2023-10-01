#!/usr/bin/env python3

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Resource, Api, reqparse, abort
from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return '<h2>Welcome To Flask-Superhero-API</h2>'

# Resource for getting all heroes
class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        hero_list = [{'id': hero.id, 'name': hero.name, 'super_name': hero.super_name} for hero in heroes]
        return jsonify(hero_list)

# Resource for getting a specific hero by ID
class HeroResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero is None:
            abort(404, error='Hero not found')

        hero_data = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'powers': [{'id': power.id, 'name': power.name, 'description': power.description} for power in hero.powers]
        }
        return jsonify(hero_data)

# Resource for getting all powers
class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        power_list = [{'id': power.id, 'name': power.name, 'description': power.description} for power in powers]
        return jsonify(power_list)

# Resource for getting a specific power by ID
class PowerResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power is None:
            abort(404, error='Power not found')

        power_data = {'id': power.id, 'name': power.name, 'description': power.description}
        return jsonify(power_data)

# Resource for updating an existing power by ID
class UpdatePowerResource(Resource):
    def patch(self, id):
        power = Power.query.get(id)
        if power is None:
            abort(404, error='Power not found')

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

# Resource for creating a new HeroPower
class CreateHeroPowerResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('strength', type=str, required=True)
        parser.add_argument('power_id', type=int, required=True)
        parser.add_argument('hero_id', type=int, required=True)
        data = parser.parse_args()
        strength = data['strength']
        power_id = data['power_id']
        hero_id = data['hero_id']

        # Validate strength (you can reuse the HeroPower validation)

        # Check if the Hero and Power exist
        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)

        if not hero or not power:
            abort(404, error='Hero or Power not found')

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

# Add resources to the API
api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(UpdatePowerResource, '/powers/<int:id>')
api.add_resource(CreateHeroPowerResource, '/hero_powers')


if __name__ == '__main__':
    app.run(port=5555)
