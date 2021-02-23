from time import time

from block import Block


class Blockchain:

    @classmethod
    def create(cls):
        obj = cls()

        obj.blocks = [Block.create_genesis()]

        return obj

    @classmethod
    def from_json(cls, json):
        obj = cls()

        obj.blocks = [Block.from_json(b) for b in json['blocks']]

        return obj

    def to_json(self):
        return {
            'blocks': [b.to_json() for b in self.blocks]
        }

    def __len__(self):
        return len(self.blocks)

    def add_block(self, block):
        self.blocks.append(block)

    def last_block(self):
        return self.blocks[-1]

    def validate(self, utxo):
        try:
            genesis_block = self.blocks[0]
            assert genesis_block.transactions == []
            assert genesis_block.previous_hash == ''
            assert genesis_block.merkle_root == ''
            assert genesis_block.nonce == 0
            assert genesis_block.difficulty == 1
            assert genesis_block.timestamp < time()

            TWO_WEEKS = 60 * 60 * 24 * 7 * 2

            previous_block = genesis_block
            previous_timestamp = genesis_block.timestamp

            for block in self.blocks[1:]:
                block.fees = 0
                for transaction in block.transactions[1:]:
                    assert transaction.validate(utxo, block)
                assert block.transactions[0].validate_mining_rewards(utxo, block)

                assert block.previous_hash == previous_block.hash()
                assert block.merkle_root == block.calculate_merkle_root()
                assert block.height == 1 + previous_block.height
                assert previous_block.timestamp < block.timestamp < time()
                assert block.hash(integer=True) < (2**224 / block.difficulty)

                if block.height % 2016 == 0:
                    time_difference = block.timestamp - previous_timestamp
                    previous_timestamp = previous_block.timestamp
                    assert difficulty == previous_block.difficulty * TWO_WEEKS / time_difference
                else:
                    assert block.difficulty == previous_block.difficulty

                previous_block = block

            return True
        except:
            return False

