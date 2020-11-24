#!/usr/bin/python
# -*- coding: utf-8 -*

import serial
import serial.tools.list_ports
import sys
import socket
import time
import select
#import msvcrt
import threading
import platform
if platform.system() == 'Linux':
	import termios
	import tty
else:
	import msvcrt

g_comport = ''
exit_flg = False


def kbhit():
	fd = sys.stdin.fileno()
	r = select.select([sys.stdin],[],[],0.01)
	rcode = ''
	if len(r[0]) > 0:
		rcode = sys.stdin.read(1)
	return rcode

'''
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：server.py

import socket

s = socket.socket()
host = ''
print('host is %s'%host)
port = 12345
s.bind((host, port))

s.listen(5)
while True:
	c, addr = s.accept()
	print('connection:%s'%str(addr))
	while(1):
		ret = ''
		#try:
		ret = c.recv(1024).decode()
		if ret!='':
			print('recv data:%s'%ret)
			c.sendall('hello')
		#except:
		#print('disconnected')
		c.close()
		break
		#c = None
		#if not c:
		#	break

def relay_cmd(ch, boad_ad = 0):
	s = socket.socket() 
	host = socket.gethostbyname('192.168.1.46')
	print(host)
	port = 12345

	s.connect((host, port))
	data = 'hello'
	s.sendall(data.encode())
	print(s.recv(1024))
	s.close()
'''
'''
for i in range(10000):
	relay_cmd(1)
	time.sleep(0.02)
'''

def crc_cmd(cmd):
	x = 0
	for i in cmd[0:12]:
		x = x + i
	return x&0xff


def relay_open(serialName):
	print serialName
	try:
		serialFd = serial.Serial(serialName,115200,timeout = 60)
		serialFd.timeout = 2
		#serialFd.open()
		return serialFd
	except:
		return None

def relay_allchannel(fd, addr, map):
	print('relay_allchannel')
	sReadCmd = [0X48,0X3A,0X01,0X53,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0XD5,0X45,0X44]
	crc = crc_cmd(sReadCmd)
	sReadCmd[12] = crc
	sWriteCmd = [0X48,0X3A,0X01,0X57,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0XD5,0X45,0X44]
	for i in range(16):
		offset = i/2
		val = 0
		#print((map >> i) & 1)
		if ((map >> i) & 1):
			val = sWriteCmd[offset + 4] | (1 << ((i%2)*4))
			#print 1, offset, val,((i%2)*4),sWriteCmd[offset + 4]
		else:
			val = sWriteCmd[offset + 4] & (0xf << (((i%2 +1)%2)*4))
			#print 0, offset, val,((i%2 +1)*4),sWriteCmd[offset + 4]
		sWriteCmd[offset + 4] = val
		#print sWriteCmd
	crc = crc_cmd(sWriteCmd)
	sWriteCmd[12] = crc
	

	cmd_ch = []
	for ch in sWriteCmd:
		cmd_ch.append(chr(ch))

	cmdstr1 = ''.join(cmd_ch)
	#print cmd_ch
	fd.write(cmdstr1)
	#time.sleep(0.1)	

	cmd_ch = []
	for ch in sReadCmd:
		cmd_ch.append(chr(ch))
	cmdstr = ''.join(cmd_ch)

	time.sleep(0.1)
	fd.write(cmdstr)
	#time.sleep(0.1)
	line = fd.read(15)
	
	#print line
	
	#print('line is %s'%list(line))
	#print('cmdstr1 is %s'%list(cmdstr1))
	str1 = line[4:12]
	str2 = cmdstr1[4:12]
	if str1 == str2:
		return True
	return False

	
