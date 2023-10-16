from app import db
from model import Transaction


class TransactionPersistence:

    @classmethod
    def get_transaction(cls, card_id):
        transaction = Transaction.query.filter_by(card_id=card_id).all()
        return transaction

    @classmethod
    def add_transaction(cls, card_id, amount, description):
        new_transaction = Transaction(card_id=card_id, amount=amount, description=description)
        db.session.add(new_transaction)
        db.session.commit()