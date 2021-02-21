from random import randint
from time import time
from itertools import zip_longest

from crypto import key_to_string, sha256


class Block:

    @classmethod
    def create(cls, key, transactions, previous_hash, difficulty):
        obj = cls()

        obj.miner = key_to_string(key.public_key())
        obj.transactions = transactions
        obj.previous_hash = previous_hash
        obj.merkle_root = obj.calculate_merkle_root()
        obj.nonce = randint(0, 2**32)
        obj.difficulty = difficulty
        obj.timestamp = str(time())

        return obj

    def from_json(cls, json):
        obj = cls()

        obj.miner = json['miner']
        obj.transactions = [Transaction.from_json(t) for t in json['transactions']]
        obj.previous_hash = json['previous_hash']
        obj.merkle_root = json['merkle_root']
        obj.nonce = json['nonce']
        obj.difficulty = json['difficulty']
        obj.timestamp = json['timestamp']

        return obj

    def to_json(self):
        return {
            'miner': self.miner,
            'transactions': [t.to_json() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp
        }

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
        string = self.miner
        for t in self.transactions:
            string += t.hash()
        string += self.previous_hash
        string += self.merkle_root
        string += self.nonce
        string += self.difficulty
        string += self.timestamp

        return sha256(string)

