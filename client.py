import socket
import sys
import getopt
import struct
import logging
import os

#Program 1 CSC 4200
#Author: Tyler Fulghum


def main(argv):
	#STEP 1 - create the socket object. This example uses TCP over IPv4
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Empty variables fo input
	cPort = ''
	cAddr = ''
	cLog = ''
	#STEP 2 - connect!
	try:
		opts, args = getopt.getopt(argv,"p:a:l:", ["PORT=", "ADDRESS=", "LOG="])
	except getopt.GetoptError:
		print("Please enter an ip address and a port number")
		sys.exit(2)

	#Validating arguements
	for opt, arg in opts:
		if opt == ("-p"):
			cPort = arg
		if opt == ("-a"):
			cAddr = arg
		if opt == ("-l"):
			logging.basicConfig(filename=(os.getcwd() + '/' + arg), level=logging.INFO)
	try:
		cPort = int(cPort)
	except ValueError:
		print("Please use a valid integer for port value.")
		sys.exit(2)

	server_address = (cAddr, cPort)
	print("Connecting to...", server_address)
	sock.connect(server_address)

	print("Yay! connected to...", server_address)

	#Creating hello packet
	pack_start = struct.Struct('>iii5s')
	pack_hello = pack_start.pack(17, 1, 5, b"HELLO")

	print("Sending message")
	sock.sendall(pack_hello)

	#Receive hello packet
	s_head = sock.recv(12)
	s_version, s_type, s_len = struct.unpack('>iii', s_head)
	response = sock.recv(s_len).decode()

	#Log
	logs = ("Received Data: version:", s_version, "message type:", s_type, "length:", s_len, "message:", response)
	logging.info(logs)
	print(logs)

	#Version check
	if(s_version == 17):
		logging.info("VERSION ACCEPTED")
		print("VERSION ACCEPTED")
		logging.info("Hello recieved")
		print("Hello recieved")
	else:
		logging.error("VERSION MISMATCH")
		print("VERSION MISMATCH")
		logging.info("Hello recieved")
		print("Hello recieved")

	try:
		x = int(input("Enter 1 for LIGHTON 2 for LIGHTOFF: "))
	except ValueError:
		print("Please use a valid integer.")
		sys.exit(2)

	#Send the command
	if(x == 1):
		pack_com = struct.Struct('>iii7s')
		pack_com_msg = pack_com.pack(17, 1, 7, b"LIGHTON")
		print("Sending command")
		logging.info("Sending command")
		sock.sendall(pack_com_msg)
	if(x == 2):
		pack_com = struct.Struct('>iii8s')
		pack_com_msg = pack_com.pack(17, 2, 8, b"LIGHTOFF")
		print("Sending command")
		logging.info("Sending command")
		sock.sendall(pack_com_msg)
	else:
		pack_com = struct.Struct('>iii7s')
		pack_com_msg = pack_com.pack(17, 3, 7, b"UNKNOWN")
		print("Sending command")
		logging.info("Sending command")
		sock.sendall(pack_com_msg)

	#Receive success packet
	su_head = sock.recv(12)
	su_version, su_type, su_len = struct.unpack('>iii', su_head)
	sresponse = sock.recv(su_len).decode()

	#Log
	logs = ("Received Data: version:", su_version, "message type:", su_type, "length:", su_len, "message:", sresponse)
	logging.info(logs)
	print(logs)
	logs = ("Received message:", sresponse)
	
	if(su_version == 17):
		logging.info("VERSION ACCEPTED")
		print("VERSION ACCEPTED")
		logging.info(logs)
		print(logs)
	else:
		logging.error("VERSION MISMATCH")
		print("VERSION MISMATCH")
		logging.info(logs)
		print(logs)

	#Command state
	if(sresponse == "SUCCESS"):
		print("Command Successful")
		logging.info("Command Successful")
	else:
		print("Command Unsuccessful")
		logging.info("Command Unsuccessful")

	#Make sure we cleanly exit
	sock.close()
	print("Closing Socket")
	logging.info("Closing Socket")


if __name__ == "__main__":
   main(sys.argv[1:])