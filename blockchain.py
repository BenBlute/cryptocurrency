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

