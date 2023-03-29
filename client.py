from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
from time import time

import psutil
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

        self.__max_transmission_unit, self.__max_segment_size = self.__get_mtu_and_mss()

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

    def __get_mtu_and_mss(interface_name):
        """
        Going to be used for determining the sliding window size.
        MTU = Maximum transmission unit
        MSS = Maximum segment size
        Should be used to determine maximum packet size that should be received when using recvfrom() function of sockets

        Args:
            interface_name(str): takes the name of the ip connection. You can get it by doing ifconfig or ipconfig.
            mine is "wlan0".

        Returns:
            MTU and MSS, usually 1500 and 1460 but depends on the connection
        """
        if_addrs = psutil.net_if_addrs()
        if_stats = psutil.net_if_stats()

        if interface_name not in if_addrs:
            raise ValueError(f"Interface '{interface_name}' not found")

        addrs = if_addrs[interface_name]
        stats = if_stats[interface_name]

        mtu = stats.mtu
        mss = mtu - 40  # Subtract 20 bytes for IP header and 20 bytes for UDP header

        return mtu, mss

    def request_handshake(self, ip_address: str, port: int) -> bool:
        try:
            message = ""
            while self.__number_of_retries > 0:
                if message == "":
                    print(
                        f"Sending Handshake request to {(ip_address, port)}...")
                    self.send(str(TransportSegment(
                        0, HandshakeMessage.SYN)), ip_address, port)

                if message == HandshakeMessage.SYN_ACK.value:
                    print(
                        f"Sending Acknowledgment to {(ip_address, port)}...")
                    self.send(str(TransportSegment(
                        0, HandshakeMessage.ACK)), ip_address, port)

                data, address = self.receive(self.__max_transmission_unit)

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

    def message(self, data: str, ip_address: str, port: int):
        pass

    def post(self, data: str, ip_address: str, port: int):
        messages = TransportSegment.divide_data(
            self.__max_segment_size, data) if (len(data.encode()) > self.__max_segment_size) else TransportSegment(1, data)

        for message in messages:
            while self.__number_of_retries > 0:
                self.send(message, ip_address, port)
                self.__packet_sent += 1
                d, address = self.receive(self.__max_transmission_unit)
                segment = TransportSegment.read_json(d)

                if segment.verify_payload():
                    self.__number_of_retries = 3
                    self.__packet_received += 1
                    print(
                        f"Message received from {(ip_address, port)}: {segment.get_data()}")
                    break

        message, address = self.receive(self.__max_transmission_unit)
        d = TransportSegment.read_json(message)
        if d.get_data() == "Okay I received all segment":
            self.close()

    def get(self, data: str, ip_address: str, port: int):
        pass

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
        print(
            f"Packet sent = {self.__packet_sent}, Packet received = {self.__packet_received}")
        print(
            f"Packet Loss = {self.__packet_received / (self.__packet_sent + self.__packet_received)}")
        self.__socket.close()
