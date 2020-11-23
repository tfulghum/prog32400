import socket
import sys
import getopt
import struct
import logging
import os
import urllib.request, urllib.error, urllib.parse

headerSize = 12
randomNum = 12345
counter = 1
pingNum = 54321

#This is the size of the server payloads minus the header size
#4 is the size of a bye and we recieve 2 of them
MTU = 1500-(4*2)

#Currently means the same as MTU but may change in the future
packetSize = MTU


#Gets the content of given url	
def URLDownload(url):
    url = 'http://' + url
    with urllib.request.urlopen(url) as f:
        html = f.read()
        h = open('url.html', 'wb')
        h.write(html)
        h.close()
    return html

def fileParser(myFile, payloadNumber):
	if len(myFile) < (MTU*payloadNumber)-1:
		finished = True
				
		return myFile[(payloadNumber-1)*MTU : len(myFile)], finished
	else:
		finished = False
	
	#Returns the payload portion
	return myFile[(payloadNumber-1)*MTU : ((payloadNumber*MTU)-1)], finished

def numCheck(numToTest):
	for i in (1,2,3,4,5):
		if(str(numToTest)[i] != str(randomNum)[i-1]):
			#Log that the response was not correct and figure out what to do
			
			print(str(numToTest)[i])
			print(str(randomNum)[i-1])
			logs = ("Incorrect response")
			logging.info(logs)
			print(logs)
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
				print(logs)
				pingNumCorrect = False
				continue
			else:
				pingNumCorrect = True
	else:
		pingNumCorrect = False
	return randomNumCorrect, pingNumCorrect

def main(argv):
	#STEP 1 - create the socket object. This example uses TCP over IPv4
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = ''
	url = ''
	log = ''
	#Get CL arguments
	try:
		opts, args = getopt.getopt(argv,"p:l:u:", ["PORT=","LOG="])
	except getopt.GetoptError:
		print("Please enter an ip address and a port number")
		sys.exit(2)
	for opt, arg in opts:
		if opt == ("-p"):
			port = arg
		if opt == ("-l"):
			logging.basicConfig(filename=(os.getcwd() + '/' + arg), level=logging.INFO)
		if opt == ("-u"):
			url = arg

	#STEP 2 - specify where the server should listen on, IP and PORT
	try:
		port = int(port)
	except ValueError:
		print("Please use a valid integer for port value.")
		sys.exit(2)

	server_address_object = ('localhost', port)
	sock.bind(server_address_object)

	print("Sever is up and listening")

	#STEP 3 - do the actual listening
	sock.listen(1)
	goFlag = 1

	#call URLDownload
	downloadedHTML = URLDownload(url)

	#Loop lets us get multiple packets
	while True:
		connection_object, client_address = sock.accept()
		logs = ("Received connection from", client_address[0], client_address[1])
		print("Received connection from", client_address)
		logging.info(logs)

		dataRequest = connection_object.recv(headerSize)
		print(dataRequest)
		recievedNum = struct.unpack('>i', dataRequest)

		randomNumCorrect, pingNumCorrect = numCheck(recievedNum)
		print(randomNumCorrect, pingNumCorrect)


		#Does logic for pinging request
		if(pingNumCorrect == True):
			header = serverHead.pack(randomNum, 0)
			connection_object.send(header)
			ack = connection_object.recv(headerSize)
			recievedNum = struct.unpack('>i', ack)
		doneSending = False
		counter = 0
		while(doneSending != True and randomNumCorrect == True):
			#Creates payload and header and sends it

			currentPayload, doneSending = fileParser(downloadedHTML, counter)
			packetSize = sys.getsizeof(currentPayload)
			header = struct.pack('>ii',randomNum, packetSize)
			print("Header size: ", sys.getsizeof(header))
			connection_object.send(header)
			print("Done sending: ", doneSending)
			#Sends HTML 
			connection_object.send(currentPayload)

			#Recieves data from the client
			ack = connection_object.recv(headerSize)
			print(ack)
			recievedNum = struct.unpack('>i', ack)
			randomNumCorrect, pingNumCorrect = numCheck(recievedNum)
			if(randomNumCorrect == False):
				#Log that the response was not correct and figure out what to do
				logs = ("Incorrect reponse")
				logging.info(logs)
				print(logs)
			else:
				counter += 1
if __name__ == "__main__":
   main(sys.argv[1:])