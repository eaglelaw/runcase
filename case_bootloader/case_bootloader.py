
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
from intelhex import IntelHex as IH

FLASH_BASE = 0x60000000

def crc16(a,x):
	#print(x)
	if(x is None):
		return a
	if(type(x) is not bytes):
		return None
	#a = 0#xFFFF
	b = 0xa001#0x1021#0xA001
	for byte in x:
		#print(byte, type(a), type(byte)	)
		a ^= byte
		for i in range(8):
			last = a % 2
			a >>= 1
			if last == 1:
				a ^= b
	#s = hex(a).upper()
	#print(s)
	return a


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

	
def boot_quit():
	ret = True
	gw_report.clear()
	
	ret = func.cmd('quit')

	return gw_report.result(str(ret))
	

	
#program with boot sector, idx = 0 is boot segment
#path should be a hex file, and the hex file should onluy contain ONE segment
def boot_uartrun(path, faddr, xmmode1k = False):
	ret = False
	rsp = None
	gw_report.clear()
	
	data = func.hexfile_analyze(path)
	if(len(data) != 1):
		return gw_report.result(str(False))
		
	#print(data)
	itm = data[0]
	#uartrun [hex(addr), hex(size), checksum]
	ret, rsp = func.cmd('uartrun', [hex(itm[0]), hex(len(itm[1])), crc16(0, itm[1])])
	#print(ret)
	if(ret == False):
		return gw_report.result(str(ret))
	#print(itm[1])
	if(xmmode1k):
		ret = func.xmdm_send_1k(itm[1])
	else:
		ret = func.xmdm_send(itm[1])
	print(ret)

	return gw_report.result(str(ret))


#program with boot sector, idx = 0 is boot segment
#path should be a hex file
def boot_prog_bin(path, faddr, xmmode1k = False):
	ret = False
	rsp = None
	gw_report.clear()
	try:
		size = os.path.getsize(path)
		fp = open(path, 'rb')
		data = list(fp.read(size))
	except:
		traceback.print_exc()
		return gw_report.result(str(False))
	
	#progr [hex(addr), hex(size), checksum]
	ret, rsp = func.cmd('progr', [hex(faddr), hex(size), crc16(0, data)])
	#print(ret)
	if(ret == False):
		return gw_report.result(str(ret))
	#print(itm[1])
	if(xmmode1k):
		ret = func.xmdm_send_1k(data)
	else:
		ret = func.xmdm_send(data)
	print(ret)

	return gw_report.result(str(ret))


#program with hexf file
#hexf file is flash image file, the segment will map to flash directly
def boot_prog_hexf(hexf_path, xmmode1k = False):
	ret = True
	rsp = None
	gw_report.clear()
	
	data = func.hexfile_analyze(hexf_path)
	#print(hex(data[0][0]), hex(len(data[0][1])))
	#print(hex(data[1][0]), hex(len(data[1][1])))
	#return
	#print(data)
	for itm in data:
		#progr [addr, size]
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
	
	
def boot_wrreg(reg, value):
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('wrreg', [hex(reg), hex(value)])
	#print(ret)

	return gw_report.result(str(ret))

def boot_rdreg(reg):
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('rdreg', [hex(reg)])
	#print(ret)

	return gw_report.result(str(ret))
	

# erase chip	
def boot_erfcp():
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('erfcp', None, 5)
	#print(ret)

	return gw_report.result(str(ret))		

# erase all
def boot_erall():
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('erall', None, 5)
	#print(ret)

	return gw_report.result(str(ret))

# erase sector 0
def boot_etfsf():
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('etfsf', None, 5)
	#print(ret)

	return gw_report.result(str(ret))

# erase sector 0x1000
def boot_etssf():
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('etssf', None, 5)
	#print(ret)

	return gw_report.result(str(ret))

#
def boot_era4k(faddr):
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('era4k', [hex(faddr)], 5)
	#print(ret)

	return gw_report.result(str(ret))

