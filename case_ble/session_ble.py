
import sys
import os
import time
import imp
import threading
import traceback
from utils import session
from case_ble import def_ble
from datetime import timedelta
from datetime import datetime
from case_ble import cmd_list
import json

g_sock_mobile = None
g_sock_session = None

g_q_mobile_rsp = ['BLEMobileRspQueue', False,[]]

EOF_FLAG = '},EOF,'
EOF_TAG = ',EOF,'

def p2m_package(json_pkg):
	
	pkg = str(json_pkg) + EOF_TAG
	return pkg

def cmd_create(cmd):
	cmd_dict = {}
	cmd_dict['type'] = def_ble.p2mcmd
	cmd_dict['api'] = cmd
	cmd_dict['payload'] = cmd_list.m_cmd[cmd]
	print(cmd_dict)
	return cmd_dict

def cmd_param(cmd_dict, param):
	cmd_dict['payload'] = param
	return cmd_dict

def hook_create(event = None):
	hook_dict = {}
	hook_dict['type'] = def_ble.p2mhook
	if(event is not None):
		if(type(event) == str):
			if(event in cmd_list.m_hook):
				hook_dict['event'] = [event]
			else:
				print('Error event type:', event)
				return None
		elif(type(event) == list):
			if(set(event).issubset(set(cmd_list.m_hook)) == False):
				print('Error event type:', event)
				return None
			hook_dict['event'] = event
		else:
			print('Error event type:', event)
			return None
	else:
		hook_dict['event'] = []
	return hook_dict

def hook_add(hook_dict, event):
	if(event is not None):
		if(type(event) == str):
			if(event in cmd_list.m_hook):
				hook_dict['event'] += [event]
			else:
				print('Error event type:', event)
				return None
		elif(type(event) == list):
			if(set(event).issubset(set(cmd_list.m_hook)) == False):
				print('Error event type:', event)
				return None
			hook_dict['event'] += event
		else:
			print('Error event type:', event)
			return None

def mobile_sock_thread():
	global g_sock_mobile
	global g_sock_session
	global g_q_mobile_rsp
	
	#print(g_q_mobile_rsp)
	
	if(g_sock_mobile is None):
		print('')
		return
	line_full = ''
	while(True):
		line = session.recv(g_sock_mobile)
		try:
			if(line != '' and line != ' '):
				print('RSP------------>',line)
				line_full += line
				ps = line_full.find(EOF_FLAG)
				if(ps < 0):
					continue
				ps += 1
				line = line_full[:ps]
				print('Merged line >>>>>>>>>>>',line)
				line_full = line_full[ps + len(EOF_TAG):]
				line_dict = json.loads(line)
				session.q(g_q_mobile_rsp, line_dict)
				#print('             ',line_dict)
			if(line == ''):
				print('Mobile sock lossed!')
				os._exit(1)
		except:
			traceback.print_exc()
			continue


def session_sock_handle(s, req):
	global g_sock_mobile
	global g_q_mobile_rsp
	
	#print(type(s))
	#print('get:',req)
	if(req == 'RSP\n'):
		#print('req response',g_q_mobile_rsp)
		rsp = session.dq(g_q_mobile_rsp)
		if(rsp is None):
			rsp = 'None'
		else:
			print('response to case:',rsp)
		session.send(s, rsp)
	elif(req == 'QCLR\n'):
		#print('clear queue')
		session.do_qclr(g_q_mobile_rsp)
	else:
		print('send to mobile...',req)
		session.send(g_sock_mobile,req)
		#time.sleep(0.05)


#param[0] is host COM port, param[1] is slave COM port
def start(param):
	global g_sock_mobile
	global g_sock_session
	global g_q_mobile_rsp
	
	g_q_mobile_rsp = session.do_qinit('BLEMobileRspQueue') #['RawpassHostRspQueue', False,[]]
	print('************** BLE session start **************')

	g_sock_mobile = session.connect('BLE_MOBILE', session.get_host(), None)
	if(g_sock_mobile is None):
		print('client socket connect failed') 
		return False

	g_sock_session = session.bind('BLE_SESSION')
	if(g_sock_session is None):
		print('server socket bind failed') 
		return False

	tc = threading.Thread(target=mobile_sock_thread,args=())
	tc.setDaemon(True)
	tc.start()
	
	ts = threading.Thread(target=session.listen,args=((g_sock_session, session_sock_handle)))
	ts.setDaemon(True)
	ts.start()

	return True


class ble_ss:
	def __init__(self, portname):
		self.sock = session.connect(portname)
	
	def __init__(self):
		self.sock = None
		
	def __del__(self):
		if(self.sock != None):
			session.disconnect(self.sock)

	def connect(self):
		if(self.sock is not None):
			print('Connected')
			return True
		print('Connecting')
		s = session.connect('BLE_SESSION')
		if(s is None):
			print('Connect to session failed')
			return False
		self.sock = s
		return True
	
	def send_cmd(self, cmd):
		if(self.sock is None):
			print('No connection!')
			return
		json_cmd = json.dumps(cmd)
		req = p2m_package(json_cmd)
		print(req)
		session.send(self.sock, req)


	def qclr(self):
		if(self.sock is None):
			print('No connection!')
			return
		#print('clear queue')
		session.send(self.sock, 'QCLR\n')
		
	def wait_rsp(self, timeout = 0):
		loopcnt = 0xffffffff
		s = datetime.now()
		try:
			if(timeout == -1):
				loopcnt = 1
			for i in range(loopcnt):
				time.sleep(0.01)
				if(timeout > 0):
					if((datetime.now() - s).total_seconds() >= timeout):
						print('wait_rsp timeout')
						return None
				#print('wait_rsp')
				session.send(self.sock, 'RSP\n')
				rsp_msg = session.recv(self.sock)
				#print(rsp_msg)
				if(rsp_msg == 'None'):
					continue
				print('rspmsg is :',rsp_msg)
				rsp_pack = eval(rsp_msg)
				print(rsp_pack)
				if(len(rsp_pack) == 2):
					rsp = rsp_pack[1]
					return rsp
					
		except:
			traceback.print_exc()
			os._exit(1)
			return None

		return None		

