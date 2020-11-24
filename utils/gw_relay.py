import sys
import socket
import time
import os
def relay_cmd(host, ad, ch, set = -1):
	s = socket.socket() 
	host = socket.gethostbyname(host)
	#print('host is %s'%host)
	port = 12345

	s.connect((host, port))
	data = str(ad) + ','+str(ch) +','+str(set)
	print('Relay:%s'%data)
	s.sendall(data.encode())
	ret = None
	for i in range(1000):
		ret = s.recv(1024)
		if ret != b'':
			#print(ret)
			#print('break')
			break;
		time.sleep(0.1)
	s.close()
	ret = ret.decode()
	if str(ret) == 'True':
		return True
	return False

def sync_time(host):
	s = socket.socket() 
	host = socket.gethostbyname(host)
	#print('host is %s'%host)
	port = 12345

	s.connect((host, port))
	data = 'sync_time'
	s.sendall(data.encode())
	ret = None
	for i in range(1000):
		ret = s.recv(1024)
		if ret != b'':
			#print(ret)
			#print('break')
			break;
		time.sleep(0.1)
	s.close()
	ret = ret.decode()
	if str(ret) == 'False':
		return False
		
	timecmd = 'date -s '+ret
	os.system(timecmd)
	return True
	
def gatewaylog(data, host, port):	
	ret = False
		
	s = socket.socket() 
	host = socket.gethostbyname(host)
	#print('host is %s'%host)
	#port = 12346

	s.connect((host, port))
	s.sendall(data.encode())
	retval = None
	for i in range(1000):
		retval = s.recv(1024)
		if retval != b'':
			#print(retval)
			break;
		time.sleep(0.1)
	s.close()
	retval = retval.decode()
	if str(retval) == 'True':
		return True
	return ret
	
'''
for i in range(16):
	relay_cmd('192.168.1.46', 1, i, 1)
	time.sleep(0.9)
	
for i in range(16):
	relay_cmd('192.168.1.46', 1, i, 0)
	time.sleep(0.9)
	
for i in range(16):
	relay_cmd('192.168.1.46', 1, i, 1)
	time.sleep(0.9)

for i in range(16):
	relay_cmd('192.168.1.46', 1, i, 0)
	time.sleep(0.9)
'''	

	