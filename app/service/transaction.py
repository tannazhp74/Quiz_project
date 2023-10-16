from persistence.card import CardPersistence
from persistence.transaction import TransactionPersistence


class TransactionService:

    @classmethod
    def transaction_insert(cls, card_id, amount, description):
        card = CardPersistence.get_card_by_id(card_id)
        if not card:
            return {'message': 'Card not found'}, 404
        if card.status != "ACTIVE":
            return {'message': 'Card is not active'}, 400
        # Create a new transaction associated with the card
        TransactionPersistence.add_transaction(card.id, amount, description)

    @classmethod
    def transaction_list_summary(cls, user_id):
        # Retrieve user's active and passive cards
        all_cards = CardPersistence.get_all_cards(user_id=user_id)
        active_cards = [card for card in all_cards if card.status == 'ACTIVE']
        passive_cards = [card for card in all_cards if card.status == 'PASSIVE']

        # Calculate the total amount spent on active and passive cards
        active_total_amount = sum([t.amount for card in active_cards for t in card.transactions])
        passive_total_amount = sum([t.amount for card in passive_cards for t in card.transactions])

        transaction_list = {
            'active_cards_count': len(active_cards),
            'active_total_amount': active_total_amount,
            'passive_total_amount': passive_total_amount
        }

        return transaction_list

    @classmethod
    def transaction_list_detailed(cls, data):
        card_id = data.get('card_id')
        description = data.get('description')  # The filter argument specifies the view type

        if not card_id:
            raise Exception('Enter card id')
        card = CardPersistence.get_card_by_id(card_id)
        if not card:
            raise Exception('Card not found')

        # Retrieve transactions associated with the card in a detailed view
        transactions = TransactionPersistence.get_transaction(card.id)
        transaction_list = [
            {
                'id': t.id,
                'amount': t.amount,
                'description': t.description,
                'date_created': str(t.date_created)
            }
            for t in transactions if t.description == description
        ]
        return transaction_list
