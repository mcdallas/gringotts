import click
import sys
import json
import src.backends
from decimal import Decimal, getcontext, InvalidOperation
from src.grin import GrinOwnerApi, GrinForeignApi, read_secret_key
from src.errors import UserError, GrinError, BackEndError


backends = click.Choice([b.lower() for b in src.backends.__all__])
getcontext().prec = 9


def grins_to_nanogrins(ctx, param, value):
    """Handle floating point conversion"""
    try:
        value = Decimal(value)
        if value > 10**5:
            raise click.BadParameter('AMOUNT should be in GRINs')
        value = (value * 10 ** 9)
        if value.to_integral_value() != value:
            raise click.BadParameter('The smallest unit is 1 nanoGRIN or 10^-9 GRIN')
    except InvalidOperation:
        raise click.BadParameter(f'AMOUNT should be a number')
    return int(value)


@click.group()
@click.version_option()
def cli():
    """Sends or receives grins using the specified backend for communication.
    You need to have a grin node running and the selected backend installed"""
    pass


@cli.command()
@click.argument('amount', type=float, callback=grins_to_nanogrins)
@click.argument('recipient', type=str)
@click.option('--backend', '-b', default='keybase', type=backends, help='Which backend to use for communication')
@click.option('--ttl', '-t', default=60, help='Duration in seconds before transaction is reversed')
@click.option('--confirmations', '-c', default=5, help='Number of confirmations')
@click.option('--fluff', '-f', is_flag=True, help='Whether to fluff the transaction upon broadcasting')
@click.option('--outputs', '-o', default=2, help='Maximum outputs to use')
@click.option('--host', '-h', default='127.0.0.1:13420', help='The address that grin owner api is listening on')
@click.option('--username', '-u', default='grin', help='Grin owner api username')
@click.option('--secret', '-s', default='', help='Grin owner api secret')
def send(amount, recipient, backend, ttl, confirmations, fluff, outputs, host, username, secret):
    """Args: [AMOUNT in grins] [RECIPIENT]"""
    try:
        backend = getattr(src.backends, backend.title())()
        grin = GrinOwnerApi(host=host, username=username, secret=secret or read_secret_key())
        slate = grin.create_tx(amount=amount, confirmations=confirmations, fluff=fluff, max_outputs=outputs)
        slate_id = slate['id']
        backend.send_message(msg=json.dumps(slate), recipient=recipient, ttl=ttl)
    except (UserError, GrinError, BackEndError) as e:
        click.echo(e, err=True)
        sys.exit(1)
    try:
        reply = backend.poll(nseconds=ttl, sender=recipient)
        if not reply:
            grin.rollback(slate_id)
        else:
            click.echo(f'Recieved reply from {recipient}')
            tx = grin.finalize(reply)
            grin.broadcast(tx)
            click.echo(f'Transaction {slate_id} broadcasted')
    except Exception as e:
        grin.rollback(slate_id)
        click.echo(e, err=True)
        sys.exit(1)


@cli.command()
@click.argument('sender', type=str)
@click.option('--backend', '-b', default='keybase', type=backends, help='Which backend to use for communication')
@click.option('--host', '-h', default='127.0.0.1:13415', help='The address that grin foreign api is listening on')
def receive(sender, backend, host):
    """Args: [SENDER]"""
    wait = 300
    try:
        backend = getattr(src.backends, backend.title())()
        grin = GrinForeignApi(host=host)
        slate = backend.poll(wait, sender)
        if not slate:
            click.echo(f'Did not receive message from {sender} after {wait} seconds.')
        else:
            click.echo(f'Received slate from {sender}')
            tx = grin.receive(slate)
            click.echo(f'Returning signed slate to {sender}')
            backend.send_message(msg=json.dumps(tx), recipient=sender)
            click.echo('Done')
    except (GrinError, UserError, BackEndError) as e:
        click.echo(e, err=True)
        sys.exit(1)

