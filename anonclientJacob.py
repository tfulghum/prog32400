import socket
import sys
import struct

#functions

def packThePacket(sNum, aNum, A, S, F):
	#This struct needs some work but will otherwise function
	packer = struct.Struct('>iii')
	print(A*2*2 + S*2 + F, hex(sNum), hex(aNum))
	lastLine = A*2*2 + S*2 + F
	packet = packer.pack(sNum, aNum, lastLine)
	print(packet)
	return packet


msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

#Sets sequence number to 32 bits
seqNumber = 12345

#Sets ACK number to 32 bits
ackNumber = 100

#Creates the unused portion
#Set default for flags
A = 0
S = 1
F = 0

firstPacket = packThePacket(seqNumber, ackNumber, A, S, F)

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)
