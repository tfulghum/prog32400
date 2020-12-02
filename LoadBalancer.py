import socket
import sys
import getopt
import struct
import logging
import os
from timeit import default_timer as timer

headerSize = 4
randomNum = 12345
pingNum = 54321
totalSent = 0

#Period of time (in seconds) for table refresh
refreshTime = 5

packHeader = struct.Struct('>i')
packResponse = struct.Struct('>ii')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Ping all servers

def numCheck(numToTest):
	for i in (1,2,3,4,5):
		if(str(numToTest)[i] != str(randomNum)[i-1]):
			#Log that the response was not correct and figure out what to do
			
			logs = ("Incorrect response")
			logging.info(logs)
			randomNumCorrect = False
			continue
		else:
			randomNumCorrect = True
	if(randomNumCorrect != True):
		for i in (1,2,3,4,5):
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
	print("End of function: ", randomNumCorrect, pingNumCorrect)
	return randomNumCorrect, pingNumCorrect

def pingIt(serverIPs):
	pingPacket = packHeader.pack(pingNum)
	count = 0
	port = 5555
	preferences = [None] * len(serverIPs)
	for k in serverIPs:
		pingNumCorrect = False
		currentAddress = k
		totalSent = 0
		currentConnection = (currentAddress, port)
		try:
			sock.connect(currentConnection)
		except:
			print("Error: Endpoint is already connected")
			continue
		#Start timer here
		sock.sendall(pingPacket)
		#Times the packet send to receive time
		start = timer()
		totalSent += 1
		numErrors = 0		
		
		#Waits for a response
		receivedData = sock.recv(headerSize)
		receivedNum = struct.unpack('>i', receivedData)
		
		randomNumCorrect, pingNumCorrect = numCheck(receivedNum)
		#Parses incorrect reveived number
		while(pingNumCorrect == False):
			#Resends when received packet failed
			print("Error detected")
			numErrors += 1
			sock.sendall(pingPacket)
			totalSent = totalSent + 1
			receivedData = sock.recv(headerSize)
			receivedNum = struct.unpack('>ii', receivedData)
			randomNumCorrect, pingNumCorrect = numCheck(receivedNum)
		sock.shutdown(1)
		
		#Calculates time and weight
		end = timer()
		elapsedTime = end-start
		#Calculate here
		calculatedVal = .25*elapsedTime + .75*(numErrors/totalSent)
		preferences[count] = calculatedVal
		numErrors = 0

		sock.shutdown(1)
	prefCount = 0

	for i in preferences:
		if(max(preferences) == i):
			firstPref = serverIPs[prefCount]
			preferences.pop(prefCount)
		else:
			prefCount += 1

	prefCount = 0
	for i in preferences:
		if(max(preferences) == i):
			secondPref = serverIPs[prefCount]
			logs = f"Second preference: {secondPref}"
			logging.info(logs)
			print(logs)
		else:
			prefCount += 1

	return firstPref

def main(argv):
	port = ''
	url = ''
	log = ''
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
	myFile = open(ipAddresses, 'r')
	lines = myFile.readlines()
	myFile.close()
	
	try:
		port = int(port)
	except ValueError:
		print("Please use a valid integer for port value.")
		sys.exit(2)
	#Calculates the best IP for client use
	ipAddress = pingIt(lines)

	#Starts the load balancer listener
	server_address_object = (socket.gethostbyname(socket.gethostname()), port)
	sock.bind(server_address_object)
	print("Bound")
	loopNum = 0
	#Starts the table refresh timer
	start = timer()
	while True:
		loopNum += 1
		print("Waiting for connection")
		if(timer()-start > refreshTime):
			sock.shutdown(1)
			ipAddress = pingIt(lines)
			start = timer()
			print("Table has been refreshed")
			
		#Waits for a connection
		sock.listen(1)
		connection_object, client_address = sock.accept()
		
		#Logs the received connection
		logs = ("Received connection from", client_address[0], client_address[1])
		print("Received connection from", client_address)
		logging.info(logs)
		
		#Receives the packet and parses the contents as need be
		try:
			dataRequest = connection_object.recv(headerSize)
			receivedNum = struct.unpack('>i', dataRequest)
			for i in (1,2,3,4,5):
				if str(receivedNum)[i] != str(randomNum)[i-1]:
					numMisMatch = True
					break
				else:
					numMisMatch = False

			if(numMisMatch == True):
				#Log error
				print("Error: Number mismatch")
			else:
				ipSize = sys.getsizeof(ipAddress)
				balancerHead = struct.Struct('>ii')
				header = struct.pack('>ii',randomNum, ipSize)
				connection_object.send(header)
				logs = f"Request from {client_address}. Redirecting to {ipAddress}"
				logging.info(logs)
				print(logs)
				ipBytes = str.encode(str(ipAddress))
				connection_object.send(ipBytes)
		except:
			logs = f"Error: Unable to handle request between {client_address}, {ipAddress}, Unable to communicate with client"
			logging.info(logs)
			print(logs)
if __name__ == "__main__":
   main(sys.argv[1:])