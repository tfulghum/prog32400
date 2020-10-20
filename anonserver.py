import socket
import struct
import sys
import urllib.request, urllib.error, urllib.parse
import time

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

def packetLog(sNum, aNum, A, S, F, File_object, logType):
	
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
		File_object.write(f"RECV {sNum} {aNum} {ACK} {SEQ} {FIN}")
	elif logType == 1:
		File_object.write(f"SEND {sNum} {aNum} {ACK} {SEQ} {FIN}")
	elif logType == 2:
		File_object.write(f"RETRAN {sNum} {aNum} {ACK} {SEQ} {FIN}")


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

def stopAndWait(mySocket, buffSiz, myHeader, myPayload, portNum, seqNumber, ackNumber, A, S, F, File_object):
    servMsg = 0
    mySocket.settimeout(100)
    
    #Can get rid of exponential backoff
    while not servMsg:
        servMsg = mySocket.recvfrom(buffSiz)
        
        if not servMsg:
            #Resends the packet
            UDPClientSocket.sendto(myHeader, serverAddressPort)
            UDPClientSocket.sendto(myPayload, serverAddressPort)
            
            #Logs that a retransmit was made
            logType = 2
            packetLog(seqNumber, ackNumber, A, S, F, File_object, logType)
            #I don't think we need this anymore
            #servMsg = "Message from Server {}".format(msgFromServer[0])
        time.sleep(.5)
    return servMsg

File_object = open(logfile, "w")
doneSending = False
counter = 1

#Downloads the webpage here
downloadedHTML = URLDownload(url)

localIP     = "localhost"
#socket.gethostbyname(socket.gethostname())

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams
go = 1
while(go == 1):
    try:
        #First packet headers
        recvInfo, addr = UDPServerSocket.recvfrom(96)

        seqNumberR, ackNumberR, Ar, Sr, Fr = msgParser(recvInfo)

        print("Got ", seqNumberR, ackNumberR, Ar, Sr, Fr)
        packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, File_object, 0)

        tempVar = ackNumberR

        ackNumberR = seqNumberR + 1
        seqNumberR = 100

        if(Ar == 0):
            Ar = 1

        print("Sending ", seqNumberR, ackNumberR, Ar, Sr, Fr)
        packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, File_object, 1)

        handshakePack = packThePacket(seqNumberR, ackNumberR, Ar, Sr, Fr)
        #Send ack back
        UDPServerSocket.sendto(handshakePack, addr)

        #Complete handshake
        recvInfo, addr = UDPServerSocket.recvfrom(96)
        seqNumberR, ackNumberR, Ar, Sr, Fr = msgParser(recvInfo)

        print("Got ", seqNumberR, ackNumberR, Ar, Sr, Fr)
        packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, File_object, 0)
        
        Sr = 0
        tempVar = ackNumberR

        ackNumberR = seqNumberR + 1
        seqNumberR = tempVar

        print(seqNumberR, ackNumberR, Ar, Sr, Fr)
        print("Handshake Complete")
		
        while(doneSending == False):
			
			#Needs to swap and send header first
            if Ar:
                newAckNumber = seqNumberR+1
				
            newHeader = packThePacket(seqNumberR, ackNumberR, Ar, Sr, Fr)
			
            currentPayload, doneSending = fileParser(downloadedHTML, counter)
			
            newAckNumber = seqNumberR
            newSeqNumber = seqNumberR+len(currentPayload)
			
            UDPServerSocket.sendto(newHeader, addr)
            packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, File_object, 0)
            UDPServerSocket.sendto(currentPayload, addr)
            packetLog(seqNumberR, ackNumberR, Ar, Sr, Fr, File_object, 1)
			
            print("Sent payload number: ", counter)
			
            counter = counter + 1
            
            print("Listening")
            stopAndWait(UDPServerSocket, 96, newHeader, currentPayload, localPort, newSeqNumber, newAckNumber, Ar, Sr, Fr, File_object)
			
        go = 0

    except KeyboardInterrupt:
        print("Exiting now...")
        UDPServerSocket.close()
        break
