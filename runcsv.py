#! /usr/bin/env python3
import threading
import select
import os
import sys
import time
import random
import csv
import copy
import msvcrt
import traceback
from datetime import datetime
from utils import case
from utils import gw_report


exit_flag = False
dict_setting=[]
dict_tstcase_variable={}
list_tstcase_cmd=[]
global_sock = None
global_Notify_Index = 0

def csv_register_variable(line):
	global dict_tstcase_variable
	#print('%s is %s'%(line[0],line[1]))
	dict_tstcase_variable[line[0]] = line[1]
	return True


def csv_register_cmd(line):
	global list_tstcase_cmd
	print(line)
	while len(line) < 4:
		line.append('')
	cmdlist = line[0:3]
	cmdverif = line[3]
	cmdverif = cmdverif.split(',')
	if len(cmdverif) == 1:
		cmdlist.append(cmdverif[0])
	else:
		cmdlist.append(cmdverif)
		
	list_tstcase_cmd.append(cmdlist)
	return True


def is_monitoring_mode():
	m = dict_setting.get('monitoring')
	if m is not None:
		return True
	return False


def csv_parse(fname):
	global dict_setting
	global list_tstcase_cmd
	ret = False
	try:
		csvfile = open('./csv/'+fname, 'r')
	except:
		print('Error: Open file <%s> failed '%fname)
		return False
		
	if csvfile is None:
		return ret
	reader = csv.reader(csvfile)
	for line in reader:
		if(line[0][0] == '#'):
			continue
		if(line[0] == 'V'):
			ret = csv_register_variable(line[1:])
		elif (line[0][0] == 'C'):
			ret = csv_register_cmd(line)
		else:
			print('Error: Incorrect plan format:%s'%line)
			ret = False
			
		if(ret is False):
			csvfile.close()
			return ret
	
	csvfile.close()
	
	casestart = dict_setting.get('casestart')
	caseend = dict_setting.get('caseend')
	start_id = -1
	end_id = -1
	#case start and case end
	#print('\n\n')
	#print(list_tstcase_cmd)
	#print('\n\n')
	if casestart != None:
		for l in list_tstcase_cmd:
			#print('Check start: %s'%l)
			if(casestart == l[0]):
				start_id = list_tstcase_cmd.index(l)
				break;
		if start_id == -1:
			print('\nError:   Can\'t find case [%s]'%casestart)
			return False
	if caseend != None:
		for l in list_tstcase_cmd:
			if(caseend == l[0]):
				end_id = list_tstcase_cmd.index(l)+1
				break;
		if end_id == -1:
			print('\nError:   Can\'t find case [%s]'%caseend)
			return False
	if start_id == -1:
		start_id = 0
	if end_id == -1:
		end_id = len(list_tstcase_cmd)
	
	if(end_id < start_id):
		return False
	
	list_tstcase_cmd = list_tstcase_cmd[start_id:end_id]
	
	print(list_tstcase_cmd)
	
	return ret


def write_result(casecmd, result):
	cstr = ''
	if result == True:
		cstr = ':Pass'
	elif result == False:
		cstr = ':Failed'
	else:
		cstr = ':'+str(result)
	cstr =  str(casecmd[0]) +'	' + str(casecmd) + '\n' + cstr + '\n'
	gw_report.wr(cstr)


def report(casecmd, result):
	global dict_tstcase_variable
	gw_report.tm()
	if result == True or result == False:
		write_result(casecmd, result)
		return
	expect = casecmd[3]
	expect_val =None
	
	#print('1 expect: %s and expect_val: %s'%(expect,expect_val))
	if type(expect) == str:
		expect_val = dict_tstcase_variable.get(expect)
	if expect_val == None:
		expect_val = expect
	if type(expect_val) == list:
		ret = expect_val.count(result) > 0
		write_result(casecmd, ret)
		return
	elif expect_val == 'BOOL':
		if result == False:
			write_result(casecmd, result)
			return
		else:
			write_result(casecmd, True)
			return

	#print('2 expect: %s and expect_val: %s'%(expect,expect_val))
	if expect_val == '' or  expect_val == None :
		ret = result
	else:
		ret = expect_val == result
	write_result(casecmd, ret)
	return


