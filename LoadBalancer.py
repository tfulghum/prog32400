import socket
import sys
import getopt
import struct
import logging
import os
from timeit import default_timer as timer

headerSize = 12
randomNum = 12345
pingNum = 54321
totalSent = 0

packHeader = struct.Struct('>i')
packResponse = struct.Struct('>ii')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Ping all servers

def pingIt(serverIPs):
	pingPacket = packHeader.pack(pingNum)
	for i in serverIPs
		sock.connect(serverIPs(i))
		#Start timer here
		socket.sendall(pingPacket)
		
		#Times the packet send to receive time
		start = timer()
		totalSent++
		
		#Waits for a response
		recievedData = sock.recv(headerSize)
		recievedNum = struct.unpack('>ii', recievedData)
		
		#Parses incorrect reveived number
		while(recievedNum != randomNum):
			#Resends when received packet failed
			numErrors++
			socket.sendall(pingPacket)
			totalSent++
			recievedData = sock.recv(headerSize)
			recievedNum = struct.unpack('>ii', recievedData)
		
		#Calculates time and weight
		end = timer()
		elapsedTime = end-start
		#Calculate here
		calculatedVal = .25*elapsedTime + .75*(numErrors/totalSent)
		preferences(i) = calculatedVal
		numErrors = 0
		totalSent = 0
	return max(preferences)

def main(argv):
	port = ''
	url = ''
	log = ''
	
	#Get CL arguments
	try:
		opts, args = getopt.getopt(argv,"hp:l:", ["PORT=","LOG="])
	except getopt.GetoptError:
		print("Please enter an ip address and a port number")
		sys.exit(2)
	for opt, arg in opts:
		if opt == ("-p"):
			port = arg
		if opt == ("-s"):
			ipAddresses = arg
		if opt == ("-l"):
			logging.basicConfig(filename=(os.getcwd() + '/' + arg), level=logging.INFO)

	#Parses the server IP file
	myFile = open(ipAddresses, "r")
	lines = myFile.readlines()
	for i in lines:
		IPs[i] = line.strip()
	
	#Calculates the best IP for client use
	ipAddress = pingIt(IPs)

	#Starts the load balancer listener
	server_address_object = ('localhost', port)
	sock.bind(server_address_object)

	while True:
		#Waits for a connection
		sock.listen(1)
		connection_object, client_address = sock.accept()
		
		#Logs the received connection
		logs = ("Received connection from", client_address[0], client_address[1])
		print("Received connection from", client_address)
		logging.info(logs)
		
		#Receives the packet and parses the contents as need be
		dataRequest = connection_object.recv(headerSize)
		recievedNum = struct.unpack('>i', dataRequest)
		if(recievedNum != randomNum):
			#Log error
			sock.close()
		else:
			balancerHead = struct.Struct('>ii')
			header = balancerHead.pack(randomNum, ipSize)
			connection_object.send(header)
			connection_object.send(ipAddress)
			recievedData = sock.recv(headerSize)
			recievedNum = struct.unpack('>i', ack)
			if(recievedNum != randomNum):
				#Log an error
				sock.close()
			else:
				sock.close()