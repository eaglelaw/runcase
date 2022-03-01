
#case  pool format:
#INFO = {
#	'desc':'raw pass test case',
#	'name':'case_rawpass',
#	'abbr':'rp',
#	'obj':case_rawpass
#}
import os
import importlib

g_case_pool = []

def case_parse(cmdlist):
	global g_case_pool
	caseinfo = g_case_pool
	cmd = cmdlist[0]
	cmdsp = cmd.split('.')
	modulename = ''
	abbrname = ''
	module = {}
	for info in caseinfo:
		#print(info)
		if(cmdsp[0] == info['name'] or cmdsp[0] == info['abbr']):
			modulename = info['name']
			abbrname = info['abbr']
			module = info['obj']
	#print(cmdsp)
	#print(module, abbrname)
	func = getattr(module, abbrname + '_' + cmdsp[1])
	paramstr = '('
	if len(cmdlist[1:]) > 0:
		for p in cmdlist[1:]:
			paramstr += p+','
		paramstr = paramstr[:len(paramstr)-1] + ')'
	else:
		paramstr += ')'
	return func, paramstr		


def case_register():
	global g_case_pool

	#must run at the root path
	run_path = os.getcwd()
	for path, dirs, files in os.walk(run_path):
		sp = path.split('\\')[-1]
		if(not sp.startswith('case_')):
			continue
		for item in files:
			if item.startswith('def') and item.endswith('py'):
				file = item.split(".")[0]			#def_rawpass
				case_name = file.split('_')[1]		#rawpass
				#print(case_name)
				case_obj = importlib.import_module('case_'+case_name+'.case_'+case_name)		#rawpass.case_rawpass
				case_info = importlib.import_module('case_'+case_name+'.'+file).INFO 			#case_rawpass.INFO
				case_info['obj'] = case_obj
				g_case_pool.append(case_info)
	#print(g_case_pool)
