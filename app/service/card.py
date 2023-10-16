from persistence.card import CardPersistence
from persistence.user import UserPersistence


class CardService:
    @classmethod
    def card_insert(cls, user_id, card_no):
        user = UserPersistence.get_user_by_id(user_id)
        if not user:
            return {'message': 'User not found'}

        card = CardPersistence.check_card(card_no, user_id)
        if card is None:
            CardPersistence.add_card(user_id, card_no, status='ACTIVE',label='NOT_SYSTEM_CARD' )
        else:
            raise Exception('The user has already this card')

    @classmethod
    def card_update(cls, data):
        card = CardPersistence.get_card_by_id(data.get('card_id'))
        if not card:
            raise Exception('Card not found')
        if card.label != "SYSTEM_CARD":
            CardPersistence.update_card(
                card,
                card_no=data.get('card_no', card.card_no),
                status=data.get('status', card.status)
                )

    @classmethod
    def card_delete(cls, card_no, user_id):
        card = CardPersistence.check_card(card_no, user_id=user_id)
        if not card:
            raise Exception('Card not found')
        if not card.label == 'SYSTEM_CARD':
            # Mark the card as "DELETED"
            CardPersistence.delete_card(card, status="DELETED")
        else:
            return Exception('SYSTEM_CARD This card can not be modified')

    @classmethod
    def card_list(cls, user_id):
        user = UserPersistence.get_user_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 401
        cards = CardPersistence.get_all_cards(user_id)
        if not cards:
            return {'message': "The user hasn't this card no"}, 401
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
