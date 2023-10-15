from flask import Flask, request, jsonify
from app import db
from model import Transaction
from model.card import Card


class TransactionService:

    def __init__(self):
        pass

    @classmethod
    def transaction_insert(cls, card, amount, description):
        # Create a new transaction associated with the card
        new_transaction = Transaction(card_id=card.id, amount=amount, description=description)
        db.session.add(new_transaction)
        db.session.commit()

    @classmethod
    def transaction_list_summary(cls, user_id):
        # Retrieve user's active and passive cards
        active_cards = Card.query.filter_by(user_id=user_id, status="ACTIVE").all()
        passive_cards = Card.query.filter_by(user_id=user_id, status="PASSIVE").all()

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
    def transaction_list_detailed(cls, card):
        description = request.json.get('description')  # The filter argument specifies the view type

        # Retrieve transactions associated with the card in a detailed view
        transactions = Transaction.query.filter_by(card_id=card.id).all()
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