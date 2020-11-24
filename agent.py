#!/usr/bin/python
# -*- coding: utf-8 -*

import serial
import serial.tools.list_ports
import sys
import socket
import time
import struct
import select
import threading
import platform
import msvcrt
import traceback


#ding: use agent to start session 
def help():
	print('Usage: agent.py -p ["[\'SessionModuleName1\', \'param1\',\'param\'...]"] ...["[\'SessionModuleNamen\', \'param1\',\'param\'...]"]')
	print('Usage: agent.py -f configfile')
	print('Example: agent.py -p "[\'session_rawpass\',\'COM5\',\'COM6\']"')
	print('Example: agent.py -f config_a.txt')


def wait_exit():
	#after loading session, keep waiting console input
	while(True):
		ch = msvcrt.kbhit()
		if(ch == 1):
			ch = msvcrt.getch()
			ch = ch[0]
			#print(ch)
			if ch == ord('q') or ch == ord('Q'):
				print('Exit ?(y|n)')
				ch = msvcrt.getch()
				ch = ch[0]
				if ch == ord('y') or ch == ord('Y'):
					return True


def wait_input():
	print('Input config command(Q|q exit):')
	while(True):
		lstr = input()
		if(lstr == 'q' or lstr == 'Q'):
			print('Exiting...')
			break


def main(argv):
	if len(argv) < 3:
		help()
		return
	param = argv[2:]
	
	slist = []
	if(argv[1] == '-p'):
		for lstr in param:
			print(lstr)
			l = eval(lstr)
			slist.append(l)
	elif(argv[1] == '-f'):
		print(param[0], param)
		fp = open(param[0])
		if(fp == None):
			print('File:',param[0], ' open failed\n')
			return
		while(True):
			lstr = fp.readline()
			if(lstr == ''):
				break;
			if(lstr[0] == '['):
				l = eval(lstr)
				slist.append(l)
				
	#start load session
	for ss in slist:
		try:
			imstr = 'from '+ss[0].split('_')[1]+' import '+ss[0]
			exec(imstr)
			ss_start = eval(ss[0]+'.start')
			ss_start(ss[1:])
		except:
			traceback.print_exc()
	
	wait_input()
	
	
if __name__ == '__main__':
	main(sys.argv)
