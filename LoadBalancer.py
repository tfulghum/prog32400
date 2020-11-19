import socket
import sys
import getopt
import struct
import logging
import os

headerSize = 12
randomNum = 12345
pingNum = 54321
totalSent = 0

packHeader = struct.Struct('>i')
packResponse = struct.Struct('>ii')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Ping all servers

def pingIt():
	pingPacket = packHeader.pack(pingNum)
	for i in serverIPs
		sock.connect(serverIPs(i))
		#Start timer here
		socket.sendall(pingPacket)
		totalSent++
		recievedData = sock.recv(headerSize)
		recievedNum = struct.unpack('>ii', recievedData)
		while(recievedNum != randomNum):
			numErrors++
			socket.sendall(pingPacket)
			totalSent++
			recievedData = sock.recv(headerSize)
			recievedNum = struct.unpack('>ii', recievedData)
		#End timer here
		#Calculate here
		calculatedVal = .25*elapsedTime + .75*(numErrors/totalSent)
		preferences(i) = calculatedVal
		numErrors = 0
	return max(preferences)

#Calculate best one to use

#Wait for request to connect

#Connect

#Send best IP address

#Wait for ACK

#Close the conenction