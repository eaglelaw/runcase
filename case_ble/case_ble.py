import sys
import time
import random
import ctypes
import socket
import struct
import msvcrt
import os
from datetime import datetime
from utils import session
from utils import gw_icmd
from utils import gw_report
from utils import hex2bin
from case_ble import session_ble
from case_ble import cmd_list


def ble_hook(event_name):
	global cancelPairing
	gw_report.clear()

	hook = session_ble.hook_create(event_name)

	ss = session_ble.ble_ss()
	if(ss.connect() == False):
		return gw_report.result('False')
	ss.qclr()
	print('start send packet')
	ss.send_cmd(hook)

	print('wait response...')
	ret = ss.wait_rsp(0)
	print(ret)
	return gw_report.result(str(ret))		


def ble_wait(ms = 1000):
	time.sleep(0.001*ms)
	return gw_report.result('True')	

def ble_cmd(api, param = None, rsp_cnt = 0):
	global cancelPairing
	gw_report.clear()
	cmd = session_ble.cmd_create(api)
	if(param is not None):
		cmd = session_ble.cmd_param(cmd, param)
	print(cmd)

	ss = session_ble.ble_ss()
	if(ss.connect() == False):
		return gw_report.result('False')
	ss.qclr()
	print('start send packet')
	ss.send_cmd(cmd)
	
	print('wait response...')
	ret = ss.wait_rsp(0)
	print(ret)

	for i in range(rsp_cnt):
		ret = ss.wait_rsp(0)
		print(ret)
	return gw_report.result(str(ret))		
	
def ble_hook(event):
	global cancelPairing
	gw_report.clear()
	hook = session_ble.hook_create(event)
	print(hook)

	ss = session_ble.ble_ss()
	if(ss.connect() == False):
		return gw_report.result('False')
	ss.qclr()
	print('start send packet')
	ss.send_cmd(hook)
	
	print('wait response...')
	ret = ss.wait_rsp(0)
	print(ret)

	for i in range(rsp_cnt):
		ret = ss.wait_rsp(0)
		print(ret)
	return gw_report.result(str(ret))		
	
	
def ble_hooktest(event):
	hook = session_ble.hook_create(event)
	print(session_ble.p2m_package(hook))


def ble_evt(num = 1):
	print(num)
	
def ble_print(num = 1):
	print('just print:',num)
	return gw_report.result(str(True))		
