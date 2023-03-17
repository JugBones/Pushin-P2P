import requests
import json
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#IP and port of the server
ip = input('Enter server IP address: ')
port = int(input('Enter server PORT: '))

#Loop for asking inputs
while True:
    cmd = input('Enter "get", "msg" or "post" command (or "exit" to quit): ')
    if cmd == 'exit':
        break
    #GET method 
    if cmd == 'get':
        query = input("What do you want ?: ")
        sock.sendto(("I WANT " + query).encode(), (ip, port))
        #receives 1024 bytes in socketserver
        data, addr = sock.recvfrom(1024)
        print(data)
    
    #P2P messaging
    if cmd == 'msg':
        query = input("Input message: ")
        sock.sendto(query.encode(), (ip, port))
        data, addr = sock.recvfrom(1024)
        print(data)

    #POST method
    elif cmd == 'post':
        hd = input("Head of message: ")
        msg = input("Message to be sent: ")
        #JSON file format
        payload = json.dumps({"head": hd, "message": msg})
        headers = '{"Content-Type":"application/json"}'
        #Send payload to server
        response = sock.sendto(("PUTTING" + " \n " +str(headers) + " \n " + str(payload)).encode(), (ip, port))

    else:
        print('Invalid command')