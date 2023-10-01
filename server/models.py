from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from datetime import datetime

metadata = MetaData(naming_convention={
    "fk" : "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    serialize_rules = ('-powers.hero',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    powers = db.relationship('Power', secondary='hero_powers', back_populates = 'heroes')

    def __repr__(self):
        return f'(id={self.id}, name={self.name}, super_name={self.super_name})'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    serialize_rules = ('-hero.powers', '-power.heroes')

    id = db.Column(db.Integer, primary_key = True)
    strength = db.Column(db.String)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    power = db.relationship('Power', backref=db.backref('hero_powers', lazy=True))
    hero = db.relationship('Hero', backref=db.backref('hero_powers', lazy=True))

    def __repr__(self):
        return f'(id={self.id}, heroID={self.hero_id} strength={self.strength}) powerID={self.power_id}'

    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ["Strong", "Weak", "Average"]:
            raise ValueError("Strength must be either one of the following:  'Strong', 'Weak', 'Average'")
        return value
    

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    serialize_rules = ('-heroes.power',)

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    heroes = db.relationship('Hero', secondary='hero_powers', back_populates='powers')
    
    @validates('description')
    def checks_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be longer than 20 characters")
        else:
            return description