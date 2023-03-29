from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
from time import time
from transport_segment import TransportSegment, HandshakeMessage
# represent host address type Tuple[IP adress, port number]
address_type = Tuple[str, int]


class Client:
    """A class representing the client side of the connection."""

    def __init__(self, number_of_retries: int = 3, timeout: float = 5):
        """A class that represents the client side of the connection

        Args:
            timeout (float, optional): set the timeout for the connection. Defaults to 5 (seconds).
        """
        # A socket object that use UDP over IPv4
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.__socket.settimeout(timeout)
        self.__number_of_retries = number_of_retries
        self.__packet_sent = 0
        self.__packet_received = 0

    def send(self, data: str, ip_address: str, port: int) -> None:
        """
        Send a request to the server.

        This function does not return anything.

        Args:
            data (str): The data to send to the server.
            ip_address (str): The IP address of the server.
            port (int): The port number of the server.
        """
        print(f"Sending to ({ip_address}, {port}): {data}")
        self.__socket.sendto(data.encode(), (ip_address, port))

    def request_handshake(self, ip_address: str, port: int) -> bool:
        seq_number = 1

        is_corrupted = False

        try:
            message = ""
            while self.__number_of_retries > 0:
                if message == "":
                    print(
                        f"Sending Handshake request to {(ip_address, port)}...")
                    self.send(str(TransportSegment(
                        seq_number, HandshakeMessage.SYN)), ip_address, port)

                if message == HandshakeMessage.SYN_ACK.value:
                    print(
                        f"Sending Acknowledgment to {(ip_address, port)}...")
                    self.send(str(TransportSegment(
                        seq_number, HandshakeMessage.ACK)), ip_address, port)

                data, address = self.receive()

                ts = TransportSegment.read_json(data)

                if ts.verify_payload():
                    self.__number_of_retries = 3
                    message = ts.get_data()
                    print(f"Connection to {(ip_address, port)} established...")
                    return True

                self.__number_of_retries -= 1

        except Exception as e:
            print(f"UDP Handshake failed! {e}")
            return False

    def receive(self, buffer_size: int = 1024) -> Tuple[str, address_type]:
        """
        Receive a response from the server.

        Args:
            buffer_size (int): the amount of maximum bytes to be received.

        Returns:
            Tuple[str, address_type]: Payload from the server including the server IP address and port number.
        """
        message, server_address = self.__socket.recvfrom(buffer_size)
        print(f"Received from {server_address}: {message.decode()}")
        return (message.decode(), server_address)

    def close(self) -> Tuple[int, int]:
        """Closing the socket connection."""
        self.__socket.close()
