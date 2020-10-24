"""Datagram support"""

import asyncio
from asyncio import (
    DatagramProtocol,
    Future,
    DatagramTransport,
    BaseTransport,
    Queue,
    AbstractEventLoop
)
import socket
from typing import Any, Dict, Optional, Set, Tuple, Union, cast

from .client import DatagramClientProtocol, DatagramClient

Address = Tuple[str, int]


class DatagramServerProtocol(DatagramProtocol):
    """The datagram server protocol implementation"""

    def __init__(
            self,
            *,
            loop: Optional[AbstractEventLoop] = None,
            backlog: int = 10,
            maxreadqueue: int = 0
    ) -> None:
        """Initialise the datagram server protocol implementation

        Args:
            loop (Optional[AbstractEventLoop], optional): The event loop.
                Defaults to None.
            maxreadqueue (int, optional): The maximum size of the read
                queue. Defaults to 0.

        Attributes:
            close_waiter: (Future[bool]): A future that gets set when the
                connection is closed.
            error_waiter: (Future[Any]): A future that gets set when there is an
                error.
        """
        self._connection_queue: "Queue[Tuple[socket.socket,bytes]]" = Queue(
            backlog,
            loop=loop
        )
        self.loop = loop
        self.maxreadqueue = maxreadqueue
        self._transport: Optional[DatagramTransport] = None
        self._local_addr: Optional[Address] = None
        self.close_waiter: "Future[bool]" = Future(loop=loop)
        self.error_waiter: "Future[Any]" = Future(loop=loop)
        self._clients: Dict[Address, socket.socket] = {}

    def connection_made(self, transport: BaseTransport) -> None:
        extra_info = transport.get_extra_info('socket')
        self._local_addr = extra_info.getsockname()
        self._transport = cast(DatagramTransport, transport)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.close_waiter.set_result(exc is None)
        if exc:
            self.close_waiter.set_exception(exc)

    def datagram_received(self, data: bytes, addr: Address) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self._local_addr)
        sock.connect(addr)
        self._connection_queue.put_nowait((sock, data))

    def error_received(self, exc: Exception) -> None:
        self.error_waiter.set_exception(exc)

    async def accept(self) -> DatagramClient:
        sock, buf = await self._connection_queue.get()
        _, protocol = await self.loop.create_datagram_endpoint(
            lambda: DatagramClientProtocol(
                loop=self.loop,
                maxreadqueue=self.maxreadqueue,
                buf=buf
            ),
            sock=sock
        )
        return DatagramClient(cast(DatagramClientProtocol, protocol))


class DatagramServer:
    """The datagram server"""

    def __init__(self, protocol: DatagramServerProtocol) -> None:
        """Initialise the datagram server.

        Args:
            base (DatagramServerProtocol): The datagram server protocol
                implementation.
        """
        self._protocol = protocol

    def close(self) -> None:
        """Close the connection
        """
        self._protocol.transport.close()

    async def wait_closed(self) -> None:
        """Wait until the connection is closed.

        Can be called after closing the connection.
        """
        await self._protocol.close_waiter

    def abort(self) -> None:
        """Close immediately without waiting for pending operations to complete.

        Any buffered data will be lost.
        """
        self._protocol.transport.abort()

    async def accept(self) -> DatagramClient:
        return await self._protocol.accept()


async def start_udp_server(
        addr: Address,
        *,
        loop: Optional[AbstractEventLoop] = None,
        maxreadqueue: int = 0
) -> DatagramServer:
    """Start a UDP server.

    Args:
        addr (Address): The address of the server
        loop (Optional[AbstractEventLoop], optional): The asyncio event loop.
            Defaults to None.
        maxreadqueue (int, optional): The maximum size of the read queue. Defaults to
            0.

    Returns:
        DatagramServer: A datagram server.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    loop = loop if loop is not None else asyncio.get_running_loop()
    _, protocol = await loop.create_datagram_endpoint(
        lambda: DatagramServerProtocol(
            loop=loop,
            maxreadqueue=maxreadqueue,
            backlog=10
        ),
        sock=sock
    )
    return DatagramServer(cast(DatagramServerProtocol, protocol))
