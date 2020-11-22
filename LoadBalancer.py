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

#Period of time (in seconds) for table refresh
refreshTime = 5

packHeader = struct.Struct('>i')
packResponse = struct.Struct('>ii')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Ping all servers

def pingIt(serverIPs):
	pingPacket = packHeader.pack(pingNum)
	preferences = []
	for i in serverIPs:
		sock.connect(serverIPs(i))
		#Start timer here
		socket.sendall(pingPacket)
		
		#Times the packet send to receive time
		start = timer()
		totalSent = totalSent + 1
		
		#Waits for a response
		recievedData = sock.recv(headerSize)
		recievedNum = struct.unpack('>ii', recievedData)
		
		#Parses incorrect reveived number
		while(recievedNum != randomNum):
			#Resends when received packet failed
			numErrors = numErrors + 1
			socket.sendall(pingPacket)
			totalSent = totalSent + 1
			recievedData = sock.recv(headerSize)
			recievedNum = struct.unpack('>ii', recievedData)
		
		#Calculates time and weight
		end = timer()
		elapsedTime = end-start
		#Calculate here
		calculatedVal = .25*elapsedTime + .75*(numErrors/totalSent)
		preferences[i] = calculatedVal
		numErrors = 0
		totalSent = 0
	#return max(preferences)
	return 1

def main(argv):
	port = ''
	url = ''
	log = ''
	
	#Get CL arguments
	try:
		opts, args = getopt.getopt(argv,"p:s:l:", ["PORT=","LOG="])
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
	IPs = []
	myFile = open(ipAddresses, 'r')
	lines = myFile.readlines()
	
	count = 0
	while True:
		line = myFile.readline()
		if not line:
			break
		IPs[count] = line.strip()
		count += 1
	
	try:
		port = int(port)
	except ValueError:
		print("Please use a valid integer for port value.")
		sys.exit(2)
	#Calculates the best IP for client use
	#ipAddress = pingIt(IPs)

	#Starts the load balancer listener
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address_object = ('localhost', port)
	sock.bind(server_address_object)
	ipAddress = '192.168.1.1'
	loopNum = 0
	#Starts the table refresh timer
	start = timer()
	while True:
		loopNum += 1
		print("Waiting for connection")
		if(timer()-start > refreshTime):
			ipAddress = pingIt(IPs)
			start = timer()
			print("Table has been refreshed")
			
		#Waits for a connection
		print("Loop number: ", loopNum)
		sock.listen(1)
		connection_object, client_address = sock.accept()
		
		#Logs the received connection
		logs = ("Received connection from", client_address[0], client_address[1])
		print("Received connection from", client_address)
		logging.info(logs)
		
		#Receives the packet and parses the contents as need be
		dataRequest = connection_object.recv(headerSize)
		recievedNum = struct.unpack('>i', dataRequest)
		for i in (1,2,3,4,5):
			if str(recievedNum)[i] != str(randomNum)[i-1]:
				numMisMatch = True
				break
			else:
				numMisMatch = False

		if(numMisMatch == True):
			#Log error
			print("Error")
			print(recievedNum)
		else:
			ipSize = len(str(ipAddress))
			balancerHead = struct.Struct('>ii')
			header = struct.pack('>ii',randomNum, ipSize)
			connection_object.send(header)
			ipBytes = str.encode(str(ipAddress))
			connection_object.send(ipBytes)
			recievedData = connection_object.recv(headerSize)
			recievedNum = struct.unpack('>i', recievedData)
			
if __name__ == "__main__":
   main(sys.argv[1:])