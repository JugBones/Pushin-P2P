import socket
import psutil
import multiprocessing
import hashlib
import pickle
import os
import sys
import time

def get_network_interface_info(interface_name):
    if_addrs = psutil.net_if_addrs()
    if_stats = psutil.net_if_stats()

    if interface_name not in if_addrs:
        raise ValueError("nope")

    addrs = if_addrs[interface_name]
    stats = if_stats[interface_name]

    mtu = stats.mtu
    mss = mtu - 40  #Subtract 20 bytes for IP header and 20 bytes for header

    return mtu, mss

def divide_data(data, max_segment_size, seq_num_size=4, checksum_size=16):
    """Divides data into segments with sequence numbers and checksums."""
    segments = []
    seq_num = 0
    while seq_num * max_segment_size < len(data):
        #Calculate segment boundaries
        start = seq_num * max_segment_size
        end = min(start + max_segment_size, len(data))
        segment_data = data[start:end]

        # Calculate checksum
        segment_checksum = hashlib.md5(segment_data).digest()[:checksum_size]

        # Assemble segment
        segment = len(segment_data).to_bytes(seq_num_size, byteorder='big') + \
                  seq_num.to_bytes(seq_num_size, byteorder='big') + \
                  segment_checksum + \
                  segment_data

        #Append (seq_num, segment) tuple to list
        segments.append((seq_num, segment))
        seq_num += 1

    return segments


def reassemble_data(received_segments, max_segment_size, data_size, seq_num_size=4, checksum_size=16):
    received_data = bytearray(data_size)
    combined_checksum = hashlib.md5(bytearray()).digest()[:checksum_size]
    for seq_num, segment in received_segments:
        segment_len = int.from_bytes(segment[:seq_num_size], byteorder='big')
        segment_seq_num = int.from_bytes(segment[seq_num_size:2*seq_num_size], byteorder='big')
        segment_checksum = segment[2*seq_num_size:2*seq_num_size+checksum_size]
        segment_data = segment[2*seq_num_size+checksum_size:2*seq_num_size+checksum_size+segment_len]

        if len(segment_data) != segment_len:
            print(f"Segment {segment_seq_num} has incorrect length")
            return None

        if segment_seq_num != seq_num:
            print(f"Segment {segment_seq_num} received out of order")
            return None

        if hashlib.md5(segment_data).digest()[:checksum_size] != segment_checksum:
            print(f"Segment {segment_seq_num} has incorrect checksum")
            return None

        #Add segment data to received data and update combined checksum
        start = seq_num * max_segment_size
        end = min(start + max_segment_size, data_size)
        data_len = end - start
        received_data[start:end] = segment_data[:data_len]
        combined_checksum = hashlib.md5(segment_checksum+combined_checksum).digest()[:checksum_size]

        seq_num += 1

    #Verifying data integrity
    if combined_checksum == received_segments[-1][1][2*seq_num_size+segment_len:2*seq_num_size+segment_len+checksum_size]:
        print("Data transmission successful!")

    return received_data

