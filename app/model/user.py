import json

from app import db

from datetime import datetime, timedelta


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.username}>'

    def to_json(self):
        return json.dumps({'id': self.id, 'username': self.username, 'email': self.email, 'date_created': str(self.date_created)})
