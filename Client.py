import socket
import sys
import getopt
import struct
import logging
import os

randNum = 12345
finalACKNum = 12345
headerSize = 8

#This is the size of the server payloads minus the header size
#4 is the size of a bye and we recieve 2 of them
MTU = 1524

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

	balancer_address = ('localhost', cPort)
	print("Connecting to...", balancer_address)
	sock.connect(balancer_address)

	print("Yay! connected to...", balancer_address)

	#Creates a standard header and sends to the load balancer
	packHeader = struct.Struct('>i')
	packResponse = struct.Struct('>ii')
	header = packHeader.pack(randNum)
	sock.sendall(header)

	s_head = sock.recv(headerSize)
	print(sys.getsizeof(s_head))
	recievedNum, payloadSize = struct.unpack('>ii', s_head)
	print(payloadSize)
	#Detects if the recieved number is the same as what it should be
	if(recievedNum != randNum):
		print("No bueno")
		#Log that the response was not correct and figure out what to do
	recievedIp = sock.recv(payloadSize).decode()
	header = packHeader.pack(randNum)
	sock.sendall(header)

	#Closes the connection with the load balancer after the IP is recieved
	sock.close()
	#serverAddress = (recievedIp, cPort)
	serverAddress = ('localhost', 5555)
	#Opens a connection with the recieved replica server and requests data
	newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	newSock.connect(serverAddress)
	newSock.sendall(header)
	stillRecieving = True
	counter = 0
	while stillRecieving == True:
		s_head = newSock.recv(headerSize)
		print(s_head)
		recievedNum, payloadSize = struct.unpack('>ii', s_head)
		recievedData = newSock.recv(payloadSize).decode()
		print(sys.getsizeof(recievedData))
		print(payloadSize)
		#Write to a file
		logs = (f"Packet number {counter+1} received")
		print(f"Packet number {counter+1} received")
		logging.info(logs)


		#Detects the last packet
		if(payloadSize != MTU):
			stillRecieving = False;
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