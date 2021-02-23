from sys import argv
from flask import Flask, jsonify, request
import requests
from threading import Thread

from crypto import generate_key, import_key, export_key
from blockchain import Blockchain
from block import Block
from transaction import Transaction


DEBUG = 'debug' in argv
MINE = 'mine' in argv

app = Flask(__name__)


### Wallet ###


key = import_key('private_key.pem')
if key is None:
    key = generate_key()

export_key(key, 'private_key.pem')
export_key(key.public_key(), 'public_key.pem')


### Node Discovery ###


with open('seed_nodes', 'r') as f:
    seed_nodes = f.readlines()
seed_nodes = [s.strip() for s in seed_nodes]
seed_nodes = [s for s in seed_nodes if s != '' and s[0] != '#']

nodes = set(seed_nodes)
checked_nodes = set()

while len(checked_nodes) < len(nodes) < 100:
    node = (nodes - checked_nodes).pop()

    try:
        url = f'http://{node}/nodes'
        new_nodes = requests.get(url).json()

        for new_node in new_nodes:
            url = f'http://{new_node}/send_node'
            if requests.post(url).status_code == requests.codes.ok:
                nodes.add(new_node)
    except:
        pass

    checked_nodes.add(node)

nodes = list(nodes)


@app.route('/nodes', methods=['GET'])
def nodes_endpoint():
    return jsonify(nodes)


@app.route('/send_node', methods=['POST'])
def send_node_endpoint():
    if len(nodes) >= 100:
        nodes.pop(0)
    nodes.append(request.remote_addr)


### Blockchain ###


blockchain = Blockchain.create()
utxo = {}

for node in nodes:
    try:
        url = f'http://{node}/blockchain'
        new_blockchain_json = requests.get(url).json()
        new_blockchain = Blockchain.from_json(new_blockchain_json)
        new_utxo = {}
        if len(new_blockchain) > len(blockchain) and new_blockchain.validate(new_utxo):
            blockchain = new_blockchain
            utxo = new_utxo
    except:
        pass


def new_block():
    last_block = blockchain.last_block()

    previous_hash = last_block.hash()
    height = last_block.height + 1
    difficulty = last_block.difficulty

    if height % 2016 == 0:
        TWO_WEEKS = 60 * 60 * 24 * 7 * 2
        time_difference = previous_block.timestamp - blockchain.blocks[-2016].timestamp
        difficulty *= TWO_WEEKS / time_difference

    return Block.create(key, previous_hash, difficulty, height)


block = new_block()


@app.route('/send_blockchain', methods=['POST'])
def send_blockchain_endpoint():
    global blockchain
    global utxo

    new_blockchain_json = request.json
    new_blockchain = Blockchain.from_json(new_blockchain_json)
    new_utxo = {}

    if len(new_blockchain) > len(blockchain) and new_blockchain.validate(new_utxo):
        blockchain = new_blockchain
        utxo = new_utxo
        block.reset_transactions(utxo)

        for node in nodes:
            url = f'http://{node}/send_blockchain'
            requests.post(url, json=new_blockchain_json)


@app.route('/blockchain', methods=['GET'])
def blockchain_endpoint():
    return jsonify(blockchain.to_json())


### Transactions ###


@app.route('/send_transaction', methods=['POST'])
def send_transaction_endpoint():
    transaction_json = request.json
    transaction = Transaction.from_json(transaction_json)

    if transaction.validate():
        block.add_transactions([transaction])

        for node in nodes:
            url = f'http://{node}/send_transaction'
            requests.post(url, json=transaction_json)


### Mining ###


if MINE:
    def mining_thread():
        while True:
            global block

            block.mine()
            blockchain.add_block(block)
            block = new_block()

            blockchain_json = blockchain.to_json()
            for node in nodes:
                url = f'http://{node}/send_blockchain'
                requests.post(url, json=blockchain_json)

    Thread(target=mining_thread).start()


app.run(debug=DEBUG)

