Program by Tyler Fulghum, Maddison Davenport, and Jacob Johnson for CSC 4200.

Run with python 3 in the format.
Use Ctrl-C to exit cleanly.

sudo python3 Server.py -p PORT -u URL -l LOGFILE
sudo python3 Client.py -s SERVER-IP -p PORT -l LOGFILE
sudo python3 LoadBalancer.py -s IPADDRESSFILE -p PORT -l LOGFILE

The URL cannot include http in the program. Example:
sudo python3 Server.py -p 5555 -l test.txt -u tntech-ngin.github.io/csc4200/programming1/index.html -l ServerLog.txt
sudo python3 Client.py -s localhost -p 5555 -l ClientLog.txt
sudo python3 LoadBalancer.py -p 5555 -s ipAddresses.txt -l LoadBalancerLog.txt

The server must use the port number 5555 as it is required by the load balancer.
A text file must contain the replica servers IP addresses with 1 per line and no port numbers.