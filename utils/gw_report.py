import sys
import time

filename = ''
filename_m = ''

g_result_value = False


def result(value = None):
	global g_result_value
	if value != None:
		g_result_value = value
	return g_result_value

def clear():
	global g_result_value
	g_result_value = None
	

def init(path):
	global filename
	timestr = time.strftime(".%Y%m%d%H%M%S.",time.localtime(time.time()))
	filename = path + timestr +'report.txt'
	print(filename)
def tm():
	global filename
	if filename == '':
		return
	fp = open('./LOG/' + filename, 'a')
	timestr = time.strftime("%d-%H-%M-%S:\n",time.localtime(time.time()))
	fp.write(timestr)
	fp.close()
	
def wr(str):
	global filename
	if filename == '':
		return
	fp = open('./LOG/' + filename, 'a')
	fp.write(str+'\n\n')
	fp.close()

# for monitoring_mode	
def init_m(path):
	global filename_m
	timestr = time.strftime(".%Y%m%d%H%M%S.",time.localtime(time.time()))
	filename_m = path + timestr +'monitoring.txt'
	print(filename_m)
	
# for monitoring_mode	
def wr_m(str):
	global filename_m
	if filename_m == '':
		return
	fp = open('./LOG/' + filename_m, 'a')
	timestr = time.strftime("%d-%H-%M-%S:	",time.localtime(time.time()))
	fp.write(timestr+str+'\n')
	fp.close()
	
