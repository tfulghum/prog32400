import socket
import sys
import struct

#functions
def flagSet(zeroPad, A, S, F):
    if A:
        print("A: ", A)
        zeroPad[3] = zeroPad | b'4'

    if S:
        print("S: ", S)
        zeroPad[3] = zeroPad | b'2'

    if F:
        print("F: ", F)
        zeroPad[3] = zeroPad | b'1'
    print("zeropad in function: ", zeroPad)

 

msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

#Sets sequence number to 32 bits
seqNumber = 12345
seqPad = 32 - sys.getsizeof(seqNumber)

#Sets ACK number to 32 bits
ackNumber = 100
ackPad = 32 - sys.getsizeof(ackNumber)

#Creates the unused portion
zeroPad = bytearray(4)
print(zeroPad)

#Set default for flags
A = b'0'
S = b'1'
F = b'0'

#Get flags from flag packer
flagSet(zeroPad, A, S, F)


#Then pack it all here
myPacket = struct.pack('!i', seqPad)
myPacket += struct.pack('!i', seqNumber)
myPacket += struct.pack('!i', ackPad)
myPacket += struct.pack('!i', ackNumber)
#myPacket += struct.pack('!i', zeroPad)
#myPacket += struct.pack('!i', placeholder for flags at some point)

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)
