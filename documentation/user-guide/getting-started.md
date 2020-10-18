## Echo Server

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
