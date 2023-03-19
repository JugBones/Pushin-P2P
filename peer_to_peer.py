from client import Client
from server import Server
from multiprocessing import Process


class PeerToPeer:
    def __init__(self, server_ip_address: str = "0.0.0.0", server_port: int = 12000):
        self.__client = None
        self.__server = Server(server_port, server_ip_address)
        self.__server_process = Process(target=self.__server.start)

    def start(self):
        self.__server_process.start()

        while True:
            self.__client = Client()
            destination_ip = input("Enter destination IP: ")
            destination_port = input("Enter destination Port: ")
            message = input("Enter message: ")
            self.__client.send(message, destination_ip,
                               eval(destination_port))
            self.__client.receive()
            self.__client.close()
