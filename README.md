
# CompNetwork Assignment L4BC

<h3 align="center">
Hi there, We're L4BC</a> 👋
</h3>

## 📝 The purpose of this project is :

- Creating P2P Protocol on top of the UDP 
- Simulating packet loss of data
- HTTP-like operations such as GET and POST

## 💻↔💻 What is P2P Network ?
![image](https://user-images.githubusercontent.com/91533574/226385702-7bd4f5b1-8b47-45cd-8f50-025840e84a1e.png)
***A peer-to-peer (P2P) network*** is a communications model in which each computing device on the network can function as either a server or a client. In a P2P network, two individuals interact directly with each other, without intermediation by a third party. P2P networks use both TCP and UDP as transport protocols, but there are some differences in each transport protocol.

## UDP
User Datagram Protocol (UDP) is a connectionless protocol that doesn’t require the establishment of a three-way handshake. Because it doesn't require an acknowledgement packet (ACK), it is regarded as one of the fastest protocols. Due to its fast speed, it is used to transmit data on applications that require fast transmissions like online games and video streaming services. However, since there’s no handshaking in UDP, it is unreliable, which in other words means there’s no guarantee of delivery of data transmitted.

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
>>>>>>> 1bf42520a664b9c66a4e066cdba5612aa06408dc
