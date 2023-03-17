import socket
import os

#udp socket
UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#address of server
#your own ip address and port of choice
ip = input("Enter ip address of server: ")
port = int(input("Enter port number of server: "))
server_address = (str(ip), port)
UDPServerSocket.bind(server_address)
print(f"Listening on {ip} port {port}")

#server loop to receive data
while True:
    #receive data from client max at 1024 bytes because of the buffer size of the socket 
    data = UDPServerSocket.recvfrom(1024)

    try:
        #data[0] is the data received, it contains the actual message, data[1] is the address of the client in a tuple (ip, port)
        print(f"Connection from {data[1]}")

        print(f"Received {len(data)} bytes from :\n{data[1]}")

        #we need to decode the data to be able to read it as a string
        #can be read as "I want (this specific html file) easy syntax to read"
        if data[0].decode().startswith("I WANT"):
            if data[0].decode().split(" ")[-1] == "index.html":
                response = "NOT HTTP/1.0 9000 OKAY!\nContent-Type: text/html\n\n<html><body><h1>This is Index.html</h1></body></html>".encode()

            elif data[0].decode().split(" ")[-1] == "main.html":
                response = "NOT HTTP/1.0 9000 OKAY!\nContent-Type: text/html\n\n<html><body><h1>This is main.html</h1></body></html>".encode()
        
        #makeshift post method to send data to the server
        elif data[0].decode().startswith("PUTTING"):
            #split the data into parts to get the body of the message
            data_parts = data[0].decode().split("\n")
            #takes the last part of the message containing the message after the method (PUTTING !blahblahblah!)
            data_body = data_parts[-1]

            #write the data to a file to be read by the client
            with open("requestdata.txt", "a") as f:
                f.write(f"{data_body.encode()}\n")

            response = "OK".encode()
        else:
            #if the message is not a get or post method, it will be instead seen as p2p messaging
            print(data[0].decode()) 
            response = input("Enter response: ").encode()

        #send the response to the client 
        UDPServerSocket.sendto(response, data[1])

    except Exception as e:
        print(f"Rejected because {e}")





