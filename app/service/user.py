
from datetime import timedelta, datetime
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from app import db
from config import Config
from model import Transaction
from model.card import Card
from model.user import User
from service import redis_client


class UserService:

    def __init__(self):
        pass

    @classmethod
    def user_register(cls, username, password, email):
        # Create a new user and add it to the database
        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Automatically create a card for the user and set its status to "ACTIVE"
        auto_card = Card(label='SYSTEM_CARD', user_id=new_user.id, status='PASSIVE', card_no=1)
        db.session.add(auto_card)
        db.session.commit()

    @classmethod
    def user_login(cls, user):
        # Generate a JWT token for the user
        token_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=5)  # Token expiration time
        }

        token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')

        redis_client.set(f'user :{user.id}', user.to_json(), ex=300)  # 300 seconds (5 minutes) expiration

        precreated_card = Card.query.filter_by(label='SYSTEM_CARD', user_id=user.id).first()
        if precreated_card and precreated_card.status != "ACTIVE":
            precreated_card.status = "ACTIVE"
            db.session.commit()

        redis_data = redis_client.get(f'user :{user.id}')
        return token, redis_data
