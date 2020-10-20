import socket
import struct
import sys
import urllib.request, urllib.error, urllib.parse
import time
import logging
import os

def packThePacket(sNum, aNum, A, S, F):
    #This struct needs some work but will otherwise function
    packer = struct.Struct('>iii')
    lastLine = A*2*2 + S*2 + F
    packet = packer.pack(sNum, aNum, lastLine)
    return packet

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

def packetLog(sNum, aNum, A, S, F, logType):
	
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
		logging.info(f"RECV {sNum} {aNum} {ACK} {SEQ} {FIN}\n")
	elif logType == 1:
		logging.info(f"SEND {sNum} {aNum} {ACK} {SEQ} {FIN}\n")
	elif logType == 2:
		logging.info(f"RETRAN {sNum} {aNum} {ACK} {SEQ} {FIN}\n")


#getting command line arguments
for args in sys.argv:
    if args == '-p':
        localPort = int(sys.argv[sys.argv.index(args)+1])
    if args == '-l':
        logfile = sys.argv[sys.argv.index(args)+1]
    if args == '-u':
        url = sys.argv[sys.argv.index(args)+1]
		
#Gets the content of given url	
def URLDownload(url):
	
	url = 'http://' + url
	with urllib.request.urlopen(url) as f:
		html = f.read()
	return html
	
#Returns the specified payload number for the given file
def fileParser(myFile, payloadNumber):
	
	#Defines how large the payload to send is
	payloadSize = 512
	
	if len(myFile) < (512*payloadNumber)-1:
		finished = True
		
		theDifference = (payloadNumber*512) - len(myFile)
		
		return myFile[(payloadNumber-1)*512 : len(myFile)]+bytes("0"*theDifference, 'utf-8'), finished
	else:
		finished = False
	
	#Returns the payload portion
	return myFile[(payloadNumber-1)*512 : ((payloadNumber*512)-1)], finished

def stopAndWait(mySocket, buffSiz, myHeader, myPayload, portNum, seqNumber, ackNumber, A, S, F):
    servMsg = 0
    mySocket.settimeout(300)
    
    #Can get rid of exponential backoff
    while not servMsg:
        servMsg = mySocket.recvfrom(buffSiz)
        
        if not servMsg:
            #Resends the packet
            UDPClientSocket.sendto(myHeader, serverAddressPort)
            UDPClientSocket.sendto(myPayload, serverAddressPort)
            
            #Logs that a retransmit was made
            logType = 2
            packetLog(seqNumber, ackNumber, A, S, F, logType)
            #I don't think we need this anymore
            #servMsg = "Message from Server {}".format(msgFromServer[0])
        time.sleep(.5)
    return servMsg

def numberUpdater(seqNumber, ackNumber):
    newAckNumber = seqNumber + 1
    
    if ackNumber == 0:
        newSeqNumber = 100
    else:
        newSeqNumber = ackNumber
    return newSeqNumber, newAckNumber

logging.basicConfig(filename=(os.getcwd() + '/' + logfile), level=logging.INFO)
doneSending = False
counter = 1

#Downloads the webpage here
downloadedHTML = URLDownload(url)

localIP     = "localhost"
#socket.gethostbyname(socket.gethostname())

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

# Listen for incoming datagrams
go = 1
while(go == 1):
    try:
        print("UDP server up and listening")
        #First packet headers
        recvInfo, addr = UDPServerSocket.recvfrom(96)

        seqNumberR, ackNumberR, Ar, Sr, Fr = msgParser(recvInfo)
        packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, 0)

        seqNumberR, ackNumberR = numberUpdater(seqNumberR, ackNumberR)

        if(Ar == 0):
            Ar = 1
        packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, 1)

        handshakePack = packThePacket(seqNumberR, ackNumberR, Ar, Sr, Fr)
        #Send ack back
        UDPServerSocket.sendto(handshakePack, addr)

        #Complete handshake
        recvInfo, addr = UDPServerSocket.recvfrom(96)
        seqNumberR, ackNumberR, Ar, Sr, Fr = msgParser(recvInfo)

        packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, 0)
        
        Sr = 0
        tempVar = ackNumberR

        ackNumberR = seqNumberR + 1
        seqNumberR = tempVar

        print("Handshake Complete")
		
        while(doneSending == False):
			
			#Needs to swap and send header first
            if Ar:
                newAckNumber = seqNumberR+1
			
            currentPayload, doneSending = fileParser(downloadedHTML, counter)
			
            if doneSending == 1:
                    Fr = 1
            newHeader = packThePacket(seqNumberR, ackNumberR, Ar, Sr, Fr)

            seqNumberR, ackNumberR = numberUpdater(seqNumberR, ackNumberR)
			
            UDPServerSocket.sendto(newHeader, addr)
            packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, 0)
            UDPServerSocket.sendto(currentPayload, addr)
            packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, 1)
			
            print("Sent payload number: ", counter)
			
            counter = counter + 1
            
            stopAndWait(UDPServerSocket, 96, newHeader, currentPayload, localPort, seqNumberR, ackNumberR, Ar, Sr, Fr)
			
        doneSending = False
        F = 0
        counter = 1
        print("Payload transfer complete")
        #Close the file here
    except KeyboardInterrupt:
        print("Exiting now...")
        UDPServerSocket.close()
        break
