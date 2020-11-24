import socket
import sys
import getopt
import struct
import logging
import os

randNum = 12345
finalACKNum = 12345
pingNum = 54321
headerSize = 8

#This is the size of the server payloads minus the header size
#4 is the size of a bye and we recieve 2 of them
MTU = 500

def numCheck(numToTest):
	for i in (0,1,2,3,4):
		if(str(numToTest)[i] != str(randNum)[i]):
			#Log that the response was not correct and figure out what to do
			print("Num to test: ",str(numToTest)[i])
			print("Rand num: ",str(randNum)[i])
			logs = ("Incorrect response")
			logging.info(logs)
			randomNumCorrect = False
			break
		else:
			randomNumCorrect = True
	if(randomNumCorrect != True):
		for i in (0,1,2,3,4):
			if(str(numToTest)[i] != str(pingNum)[i-1]):
				#Log that the response was not correct and figure out what to do
				logs = ("Incorrect response")
				logging.info(logs)
				pingNumCorrect = False
				continue
			else:
				pingNumCorrect = True
	else:
		pingNumCorrect = False
	return randomNumCorrect, pingNumCorrect

def main(argv):
	#Create TCP connection to load balancer
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Empty variables for input
	cPort = ''
	cAddr = ''
	cLog = ''
	#STEP 2 - connect!
	try:
		opts, args = getopt.getopt(argv,"p:s:l:", ["PORT=", "ADDRESS=", "LOG="])
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
	packHeader = struct.Struct('>i')
	packResponse = struct.Struct('>ii')
	header = packHeader.pack(randNum)
	sock.sendall(header)

	s_head = sock.recv(headerSize)
	receivedNum, payloadSize = struct.unpack('>ii', s_head)
	#Detects if the recieved number is the same as what it should be
	randomNumCorrect, pingNumCorrect = numCheck(receivedNum)
	if(randomNumCorrect != True):
		print("Incorrect number")
		#Log that the response was not correct and figure out what to do
	receivedIp = sock.recv(payloadSize).decode()
	header = packHeader.pack(randNum)
	sock.sendall(header)
	print("Received IP: ",receivedIp)

	#Closes the connection with the load balancer after the IP is recieved
	sock.close()
	#serverAddress = (recievedIp, cPort)
	#Opens a connection with the recieved replica server and requests data
	newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverAddress = (receivedIp, 5555)
	newSock.connect(serverAddress)
	stillReceiving = True
	counter = 0
	while stillReceiving == True:
		
		#Sends the ack packet
		newSock.sendall(header)
		
		#Receives in the new header and payload from server
		s_head = newSock.recv(headerSize)
		receivedNum, payloadSize = struct.unpack('>ii', s_head)
		receivedData = newSock.recvfrom(payloadSize*2)
		logs = receivedData
		#Write to a file
		logs = (f"Packet number {counter+1} received")
		print(f"Packet number {counter+1} received")
		logging.info(logs)


		#Detects the last packet
		if(payloadSize < MTU):
			stillReceiving = False;
			#Send final ACK
			finalACK = packHeader.pack(finalACKNum)
			newSock.sendall(finalACK)
			print("End detected")
		else:
			newSock.sendall(header)
		counter += 1
		print("Counter: ",counter)
	
	newSock.shutdown(1)
	newSock.close()
if __name__ == "__main__":
   main(sys.argv[1:])