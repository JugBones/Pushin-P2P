
# CompNetwork Assignment L4BC

<h3 align="center">
Hi there, We're L4BC</a> 👋
</h3>

## 📝 The purpose of this project is :

- Creating P2P Protocol on top of the UDP 
- Simulating packet loss of data
- HTTP-like operations such as GET and POST

## Table of Contents
- [P2P Network](#-what-is-p2p-network-)
- [UDP](#udp)
- [Features](#features)
- [Sequence Diagram](#sequence-diagram)
- [Testing](#testing)

## 💻↔💻 What is P2P Network ?
![image](https://user-images.githubusercontent.com/91533574/226385702-7bd4f5b1-8b47-45cd-8f50-025840e84a1e.png)
***A peer-to-peer (P2P) network*** is a communications model in which each computing device on the network can function as either a server or a client. In a P2P network, two individuals interact directly with each other, without intermediation by a third party. P2P networks use both TCP and UDP as transport protocols, but there are some differences in each transport protocol.

## UDP
User Datagram Protocol (UDP) is a connectionless protocol that doesn’t require the establishment of a three-way handshake. Because it doesn't require an acknowledgement packet (ACK), it is regarded as one of the fastest protocols. Due to its fast speed, it is used to transmit data on applications that require fast transmissions like online games and video streaming services. However, since there’s no handshaking in UDP, it is unreliable, which in other words means there’s no guarantee of delivery of data transmitted.

## TCP
Transmission Control Protocol (TCP) is a core protocol of the internet protocol (IP) suite. It is responsible for establishing and maintaining reliable communication between two endpoints over an IP network. TCP provides guaranteed delivery of data by breaking it down into small packets and reassembling them at the receiver’s end, while also ensuring that they arrive in the correct order. TCP uses a three-way handshake mechanism to establish a connection between the sender and receiver, where the two parties exchange control messages to synchronize their sequence and acknowledgement numbers. Once the connection is established, TCP uses a sliding window algorithm to control the flow of data and avoid network congestion. 

## Features

Although the P2P Protocol is created on top of a UDP, it will have features that are commonly observed in TCP. These features are described below.

- 3-Way Handshake

  Positive Acknowledgement with Retransmission (PAR), specifically SYN-ACK signals, will be used to establish a connection between peers. Using a 3-way handshake to establish a connection increases the reliability of protocol communication.

- Dynamic Memory Flow

  The memory of data transmissions will be changed dynamically. This allows a more extensive variety of bytes to be used in transmissions. The bytes are not limited by a fixed number stated in the code beforehand.

- Packet Loss Control

  In order to prevent packet loss, a timer will be used alongside ACK and NAK signals. This ensures that packets are properly received or retransmitted if necessary. This will be further demonstrated in the Sequence Diagram.
  
TCP features are used in this protocol to improve the reliability of its communication. UDP is said to be an unreliable protocol due to its lack of guarantee in the arrival of the data. Hence, a number of features that are observed in TCP have been implemented in this protocol to prevent that unreliability. 

## Sequence Diagram

## Testing
In order to test the protocol, two end-systems are needed. This can be done in the form of multiple VMs or two operating systems for both receiving and sending files.

Initialize Git:
```console
git init
```
Clone the repository:
```console
git clone https://github.com/JugBones/CompNetwork-Assignment-L4BC.git
```
Now run the python scripts for the testing of the POST and GET functions


## 💼 Language & Tools :
![](https://img.shields.io/badge/Tools-Git-informational?style=flat&logo=Git&color=F05032)
![](https://img.shields.io/badge/Tools-GitHub-informational?style=flat&logo=GitHub&color=181717)
![](https://img.shields.io/badge/Tools-Visual-Studio?style=flat&logo=VisualStudioCode&color=0044F9)
![](https://img.shields.io/badge/Code-Python-informational?style=flat&logo=Python&color=FBFF00)
