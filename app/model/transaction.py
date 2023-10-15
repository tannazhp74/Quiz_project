
from datetime import datetime

from app import db


class Transaction(db.Model):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, onupdate=datetime.utcnow)
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
