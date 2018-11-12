import json
import shutil
from time import time, sleep
from subprocess import PIPE, run

from .errors import ApiError, UserError

__all__ = ['Keybase']


class Backend:

    def send_message(self, msg, sender):
        raise NotImplementedError

    def receive_message(self, recipient):
        raise NotImplementedError

    def exists(self):
        raise NotImplementedError


def is_slate(blob):
    try:
        slate = json.loads(blob)
    except json.decoder.JSONDecodeError:
        return False
    if not isinstance(slate, dict):
        return False
    return all(key in slate for key in ('num_participants', 'id', 'tx'))


class Keybase(Backend):

    def __init__(self):
        self.exists()

    def exists(self):
        if not shutil.which('keybase'):
            raise UserError('Keybase executable not found. Make sure it is installed and in your PATH.')

    def api_send(self, payload):
        proc = run(['keybase', 'chat', 'api', '-m', json.dumps(payload)], stdout=PIPE, stderr=PIPE)

        if proc.stderr:
            raise ApiError(proc.stderr)

        try:
            response = json.loads(proc.stdout)
        except json.decoder.JSONDecodeError:
            raise ApiError('Bad response')
        return response

    def send_message(self, msg, recipient, ttl='1m'):
        if isinstance(ttl, (int, float)):
            ttl = f"{int(ttl)}s"
        proc = run(['keybase', 'chat', 'send', '--exploding-lifetime', ttl, '--topic-type', 'dev', recipient, msg], stdout=PIPE, stderr=PIPE)
        return not proc.returncode

    def receive_message(self, sender):
        payload = {"method": "read", "params": {"options": {"channel": {"name": sender, 'topic_type': 'dev'}}, 'unread_only': True, 'peek': False}}
        response = self.api_send(payload)
        messages = response['result']['messages']

        unread = [m for m in messages if m['msg']['content']['type'] == 'text' and m['msg'].get('unread') is True]

        return unread

    def poll(self, nseconds, sender):
        print(f'Waiting for message from {sender}..')
        start = time()
        while time() - start < nseconds:
            messages = self.receive_message(sender)
            for msg in messages:
                body = msg['msg']['content']['text']['body']
                if is_slate(body):
                    return json.loads(body)
            sleep(1)

