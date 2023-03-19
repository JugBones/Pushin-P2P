from socket import AF_INET, SOCK_DGRAM, socket

address_type = tuple[str, int]


class Server:
    def __init__(self, port: int, ip_address: str = "0.0.0.0"):
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.__port = port
        self.__ip_address = ip_address

    def __receive(self, buffer_size: int = 1024) -> tuple[str, address_type]:
        message, client_address = self.__socket.recvfrom(buffer_size)
        return (message.decode(), client_address)

    def __send(self, data: str, client_address) -> None:
        self.__socket.sendto(data.encode(), client_address)

    def start(self):
        self.__socket.bind((self.__ip_address, self.__port))

        while True:
            message, client_address = self.__receive()
            print(f"Received from {client_address}: {message}")
            self.__send(message, client_address)

    def stop(self):
        self.__socket.close()
