from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, DateTime, String, JSON, ARRAY, Text
from app import db
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
    label = db.Column(db.String(50), default="SYSTEM_CARD")
    card_no = db.Column(db.String(16), unique=True, nullable=False)
    status = db.Column(db.String(20), default="PASSIVE")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='cards')

    def __init__(self, card_no, user_id):
        self.card_no = card_no
        self.user_id = user_id

    def __repr__(self):
        return f'<Card {self.card_no}>'
