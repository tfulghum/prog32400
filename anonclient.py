import socket
import sys

 

msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

#Sets sequence number to 32 bits
seqNumber = 12345
seqPad = 32 - sys.getsizeof(seqNumber)

#Sets ACK number to 32 bits
ackNumber = 100
ackPad = 32 - sys.getsizeof(ackNumber)

#Creates the unused portion
zeroPad = 0x0000
#Get flags from flag packer

#Then pack it all here
myPacket = pack(seqPad,seqNumber,ackPad,ackNumber,zeroPad,flags)

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)