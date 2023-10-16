from datetime import datetime

from app import db


class Card(db.Model):
    __tablename__ = 'cards'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, onupdate=datetime.utcnow)
    label = db.Column(db.String(50), default="SYSTEM_CARD")
    card_no = db.Column(db.String(16), unique=False, nullable=False)
    status = db.Column(db.String(20), default="PASSIVE")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='cards')

    def __init__(self, card_no, user_id, label, status):
        self.card_no = card_no
        self.user_id = user_id
        self.label = label
        self.status = status

    def __repr__(self):
        return f'<Card {self.card_no}>'
