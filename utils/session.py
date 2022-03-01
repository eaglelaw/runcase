import sys
import os
import time
import traceback
from utils import agent_socket


#session tp
#value should be a tuple
#tuple format:
ss_dict = {
	'RAWPASS':(50001),	#localhost
	'WRIST_CLIENT':(50000),	#LAN, connected to mobile
	'WRIST_SERVER':(50002),	#localhost
	'OTA_MOBILE':(50000),	#LAN, connected to mobile
	'OTA_SESSION':(50003),	#localhost
	'BLE_MOBILE':(50000),	#LAN, connected to mobile
	'BLE_SESSION':(50003),	#localhost
	'DUMMY':(50032,1)
}


def get_host():
	hostname = ''
	try:  
		hostname = agent_socket.get_hostname()
	except:
		os._exit()
	return hostname


def connect(sname, hostname = 'localhost', timeout = 3):
	global ss_dict
	sock = None
	try:
		sock = agent_socket.connect(hostname, ss_dict[sname], timeout)
	except:
		traceback.print_exc()
		print('Connect %s failed'%sname)
	return sock


def disconnect(sock):
	agent_socket.disconnect(sock)
	

def send(sock, msg):
	agent_socket.send(sock, msg)


def recv(sock):
	line = agent_socket.recv(sock)
	return line


def bind(sname):
	sock = None
	try:
		sock = agent_socket.bind(ss_dict[sname])
	except:
		traceback.print_exc()
		print('bind %s failed'%sname)
	return sock


def listen(sock, func):
	agent_socket.listen(sock, func)
	

#The following is used for queue
#key words for session
CMDRSP = 'RSP'
CMDQCLR = 'QCLR'

REQTP = 0
REQLEN = 1
REQVAL = 2


#sample, field QOVF is flag for queue push overflow
#g_q_mobile_rsp = ['BLEMobileRspQueue', False,[]]

QNAME = 0
QOVF = 1
QLST = 2
QSIZE = 128


#default queue size = 16
def q(qlist, msg, qsize = QSIZE):
	#print(qlist,msg)
	if(len(qlist[QLST]) >= qsize):
		print('queue overflow!', qlist[QNAME])
		qlist[QOVF] = True
		while(len(qlist[QLST])>=qsize):
			qlist[QLST].pop(0)
	qlist[QLST].append(msg)
	#print(qlist)


def dq(qlist):
	#print('dq:',qlist)
	if(len(qlist[QLST]) >0):
		msg = qlist[QLST].pop(0)
		msg = [qlist[QOVF], msg]
		qlist[QOVF] = False
		#print('dq:',msg)
		return msg
	return None
	

def do_qclr(qlist):
	qlist[1] =False
	qlist[2] = []


#create struct of queue
def do_qinit(qname):
	return [qname, False, []]
	
