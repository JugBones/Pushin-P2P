from client import Client
from server import Server
import select
import json
from multiprocessing import Process
import time
import random

from transport_segment import TransportSegment, HandshakeMessage


class PeerToPeer:
    """A class that represents a node it can send and receive messages from other nodes."""

    def __init__(self, server_ip_address: str = "0.0.0.0", server_port: int = int(input("WELCOME TO THE PROGRAM\n" + 8*"-------" + "\nEnter the port number this peer will use: "))):
        # A class Client instance, use to send request to other nodes.
        self.__client = None

        # A class Server instance, use to listen to requests from other nodes.
        self.__server = Server(server_port, server_ip_address)

        # An instance of Process from multiprocessing module,
        # use to run server instance, so it can run simultaneously along with client instance.
        self.__server_process = Process(target=self.__server.start)

        self.__server_port = server_port

    def start(self):
        """
        Start the server instance, while also sends request if user input destination IP address, Port and message.
        """
        self.__server_process.start()

        # boolean to check if the program is still running
        is_started = True

        while is_started:
            # try:
            connection_established = False
            while not connection_established:
                print(8*"-------")
                destination_ip = input("Enter destination IP: ")
                destination_port = int(input("Enter destination port: "))

            # Three-way UDP handshake
                self.__client = Client()
                connection_established = self.__client.request_handshake(
                    destination_ip, destination_port)

            print(8*"-------")
            cmd = input(
                '\nEnter "get" or "post" command (or "exit" to quit): \n')

            # Get method
            if cmd == 'get':
                self.__client.get(destination_ip, destination_port)
                continue

            # Post method
            if cmd == 'post':
                self.__client.post(destination_ip, destination_port)
                continue

            elif cmd == 'exit':
                is_started = False
            else:
                print("INVALID STATEMENT!")
                continue

