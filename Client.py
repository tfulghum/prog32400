import socket
import sys
import getopt
import struct
import logging
import os

randNum = 12345
finalACKNum = 54321
headerSize = 12

#This is the size of the server payloads minus the header size
#4 is the size of a bye and we recieve 2 of them
MTU = 1500-(4*2)

def main(argv):
	#Create TCP connection to load balancer
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Empty variables for input
	cPort = ''
	cAddr = ''
	cLog = ''
	#STEP 2 - connect!
	try:
		opts, args = getopt.getopt(argv,"p:a:l:", ["PORT=", "ADDRESS=", "LOG="])
	except getopt.GetoptError:
		print("Please enter an ip address and a port number")
		sys.exit(2)

	#Validating arguements
	for opt, arg in opts:
		if opt == ("-p"):
			cPort = arg
		if opt == ("-s"):
			cAddr = arg
		if opt == ("-l"):
			logging.basicConfig(filename=(os.getcwd() + '/' + arg), level=logging.INFO)
	try:
		cPort = int(cPort)
	except ValueError:
		print("Please use a valid integer for port value.")
		sys.exit(2)

	balancer_address = (cAddr, cPort)
	print("Connecting to...", balancer_address)
	sock.connect(balancer_address)

	print("Yay! connected to...", balancer_address)

	#Creates a standard header and sends to the load balancer

	#maddison - the num of bytes for what's being packed, received, and unpacked confuses me

	packHeader = struct.Struct('>i')
	header = packHeader.pack(randNum)
	sock.sendall(header)

	s_head = sock.recv(headerSize)
	recievedNum, payloadSize = struct.unpack('>ii', s_head)

	#Detects if the recieved number is the same as what it should be
	if(recievedNum != randNum):
		#Log that the response was not correct and figure out what to do
		logs = ("Response was incorrect")
		logging.info(logs)
		print(logs)
		#if this is the case, we wouldn't be able to continue, right? We would have to loop back to the beginning and try again?

	recievedIp = sock.recv(payloadSize).decode()

	#Closes the connection with the load balancer after the IP is recieved
	sock.close()

	#Opens a connection with the recieved replica server and requests data
	sock.connect(recievedIp)
	sock.sendall(header)
	stillReceiving = True

	while stillReceiving == True:
		s_head = sock.recv(headerSize)
		receivedNum, payloadSize = struct.unpack('>ii', s_head)
		receivedData = sock.recv(payloadSize).decode()

		#Write to a file
		logs = (f"Payload: {receivedData}")
		logging.info(logs)
		print(logs)

		#Detects the last packet
		if(payloadSize != MTU):
			stillReceiving = False;
			#Send final ACK
			finalACK = packHeader.pack(finalACKNum)
			sock.sendall(finalACK)
		else:
			sock.sendall(header)
	sock.close()