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
from typing import Any, Optional, Tuple, Union, cast

Address = Tuple[str, int]


class DatagramClientProtocol(DatagramProtocol):
    """The datagram client protocol implementation"""

    def __init__(
            self,
            *,
            loop: Optional[AbstractEventLoop] = None,
            maxreadqueue: int = 0,
            buf: Optional[bytes] = None
    ) -> None:
        """Initialise the datagram client protocol implementation

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
        self._read_queue: "Queue[Tuple[bytes, Address]]" = Queue(
            maxreadqueue,
            loop=loop
        )
        if buf is not None:
            self._read_queue.put_nowait(buf)
        self._transport: Optional[DatagramTransport] = None
        self.close_waiter: "Future[bool]" = Future(loop=loop)
        self.error_waiter: "Future[Any]" = Future(loop=loop)

    def connection_made(self, transport: BaseTransport) -> None:
        self._transport = cast(DatagramTransport, transport)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.close_waiter.set_result(exc is None)
        if exc:
            self.close_waiter.set_exception(exc)

    def datagram_received(self, data: bytes, addr: Address) -> None:
        try:
            self._read_queue.put_nowait((data, addr))
        except asyncio.QueueFull as error:
            self.error_waiter.set_exception(error)

    def error_received(self, exc: Exception) -> None:
        self.error_waiter.set_exception(exc)

    @property
    def transport(self) -> DatagramTransport:
        """The underlying transport.

        Raises:
            ValueError: If the socket has not connected.

        Returns:
            DatagramTransport: The datagram transport.
        """
        if self._transport is None:
            raise ValueError('Not connected')
        return self._transport

    async def read(self) -> Tuple[bytes, Address]:
        """Read a datagram

        Raises:
            Exception: If an error has occurred.

        Returns:
            Tuple[bytes, Address]: THe message and address of the sender.
        """
        read_task = asyncio.create_task(self._read_queue.get())
        done, _ = await asyncio.wait(
            {self.error_waiter, read_task},
            return_when=asyncio.FIRST_COMPLETED
        )
        if self.error_waiter in done:
            read_task.cancel()
            try:
                await read_task
            except asyncio.CancelledError:
                pass
            raise self.error_waiter.exception() or Exception
        return read_task.result()


class DatagramClient:
    """The base class for datagram clients and servers"""

    def __init__(self, base: DatagramClientProtocol) -> None:
        """Initialise the datagram base class

        Args:
            base (DatagramProtocolImpl): The datagram protocol implementation.
        """
        self._base = base

    def close(self) -> None:
        """Close the connection
        """
        self._base.transport.close()

    async def wait_closed(self) -> None:
        """Wait until the connection is closed.

        Can be called after closing the connection.
        """
        await self._base.close_waiter

    def abort(self) -> None:
        """Close immediately without waiting for pending operations to complete.

        Any buffered data will be lost.
        """
        self._base.transport.abort()

    def send(self, data: bytes) -> None:
        """Send a datagram.

        Args:
            data (bytes): The data to send.
        """
        self._base.transport.sendto(data)

    async def recv(self) -> bytes:
        """Read a datagram

        Raises:
            Exception: If an error has occurred.

        Returns:
            bytes: THe message.
        """
        return await self._base.read()


async def open_udp_connection(
        addr: Address,
        *,
        loop: Optional[AbstractEventLoop] = None,
        maxreadqueue: int = 0
) -> DatagramClient:
    """Open a UDP connection.

    Args:
        addr (Address): The address of the server.
        loop (Optional[AbstractEventLoop], optional): THe asyncio event loop.
            Defaults to None.
        maxreadqueue (int, optional): The maximum size of the read queue. Defaults to
            0.

    Returns:
        DatagramClient: [description]
    """
    loop = loop if loop is not None else asyncio.get_running_loop()
    _, protocol = await loop.create_datagram_endpoint(
        lambda: DatagramClientProtocol(
            loop=loop,
            maxreadqueue=maxreadqueue
        ),
        remote_addr=addr)
    return DatagramClient(cast(DatagramClientProtocol, protocol))
