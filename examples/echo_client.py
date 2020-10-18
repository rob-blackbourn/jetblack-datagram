import asyncio

from jetblack_datagram import create_datagram_client


async def main():
    client = await create_datagram_client(('127.0.0.1', 9999))

    print("Sending data")
    client.send(b'Hello, World!')
    print("reading data")
    data, addr = await client.read()
    print('Received %r from %s' % (data, addr))

    print("closing client")
    client.close()
    print("waiting for client to close")
    await client.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
