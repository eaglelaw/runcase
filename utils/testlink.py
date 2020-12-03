from xml.etree.ElementTree import ElementTree
import sys
import pathlib
import html


def processTree(tree, f):
	output = ''
	root = tree.getroot()
	max_depth = findDepth(root)

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


def testlink_to_csv(xml_path,f):
	tree = ElementTree()
	tree.parse(xml_path)
	processTree(tree,f)
	

from xml.dom import minidom
import html

class Testsuite:

	def __init__(self,name):
		self.case_list = []
		self.dom = minidom.Document()
		self.root_node = self.dom.createElement('testsuite')
		self.dom.appendChild(self.root_node)
		self.root_node.setAttribute('name', name)

	def add_Commonts(self, detail_info):
		detail_node = self.dom.createElement('details')
		cdata_text = self.dom.createCDATASection(detail_info)
		detail_node.appendChild(cdata_text)
		self.root_node.appendChild(detail_node)


	#method get TestCase --> return an existing instance of the TestCase or creates it in the dictionary
	def add_TestCase(self,name, case_cmd, case_param = '', expected_result = 'True', summary = '', preconditions = ''):
		print('	testcase name:',name)
		if name in self.case_list:
			print('Error: Duplicate case name <',name,'>')
			return False
			
		self.case_list.append(name)
		
		case_node = self.dom.createElement('testcase')
		case_node.setAttribute('name', name)
		
		summary_node = self.dom.createElement('summary')
		cdata_text = self.dom.createCDATASection(summary)
		summary_node.appendChild(cdata_text)
		case_node.appendChild(summary_node)
		
		preconditions_node = self.dom.createElement('preconditions')
		cdata_text = self.dom.createCDATASection(preconditions)
		preconditions_node.appendChild(cdata_text)
		case_node.appendChild(preconditions_node)
		
		execution_type_node = self.dom.createElement('execution_type')
		cdata_text = self.dom.createCDATASection('2')
		execution_type_node.appendChild(cdata_text)
		case_node.appendChild(execution_type_node)
		
		#add steps sould only have one step for runcase tool
		#steps
		steps_node = self.dom.createElement('steps')
		case_node.appendChild(steps_node)
		
		#add step
		step_node = self.dom.createElement('step')
		steps_node.appendChild(step_node)
		
		#expected_result
		step_number_node = self.dom.createElement('step_number')
		cdata_text = self.dom.createCDATASection('1')
		step_number_node.appendChild(cdata_text)
		step_node.appendChild(step_number_node)
		
		#actions as case_cmd + case_param
		actions_node = self.dom.createElement('actions')
		actions = case_cmd
		if(case_param is not ''):
			actions = actions + '\n' + case_param
		cdata_text = self.dom.createCDATASection(actions)
		actions_node.appendChild(cdata_text)
		step_node.appendChild(actions_node)
		
		#expected_result
		expected_result_node = self.dom.createElement('expected_result')
		cdata_text = self.dom.createCDATASection(expected_result)
		expected_result_node.appendChild(cdata_text)
		step_node.appendChild(expected_result_node)
		
		self.root_node.appendChild(case_node)
		
		return True

	#methods print xml --> build the xml file from the instances of the objects created
	#the method calls itself as there can be TestSuite parents of other TestSuites; as we "get" an instance of a test suite, we also get the dictionary associated
	#we can then loop through each key of that dictionary, until we get to the testcases dictionary
	#after going through all entries, we append the xml tags in the end
	def print_xml(self, fname):
		fp = open(fname, 'w', encoding = 'UTF-8')
		self.dom.writexml(fp, indent='',newl='\n',encoding='UTF-8')
		fp.close()


