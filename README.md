# jetblack-datagram

A Python 3 asyncio helper library for UDP datagram clients and servers.

## Status

This is working, but still under continuous development, so there may be breaking changes.

## Overview

This package provides a simple asyncio API for UDP datagrams, following a
similar pattern to the TCP streams API.

A UDP server is started by calling `start_udp_server` which is
analagous to the
[start_server](https://docs.python.org/3/library/asyncio-stream.html#asyncio.start_server)
function provided by `asyncio`.
This returns a `DatagramServer`, which provides methods for reading (`read`), writing (`sendto`),
and closing (`close` and `wait_closed`). This differs from the TCP variant which provides
a callback when a client connects with a read and write stream. This is because UDP is connection-less
so there is no connect (or disconnect) event. Also the data is sent and received in *packets*,
so there seems to eb no benefit to provide separate read and write stream.

The following creates a server, reads then writes some data.

```python
server = await start_udp_server(('0.0.0.0', 8000))

data, addr = await server.read()
print(f"Received {data} from {addr}")
server.sendto(b"Hello", addr)

server.close()
await server.wait_closed()
```

A UDP client is started by calling `open_udp_connection` which is analogous
to the
[open_connection](https://docs.python.org/3/library/asyncio-stream.html#asyncio.open_connection)
function provided by the `asyncio` library for TCP, which returns a `DatagramClient`. This provides similar functionality to the
server, however the `addr` is not present when reading or writing, as the socket is bound
to the server address when it is created.

```python
client = await open_udp_connection(('127.0.0.1', 8000))

client.send(b'Hello, World!')
data = await client.read()
print(f'Received {data}')

client.close()
await client.wait_closed()
```



## Installation

Install using pip.

```bash
pip install jetblack-datagram
```

## Getting Started

To create an echo server:

```python
import asyncio

from jetblack_datagram import start_udp_server


async def main():
    server = await start_udp_server(('127.0.0.1', 9999))

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

from jetblack_datagram import open_udp_connection


async def main():
    client = await open_udp_connection(('127.0.0.1', 9999))

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
* async wait_closed() -> None

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
async def start_udp_server(
        addr: Address,
        *,
        loop: Optional[AbstractEventLoop] = None,
        maxsize: int = 0
) -> DatagramServer:
```

For the client:

```python
async def open_udp_connection(
        addr: Address,
        *,
        loop: Optional[AbstractEventLoop] = None,
        maxsize: int = 0
) -> DatagramClient:
```
