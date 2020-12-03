
import sys
import time
import random
import ctypes
import socket
import struct
import msvcrt
import os
from utils import hex2bin
from utils import testlink
from utils.testlink import Testsuite
from case_bootloader import func
import numpy as np
import csv
import traceback

#usage: python runcase.py tlink.csv2xml 'testsuites\\csv\\runcase_mbt_connect_test1.csv'
def tlink_csv2xml(csvpath):
	
	try:
		xmlpath = csvpath.replace('/','\\')
		xmlpath = xmlpath.split('\\')[-1]
		xmlpath = xmlpath.split('.')[0]
		if(os.path.exists('testsuites\\xml') == False):
			os.makedirs('testsuites\\xml')
		xmlpath = 'testsuites\\xml\\' + xmlpath + '.xml'
		f = open(csvpath, "r")
		readCSV = csv.reader(f, delimiter=',')
		
		#first line should be suite name
		isFirstline = True 
		ts = None
		tsuite_name = ''
		for row in readCSV:
			#print(row)
			#continue
			#row_id is used to avoid parsing the first line (header in the file)
			if (isFirstline):
				print('xxxxx')
				if(row[0].startswith('#runcase') is not True):
					print('can\'t find testsuite description at first row')
					exit()
				tsuite_name = row[0][1:]
				ts = Testsuite(tsuite_name)
				print('ts is:', ts)
				if(len(row)>1):
					 ts.add_Commonts(str(row[1]))
				isFirstline = False
				continue
			case_name = row[0]
			case_cmd = row[1]

			case_param = ''
			if(len(row) > 2):
				case_param = row[2]

			expected_result = 'True'
			if(len(row) > 3):
				expected_result = row[3]
				
			summary = ''
			if(len(row) > 4):
				expected_result = row[4]
				
			preconditions = ''
			if(len(row) > 5):
				preconditions = row[5]
				
				
			if ts.add_TestCase(case_name, case_cmd, case_param,expected_result,summary,preconditions) is False:
				print('add_TestCase failed')
				exit()
			
		ts.print_xml(xmlpath)		
		
		f.close()
		print('Output:',os.path.abspath(".") + '\\'+xmlpath)
	except:
		traceback.print_exc()
		print('Error: xml2csv failed')
	

#usage: python runcase.py tlink.xml2csv 'testsuites\\xml\\runcase_mbt_connect_test.xml'
def tlink_xml2csv(xmlpath):
	try:
		csvpath = xmlpath.replace('/','\\')
		csvpath = csvpath.split('\\')[-1]
		csvpath = csvpath.split('.')[0]
		if(os.path.exists('testsuites\\csv') == False):
			os.makedirs('testsuites\\csv')
		csvpath = 'testsuites\\csv\\' + csvpath + '.csv'
		f = open(csvpath, "w", encoding="ANSI")
		
		testlink.testlink_to_csv(xmlpath ,f)
		f.close()
		print('Output:',os.path.abspath(".") + '\\'+csvpath)
	except:
		traceback.print_exc()
		print('Error: xml2csv failed')

