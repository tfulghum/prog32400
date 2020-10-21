import socket
import socket
import sys
import struct
import random
import logging
import time

#functions
 
def packThePacket(sNum, aNum, A, S, F):
	#This struct needs some work but will otherwise function
	packer = struct.Struct('>iii')
	lastLine = A*2*2 + S*2 + F
	packet = packer.pack(sNum, aNum, lastLine)
	return packet

def stopAndWait(mySocket, buffSiz, myPacket, portNum, seqNumber, ackNumber, A, S, F, File_object):
	servMsg = 0
	mySocket.settimeout(1)
	
	#Can get rid of exponential backoff
	while not servMsg:
		try:
			servMsg = mySocket.recvfrom(buffSiz)
		except ConnectionResetError:
			print("Not a port number of the valid server")
			exit(0)
		if not servMsg:
			#Resends the packet
			UDPClientSocket.sendto(firstPacket, serverAddressPort)
			
			#Logs that a retransmit was made
			logType = 2
			packetLog(seqNumber, ackNumber, A, S, F, File_object, logType)
			print("Seq: ", seqNumber, "Ack: ", ackNumber)
			#I don't think we need this anymore
			#servMsg = "Message from Server {}".format(msgFromServer[0])
		time.sleep(.5)
	return servMsg

def msgParser(msg):
	packer = '>iii'
	unpackedMsg = struct.unpack('>iii', msg)
	seqNumber = unpackedMsg[0]
	ackNumber = unpackedMsg[1]
	flags = unpackedMsg[2]
	
	#Determines which flags are set based on the value of the flags variable
	if flags >= 4:
		A = 1
		flags = flags - 4
	else:
		A = 0
	if flags >= 2:
		S = 1
		flags = flags - 2
	else:
		S = 0
	if flags >= 1:
		F = 1
	else:
		F = 0
	
	return seqNumber, ackNumber, A, S, F
	
def packetLog(sNum, aNum, A, S, F, File_object, logType):
	
	#Converts from binary to string for logging purposes
	if A == 1:
		ACK = "ACK"
	else:
		ACK = ""
	
	if A == 1:
		SEQ = "SEQ"
	else:
		SEQ = ""
	
	if F == 1:
		FIN = "FIN"
	else:
		FIN = ""
	
	
	if logType == 0:
		File_object.write(f"RECV {sNum} {aNum} {ACK} {SEQ} {FIN}\n")
	elif logType == 1:
		File_object.write(f"SEND {sNum} {aNum} {ACK} {SEQ} {FIN}\n")
	elif logType == 2:
		File_object.write(f"RETRAN {sNum} {aNum} {ACK} {SEQ} {FIN}\n")

def numberUpdater(seqNumber, ackNumber):
	newAckNumber = seqNumber + 512

	newSeqNumber = ackNumber
	return newSeqNumber, newAckNumber

#getting command line arguments
for args in sys.argv:
    if args == '-s':
        server = sys.argv[sys.argv.index(args)+1]
    elif args == '-p':
        port = int(sys.argv[sys.argv.index(args)+1])
    elif args == '-l':
        logfile = sys.argv[sys.argv.index(args)+1]
		
File_object = open(logfile, "w")

msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = (server, port)

bufferSize          = 96

#Number of failed attempts to send/recieve data from server
numFails = 0

#Sets sequence number to 32 bits
seqNumber = 12345

#Sets ACK number to 32 bits
ackNumber = 0

#Creates the unused portion
#Set default for flags
A = 0
S = 1
F = 0

firstPacket = packThePacket(seqNumber, ackNumber, A, S, F)

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Handshake start

# Send to server using created UDP socket
UDPClientSocket.sendto(firstPacket, serverAddressPort)
logType = 0

#log to file
packetLog(seqNumber, ackNumber, A, S, F, File_object, logType)

#Response from the server
msg = stopAndWait(UDPClientSocket, bufferSize, firstPacket, serverAddressPort, seqNumber, ackNumber, A, S, F, File_object)
#Parse the response
seqNumber, ackNumber, A, S, F = msgParser(msg[0])
logtype = 1
packetLog(seqNumber, ackNumber, A, S, F, File_object, logType)

print("Handshake complete")

#Create response packet
myPacket = packThePacket(seqNumber, ackNumber, A, S, F)

#Second half of handshake
UDPClientSocket.sendto(myPacket, serverAddressPort)

#Payload loop
while(not F):
	#Get response from the server
	seqNumber = 1000000
	while seqNumber > 999999:
		header = stopAndWait(UDPClientSocket, bufferSize, myPacket, serverAddressPort, seqNumber, ackNumber, A, S, F, File_object)
		seqNumber, ackNumber, A, S, F = msgParser(header[0])
	payload = UDPClientSocket.recvfrom(512)

	packetLog(seqNumber, ackNumber, A, S, F, File_object, 0)


	#Send seq and ack depending on recieved values
	
	seqNumber, ackNumber = numberUpdater(seqNumber, ackNumber)
	packetLog(seqNumber, ackNumber, A, S, F, File_object, 1)
	print("Seq number: ", seqNumber,"\n", "Ack number: ", ackNumber)

	myPacket = packThePacket(seqNumber, ackNumber, A, S, F)
	UDPClientSocket.sendto(myPacket, serverAddressPort)

print("Payload transfer complete")
UDPClientSocket.close()