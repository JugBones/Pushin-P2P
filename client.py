from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
# represent host address type Tuple[IP adress, port number]
address_type = Tuple[str, int]


class Client:
    """A class representing the client side of the connection."""

    def __init__(self):
        # A socket object that use UDP over IPv4
        self.__socket = socket(AF_INET, SOCK_DGRAM)

    def send(self, data: str, ip_address: str, port: int) -> None:
        """
        Send a request to the server.

        This function does not return anything.

        Args:
            data (str): The data to send to the server.
            ip_address (str): The IP address of the server.
            port (int): The port number of the server.
        """
        self.__socket.sendto(data.encode(), (ip_address, port))

    def receive(self, buffer_size: int = 1024) -> Tuple[str, address_type]:
        """
        Receive a response from the server.

        Args:
            buffer_size (int): the amount of maximum bytes to be received.

        Returns:
            Tuple[str, address_type]: Payload from the server including the server IP address and port number.
        """
        message, server_address = self.__socket.recvfrom(buffer_size)
        print(f"Sending to {server_address}: {message.decode()}")
        return (message, server_address)

    def close(self):
        """Closing the socket connection."""
        self.__socket.close()