def exec_case(casecmd):
	global dict_setting
	global global_sock
	global dict_tstcase_variable
	global global_Notify_Index
	param = []
	if len(casecmd[2]) > 0:
		param = casecmd[2].split(' ')
	cmdlist = [casecmd[1]]
	cmdlist = cmdlist+ param
	#print('cmdlist is:',cmdlist)
	
	#global variable replacement
	for i in range(len(cmdlist)-1):
		v = dict_tstcase_variable.get(cmdlist[i+1])
		if(v is not None):
			cmdlist[i+1] = v
	
	func, paramstr = case.case_parse(cmdlist)
	cmd = cmdlist[0]
	#print(cmd)
	try:
		exec('func'+paramstr)
	except:
		traceback.print_exc()
		print('Error: Unknow command: %s'%cmd)
		return False
	result = gw_report.result()
	# print("result = gw_report.result():")
	# print(type(result))
	# print(result)
	# print("here:")
	# print(casecmd)
	# print(result)
	if eval(result) == None or eval(result) == False:
		report(casecmd, result)
	elif isinstance(eval(result), list):
		if len(eval(result)) >= 3:
			for i in eval(result)[2]:
				# len(i) == 0 , htest.disconnect will return []
				# print(i)
				if len(i) <= 3:
					pass
				elif i[0] != 0:
					if len(i) == 9 and i[0] == 4 and i[1] == 0xFF and i[3] == 0x06 and i[4] == 0x06 and i[8] != 0x16:
						print("BLE disconnected")
						raise Exception("BLE disconnected")
					elif len(i) == 9 and i[0] == 4 and i[1] == 0xFF and i[3] == 0x06 and i[4] == 0x06 and i[8] == 0x16:
						global_Notify_Index = 0
					# notify data
					elif len(i) > 5 and i[3] == 0x1b and i[4] == 0x05:
						recv_notify_idx = i[-1] + i[-2] * 256
						if global_Notify_Index != recv_notify_idx:
							# print("Notify Index Error")
							# casecmd[-1]="Notify Index Error"
							rets =["Notify Received Index","","Should be",""]
							rets[1] = recv_notify_idx
							rets[3] = global_Notify_Index
							# print(rets)
							report(casecmd, str(rets))
						global_Notify_Index = recv_notify_idx + 1
					elif len(i) == 9 and i[3] == 0x14 and i[4] == 0x04 and i[5] == 0:
							rets = "PER Reset Success"
							report(casecmd, str(rets))
					elif len(i) == 17 and i[3] == 0x14 and i[4] == 0x04 and i[5] == 0:
							rets = ["PER Read:", "NumPkts", "", "NumCrcErr", "", "NumEvents", "", "NumMissedEvents", ""]
							rets[2] = i[9] + i[10] << 8
							rets[4] = i[11] + i[12] << 8
							rets[6] = i[13] + i[14] << 8
							rets[8] = i[15] + i[16] << 8
							report(casecmd, str(rets))
					elif i[0] == 4 and i[1] == 0xFF and i[3] == 0x7F and i[4] == 0x06 and i[5] != 0:
						print("BLE disconnected when write")
						raise Exception("BLE disconnected when write")
					elif i[0] != 0:
						# disconnect
						# ..
						# ..
						# SetPhy
						# updateDataLength
						if (len(i) == 9 and i[0] == 4 and i[1] == 0xFF and i[3] == 0x06 and i[4] == 0x06) or \
							(i[0] == 4 and i[1] == 0x3E and i[3] == 0x0c and i[4] == 0) or \
							(i[0] == 4 and i[1] == 0x0E and i[6] == 0x0c ) or \
							(len(i) == 7 and i[0] == 4 and i[1] == 0x0F and i[3] == 0 and i[5] == 0x32 and i[6] == 0x20) or \
							(len(i) == 9 and i[0] == 4 and i[1] == 0x0E and i[4] == 0x22 and i[
									5] == 0x20 and i[6] == 0):
							pass
						else:
							report(casecmd, str(i))
				elif i[0] == 0:
					if len(i) == 9 and i[1] == 0xFF and i[-1] == 0xFF:
						report(casecmd, str(i))
						rets = ["Uart Received seq missed serialized data", "", "", ""]
						report(casecmd, str(rets))
	return True


def timedelta(before):
	if(type(before) != datetime):
		return 0
	now = datetime.now()
	diff = now - before
	return diff.seconds


def test_sleep():
	global global_sock
	intv = dict_setting['interval']
	sleep_time = intv[0]
	if len(intv) == 2:
		sleep_time = random.randint(intv[0],intv[1])
	#print('sleep time is %d'%sleep_time)
	time.sleep(sleep_time)

	
def exec_case_list(list_case):
	global dict_setting
	global list_tstcase_cmd
	rnd_exe = dict_setting['random']
	
	for i in range(0, len(list_case)):
		#print(list_case)
		if(i > 0):
			test_sleep()
		if rnd_exe == False:
			cmd = list_case.pop(0)
		else:
			idx = random.randint(0, len(list_case)-1)
			cmd = list_case.pop(idx)
		print('\n',cmd[0],':', cmd[1:],'\n')
		ret = exec_case(cmd)
		#print('exec_case(cmd) finished')
		if ret == False:
			return False
	return True


def csv_case_thread():
	global exit_flag
	global dict_setting
	global list_tstcase_cmd
	gw_report.init(dict_setting['filename'])
	monitoring_mode = is_monitoring_mode()
	if monitoring_mode is True:
		gw_report.init_m(dict_setting['filename'])
		gw_gateway.register_monitor(dict_setting.get('monitoring'))
	try:
		for i in range(0,dict_setting['loop']):
			#copy test case list
			if(i > 0):
				test_sleep()
			list_case_copy = copy.deepcopy(list_tstcase_cmd)
			ret = exec_case_list(list_case_copy)
			if(ret == False):
				break;
	except:
		traceback.print_exc()
	exit_flag =True
	return


