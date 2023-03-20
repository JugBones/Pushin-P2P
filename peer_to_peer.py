from client import Client
from server import Server
from multiprocessing import Process


class PeerToPeer:
    """A class that represents a node it can send and receive messages from other nodes."""

    def __init__(self, server_ip_address: str = "0.0.0.0", server_port: int = 12000):
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
        
        while True:
            self.__client = Client()
            destination_ip = input("Enter destination IP: ")
            message = input("Enter message: ")
            self.__client.send(message, destination_ip,
                               int(self.__server_port))
            self.__client.receive()
            self.__client.close()
