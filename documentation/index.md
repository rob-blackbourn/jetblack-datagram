# UDP Datagram library

A Python 3.8+ asyncio helper library for UDP datagram clients and servers.

## Status

This is working, but still under continuous development, so there may be breaking changes.

## Overview

This package provides a simple asyncio API for UDP datagrams, following a
similar pattern to the TCP streams API.

A UDP server is started by calling `start_udp_server` which is
analogous to the
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

data, addr = await server.recvfrom()
print(f"Received {data!r} from {addr}")
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

client.send(b"Hello, World!")
data = await client.recv()
print(f"Received {data!r}")

client.close()
await client.wait_closed()
```

