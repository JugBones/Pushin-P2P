import socket
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
sock.bind(server_address)
loss_probability = 0.2

while True:
    data, address = sock.recvfrom(4096)
    if random.random() < loss_probability:
        print('Packet lost')
    else:
        print(f'Received {len(data)} bytes from {address}')
        sock.sendto(data, address)

