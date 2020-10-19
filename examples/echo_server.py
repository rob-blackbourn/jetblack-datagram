import asyncio

from jetblack_datagram import start_udp_server


async def main():
    print("Starting UDP server")

    server = await start_udp_server(('0.0.0.0', 9999))
    print("Server created")

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
