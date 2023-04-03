from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
from time import time
import os

import psutil
from transport_segment import TransportSegment, HandshakeMessage, SegmentAckMessage, RequestMessage
# represent host address type Tuple[IP adress, port number]
address_type = Tuple[str, int]


class Client:
    """A class representing the client side of the connection."""

    def __init__(self, number_of_retries: int = 3, timeout: float = 1):
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
        self.__segments = []

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
        message = ""
        while self.__number_of_retries > 0:
            try:
                if message == "":
                    self.send(str(TransportSegment(
                        -1, HandshakeMessage.SYN)), ip_address, port)
                    self.__packet_sent += 1

                if message == HandshakeMessage.SYN_ACK.value:
                    self.send(str(TransportSegment(
                        -1, HandshakeMessage.ACK)), ip_address, port)
                    self.__packet_sent += 1
                    print(
                        f"Connection to {(ip_address, port)} established...")
                    return True

                data, _ = self.receive()

                ts = TransportSegment.read_json(data)

                if ts.verify_payload():
                    self.__number_of_retries = 3
                    self.__packet_received += 1

                    message = ts.get_data()

                # return False
            except Exception as e:
                print("Didn't receive response, retrying...")
                self.__number_of_retries -= 1

        print(f"Connection to {(ip_address, port)} failed!")
        return False

    def post(self, data: str, ip_address: str, port: int):
        chunks = TransportSegment.divide_data(
            self.__get_max_segment_size(), data) if (len(data.encode()) > self.__get_max_segment_size()) else [str(TransportSegment(1, data))]

        segment = 0

        while self.__number_of_retries > 0:
            self.send(chunks[segment], ip_address, port)
            try:
                message, _ = self.receive(self.__max_transmission_unit)
                ts = TransportSegment.read_json(message)
                if ts.verify_payload():
                    if ts.get_data() == SegmentAckMessage.ACK.value and segment < len(chunks) - 1:
                        segment += 1

                    elif ts.get_data == SegmentAckMessage.ACK.value and segment == len(chunks) - 1:
                        fin_message = TransportSegment(
                            0, SegmentAckMessage.FIN.value)
                        self.send(fin_message, ip_address, port)
                else:
                    self.__number_of_retries -= 1

            except Exception as e:
                self.__number_of_retries -= 1

            pass

        # for message in messages:
        #     while self.__number_of_retries > 0:
        #         self.send(message, ip_address, port)
        #         self.__packet_sent += 1
        #         d, address = self.receive(self.__max_transmission_unit)
        #         segment = TransportSegment.read_json(d)

        #         if segment.verify_payload():
        #             self.__number_of_retries = 3
        #             self.__packet_received += 1
        #             print(
        #                 f"Message received from {(ip_address, port)}: {segment.get_data()}")
        #             break

        # message, address = self.receive(self.__max_transmission_unit)
        # d = TransportSegment.read_json(message)
        # if d.get_data() == "Okay I received all segment":
        #     self.close()

    def get(self, ip_address: str, port: int):
        print("==========GET==========")
        query = input("What do you want ?: ")
        ts = TransportSegment(0, f"{RequestMessage.GET.value}{query}")
        self.send(str(ts), ip_address, port)

        get_in_process = True
        while get_in_process:
            message, address = self.receive()
            m = TransportSegment.read_json(message)

            if m == None:
                continue

            if m.verify_payload():
                self.__packet_received += 1
                if m.get_data() == SegmentAckMessage.NOT_FOUND.value:
                    print("File Does not exist!")
                    get_in_process = False

                elif m.get_data() != SegmentAckMessage.FIN.value:
                    print(f"Received Segment {m.get_segment_number()}...")
                    self.__segments.append(str(m))
                    ts = TransportSegment(
                        m.get_segment_number(), SegmentAckMessage.ACK.value)
                    print(f"Sending Ack Segment {m.get_segment_number()}...")
                    self.send(str(ts), ip_address, port)
                    self.__packet_sent += 1

                elif m.get_data() == SegmentAckMessage.FIN.value:
                    print("I received all segments...")
                    get_in_process = False
                    ts = TransportSegment(
                        m.get_segment_number(), SegmentAckMessage.FIN.value)
                    print(self.__segments)
                    s = TransportSegment.reassemble_data(self.__segments)
                    self.send(str(ts), ip_address, port)
                    self.__packet_sent += 1

                    dirname = os.path.dirname(__file__)
                    print(
                        f"Writing file to {os.path.join(dirname, 'get_files', query)}...")
                    with open(os.path.join(dirname, "get_files", query), "w") as f:
                        f.write(s)

        print("Closing socket...")
        self.close()
        return

        # receives 1024 bytes in socketserver

        # #boolean to check if the get process is still running

        # while get_in_process:
        #     timeout = 5
        #     data, addr = self.__client.receive()
        #     if data:
        #         file_name = data.decode().split(" ")[-1]
        #         print("File name:", file_name)

        #     # boolean to check if the data to get still exists in this process
        #     data_exists = True

        #     while data_exists:
        #         # file object uses fileno(), since on Windows, select.select won't work unless it has a fileno() method
        #         f = open("./get_files/" + file_name, 'rb')
        #         ready = select.select(
        #             [f.fileno()], [], [], timeout)
        #         if ready[0]:
        #             data, addr = self.__client.receive()
        #             received_file_name = "received_" + file_name
        #             with open(f"./received_files/" + received_file_name, "a") as f:
        #                 # writing to the new html file and decoding the data
        #                 f.write(f"{data.decode()}\n")
        #                 f.close()
        #                 print("HTML FILE GOT AND SENT!!!")
        #                 get_in_process = False
        #                 data_exists = False

        #         else:
        #             print("%s Finish!", file_name)
        #             f.close()
        #             get_in_process = False
        #             data_exists = False
        #         continue
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
        return (message.decode(), server_address)

    def close(self) -> Tuple[int, int]:
        """Closing the socket connection."""
        print(
            f"Packet sent = {self.__packet_sent}, Packet received = {self.__packet_received}")
        print(
            f"Packet Loss = {(abs(self.__packet_sent - self.__packet_received - 1) / (self.__packet_sent + self.__packet_received))*100}%")
        self.__socket.close()