def csv_run():
	t1 = threading.Thread(target=csv_case_thread,args=())
	t1.setDaemon(True)
	t1.start()
	return t1


def wait_break_loop():
	global exit_flag
	while True:
		if exit_flag == True:
			break;
		c = msvcrt.kbhit()
		if c == 1:
			print('')
			c = msvcrt.getch()
			c = str(c, encoding = "utf-8")
			if c=='q':
				print('Exit(Y|N)?')
				c = msvcrt.getch()
				c = str(c, encoding = "utf-8")
				if(c.lower() == 'y'):
					print('Exited %s'%c)
					break;
				else:
					print('N')
		else:
			time.sleep(0.1)	


def wait_break():
	try:
		wait_break_loop()
	except:
		traceback.print_exc()
		user_break = True


def help():
	print('Run test plan:\nHelp:')
	print('gw_run_csv [-L[:Count]] [-R] [-M] [-I:Interval Parameter] [-C:SelectOption]casename.csv')
	print('-L	Loop the test plan, useage: -L, -L:100')
	print('-R	Radnom option, random execute the case of the test plan')
	print('-I	Interval option, the expression can be as:')
	print('	-I:1000		#interval is 1000 seconds')
	print('	-I:10-100	#interval is randon, from 10 to 100 seconds')
	print('-M	Monitoring mode')
	print('	-M	default monitoring mode, GTKit will log jamming, supervision missing and PAN ID conflict error')
	print('	-M:all	monitoring all RF6 message')
	print('	-M:MonitoringScript.py	custom monitoring script, for example: [-M:alarm.py]')
	print('-C	Select a special case to run, or select run from a special ID, or from...to')
	print('	[SelectOption]:')
	print('	-C:C17		#Just run case C17')
	print('	-C:C17~C20		#Run case from C17 to C20')
	print('	-C:C17:		#Run case from C17 to end')


#return vallue format [csv_name, loop, random, interval, monitoring]	
def get_param(param):
	global dict_setting
	filename = ''
	intv = [30]	# default 30s
	rnd_exe = False
	monitoring_py = None
	casestart = None
	caseend = None
	loop = 1 # defalut is 1
	
	#print(param)
	for str in param:
		#check plan file: aaa.csv
		f_ext = str[-4:]
		if(f_ext == '.csv'):
			filename = str;
			continue
		opt = str[0:2]
		
		if opt == '-L': #loop option
			if str[2:3] is '': # the option no parameter
				loop = 1000000 # use max times
				continue
			else:
				str_cnt = str[3:]
				if str_cnt.isdigit() is False:
					return None
				loop = int(str_cnt)
				continue
		
		if opt == '-R': #random execute plan
			if str[2:3] != '':
				return None
			rnd_exe = True
			continue
			
		if opt == '-M': #monitoring mode
			mopt = str[2:]
			if mopt != '':
				s = mopt.find(':')
				mval = mopt[(s+1):]
				monitoring_py = mval
				if mval == 'all':
					monitoring_py = 'gw_monitor_all.py'
			else:
				monitoring_py = 'gw_monitor.py'
			continue
			
		if opt == '-C' and str[2:3]==':': #case select option
			caseopt = str[3:]
			s = caseopt.find(':')
			if s > 0:
				casestart = caseopt[:s]
				continue
			s = caseopt.find('~')
			if s > 0:
				casestart = caseopt[:s]
				caseend = caseopt[(s+1):]
				continue
			casestart = caseopt
			caseend = caseopt
			continue
			
		if opt == '-I' and str[2:3]==':': #interval opetion
			intv = []
			str_intv = str[3:]
			if str_intv.isdigit():
				intv.append(int(str_intv))
				continue
			else:
				str_intv = str_intv.split('-')
				if len(str_intv) != 2:
					return None
			if str_intv[0].isdigit() != True:
				return None
			if str_intv[1].isdigit() != True:
				return None
			intv.append(int(str_intv[0]))
			intv.append(int(str_intv[1]))
			continue
		return None

	setting = {}
	setting['filename'] = filename
	setting['loop'] = loop
	setting['random'] = rnd_exe
	setting['interval'] = intv
	setting['monitoring'] = monitoring_py
	setting['casestart'] = casestart
	setting['caseend'] = caseend
	#print(setting)
	return setting

		
def main(argv):
	global dict_tstcase_variable
	global list_tstcase_cmd
	global dict_setting
	global global_sock
	case.case_register()
	if len(argv) < 2:
		help()
		return
	dict_setting = get_param(argv[1:])
	print('setting:\n%s'%dict_setting)
	if dict_setting is None:
		help()
		return
	ret = csv_parse(dict_setting.get('filename'))
	#print(dict_tstcase_variable)
	#print(list_tstcase_cmd)

	if ret is False:
		print('CSV file parse failed')
		return ret
	
	csv_run()
	
	#waiting user break
	wait_break()
	
	
if __name__ == '__main__':
	main(sys.argv)