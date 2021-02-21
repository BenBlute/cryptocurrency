from random import randint
from time import time
from itertools import zip_longest

from crypto import key_to_string, sha256
from transaction import Transaction


class Block:

    @classmethod
    def create(cls, key, previous_hash, difficulty):
        obj = cls()

        obj.transactions = [Transaction.create_mining_rewards(key, [])]
        obj.previous_hash = previous_hash
        obj.merkle_root = obj.calculate_merkle_root()
        obj.nonce = randint(0, 2**32)
        obj.difficulty = difficulty
        obj.timestamp = time()

        return obj

    @classmethod
    def create_genesis(cls):
        obj = cls()

        obj.transactions = []
        obj.previous_hash = ''
        obj.merkle_root = ''
        obj.nonce = 0
        obj.difficulty = 1
        obj.timestamp = time()

        return obj

    @classmethod
    def from_json(cls, json):
        obj = cls()

        obj.transactions = [Transaction.from_json(t) for t in json['transactions']]
        obj.previous_hash = json['previous_hash']
        obj.merkle_root = json['merkle_root']
        obj.nonce = json['nonce']
        obj.difficulty = json['difficulty']
        obj.timestamp = json['timestamp']

        return obj

    def to_json(self):
        return {
            'transactions': [t.to_json() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp
        }

    def add_transaction(self, transaction):
        if transaction not in self.transactions:
            self.transactions.append(transaction)
            self.merkle_root = self.calculate_merkle_root()

    def add_transactions(self, transactions):
        modified = False

        for t in transactions:
            if t not in self.transactions:
                self.transactions.append(t)
                modified = True

        if modified:
            self.merkle_root = self.calculate_merkle_root()

    def calculate_merkle_root(self):
        hashes = [t.hash() for t in self.transactions]

        while len(hashes) != 1:
            args = [iter(hashes)] * 2
            hash_pairs = zip_longest(*args, fillvalue='')
            hashes = [sha256(a + b) for a, b in hash_pairs]

        return hashes[0]

    def hash(self):
        string = ''
        for t in self.transactions:
            string += t.hash()
        string += self.previous_hash
        string += self.merkle_root
        string += str(self.nonce)
        string += str(self.difficulty)
        string += str(self.timestamp)

        return sha256(string)
