#!/usr/bin/python
# -*- coding: utf-8 -*

import serial
import serial.tools.list_ports
import sys
import os
import socket
import time
import select
import threading
import platform
import msvcrt
import traceback


def get_hostname():
	hostname = ''
	print('Input your host address:')
	name = input()
	namelist = name.split('.')
	for val in namelist:
		if val.isdigit() is False:
			raise ValueError('input is not digit')
	if len(namelist) == 1:
		pcname = socket.gethostname()
		ipname = socket.gethostbyname(pcname)
		iplist = ipname.split('.')
		iplist[3] = namelist[0]
		hostname = iplist[0] + '.' + iplist[1] + '.' + iplist[2] + '.' + name
	elif len(namelist) == 4:
		hostname = name
	return hostname


#socket client code
def connect(host, port, timeout):
	# Create a local host socket 
	sock = socket.socket()
	sock.settimeout(timeout)
	print('host is %s'%host)
	# Connect the socket to the port where the server is listening  
	try:  
		sock.connect((host, port))  
	except(socket.error):
		print('time out');
		os._exit(1)
	return sock;


def send(sock, msg):  
    # Send data  
	#print('sending :',msg, type(msg))
	if(type(msg) is bytes):
		sock.sendall(msg)
	else:
		#print(sock)
		sock.sendall(str(msg).encode())
		time.sleep(0.1);
	return
	


def recv(sock):
	ret = ''
	try:
		ret = sock.recv(1024*100).decode()
		#print(ret)
	except(socket.error):
		print('time out');
		os._exit(1)
	return ret


def disconnect(sock):
	#print('closing socket')
	sock.close()
	return


def bind(port):
	sock = socket.socket()
	sock.bind(('localhost', port))
	return sock


#socket server code
def listen(sock, func):
	sock.listen(1)
	print('start listen connection...')
	while True:
		c, addr = sock.accept()
		print('connection:%s'%str(addr))
		while(1):
			try:
				if c is None:
					print(c.gethostname())
				cmd = ''
				cmd = c.recv(1024)
				#print(type(cmd))
				cmd = cmd.decode()
				if(cmd == ''):
					cmdline = 'netstat -naO|findstr \"'+ addr[0] +':' +str(addr[1])+'\"'
					#print(cmdline)
					netinfo = os.popen(cmdline)
					line = netinfo.readline()
					#print(line)
					if(line.find('WAIT') > 0):
						c.close()
				else:
					func(c, cmd)
			except:
				#traceback.print_exc()
				#print('excption')
				c.close()
				break

