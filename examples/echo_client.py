import asyncio

from jetblack_datagram import open_udp_connection


async def main():
    client = await open_udp_connection(('127.0.0.1', 9999))

    print("Sending data")
    client.send(b'Hello, World!')
    print("reading data")
    data = await client.recv()
    print(f'Received {data!r}')

    print("closing client")
    client.close()
    print("waiting for client to close")
    await client.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
