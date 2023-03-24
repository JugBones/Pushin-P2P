import psutil
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
import re
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
        mss = mtu - 40  #Subtract 20 bytes for IP header and 20 bytes for UDP header

        return mtu, mss

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
            
            try:

                #message is the data received, it contains the actual message, client_address is the address of the client in a tuple (ip, port)
                print(f"Connection from {client_address}")

                print(f"Received {len(message)} bytes from :\n{client_address}")

                #we need to decode the data to be able to read it as a string
                #can be read as "I want (this specific html file) easy syntax to read
                if message.startswith("I WANT"):
                    if message.split(" ")[-1] == "index.html":
                        f = open(r"index.html")
                        file_name = re.findall(r'[^\\]+(?=\.)', r"index.html")[0]
                        response = f.read(1024).encode()
                        f.close()

                    # elif message.split(" ")[-1] == "main.html":
                    #     response = "NOT HTTP/1.0 9000 OKAY!\nContent-Type: text/html\n\n<html><body><h1>This is main.html</h1></body></html>".encode()

                    # elif message.split(" ")[-1] == "sample.html":
                    #     f = open(r"sample.html")
                    #     file_name = re.findall(r'[^\\]+(?=\.)', r"sample.html")[0]
                    #     self.__socket.sendto(file_name.encode(), client_address)
                    #     response = f.read(1024).encode()
                    #     f.close()
        
                #makeshift post method to send data to the server
                elif message.startswith("PUTTING"):
                    #split the data into parts to get the body of the message
                    data_parts = message.split("\n")
                    #takes the last part of the message containing the message after the method (PUTTING !blahblahblah!)
                    data_body = data_parts[-1]

                    #write the data to a file to be read by the client
                    with open("requestdata.txt", "a") as f:
                        f.write(f"{data_body}\n")
                    #let the user know hey its ok ur safe ur file is with me now
                    print("JSON FILE POSTED AND PUTTED!!!")
                    response = "OK".encode()
                else:
                    #if the message is not a get or post method, it will be instead seen as p2p messaging
                    print(message.decode()) 
                    response = input("Enter response: ").encode()

                #send the response to the client 
                self.__socket.sendto(response, client_address)

            except Exception as e:
                print(f"Rejected because {e}")
            

    def close(self):
        """Closing the socket connection."""
        self.__socket.close()