def boot_er64k(faddr):
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('er64k', [hex(faddr)], 5)
	#print(ret)

	return gw_report.result(str(ret))

def boot_write(faddr, value):
	ret = False
	rsp = None
	gw_report.clear()

	ret, rsp = func.cmd('write', [hex(faddr), hex(value)], 5)
	#print(ret)

	return gw_report.result(str(ret))


#convert a executable hex file to flash image
#primary: primary hex file path
#alternate: alternate hex file path
#alt_active: defalt is primary is active, if True, alternate is active
#alt_addr: start address of alternate flash area
#We agreed that the starting run address is FLASH_BASE:0x60000000 
def boot_util_hexf(primary, alternate = None, alt_active = False, alt_addr = 0x100000):
	ret = True
	gw_report.clear()
	
	ih = IH()
	bs_word = [0xffffffff]* (int(8192/4));
	
	#primary
	#[[raddr,data]..]
	prim_data = func.hexfile_analyze(primary)

	bs_word[0] = len(prim_data) #IMAG_NUM
	bs_word[2] = FLASH_BASE #IMAG_ENTRY_ADDR 
	if(alt_active == False):
		bs_word[3] = 0x0000_000E#IMAG_BOOT_FLG = active
	else:
		bs_word[3] = 0x0000_000C#IMAG_BOOT_FLG = old firmware, alternate if no active firmware valid
		
	#base = 0x4000
	faddr = FLASH_BASE+0x4000
	for i in range(len(prim_data)):
		size = len(prim_data[i][1])
		bs_word[int(0x100/4) + 4*i] = faddr #IMAG_ADDR flash addr
		bs_word[int(0x104/4) + 4*i] = size#IMAG_SIZE
		bs_word[int(0x108/4) + 4*i] = prim_data[i][0]#IMAG_RUN
		bs_word[int(0x10c/4) + 4*i] = crc16(0,prim_data[i][1])#IMAG_CSUM
		ih.puts(faddr, bytes(prim_data[i][1]))
		faddr += (size + 3)&0xfffffffc # word aligned
		
	#alternate
	#[[raddr,data]..]
	if(alternate is not None):
		alt_data = func.hexfile_analyze(alternate)
		bs_word[0x100] = len(alt_data) #IMAG_NUM
		bs_word[0x102] = FLASH_BASE #IMAG_ENTRY_ADDR 
		if(alt_active == True):
			bs_word[0x103] = 0x0000_000E#IMAG_BOOT_FLG = active
		else:
			bs_word[0x103] = 0x0000_000C#IMAG_BOOT_FLG = old firmware, alternate if no active firmware valid
		
		#base = 0x100000
		faddr = FLASH_BASE+0x100000
		for i in range(len(alt_data)):
			size = len(alt_data[i][1])
			bs_word[int(0x500/4) + 4*i] = faddr #IMAG_ADDR flash addr
			bs_word[int(0x504/4) + 4*i] = size#IMAG_SIZE
			bs_word[int(0x508/4) + 4*i] = alt_data[i][0]#IMAG_RUN
			bs_word[int(0x50c/4) + 4*i] = crc16(0,alt_data[i][1])#IMAG_CSUM
			ih.puts(faddr, bytes(alt_data[i][1]))
			faddr += (size + 3)&0xfffffffc # word aligned
	
	bs_byte = [0xff]*8192
	for i in range(0,4096,4):
		tmp = bs_word[int(i/4)]
		bs_byte[i] = tmp & 0xff
		bs_byte[i+1] = (tmp>>8) & 0xff
		bs_byte[i+2] = (tmp>>16) & 0xff
		bs_byte[i+3] = (tmp>>24) & 0xff
	ih.puts(FLASH_BASE + 0x2000, bytes(bs_byte))
	
	ih.write_hex_file(primary+'.hexf')
	
	return gw_report.result(str(ret))

	
#just do xmodem transmit
def boot_util_xmdm(path):
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




