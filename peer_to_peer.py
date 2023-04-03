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

            # self.client.send("SYN", destination_ip, destination_port)
            # response, addr = self.client.receive()
            # if response == "SYN-ACK":
            #     self.client.send("ACK", destination_ip, destination_port)
            #     print("UDP Handshake complete!")
            # else:
            #     print("UDP Handshake failed!")
            #     continue

            print(8*"-------")
            cmd = input(
                '\nEnter "get" or "post" command (or "exit" to quit): \n')

            if cmd == 'get':
                self.__client.get(destination_ip, destination_port)
                continue
                # query = input("What do you want ?: ")
                # if random.random() < 0.2:
                #     print("YOU DROPPED A PACKET >:(")
                # else:
                #     self.__client.send(
                #         ("I WANT " + query), destination_ip, destination_port)

                # receives 1024 bytes in socketserver

                # #boolean to check if the get process is still running
                # get_in_process = True

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
            # Post method
            if cmd == 'post':
                print("==========POST==========")
                hd = input("Enter head of message: ")
                msg = input("Enter content of the message: ")
                payload = json.dumps({"head": hd, "message": msg})
                headers = '{"Content-Type":"application/json"}'
                # no need for decoding already decoded :)
                if random.random() < 0.2:
                    print("YOU DROPPED A PACKET >:(")
                else:
                    self.__client.send(
                        ("PUTTING" + " \n " + str(headers) + " \n " + str(payload)), destination_ip, destination_port)
                    continue

            elif cmd == 'exit':
                is_started = False
            else:
                print("INVALID STATEMENT!")
                continue

            # except Exception as e:
            #     print(e)