def relay(fd, addr, channel, set):
	sReadCmd = [0X48,0X3A,0X01,0X53,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0XD5,0X45,0X44]
	crc = crc_cmd(sReadCmd)
	sReadCmd[12] = crc
	cmd_ch = []
	for ch in sReadCmd:
		cmd_ch.append(chr(ch))

	cmdstr = ''.join(cmd_ch)
	#print cmd_ch
	fd.write(cmdstr)
	#time.sleep(0.1)
	AckCmd = []
	line = fd.read(15)
	for ch in line:
		AckCmd.append(ord(ch))
		
	#print AckCmd
	#time.sleep(0.1)
	
	if(len(AckCmd) < 15):
		#print 'no ack, error'
		return False

	offset = channel/2
	if set == 0:
		val = AckCmd[offset + 4] & (0xf << ((channel%2 +1)*4))
	else:
		val = AckCmd[offset + 4] | (1 << ((channel%2)*4))
	AckCmd[offset + 4] = val
	AckCmd[3] = 0x57
	crc = crc_cmd(AckCmd)
	AckCmd[12] = crc

	cmd_ch = []
	for ch in AckCmd:
		cmd_ch.append(chr(ch))

	cmdstr1 = ''.join(cmd_ch)
	#print cmd_ch
	fd.write(cmdstr1)
	#time.sleep(0.1)
	
	time.sleep(0.1)
	fd.write(cmdstr)
	#time.sleep(0.1)

	line = fd.read(15)
	
	#print line
	
	#print type(line)
	#print type(cmdstr1)
	str1 = line[4:12]
	str2 = cmdstr1[4:12]
	if str1 == str2:
		return True
	return False
	
def sync_time():
	timestr = time.strftime("%y%m%d%H%M.%S",time.localtime(time.time()))
	return timestr
	

def execute_cmd(fd, cmd):
	if(cmd=='sync_time'):
		return sync_time()
		
	cmd_lst = cmd.split(',')
	print cmd_lst
	if(len(cmd_lst) != 3):
		return False
	ad,channel,set=cmd_lst
	
	if(int(set) == -1):
		ret = relay_allchannel(fd, int(ad), int(channel))
		#if ret == False:
		#	ret = relay_allchannel(fd, int(ad), int(channel))
		return ret
	
	ret = relay(fd, int(ad), int(channel), int(set))
	if ret == False:
		ret = relay(fd, int(ad), int(channel), int(set))
	return ret
	
def relay_thread():
	global exit_flg
	global g_comport
	fd = relay_open(g_comport)
	if fd is None:
		print 'Can\'t open relay device'
		exit_flg = True
		return
	

	s = socket.socket()
	host = ''
	print('host is %s'%host)
	port = 12345
	s.bind((host, port))

	s.listen(5)
	while True:
		c, addr = s.accept()
		print('connection:%s'%str(addr))
		while(1):
			cmd = ''
			cmd = c.recv(1024).decode()
			print cmd
			ret = execute_cmd(fd, cmd)
			c.sendall(str(ret))
			c.close()
			break


def relay_run():
	t1 = threading.Thread(target=relay_thread,args=())
	t1.setDaemon(True)
	t1.start()
	return t1

def wait_break_windows():
	global exit_flg
	while(True):
		if exit_flg is True:
			break;
		ch = msvcrt.kbhit()
		if(ch == 1):
			ch = msvcrt.getch()
		else:
			continue
		print(ch)
		if ch == 'q':
			print 'Exit? (y|n)'
			ch = msvcrt.getch()
			if ch == 'y':
				break;
def wait_break_linux():
	global exit_flg
	old_settings = termios.tcgetattr(sys.stdin)
	tty.setcbreak(sys.stdin.fileno())
	try:
		while(True):
			if exit_flg is True:
				break;
			#ch = msvcrt.kbhit()
			ch = kbhit()
			#print(type(ch))
			if(ch == ''):
				continue
			if ch == 'q':
				print 'Exit? (y|n)'
				while True:
					ch = kbhit()
					if(ch != ''):
						break
				if ch == 'y':
					break;
	except:
		print('exit')
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def wait_break():
	if platform.system() == 'Linux':
		wait_break_linux()
	else:
		wait_break_windows()
	
def port_list():
	port_list = list(serial.tools.list_ports.comports())

	print('Total %d COM port:'%(len(port_list)))
	for port in port_list:
		infostr = port[1].lower()
		if(infostr.find('usb') <0):
			continue
		print('%s:	%s'%(port[0],port[1]))
				
def main(argv):
	global g_comport
	if len(argv) != 2:
		print 'Useage: relay.py COMx'
		port_list()
		#argv1 = "COM0"
		return
		
	argv1 = argv[1]
	#if(argv1.find('COM')!=0):
	#	print 'Useage: relay.py COMx'
	#	return
	g_comport = argv1
	relay_run()
	#waiting user break
	wait_break()
	return
	
if __name__ == '__main__':
	main(sys.argv)
	
