from client import Client
from server import Server
import select
import json
from multiprocessing import Process


class PeerToPeer:
    """A class that represents a node it can send and receive messages from other nodes."""

    def __init__(self, server_ip_address: str = "0.0.0.0", server_port: int = int(input("Enter the port number this peer will use: "))):
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
            try:
                destination_ip = input("Enter destination IP: ")
                destination_port = int(input("Enter destination port: "))

                print(8*"-------")
                cmd = input('\nEnter "get", "msg" or "post" command (or "exit" to quit): \n')
                self.__client = Client()
                
                if cmd == 'msg':
                    message = input("Enter message: ")
                    self.__client.send(message, destination_ip,
                                    int(self.__server_port))
                    self.__client.receive()
                    self.__client.close()

                if cmd == 'get':
                    query = input("What do you want ?: ")
                    self.__client.send(("I WANT " + query), destination_ip, destination_port)
                    #receives 1024 bytes in socketserver
                    while True:
                        timeout = 5
                        data, addr = self.__client.receive()
                        if data:
                            file_name = data.decode().split(" ")[-1]
                            print("File name:", file_name)

                        while True:
                            #file object uses fileno(), since on Windows, select.select won't work unless it has a fileno() method
                            f = open(file_name, 'rb')
                            ready = select.select([f.fileno()], [], [], timeout)
                            if ready[0]:
                                data, addr = self.__client.receive()
                                with open("requestdata.html", "a") as f:
                                    #writing to the new requestdata.html file and decoding the data
                                    f.write(f"{data.decode()}\n")
                                    print("HTML FILE GOT AND SENT!!!")
                                    f.close()
                                    continue
                                    
                            else:
                                print("%s Finish!", file_name)
                                f.close()
                                break  
                
                #Post method 
                if cmd == 'post':
                    print("=====POST=====")
                    hd = input("Enter head of message: ")
                    msg = input("Enter content of the message: ")
                    payload = json.dumps({"head": hd, "message": msg})
                    headers = '{"Content-Type":"application/json"}'
                    #no need for decoding already decoded :)
                    self.__client.send(("PUTTING" + " \n " +str(headers) + " \n " + str(payload)), destination_ip, destination_port)
                    continue

                elif cmd == 'exit':
                    break
                else:
                    print("INVALID STATEMENT!")
                    continue

            except Exception as e: print(e)


