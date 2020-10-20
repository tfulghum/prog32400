Program by Tyler Fulghum, Maddison Davenport, and Jacob Johnson for CSC 4200

Run with python 3 in the format.
Use Ctrl-C to exit cleanly.
The logfile will use your current directory unless specificed otherwise.

python3 server.py -p PORT -l LOG FILE LOCATION -u google.com
python3 client.py -s <SERVER-IP> -p <PORT> -l LOGFILE

The URL cannot include http in the program. Example:
python3 server.py -p 10005 -l test.txt -u google.com
python3 client.py -s localhost-p 10005  -l test.txt
