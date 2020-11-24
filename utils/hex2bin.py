import os
import sys
from struct import *
#hex to bin
#[[addr,bytes(data)],...]
def read_hex(hexfile):
	try:
		fin = open(hexfile)
	except:
		print('No file opened', hexfile)
		return None
	table =[]
	result = b''
	addr = 0
	addr_flg = 0
	for hexstr in fin.readlines():
		#print(hexstr)
		hexstr = hexstr.strip()
		#print(hexstr)
		size = int(hexstr[1:3],16)
		if int(hexstr[7:9],16) == 4:
			if(len(result)):
				#print(hex(addr))
				#print(addr,result)
				#input()
				table.append([addr,result])
			addr = 	int(hexstr[9:13],16) <<16
			addr_flg = 0
			result = b''
			continue
		if int(hexstr[7:9],16) == 5 or  int(hexstr[7:9],16) == 1:
			#print(hex(addr))
			#print(addr,result)
			table.append([addr,result])
			break
		
		if(addr_flg == 0):
			addr_flg = 1
			addr = addr | (int(hexstr[3:7],16))
		#end if	
		for h in range( 0, size):
			b = int(hexstr[9+h*2:9+h*2+2],16)
			#print(type(b),b,result)
			result += pack('B',b)
		#end if
		#fout.write(result)		
		#result=b''
		#input()
	#end for
	#print(table)
	fin.close()
	return table

'''

a = read_hex('ota.hex')

print(a)

fp = open('ota.ota','wb')
strline = '['+ str(a[0][0]) + ',' +str(len(a[0][1])) +']\n'
fp.write(strline.encode())
strline = str(list(a[0][1])) + '\n'
fp.write(strline.encode())


print('a len is %d'%(len(a)))
print('%x,%x'%(a[0][0],len(a[0][1])))
print('%x,%x'%(a[1][0],len(a[1][1])))
print('%x,%x'%(a[2][0],len(a[2][1])))

	
if len(sys.argv) != 3 or (sys.argv[1] != '-h' and sys.argv[1] != '-b'):
	print( 'usage:')
	print( 'convert binary format to hexadecimal format: ')
	print( ' hexbin.py -h binfile hexfile')
	print( 'convert hexadecimal format to binary format:')
	print( ' hexbin.py -b hexfile binfile')
	exit(0)

	
if sys.argv[1] == '-h':
	print('None')
else:
	print(hex_bin(sys.argv[2]))


'''
	