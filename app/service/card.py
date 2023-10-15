from app import db
from model.card import Card


class CardService:
    def __init__(self):
        pass

    @classmethod
    def card_insert(cls, user_id, card_no):

        card = Card.query.filter_by(card_no=card_no, user_id=user_id).first()
        if card is None:
            new_card = Card(card_no=card_no, user_id=user_id, label='NOT_SYSTEM_CARD', status='ACTIVE')
            db.session.add(new_card)
            db.session.commit()
        else:
            raise Exception('The user has already this card')

    @classmethod
    def card_update(cls, data, card):
        if card.label != "SYSTEM_CARD":
            card.card_no = data.get('card_no', card.card_no)
            card.status = data.get('status', card.status)
            db.session.commit()

    @classmethod
    def card_delete(cls, card):
        if not card.label == 'SYSTEM_CARD':
            # Mark the card as "DELETED"
            card.status = "DELETED"
            db.session.commit()
        else:
            raise Exception('This card can not be modified')

    @classmethod
    def card_list(cls, cards):
        card_list = [
            {
                'id': item.id,
                'card_no': item.card_no,
                'label': item.label,
                'user_id': item.user_id,
                'date_created': str(item.date_created),
                'date_modified': str(item.date_modified)
            }
            for item in cards if item.status != 'DELETED'
        ]
        return card_list