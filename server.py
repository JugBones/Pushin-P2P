from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
# represent host address type Tuple[IP adress, port number]
address_type = Tuple[str, int]


class Server:
    """A class representing the server side of the connection."""

    def __init__(self, port: int, ip_address: str = "127.0.0.1"):
        # A socket object that use UDP over IPv4
        self.__socket = socket(AF_INET, SOCK_DGRAM)

        # Port number that will be used for the connection.
        self.__port = port

        # IP address that will be used for the connection.
        # The default is "127.0.0.1" (a loopback address also known as localhost).
        self.__ip_address = ip_address

    def __receive(self, buffer_size: int = 1024) -> Tuple[str, address_type]:
        """
        Receive a response from the client.

        Args:
            buffer_size (int): the amount of maximum bytes to be received.

        Returns:
            Tuple[str, address_type]: Payload from the server including the server IP address and port number.
        """
        message, client_address = self.__socket.recvfrom(buffer_size)
        return (message.decode(), client_address)

    def __send(self, data: str, ip_address: str, port: int) -> None:
        """
        Send a response to the client.

        This function does not return anything.

        Args:
            data (str): The data to send to the client.
            ip_address (str): The IP address of the client.
            port (int): The port number of the client.
        """
        self.__socket.sendto(data.encode(), (ip_address, port))

    def start(self):
        """
        Start the server by binding to the socket with the given IP address and port,
        and start listening for incoming request on the socket. Also send back responses.
        """
        self.__socket.bind((self.__ip_address, self.__port))

        while True:
            message, client_address = self.__receive()
            print(f"Received from {client_address}: {message}")
            self.__send(message, client_address[0], client_address[1])

    def close(self):
        """Closing the socket connection."""
        self.__socket.close()
