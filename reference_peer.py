import socket
import psutil
import multiprocessing
import subprocess
import hashlib
import pickle
import os
import random
import re
import select
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

def divide_data(data, max_segment_size, seq_num_size=9, checksum_size=16):
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


def reassemble_data(received_segments, max_segment_size, data_size, seq_num_size=9, checksum_size=16):
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

def ping(host):
    ping_cmd = ['ping', '-c', '1', '-W', '1', host]
    output = subprocess.run(ping_cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')

    rtt_match = re.search(r'rtt min/avg/max/mdev = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms', output)

    if rtt_match:
        rtt = float(rtt_match.group(2))  #extract the average RTT
        return rtt
    else:
        return None
    
def receive_datacks(num, mss, queue, temp_rec):
    print(f"Receiving DATACKs from peer...")
    expected_packets = set(range(0, num))
    received_packets = set()
    while len(received_packets) < num:
        print(f"Waiting for DATACKs")
        try:
            data, addr = temp_rec.recvfrom(mss)
            if data.decode().startswith('DATACK'):
                datack_num = int(data.decode().split()[-1])
                print(f"Received DATACK for segment {datack_num}")
                received_packets.add(datack_num)
        except socket.timeout:
            break
    temp_rec.close()

    missing_packets = expected_packets - received_packets
    queue.put(missing_packets)
    queue.put([])


    
#function to receive requests from peers
def receive_requests(timeout):
    global state
    segments = []
    while True:
        #receive data from peer
        if state == 0:
             UDPRecSocket.settimeout(timeout) 
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

                try:
                    body, addr = UDPRecSocket.recvfrom(mss)
                except Exception as e:
                    body = b'nothing'
                while body != b"END":
                    if body != b'nothing':
                        print(pickle.loads(body))

                        print("Received " + str(pickle.loads(body)[0]))
                        UDPRecSocket.sendto(("DATACK " + str(pickle.loads(body)[0])).encode(), (peer_ip, peer_port + 2))
                        segments.append(pickle.loads(body))
                    try:
                      body, addr = UDPRecSocket.recvfrom(mss)
                      if body == b"END":
                            break
                    except Exception as e:
                        body = b'nothing'
                        print("Packet Loss Detected")

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
def send_requests(cmd, shared_mem, segments, timeout):
    global state
    while True:
        if state == 0:
            #set timeout for udp socket if response is not received send the syn message again
            UDPSenSocket.settimeout(timeout)

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
                    if cmd.startswith("PUTTING"):
                        body = (shared_mem.value).decode('utf-8')
                        segments = divide_data(body.encode(), mss-100)
                        cmd = cmd + "-" + str(len(body)) + "-" + str(len(segments))
                        UDPSenSocket.sendto(cmd.encode(), (peer_ip, peer_port))

                        temp_rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        temp_rec.bind((ip, port + 2))
                        temp_rec.settimeout(timeout * 2)
                        
                        temp_queue = multiprocessing.Queue()
                        temp_recv = multiprocessing.Process(target=receive_datacks, args=(len(segments), mss, temp_queue, temp_rec))
                        temp_recv.start()

                        if len(segments) <= 1:
                            print("Sending 0")
                            if random.randint(0,100) < 5:
                                UDPSenSocket.sendto(pickle.dumps(segments[0]), (peer_ip, peer_port))
                            else:
                                print("Packet lost")
                            print("Sent all segments")
                            
                            missing_packets = temp_queue.get()
                            if missing_packets != []:
                                print("Missing packets: " + str(missing_packets))

                            while len(missing_packets) > 0:
                                for i in missing_packets:
                                    print("Sending Again " + str(i))
                                    UDPSenSocket.sendto(pickle.dumps(segments[i]), (peer_ip, peer_port))

                                missing_packets = temp_queue.get()
                                if missing_packets == []:
                                    break
                                print("Missing packets: " + str(missing_packets))

                            UDPSenSocket.sendto("END".encode(), (peer_ip, peer_port))
                            print("Sent all segments")

                            temp_recv.join()
                            temp_rec.close()
                        
                        else:
                            for segment in segments:
                                if random.randint(0, 100) < 0.001:
                                    print("Packet lost")
                                    continue
                                print("Sending " + str(segment[0]))
                                UDPSenSocket.sendto(pickle.dumps(segment), (peer_ip, peer_port))
                                

                            missing_packets = temp_queue.get()
                            if missing_packets != None:
                                print("Missing packets: " + str(missing_packets))

                            while len(missing_packets) > 0:
                                for i in missing_packets:
                                    print("Sending " + str(i))
                                    UDPSenSocket.sendto(pickle.dumps(segments[i]), (peer_ip, peer_port))

                                missing_packets = temp_queue.get()
                                if len(missing_packets) == 0:
                                    break
                                print("Missing packets: " + str(missing_packets))

                            UDPSenSocket.sendto("END".encode(), (peer_ip, peer_port))
                            print("Sent all segments")

                        temp_recv.join()
                        temp_rec.close()
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

    timeout_val = ping(peer_ip) * 9

    recv_process = multiprocessing.Process(target=receive_requests, args=(timeout_val,))
    recv_process.start()

    while True:
        print('\nEnter command (or "exit" to quit): ', end='', flush=True)
        rlist, _, _ = select.select([sys.stdin], [], [], 10) #Timeout after 10 seconds
        if not rlist:
            print("\nTimeout")
            continue

        cmd = input()

        if cmd == 'exit':
            break

        if cmd.startswith("PUTTING"):
            data = input()
            shared_mem = multiprocessing.RawArray('c', data.encode('utf-8'))

        if cmd.startswith("PLACING"):
            cmd = "PUTTING-" + cmd.split("-")[1]
            try:
                with(open("file_to_send/" + cmd.split("-")[1], 'r')) as f:
                    data = f.read()
                shared_mem = multiprocessing.RawArray('c', data.encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                continue

        send_process = multiprocessing.Process(target=send_requests, args=(cmd, shared_mem, segments, timeout_val))
        send_process.start()
        send_process.join()


    #close sockets and terminate receive process
    UDPRecSocket.close()
    UDPSenSocket.close()
    recv_process.terminate()
