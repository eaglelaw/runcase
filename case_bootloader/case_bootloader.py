
import sys
import time
import random
import ctypes
import socket
import struct
import msvcrt
import os
from utils import hex2bin
from utils import gw_report
from case_bootloader import func
import numpy as np


def boot_tst():
	func.hexfile_analyze('D:\\work\\git\\ble_common\\ble\\src\\proj\\stack_proj\\Objects\\bleip.hex')


def boot_connect(port, cmd = 'URC48M'):
	ret = True
	gw_report.clear()
	print('connecting')
	ret = func.dwc(port,cmd)
	if(ret is not None):
		func.baudrate(ret[0], ret[1])
	else:
		func.baudrate('', 0)
	return gw_report.result(str(ret))		

def boot_baudrate(port=None, value = None):
	ret = True
	gw_report.clear()
	ret = func.baudrate(port,value)
	print(ret)
	return gw_report.result(str(ret))		

	
def boot_cmdquit():
	ret = True
	gw_report.clear()
	
	ret = func.cmd('quit')

	return gw_report.result(str(ret))		

#program with boot sector, idx = 0 is boot segment
#path should be a hex file
def boot_cmdprog_hex(path, entry = 0xffffffff, xmmode1k = False):
	ret = True
	rsp = None
	gw_report.clear()
	
	data = func.hexfile_analyze(path)
	#print(data)
	for itm in data:
		ret, rsp = func.cmd('progr', [hex(itm[0]), hex(len(itm[1]))])
		#print(ret)
		if(ret == False):
			break
		#print(itm[1])
		if(xmmode1k):
			ret = func.xmdm_send_1k(itm[1])
		else:
			ret = func.xmdm_send(itm[1])
		print(ret)
		if(ret == False):
			break

	return gw_report.result(str(ret))
	
def boot_cmdxmdm(path):
	ret = True
	rsp = None
	gw_report.clear()
	size = os.path.getsize(path)
	fp = open(path, 'rb')
	data = fp.read(size)
	ret = func.xmdm_send_1k(data)
	fp.close()
	print(ret)

	return gw_report.result(str(ret))		


def boot_cmd(c, para = None):
	ret = True
	rsp = None
	gw_report.clear()
	if(para is not None):
		if(type(para) is not list):
			para = [para]
	ret,rsp = func.cmd(c, para)
	print(ret)
	return gw_report.result(str(ret))		

def boot_cmd_():
	ret = True
	gw_report.clear()
	
	#ret = func.cmd('quit')

	return gw_report.result(str(ret))		



