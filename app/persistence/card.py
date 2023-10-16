from app import db
from model.card import Card


class CardPersistence:

    @classmethod
    def add_card(cls, user_id, card_no, status='PASSIVE', label='SYSTEM_CARD'):
        card = Card(card_no=card_no, user_id=user_id, label=label, status=status)
        db.session.add(card)
        db.session.commit()

    @classmethod
    def update_card(cls, card, card_no, status):
        card.card_no = card_no
        card.status = status
        db.session.commit()

    @classmethod
    def delete_card(cls, card, status):
        card.status = status
        db.session.commit()

    @classmethod
    def get_filter_card(cls, user_id):
        card = Card.query.filter_by(label='SYSTEM_CARD', user_id=user_id).first()
        return card

    @classmethod
    def get_all_cards(cls, user_id):
        card = Card.query.filter_by(user_id=user_id).all()
        return card

    @classmethod
    def check_card(cls, card_no, user_id):
        card = Card.query.filter_by(card_no=str(card_no), user_id=user_id).first()
        return card

    @classmethod
    def get_card_by_id(cls, card_id):
        card = Card.query.filter_by(id=card_id).first()
        return card
