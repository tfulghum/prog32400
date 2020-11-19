import socket
import sys
import getopt
import struct
import logging
import os
import urllib

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
		
		theDifference = (payloadNumber*MTU) - len(myFile)
		
		return myFile[(payloadNumber-1)*MTU : len(myFile)]+bytes("0"*theDifference, 'utf-8'), finished
	else:
		finished = False
	
	#Returns the payload portion
	return myFile[(payloadNumber-1)*MTU : ((payloadNumber*MTU)-1)], finished

def main(argv):
	#STEP 1 - create the socket object. This example uses TCP over IPv4
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
		if opt == ("-u"):
			url = arg
		if opt == ("-l"):
			logging.basicConfig(filename=(os.getcwd() + '/' + arg), level=logging.INFO)

	#STEP 2 - specify where the server should listen on, IP and PORT
	try:
		port = int(port)
	except ValueError:
		print("Please use a valid integer for port value.")
		sys.exit(2)

	server_address_object = ('localhost', port)
	sock.bind(server_address_object)

	#STEP 3 - do the actual listening
	sock.listen(1)
	goFlag = 1

	#call URLDownload
	downloadedHTML = URLDownload(url)

	#Loop lets us get multiple packets
	while goFlag == 1:
		try:
			connection_object, client_address = sock.accept()
			logs = ("Receivced connection from", client_address[0], client_address[1])
			print("Receivced connection from", client_address)
			logging.info(logs)

			dataRequest = connection_object.recv(headerSize)
			recievedNum = struct.unpack('>i', dataRequest)

			if(recievedNum != randomNum and recievedNum != pingNum):
				#Log that the response was not correct and figure out what to do
				logs = ("Incorrect response")
				logging.info(logs)
				print(logs)
			
			#Does logic for pinging request
			if(recievedNum == pingNum):
				header = serverHead.pack(randomNum, 0)
				connection_object.send(header)
				ack = connection_object.recv(headerSize)
				recievedNum = struct.unpack('>i', ack)
				if(recievedNum != pingNum):
					#Log that the response was not correct and figure out what to do
					logs = ("Incorrect reponse")
					logging.info(logs)
					print(logs)
				else:
					connection_object.close()

			while(doneSending != True and recievedNum == randomNum):
				#Creates payload and header and sends it

				counter = 0
				currentPayload, doneSending = fileParser(downloadedHTML, counter)
				serverHead = struct.Struct('>ii')
				header = serverHead.pack(randomNum, packetSize)
				connection_object.send(header)

				#Sends HTML 
				connection_object.send(currentPayload)

				#Recieves data from the client
				ack = connection_object.recv(headerSize)
				recievedNum = struct.unpack('>i', ack)
				if(recievedNum != randomNum):
					#Log that the response was not correct and figure out what to do
					logs = ("Incorrect reponse")
					logging.info(logs)
					print(logs)
				counter += 1

			sock.close()


			

#Wait for request to connect

#Connect

#Send IP address

#Wait for ACK

#Close connection