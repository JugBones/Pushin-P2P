import psutil
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
import re
import os
import random
from time import time
import math

from transport_segment import TransportSegment, HandshakeMessage, RequestMessage, SegmentAckMessage

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

        self.__packet_sent = 0
        self.__packet_received = 0
        self.__number_of_retries = 3
        self.__segments = []

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

    def __get_max_segment_size(self):
        return self.__max_transmission_unit - 81

    def get_mtu_and_mss(interface_name):
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

    def __handle_get_request(self, message: str, client_address: address_type):
        print(f"message: {message}")
        if message.startswith("I WANT"):
            # getting and storing the file names into variables to create the paths
            file_name = message.split(" ")[-1]
            dirname = os.path.dirname(__file__)
            file_path = os.path.join(dirname, "get_files", file_name)

            # check if the requested file exists in the get_files folder
            is_existing = os.path.exists(file_path)
            if is_existing:
                f = open(file_path)
                response = f.read()
                f.close()

                segments = []

                if len(response.encode()) > 256:
                    segments = TransportSegment.divide_data(
                        256, response)

                else:
                    segments = [str(TransportSegment(1, response))]

                index = 0
                while self.__number_of_retries > 0:
                    print(f"Sending segment {index}...")
                    self.__send(segments[index],
                                client_address[0], client_address[1])
                    self.__packet_sent += 1

                    try:
                        self.__socket.settimeout(1)
                        message, _ = self.__receive(1024)
                        ts = TransportSegment.read_json(message)

                        if ts.verify_payload():
                            self.__packet_received += 1
                            print(
                                f"Received Ack Segment {ts.get_segment_number() - 1}...")
                            if index < len(segments) - 1:
                                index = ts.get_segment_number()
                            else:
                                print("All the packet have been sent...")
                                fin_message = TransportSegment(
                                    index + 1, SegmentAckMessage.FIN.value)
                                self.__send(
                                    str(fin_message), client_address[0], client_address[1])
                                self.__packet_sent += 1
                                break
                        else:
                            print("Checksum do not match, ignoring message...")

                    except Exception as e:
                        print(e.__cause__)
                        self.__number_of_retries -= 1

            else:
                print("FILE DOES NOT EXIST! >:(")
                response = TransportSegment(
                    1, SegmentAckMessage.NOT_FOUND.value)
                self.__send(str(response),
                            client_address[0], client_address[1])
                self.__packet_sent += 1

        print(f"Disconnect from {client_address}...")
        print(
            f"Packet Sent: {self.__packet_sent}, Packet Received: {self.__packet_received}")
        print(
            f"Packet Loss: {(abs(self.__packet_sent + 1 - self.__packet_received)/(self.__packet_sent + self.__packet_received))*100}%")
        self.__packet_sent = 0
        self.__packet_received = 0
        self.__socket.settimeout(None)

    def __handle_post_request(self, message: str, client_address: address_type):
        print(f"message: {message}")
        if message.startswith("PUTTING"):
            file_name = message.split(" ")[-1]
            dirname = os.path.dirname(__file__)
            file_path = os.path.join(dirname, "posted_files", file_name)

            response = message

            segments = []

            if len(response.encode()) > 256:
                    segments = TransportSegment.divide_data(
                        256, response)

            else:
                segments = [str(TransportSegment(1, response))]

                index = 0
                while self.__number_of_retries > 0:
                    print(f"Sending segment {index}...")
                    self.__send(segments[index],
                                client_address[0], client_address[1])
                    self.__packet_sent += 1

                    try:
                        self.__socket.settimeout(1)
                        message, _ = self.__receive(1024)
                        ts = TransportSegment.read_json(message)

                        if ts.verify_payload():
                            self.__packet_received += 1
                            print(
                                f"Received Ack Segment {ts.get_segment_number() - 1}...")
                            if index < len(segments) - 1:
                                index = ts.get_segment_number()
                            else:
                                print("All the packet have been sent...")
                                fin_message = TransportSegment(
                                    index + 1, SegmentAckMessage.FIN.value)
                                self.__send(
                                    str(fin_message), client_address[0], client_address[1])
                                break
                        else:
                            print("Checksum do not match, ignoring message...")

                    except Exception as e:
                        print(e.__cause__)
                        self.__number_of_retries -= 1

        print(f"Disconnect from {client_address}...")
        print(
            f"Packet Sent: {self.__packet_sent}, Packet Received: {self.__packet_received}")
        print(
            f"Packet Loss: {(abs(self.__packet_sent + 1 - self.__packet_received)/(self.__packet_sent + self.__packet_received))*100}%")
        self.__packet_sent = 0
        self.__packet_received = 0
        self.__socket.settimeout(None)

    def start(self):
        """
        Start the server by binding to the socket with the given IP address and port,
        and start listening for incoming request on the socket. Also send back responses.
        """
        self.__socket.bind((self.__ip_address, self.__port))

        while True:

            data, client_address = self.__receive()

            ts = TransportSegment.read_json(data)

            if ts.verify_payload():
                self.__packet_received += 1
                message = ts.get_data()
                print(f"Received from {client_address}: {message}")

                if message == HandshakeMessage.SYN.value:
                    self.__send(str(
                        TransportSegment(-1, HandshakeMessage.SYN_ACK)), client_address[0], client_address[1])
                    self.__packet_sent += 1
                    continue

                elif message == HandshakeMessage.ACK.value:
                    print(
                        f"Connection to {client_address} established...")

                    continue

                elif ts.get_segment_number() == 0:
                    if ts.get_data().startswith(RequestMessage.GET.value):
                        self.__handle_get_request(
                            ts.get_data(), client_address)

                    if ts.get_data().startswith(RequestMessage.POST.value):
                        self.__handle_post_request(
                            ts.get_data(), client_address)

    def close(self):
        """Closing the socket connection."""
        self.__socket.close()
