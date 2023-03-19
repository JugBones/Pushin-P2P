from socket import AF_INET, SOCK_DGRAM, socket


class Client:
    def __init__(self):
        self.__socket = socket(AF_INET, SOCK_DGRAM)

    def send(self, data: str, ip_address: str, port: int):
        self.__socket.sendto(data.encode(), (ip_address, port))

    def receive(self, buffer_size: int = 1024):
        message, server_address = self.__socket.recvfrom(buffer_size)
        print(f"Sending to {server_address}: {message.decode()}")

    def close(self):
        self.__socket.close()
