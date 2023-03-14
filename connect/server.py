import socket
import os

# set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a public host and a well-known port
server_address = ('localhost', 5000)
server_socket.bind(server_address)

# listen for incoming connections
server_socket.listen(1)
print(f"Server listening on {server_address[0]}:{server_address[1]}")

while True:
    print("Listening")
    connection, client_address = server_socket.accept()

    try:
        print(f"Connection from {client_address}")

        data = connection.recv(1024)
        print(f"Received {len(data)} bytes from :\n{data.decode()}")

        # check if get or post
        if data.decode().startswith("GET"):
            #return html
            response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body><h1>Hello, World!</h1></body></html>".encode()
        elif data.decode().startswith("POST"):
            # extraction
            data_parts = data.decode().split("\r\n")
            data_body = data_parts[-1]

            with open("requestdata.txt", "a") as f:
                f.write(f"{data_body}\n")

            response = "OK"
        else:
            response = "rejected fsr"

        # send to client
        connection.sendall(response)

    finally:
        #stop
        connection.close()

