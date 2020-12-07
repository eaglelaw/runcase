import sys
import serial
import serial.tools.list_ports
import msvcrt
from utils import hex2bin
import traceback
from utils.xmodem import XMODEM

g_baudrate = ['',0]
g_connection = None

#merge continued partition to one segment, no 64K boundary limitation
#[[addr, data],...]
def hexfile_analyze(fpath,entry_addr = None):
	new_data = []
	seg_list = hex2bin.read_hex(fpath)
	if(len(seg_list) == 0):
		return None
	new_data.append(seg_list[0])
	new_idx = 0
	for i in range(len(seg_list)-1):
		if(seg_list[i][0] + len(seg_list[i][1]) == seg_list[i+1][0]):
			new_data[new_idx][1] = new_data[new_idx][1] + seg_list[i+1][1]
		else:
			new_data.append(seg_list[i+1])
	#for i in range(len(new_data)):
	#	print(hex(new_data[i][0]), hex(len(new_data[i][1])))
	return new_data



def baudrate(port=None, value = None):
	global g_baudrate
	path = 'case_bootloader\\__tmp.br.tmp'
	try:
		if(port is None and value is None):
			if(g_baudrate[0] == ''):
				f = open(path,'r')
				l = f.readline()
				f.close()
				return eval(l)
			else:
				return g_baudrate
		elif(port is not None and value is not None):
			f = open(path,'w')
			f.write(str([str(port), int(value)]))
			f.close()
			g_baudrate = [str(port),int(value)]
			return g_baudrate
	except:
		traceback.print_exc()
		return None
	return None


def connect(timeout = 0.05):
	global g_connection
	#print(g_connection)
	try:
		if(g_connection is not None):
			return g_connection
		else:
			br = baudrate()
			#print(br[0],br[1])
			fd = serial.Serial(br[0],br[1],timeout=timeout)
			#fd = serial.Serial('COM57',115200,timeout=timeout)
			g_connection = fd
			return fd
	except:
		traceback.print_exc()
		return None
		


def dwc(port, cmd = 'URC48M'):
	fd = serial.Serial(port,9600,timeout = 0.03)
	while(True):
		ch = msvcrt.kbhit()
		if(ch == 1):
			ch = msvcrt.getch()
			print(ch)
			if ch == b'q':
				break
		fd.write(cmd.encode())
		rsp = fd.read(20)
		#eturn None
		if(len(rsp) > 4):
			rsp = rsp.decode()
			print(rsp)
			if(rsp.find('cmd')>=0):
				rsp = fd.read(20)
				fd.close()
				return [port,115200]
	return None
		
		
#return [False|True,result]
def cmd(c, param = None, timeout = 1):
	fd = connect();
	if(fd is None):
		print('connection failed')
		return [False, None]
	cmd_str = c
	if(param is not None):
		for itm in param:
			if(type(itm) is not str):
				itm = str(itm)
			cmd_str = cmd_str + ' ' + itm
	cmd_str = cmd_str + '\n'
	print('cmd:',cmd_str)
	fd.write(cmd_str.encode())
	
	rsp = ''
	ret = False
	pos = -1
	for i in range(timeout*10):
		rsp = rsp + fd.read(200).decode()
		#print('~',rsp)
		pos = rsp.find('#OK')
		if(pos >=0):
			ret = True
			break
		pos = rsp.find('#ER')
		if(pos >=0):
			ret = False
			break
	if(pos < 0):
		print(c, 'timeout')
		return [False,None]
	if(pos == 0):
		return [ret, None]
	return [ret, rsp[:pos]]

def getc(size, timeout=1):
	global g_connection
	a = bytes()
	for i in range(100):
		b = g_connection.read(size)
		a = a + b
		size = size - len(b)
		if(size == 0):
			break
	return a
def putc(data, timeout=1):
	global g_connection
	#print(data)
	g_connection.write(data)

def xmdm_send(data):
	print('xmodem...')
	fd = connect();
	m = XMODEM(getc, putc)
	status = m.sendb(data, retry=10000)
	return status
	
def xmdm_send_1k(data):
	print('xmodem(1K)...')
	fd = connect();
	m = XMODEM(getc, putc, 'xmodem1k')
	status = m.sendb(data, retry=10000)
	return status

