import socket
import sys
import struct
import random

#functions

def packThePacket(sNum, aNum, A, S, F):
	#This struct needs some work but will otherwise function
	packer = struct.Struct('>iii')
	print(A*2*2 + S*2 + F, hex(sNum), hex(aNum))
	lastLine = A*2*2 + S*2 + F
	packet = packer.pack(sNum, aNum, lastLine)
	print(packet)
	return packet

def stopAndWait(mySocket)
	mySocket.settimeout(currentTime)
	servMsg = mySocket.recvfrom(bufferSize)
	while !servMsg :
		numFails = numFails + 1
		currentTime = currentTime + min((2**numFails + randomrange(0,100)), maxWait)
	return servMsg


msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

#Maximum amount of time to wait for stop and wait protocol
maxWait = 2000

#Number of failed attempts to send/recieve data from server
numFails = 0

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

#General structure
while(1):
	
	#Wait for response
	
	#Perform the appropriate actions for response
	
	#Send the response
	
	while(#FIN flag is not set):
	
		#Wait for the response
		
		#Download response
		
		#Send seq and ack
		
	
	

