from datetime import timedelta, datetime
import jwt
from app import db
from config import Config
from persistence.card import CardPersistence
from persistence.user import UserPersistence
from service import redis_client


class UserService:

    @classmethod
    def user_register(cls, username, password, email):
        # Check if the username or email already exists in the database
        existing_user = UserPersistence.get_filter_user(username, email)
        if existing_user:
            raise Exception('Username or email already in use')

        # Create a new user and add it to the database
        new_user = UserPersistence.add_user(username, password, email)

        # Automatically create a card for the user and set its status to "PASSIVE"
        CardPersistence.add_card(new_user.id, 1)

    @classmethod
    def user_login(cls, username, password):
        # Check if the user exists in the database
        user = UserPersistence.get_user(username)

        if not user:
            raise Exception('User not found')

        # Verify the password
        if UserPersistence.authentication(user.password, password) is False:
            raise Exception('Incorrect password')

        # Generate a JWT token for the user
        token_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=5)  # Token expiration time
        }

        token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')

        redis_client.set(f'user :{user.id}', user.to_json(), ex=300)  # 300 seconds (5 minutes) expiration

        pre_created_card = CardPersistence.get_filter_card(user.id)
        CardPersistence.update_card(pre_created_card, pre_created_card.card_no, status="ACTIVE")

        redis_data = redis_client.get(f'user :{user.id}')
        return token, redis_data
