import requests
import pathlib
from src.errors import UserError, GrinError


def read_secret_key(path=None):
    secret_path = path or pathlib.Path.home() / '.grin' / '.api_secret'
    if not secret_path.is_file():
        raise UserError(f'File not found: {secret_path}')
    with open(secret_path, 'r') as f:
        return f.read()


class GrinOwnerApi:

    def __init__(self, host='127.0.0.1:13420', username='grin', secret=''):
        self.host = host
        self.username = username
        self.secret = secret

    def request(self, endpoint, **kwargs):
        url = f'http://{self.host}/v1/wallet/owner/{endpoint}'
        try:
            r = requests.request(url=url, **kwargs, auth=(self.username, self.secret))
        except requests.exceptions.ConnectionError:
            raise UserError(f'Unable to connect to {url}, make sure there is an owner api listening (try: grin wallet owner_api)') from None
        if r.status_code == 200:
            if r.content:
                return r.json()
            else:
                return True
        raise GrinError(r.text)

    def create_tx(self, amount, confirmations=5, max_outputs=2, fluff=True):
        payload = {
            'amount': amount,
            'minimum_confirmations': confirmations,
            'method': 'file',
            'dest': '',
            'max_outputs': max_outputs,
            'num_change_outputs': 1,
            'selection_strategy_is_use_all': True,
            'fluff': fluff
        }
        print('Creating new transaction..')
        return self.request('issue_send_tx', method='POST', json=payload)

    def finalize(self, slate):
        print('Finalizing transaction..')
        return self.request('finalize_tx', method='POST', json=slate)

    def broadcast(self, tx, fluff=False):
        print('Broadcasting Transaction..')
        endpoint = 'post_tx?fluff' if fluff else 'post_tx'
        self.request(endpoint, method='POST', json=tx)

    def rollback(self, slate_id):
        print(f'Rolling back transaction {slate_id}')
        index = self.find_tx_index(slate_id)
        self.request('cancel_tx', method='POST', params={'id': index})

    def find_tx_index(self, slate_id):
        response = self.request('retrieve_txs', method='GET')
        txs = response[1]
        for tx in txs:
            if tx['tx_slate_id'] == slate_id:
                return tx['id']
        raise GrinError(f'Slate_id : {slate_id} not found')


class GrinForeignApi:

    def __init__(self, host='127.0.0.1:13415'):
        self.host = host

    def request(self, endpoint, **kwargs):
        url = f'http://{self.host}/v1/wallet/foreign/{endpoint}'
        try:
            r = requests.request(url=url, **kwargs)
        except requests.exceptions.ConnectionError:
            raise UserError(f'Unable to connect to {url}, make sure there is a wallet listening (try: grin wallet listen)')
        if r.status_code == 200:
            return r.json()
        raise GrinError(r.text)

    def receive(self, slate):
        print('Signing transaction..')
        return self.request('receive_tx', method='POST', json=slate)
