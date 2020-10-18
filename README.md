# jetblack-datagram

A Python 3 asyncio helper library for UDP datagram clients and servers.

## Installation

Install using pip.

```bash
pip install jetblack-datagram
```

## Getting Started

To create an echo server:

```python
import asyncio

from jetblack_datagram import create_datagram_server


async def main():
    server = await create_datagram_server(('127.0.0.1', 9999))

    count = 0
    while count < 5:
        count += 1
        print("Reading")
        data, addr = await server.read()
        print('Received %r from %s' % (data, addr))
        print('Send %r to %s' % (data, addr))
        server.sendto(data, addr)

    print("Closing")
    server.close()
    print("Waiting for server to close")
    await server.wait_closed()
    print("Closed")

    print("Done")

if __name__ == '__main__':
    asyncio.run(main())
```

To create an echo client:

```python
import asyncio

from jetblack_datagram import create_datagram_client


async def main():
    client = await create_datagram_client(('127.0.0.1', 9999))

    print("Sending data")
    client.send(b'Hello, World!')
    print("reading data")
    data = await client.read()
    print(f'Received {data!r}')

    print("closing client")
    client.close()
    print("waiting for client to close")
    await client.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
```

## Usage

The UDP protocol is connection-less, so unlike TCP it makes
no sense to provide a reader for each server connection, or to
provide a callback for connections.

### Common

The following methods are common for both clients and servers.

* close() -> None
* async wait_closed() -None

### Server

The following methods are specific to the server.

* sendto(data: bytes, addr: Union[Address, str]) -> None
* async read() -> Tuple[bytes, Address]

### Client

The following methods are specific to the client.

* send(data: bytes) -> None
* async read() -> bytes

### Helpers

There is a helper to create the server and the client.

For the server:

```python
async def create_datagram_server(
        addr: Address,
        *,
        loop: Optional[AbstractEventLoop] = None,
        maxsize: int = 0
) -> DatagramServer:
```

For the client:

```python
async def create_datagram_client(
        addr: Address,
        *,
        loop: Optional[AbstractEventLoop] = None,
        maxsize: int = 0
) -> DatagramClient:
```