#function to receive requests from peers
def receive_requests():
    global state
    segments = []
    while True:
        #receive data from peer
        if state == 0:
             UDPRecSocket.settimeout(5) 
        mss = get_network_interface_info('wlan0')[1]
        try:
            data, addr = UDPRecSocket.recvfrom(mss)
        except Exception as e:
            continue
        try:
            #check for SYN message
            if data == b'SYN':
                #send SYN-ACK message back to peer
                print('Received SYN message from peer.')
                print('Sending SYN-ACK message...')
                UDPRecSocket.sendto(b'SYN-ACK', addr)

                #wait for ACK message from peer
                print('Waiting for ACK message...')
                data, addr = UDPRecSocket.recvfrom(mss)

                if data.decode().startswith('ACK'):
                    mss = data.decode().split(" ")[-1]
                    UDPRecSocket.sendto(f"Window size: {mss}".encode(), addr)
                    print('Connection established with peer.')
                    UDPRecSocket.settimeout(None)
                    state = 1
            #check for I WANT message
            elif data.decode().startswith("I WANT") and state == 1:
                print(data.decode())
                file_name = data.decode().split()[-1]
                file_path = os.path.join("files", file_name)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, "r") as f:
                       file_content = f.read()
                    response = ("NOT HTTP/1.0 9000 OKAY\nContent-Type: text/html\n\n" + file_content).encode()
                else:
                    response = "File not found".encode()
                UDPRecSocket.sendto(response, addr)

            elif data.decode().startswith("PUTTING") and state == 1:
                print(data.decode())
                file_name = data.decode().split("-")[-3]
                body_size = int(data.decode().split("-")[-2])
                file_num = int(data.decode().split("-")[-1])

                for i in range(0, file_num):
                    print("Received " + str(i))
                    data, addr = UDPRecSocket.recvfrom(mss)
                    segments.append(pickle.loads(data))

                print(segments)
                print("Received all segments")
                received_data = reassemble_data(segments, mss-100, body_size)

                with open("files/" + file_name, "wb") as f:
                    f.write(received_data)

                print("File saved")
                f.close()
                response = ("File uploaded successfully").encode()
                UDPRecSocket.sendto(response, (peer_ip, peer_port))

            else:
                print("msg: " + data.decode())

        except Exception as e:
            print(f"Rejected because {e}")
            continue

#function to send requests to peer
def send_requests(cmd, body, segments):
    global state
    while True:
        if state == 0:
            #set timeout for udp socket if response is not received send the syn message again
            UDPSenSocket.settimeout(5)

        mss = get_network_interface_info('wlan0')[1]

        if state == 0:
            #send SYN message to peer
            print('Sending SYN message to peer...')
            UDPSenSocket.sendto(b'SYN', (peer_ip, peer_port))

            #wait for SYN-ACK message from peer
            print('Waiting for SYN-ACK message from peer...')
        try:
            data, addr = UDPSenSocket.recvfrom(mss)

            if data == b'SYN-ACK':
                #send ACK message to peer
                print('Received SYN-ACK message from peer.')
                print('Sending ACK message to peer...')
                window_msg = 'ACK Window_size: ' + str(mss)
                UDPSenSocket.sendto(window_msg.encode(), (peer_ip, peer_port))

                try:
                    state = 1
                    UDPSenSocket.settimeout(None)
                    if cmd.startswith("PUTTING"):
                        segments = divide_data(body.encode(), mss-100)
                        cmd = cmd + "-" + str(len(body)) + "-" + str(len(segments))
                        UDPSenSocket.sendto(cmd.encode(), (peer_ip, peer_port))

                        for segment in segments:
                            print(segment)
                            UDPSenSocket.sendto(pickle.dumps(segment), (peer_ip, peer_port))

                    else:
                        #send command to peer
                        UDPSenSocket.sendto(cmd.encode(), (peer_ip, peer_port))
                        data, addr = UDPSenSocket.recvfrom(mss)


                        #receive response from peer
                    data, addr = UDPSenSocket.recvfrom(mss)
                    print(data.decode())
                    return
                        
                except Exception as e:
                    print(f"Error1: {e}")

        except Exception as e:
         print(f"Error2: {e}")

if __name__ == '__main__':
    #udp socket
    UDPRecSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPSenSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = "192.168.0.120"
    port = int(input("Port: "))
    UDPRecSocket.bind((ip, port))
    UDPSenSocket.bind((ip, port + 1))
    state = 0
    data = None

    segments = []

    #IP and port of the peer
    peer_ip = "192.168.0.120"
    peer_port = int(input("Enter peer port number: "))

    recv_process = multiprocessing.Process(target=receive_requests)
    recv_process.start()

    while True:
        cmd = input('Enter command (or "exit" to quit): ')
        if cmd == 'exit':
            break

        if cmd.startswith("PUTTING"):
            data = str(input())

        send_process = multiprocessing.Process(target=send_requests, args=(cmd, data, segments))
        send_process.start()
        send_process.join()


    #close sockets and terminate receive process
    UDPRecSocket.close()
    UDPSenSocket.close()
    recv_process.terminate()
