# Gringotts: The Grin Wizard Bank

Gringotts is a CLI app that you can use to send and receive grins instantly using one of the available backends for communication.

# How to use

Sender types `gringotts send <amount> <recipient>`

Receiver types `gringotts receive <sender>`

Gringotts then will create a slate using the grin api, send it to the receiver for signing and send it back to the sender to finalize and broadcast the transaction. If an error occures or `ttl` seconds pass without response, the transaction will be rolled back automatically.

# What do I need?

Install Gringotts:

`pip install --upgrade git+https://github.com/mcdallas/gringotts`

One of the available backends for communication (only keybase supported for now)
https://keybase.io/download

If you are sending, a grin owner api listening to the specified address (`grin wallet owner_api` to initialize, default is `127.0.0.1:13420`)

If you are receiving, a grin foreign api listening to the specified address (`grin wallet listen` to initialize, default is `127.0.0.1:13415`)


# Backends

## Keybase

Keybase offers an end-to-end encrypted messaging service which is used to exchange slates. All messages are encrypted, signed and self-destructed after `ttl` seconds.


# TODO

- Add more backends
- Async send/receive