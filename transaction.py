from time import time

from crypto import sha256, key_to_string, sign_message


class Transaction:

    @classmethod
    def create(cls, key, recipient, amount):
        transaction = cls()

        transaction.sender = key_to_string(key.public_key())
        transaction.recipient = recipient
        transaction.amount = amount
        transaction.timestamp = str(time())

        string = transaction.sender
        string += transaction.recipient
        string += transaction.amount
        string += transaction.timestamp

        transaction.signature = sign_message(key, string)

        return transaction

    @classmethod
    def from_json(cls, json):
        transaction = cls()

        transaction.sender = json['sender']
        transaction.recipient = json['recipient']
        transaction.amount = json['amount']
        transaction.timestamp = json['timestamp']
        transaction.signature = json['signature']

        return transaction

    def to_json(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature
        }

    def hash(self):
        string = self.sender
        string += self.recipient
        string += self.amount
        string += self.timestamp
        string += self.signature

        return sha256(string)

    def __eq__(self, other):
        return self.hash() == other.hash()

