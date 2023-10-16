from werkzeug.security import check_password_hash, generate_password_hash
from model.user import User
from app import db


class UserPersistence:

    @classmethod
    def add_user(cls, username, password, email):
        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_filter_user(cls, username, email):
        print('get_filter_user')
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        return user

    @classmethod
    def authentication(cls, hash_password, password):
        if not check_password_hash(hash_password, password):
            return False
        else:
            return True

    @classmethod
    def get_user(cls, username):
        user = User.query.filter_by(username=username).first()
        return user

    @classmethod
    def get_user_by_id(cls, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
