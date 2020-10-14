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
	port = ''
	log = ''
	url = ''
	havePort = False
	#Get CL arguments
	try:
		opts, args = getopt.getopt(argv,"hp:l:", ["PORT=","LOG="])
	except getopt.GetoptError:
		print("Please enter an ip address and a port number")
		sys.exit(2)
	for opt, arg in opts:
		if opt == ("-p"):
			if havePort == False:
				port = arg
				havePort = True
			else:
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
	#Loop lets us get multiple packets
	while goFlag == 1:
		try:
			connection_object, client_address = sock.accept()
			logs = ("Receivced connection from", client_address[0], client_address[1])
			print("Receivced connection from", client_address)
			logging.info(logs)
			#Will put into log later

			#Hello message back to client

			#Get packet and unpack
			client_hello = connection_object.recv(12)
			c_version, c_type, c_len = struct.unpack('>iii', client_hello)

			#Unpack the message
			client_message = connection_object.recv(c_len).decode()
			logs = ("Received Data: version:", c_version, "message type:", c_type, "length:", c_len, "message:", client_message)
			logging.info(logs)
			print(logs)

			#Version check
			if(c_version == 17):
				logging.info("VERSION ACCEPTED")
				print("VERSION ACCEPTED")
			else:
				logging.error("VERSION MISMATCH")
				print("VERSION MISMATCH")

			#Ping back hello
			pack_start = struct.Struct('>iii5s')
			pack_hello = pack_start.pack(17, 2, 5, "HELLO".encode('utf-8'))
			connection_object.send(pack_hello)

			#Get command message
			fmt = ">iii"
			client_com = connection_object.recv(12)
			co_version, co_type, co_len = struct.unpack(fmt, client_com)

			#Unpack the message
			client_com_message = connection_object.recv(co_len).decode()
			logs = ("Received Data: version:", co_version, "message type:", co_type, "length:", co_len, "message:", client_com_message)
			logging.info(logs)
			print(logs)


			#Version check
			if(co_version == 17):
				logging.info("VERSION ACCEPTED")
				print("VERSION ACCEPTED")
			else:
				logging.error("VERSION MISMATCH")
				print("VERSION MISMATCH")

			#Command processing
			if(co_version == 17):
				if(co_type == 1):
					logging.info("EXECUTING SUPPORTED COMMAND: LIGHTON")
					print("EXECUTING SUPPORTED COMMAND: LIGHTON")
					sFlag = 1

				elif(co_type == 2):
					logging.info("EXECUTING SUPPORTED COMMAND: LIGHTOFF")
					print("EXECUTING SUPPORTED COMMAND: LIGHTOFF")
					sFlag = 1
				else:
					print("IGNORING UNKNOWN COMMAND:", client_com_message)
					sFlag = 0
			else:
				print("VERSION MISMATCH")
				sFlag = 0

			#Ping back
			if(sFlag == 1):
				logging.info("Returning SUCCESS")
				print("Returning SUCCESS")
				pack_suc = struct.Struct('>iii7s')
				pack_suec_return = pack_suc.pack(17, 2, 7, "SUCCESS".encode('utf-8'))
				connection_object.send(pack_suec_return)

			elif(sFlag == 0):
				logging.info("Returning FAIL")
				print("Returning FAIL")
				pack_suc = struct.Struct('>iii4s')
				pack_suec_return = pack_suc.pack(17, 2, 4, "FAIL".encode('utf-8'))
				connection_object.send(pack_suec_return)

			#inp = input("Press 1 to keep receiving and 0 to exit: ")
			#if(inp == 0):
			goFlag = 1

		except KeyboardInterrupt:
			print("Exiting now...")
			sock.close()
			break

if __name__ == "__main__":
   main(sys.argv[1:])
