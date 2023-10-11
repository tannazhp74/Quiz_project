from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, DateTime, String, JSON, ARRAY, Text
from app import db
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    date_modified = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    card = db.relationship('Card', backref='transactions')

    def __init__(self, amount, card_id, description=None):
        self.amount = amount
        self.card_id = card_id
        self.description = description

    def __repr__(self):
        return f'<Transaction {self.id}>'