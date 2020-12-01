from xml.etree.ElementTree import ElementTree
import sys
import pathlib
import html


def processTree(tree):
	output = ''
	root = tree.getroot()
	max_depth = findDepth(root)

	output_filename = pathlib.Path(sys.argv[1]).stem + '.csv'
	f = open(output_filename, "w", encoding="utf-8")


	processTestSuite(root, f, [], max_depth)

def findDepth(testsuite, depth = 1):
	testsuites = testsuite.findall('testsuite')
	max_depth = depth
	for entry in testsuites:
			curr_depth = findDepth(entry, depth + 1)
			if curr_depth > max_depth:
				max_depth = curr_depth
	return max_depth

def processTestSuite(testsuite, file, parents, max_depth):
	testsuites = testsuite.findall('testsuite')

	parents_copy = parents.copy()
	parents_copy.append(testsuite.attrib['name']);

	if len(testsuites) == 0:
		processLine(testsuite, file, parents_copy, max_depth)
	else:
		for entry in testsuites:
			processTestSuite(entry, file, parents_copy, max_depth)
			
def str_parser(html_str):
	if(type(html_str) is not str):
		return ['','','']
	tmp = html.unescape(html_str)
	tmp = tmp.replace('<p>', '')
	tmp = tmp.replace('</p>', '')
	tmp = tmp.replace(',', '-')
	tmp = tmp.split('\n')
	while '' in tmp:
		tmp.remove('')
	tmp.append('')
	return tmp		

#test suit should uase prefix:'runcase_'
#case name: Vxxx: variable; Cxxxx: Case name
#test command: test step1 is valid:
#                  action: command; 
#                  expectedresults: result,default is True or False;
#                  execution_type:  2 is valid for autotest
#csv format:
#		#testsuite name
#		variable_flg, variable_name, variable_value, summery, preconditions
#		case_name, casecmd, case_parameter, expected_result, summery, preconditions
def processLine(testsuite, file, parents, max_depth):
	testcases = testsuite.findall('testcase')
	file.write('#'+parents[0]+'\n')
	for entry in testcases:
		l_line = ['']*6
		autotest_flg = False
		l_line[0] = entry.attrib['name'] #variable_flg or case_name
		
		for child in entry:
			#print('child.tag:',child.tag,":", child.text)
			if(child.tag == 'summary'):
				l_line[4] = str_parser(child.text)[0]
			if(child.tag == 'preconditions'):
				l_line[5] = str_parser(child.text)[0]
			if(child.tag == 'steps'):
				for step in child:
					for itm in step:
						#print('>>>>',itm.tag, ':',itm.text)
						if(itm.tag == 'actions'):
							val = str_parser(itm.text)
							l_line[1] = val[0]
							l_line[2] = val[1]
						if(itm.tag == 'expectedresults'):
							l_line[3] = str_parser(itm.text)[0]
			if(child.tag == 'execution_type'):
				#print(child.tag, child.text)
				if(child.text == '2'):#2 is autotest
					autotest_flg = True
		#print(autotest_flg, l_line)
		for itm in l_line:
			file.write(itm+',')
		file.write('\n')


def testlink_to_csv(xml_path):
	tree = ElementTree()
	tree.parse(xml_path)
	processTree(tree)
	


