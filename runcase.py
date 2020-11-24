#! /usr/bin/env python

import os
import sys
import importlib
import traceback
from utils import case


def cmd_help(cmd = None):
	caseinfo = case.g_case_pool

	if(cmd is None):
		print('==================')
		print('User case list:')
		for info in caseinfo :
			print('Case module:', info['name'], ', Abbreviation:', info['abbr'])
		return

	cmdsp = cmd.split('.')
	modulename = ''
	abbrname = ''
	module = {}
	for info in caseinfo:
		if(cmdsp[0] == info['name'] or cmdsp[0] == info['abbr']):
			modulename = info['name']
			abbrname = info['abbr']
			module = info['obj']

	if len(cmdsp) > 1:	
		funcname = modulename + '.' + abbrname + '_' + cmdsp[1]
		print(funcname)
		func = getattr(module, abbrname + '_' + cmdsp[1])
		try:
			help(func)
		except:
			print('Unknow command:', cmd, '::',funcname)
		return
	else:
		print('==================')
		print('User command list:')
		fl = dir(module)
		for l in fl:
			if(l.startswith(abbrname)):
				print('  '+l.split(abbrname+'_')[1])


def main(argv):
	if len(argv) < 2:
		print('Usage: runcase.py help [CaseModuleName | FunctionName]')
		print('Usage: runcase.py CaseModuleName.FunctionName [Param1 param2]')
		print('Example: runcase.py help case_wrist')
		print('Example: runcase.py help case_wrist.i_settime')
		print('Example: runcase.py case_wrist.i_settime 12 00 00')
		return

	case.case_register()

	if(argv[1] == 'help'):
		help_pram = None
		if(len(argv)>2):
			help_pram = argv[2]
		cmd_help(help_pram)
		return

	cmd = argv[1]
	func, paramstr = case.case_parse(argv[1:])
	try:
		cmd_str = 'func'+ paramstr
		exec(cmd_str)
	except:
		traceback.print_exc()
		e = sys.exc_info()
		if(type(e[1]) == KeyboardInterrupt):
			print('Key Break')
		elif(type(e[1]) == TypeError):
			print('Error parameter: [%s]'%cmd)
		elif(type(e[1]) == AttributeError):
			print('Unknow Command: [%s]'%cmd)
		else:
			traceback.print_exc()
		return

if __name__ == '__main__':
	main(sys.argv)


