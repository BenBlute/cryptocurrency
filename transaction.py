from time import time

from crypto import sha256, key_to_string, string_to_key, sign_message, validate_signature


class Transaction:

    @classmethod
    def create(cls, inputs, outputs):
        obj = cls()

        obj.inputs = inputs
        obj.outputs = outputs
        obj.timestamp = time()

        return obj

    @classmethod
    def create_mining_rewards(cls, key):
        obj = cls()

        obj.inputs = [Input.create_mining_rewards(key)]
        obj.outputs = [Output.create_mining_rewards(key)]
        obj.timestamp = time()

        return obj

    @classmethod
    def from_json(cls, json):
        obj = cls()

        obj.inputs = [Input.from_json(i) for i in json['inputs']]
        obj.outputs = [Output.from_json(o) for o in json['outputs']]
        obj.timestamp = json['timestamp']

        return obj

    def to_json(self):
        return {
            'inputs': [i.to_json() for i in self.inputs],
            'outputs': [o.to_json() for o in self.outputs],
            'timestamp': self.timestamp
        }

    def hash(self):
        string = ''
        for i in self.inputs:
            string += i.hash()
        for o in self.outputs:
            string += o.hash()
        string += str(self.timestamp)

        return sha256(string)

    def __eq__(self, other):
        return self.hash() == other.hash()

    def validate(self, utxo, block):
        unmodified_utxo = utxo.copy()
        try:
            sum_inputs = 0
            for input_ in self.inputs:
                utxo_id = input_.block_hash + input_.transaction_hash + input_.output_hash
                sum_inputs += utxo[utxo_id].amount
                key = string_to_key(utxo[utxo_id].recipient)
                del utxo[utxo_id]
                assert validate_signature(key, utxo_id, input_.signature)

            sum_outputs = 0
            for output in self.outputs:
                sum_outputs += output.amount
                utxo_id = block.hash() + self.hash() + output.hash()
                utxo[utxo_id] = output
                string_to_key(output.recipient)
                assert output.amount >= 0

            block.fees += sum_inputs - sum_outputs

            assert sum_inputs >= sum_outputs
            assert self.timestamp < time()


            return True
        except:
            utxo.clear()
            utxo.update(unmodified_utxo)
            return False

    def validate_mining_rewards(self, utxo, block):
        try:
            assert len(self.inputs) == 1
            assert len(self.outputs) == 1
            assert self.timestamp < time()

            input_ = self.inputs[0]
            output = self.outputs[0]

            assert input_.block_hash == ''
            assert input_.transaction_hash == ''
            assert input_.output_hash == ''

            key = string_to_key(output.recipient)

            assert validate_signature(key, '', input_.signature)

            assert output.amount == 1 + block.fees

            utxo_id = block.hash() + self.hash() + output.hash()
            utxo[utxo_id] = output

            return True
        except:
            return False

class Input:

    @classmethod
    def create(cls, key, block_hash, transaction_hash, output_hash):
        obj = cls()

        obj.block_hash = block_hash
        obj.transaction_hash = transaction_hash
        obj.output_hash = output_hash

        string = obj.block_hash
        string += obj.transaction_hash
        string += obj.output_hash

        obj.signature = sign_message(key, string)

        return obj

    @classmethod
    def create_mining_rewards(cls, key):
        obj = cls()

        obj.block_hash = ''
        obj.transaction_hash = ''
        obj.output_hash = ''

        obj.signature = sign_message(key, '')

        return obj

    @classmethod
    def from_json(cls, json):
        obj = cls()

        obj.block_hash = json['block_hash']
        obj.transaction_hash = json['transaction_hash']
        obj.output_hash = json['output_hash']
        obj.signature = json['signature']

        return obj

    def to_json(self):
        return {
            'block_hash': self.block_hash,
            'transaction_hash': self.transaction_hash,
            'output_hash': self.output_hash,
            'signature': self.signature
        }

    def hash(self):
        string = self.block_hash
        string += self.transaction_hash
        string += self.output_hash
        string += self.signature

        return sha256(string)


class Output:

    @classmethod
    def create(cls, recipient, amount):
        obj = cls()

        obj.recipient = recipient
        obj.amount = amount

        return obj

    @classmethod
    def create_mining_rewards(cls, key):
        obj = cls()

        obj.recipient = key_to_string(key.public_key())
        obj.amount = 1

        return obj

    @classmethod
    def from_json(cls, json):
        obj = cls()

        obj.recipient = json['recipient']
        obj.amount = json['amount']

        return obj

    def to_json(self):
        return {
            'recipient': self.recipient,
            'amount': self.amount
        }

    def hash(self):
        string = self.recipient
        string += str(self.amount)

        return sha256(string)

