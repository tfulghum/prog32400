import socket
import struct
import sys

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
		
		
def URLDownload(url):
{
	response = urllib.request.urlopen(url)
	#webcontent = response.read() I don't think we need this line for this program
	return response
}

#Downloads the file from the URL given
payload = URLDownload(url)


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

        tempVar = ackNumberR

        ackNumberR = seqNumberR + 1
        seqNumberR = 100

        if(Ar == 0):
            Ar = 1

        print("Sending ", seqNumberR, ackNumberR, Ar, Sr, Fr)

        handshakePack = packThePacket(seqNumberR, ackNumberR, Ar, Sr, Fr)
        #Send ack back
        UDPServerSocket.sendto(handshakePack, addr)

        #Complete handshake
        recvInfo, addr = UDPServerSocket.recvfrom(96)
        seqNumberR, ackNumberR, Ar, Sr, Fr = msgParser(recvInfo)

        print("Got ", seqNumberR, ackNumberR, Ar, Sr, Fr)
        
        Sr = 0
        tempVar = ackNumberR

        ackNumberR = seqNumberR + 1
        seqNumberR = tempVar

        print(seqNumberR, ackNumberR, Ar, Sr, Fr)
        print("Handshake Complete")

        go = 0

    except KeyboardInterrupt:
        print("Exiting now...")
        UDPServerSocket.close()
        break
