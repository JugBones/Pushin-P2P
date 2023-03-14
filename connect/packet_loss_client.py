import socket
import time
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
loss_probability = 0.2
message = 'Hello, server!'
print(f'Sending message: "{message}"')
for i in range(100000):
    if random.random() < loss_probability:
        print(f'Packet {i} lost')
    else:
        sock.sendto(message.encode(), server_address)
        print(f'Sent packet {i}')
        
    time.sleep(1)
sock.close()
