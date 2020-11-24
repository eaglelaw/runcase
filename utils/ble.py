''
import sys
import os
import time
import socket
import imp
import threading
import traceback
from datetime import timedelta
from datetime import datetime

#define command
dict_CMD = {'connect':'[8001]',
'disconnect':'[8002]',
'scan':'[8003]',
'estiblish':'[8004]',
'terminate':'[8005]',
'discovery':'[8006]',
'read':'[8007]',
'write':'[8008]',
'mtu':'[8009]',
'extcmd':'[800a]',
'dev':'[800f]',
'rsp':'[8f01]',
'clr':'[8f02]'
}

dict_RSP = {'ack':'af01',
'rsp_connect':'a001',
'rsp_disconnect':'a002',
'rsp_scan':'a003',
'rsp_estiblish':'a004',
'rsp_terminate':'a005',
'rsp_discovery':'a006',
'rsp_read':'a007',
'rsp_write':'a008',
'rsp_notify':'a009',
'rsp_indicate':'a00a',
'rsp_mtu':'a00b',
'rsp_extcmd':'a00c',
'rsp_dev':'a00f'
}


class blehost:
	SeqNum = 0
	def __init__(self):
		self.sock = None
	#def __del__(self):
	#	if(self.sock is not None):
	#		self.sock.close()
	
	def hdl(self):
		return self.sock
		
	def connect(self):
		self.sock = socket.socket()
		#print('conn',self.sock)
		self.sock.settimeout(3)
		try:  
			self.sock.connect(('127.0.0.1', 10025))  
		except(socket.error):
			print('time out')
			return False
		return True
	
	def disconnect(self):
		if(self.sock is not None):
			print('close sock')
			self.sock.close()
			self.sock = None
		
	def send_cmd(self, cmd, param = None):
		SeqFlg = True
		seqval = '[ff]'
		if(self.sock is None):
			print('No connection!')
			return
		if((cmd in dict_CMD) is False):
			print('unknow command!')
			return
		if(cmd == 'rsp'):
			SeqFlg = False
		if(SeqFlg):
			blehost.SeqNum = (blehost.SeqNum+1)%0xff
			seqval = '[%.2x]'%blehost.SeqNum
			
		cmdval = dict_CMD[cmd]
		if(param is None):
			paramval = '[]'
		else:
			paramval = '[' + str(param)+']'
		req = cmdval + seqval + paramval + '\n'
		#print(self.sock)
		self.sock.sendall(req.encode())

	def qclr(self):
		if(self.sock is None):
			print('No connection!')
			return
		cmd = 'clr'
		self.send_cmd(cmd)
		return self.wait_rsp(None,blehost.SeqNum, 2)
		print('clear response queue')
		
	def wait_rsp(self, rsp = None, seq = False, timeout = 0):
		loopcnt = 0xffffffff
		rsp_pack=[]
		rspval = None
		if(rsp is not None):
			if(rsp in dict_RSP):
				rspval = dict_RSP[rsp]
			else:
				print('unknow response type input', rsp)
				return None
		# print('rspval is :', str(rspval))
			
		s = datetime.now()
		try:
			if(timeout == -1):
				loopcnt = 1
			for i in range(loopcnt):
				time.sleep(0.01)
				if(timeout > 0):
					if((datetime.now() - s).total_seconds() >= timeout):
						print('wait_rsp timeout')
						return None
				self.send_cmd('rsp')
				rsp_msg = self.sock.recv(2048)
				rsp_msg = rsp_msg.decode()
				if(rsp_msg == 'None'):
					continue
				rspstr = rsp_msg[1:5]
				if len(rsp_msg) > 10:
					rsp_pack.append(eval(rsp_msg[10:]))
					if len(rsp_pack[-1])==9 and rsp_pack[-1][0]==0x04 and rsp_pack[-1][1]==0xFF and \
						rsp_pack[-1][4] == 0x06 and rsp_pack[-1][3] == 0x7F and \
						rsp_pack[-1][5] == 0x12:
						raise Exception("bleNotConnected")
				if(rspval is not None):
					if(rspval != rspstr):
						continue
				seqnum = int(rsp_msg[7:9],16)
				if(seq is not None):
					if(seqnum != blehost.SeqNum):
						continue
				# print(rsp_pack)
				return [rspstr, seqnum, rsp_pack]
					
		except:
			traceback.print_exc()
			#os._exit()
			return None
		return None
	
	def ext_cmd(self, cmd, event, opcode):
		cmdstr = ''
		for val in cmd:
			cmdstr = cmdstr + '%.2x'%val
		cmdstr = '0x%.4x,0x%.4x,'%(event, opcode)+cmdstr
		print(cmdstr)
		self.send_cmd('extcmd', cmdstr)
	#---------------------------------------------
	#---------------------------------------------
	#---------------------------------------------
	#---<<User defined command>>------------------
	#---------------------------------------------
	#---------------------------------------------
	def check_067f(self, rsp):
		if(rsp is not list):
			return 0xff
		if(rsp[4]==6 and rsp[3] == 0x7f):
			return rsp[5]
		return 0

	def GATT_DiscAllPrimaryServices(self):
		conn_del = False
		rsp = ''
		rep_tmp = []
		if (self.sock is None):
			conn_del = True
			print('GATT_DiscAllPrimaryServices connecting')
			ret = self.connect()
			if (ret == False):
				return False, None
		cmd = [0x01, 0x90, 0xFD, 0x02, 0x00, 0x00]
		event = 0x0511
		opcode = 0xFD90
		self.ext_cmd(cmd, event, opcode)
		while (True):
			rsp = self.wait_rsp('rsp_extcmd', True, 30)
			print(rsp)
			rep_tmp.append(rsp[2])
			if rep_tmp:
				if rep_tmp[-1][5] == 0x1A:
					print("GATT_DiscAllPrimaryServices Success")
					break
				else:
					print("Not command RSP Data")
					print(rep_tmp[-1])
		if (conn_del == True):
			self.disconnect()
		if (rsp is None):
			return None
		print(rep_tmp)
		return rep_tmp

	def GATT_DiscAllCharDescs(self, ConnHandle=0x0000, StartHandle=0x0001, EndHandle=0xFFFF):
		conn_del = False
		rsp = ''
		rep_tmp = []
		if (self.sock is None):
			conn_del = True
			print('GATT_DiscAllCharDescs connecting')
			ret = self.connect()
			if (ret == False):
				return False, None
		cmd = [0x01, 0x84, 0xFD, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		event = 0x0505
		opcode = 0xFD84
		cmd[4] = ConnHandle & 0xff
		cmd[5] = (ConnHandle >> 8) & 0xff
		cmd[6] = StartHandle & 0xff
		cmd[7] = (StartHandle >> 8) & 0xff
		cmd[8] = EndHandle & 0xff
		cmd[9] = (EndHandle >> 8) & 0xff
		self.ext_cmd(cmd, event, opcode)
		while (True):
			rsp = self.wait_rsp('rsp_extcmd', True, 30)
			# 			# print(rsp)
			rep_tmp.append(rsp[2])
			if rep_tmp:
				if rep_tmp[-1][5] == 0x1A:
					print("GATT_DiscAllCharsDes Success")
					break
				else:
					print("Not command RSP Data")
					print(rep_tmp[-1])
		# if (rsp[2][5] == 0x1A):
		# 	print("GATT_DiscAllChars Success")
		# 	break
		if (conn_del == True):
			self.disconnect()
		if (rsp is None):
			return None
		print(rep_tmp)
		return rep_tmp

	def GATT_DiscAllChars(self, ConnHandle=0x0000, StartHandle=0x0001, EndHandle=0xFFFF):
		conn_del = False
		rsp = ''
		rep_tmp = []
		if (self.sock is None):
			conn_del = True
			print('GATT_DiscAllChars connecting')
			ret = self.connect()
			if (ret == False):
				return False, None
		cmd = [0x01, 0xB2, 0xFD, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		event = 0x0509
		opcode = 0xFDB2
		cmd[4] = ConnHandle & 0xff
		cmd[5] = (ConnHandle >> 8) & 0xff
		cmd[6] = StartHandle & 0xff
		cmd[7] = (StartHandle >> 8) & 0xff
		cmd[8] = EndHandle & 0xff
		cmd[9] = (EndHandle >> 8) & 0xff
		self.ext_cmd(cmd, event, opcode)
		while (True):
			rsp = self.wait_rsp('rsp_extcmd', True, 30)
			# print(rsp)
			rep_tmp.append(rsp[2])
			if rep_tmp:
				if rep_tmp[-1][5] == 0x1A:
					print("GATT_DiscAllChars Success")
					break
				else:
					print("Not command RSP Data")
					print(rep_tmp[-1])
		if (conn_del == True):
			self.disconnect()
		if (rsp is None):
			return None
		return rep_tmp

	def HCIExt_PacketErrorRateCmd(self, cmd='Read'):
		cmd_read = [0x01, 0x14, 0xFC, 0x03, 0x00, 0x00, 0x01]
		cmd_reset = [0x01, 0x14, 0xFC, 0x03, 0x00, 0x00, 0x00]
		event = 0xFFFF
		opcode = 0xFC14
		rep_tmp = [[], [], []]
		wait_cnt = 0
		conn_del = False
		if (self.sock is None):
			conn_del = True
			print('HCIExt_PacketErrorRateCmd connecting')
			ret = self.connect()
			if ret == False:
				return False
		if cmd == 'Read':
			self.ext_cmd(cmd_read, event, opcode)
		elif cmd == 'Reset':
			self.ext_cmd(cmd_reset, event, opcode)

		while (True):
			rsp = self.wait_rsp('rsp_extcmd', True, 5)
			wait_cnt += 1
			print(rsp)
			if rsp:
				# rep_tmp.append(rsp[2])
				for di in rsp[2]:
					rep_tmp[2].append(di)
				if rep_tmp:
					# len = 9 reset
					if len(rep_tmp[-1][-1]) == 9:
						if ((rep_tmp[-1][-1][3] == 0x14) and (rep_tmp[-1][-1][4] == 0x04) and (rep_tmp[-1][-1][5] == 0)):
							print("PER Reset Success")
							break
					# len = 17 read
					if len(rep_tmp[-1][-1]) == 17:
						if ((rep_tmp[-1][-1][3] == 0x14) and (rep_tmp[-1][-1][4] == 0x04) and (rep_tmp[-1][-1][5] == 0)):
							print("PER read Success")
							print("NumPkts %d" % (rep_tmp[-1][-1][9] + rep_tmp[-1][-1][10] << 8))
							print("NumCrcErr %d" % (rep_tmp[-1][-1][11] + rep_tmp[-1][-1][12] << 8))
							print("NumEvents %d" % (rep_tmp[-1][-1][13] + rep_tmp[-1][-1][14] << 8))
							print("NumMissedEvents %d" % (rep_tmp[-1][-1][15] + rep_tmp[-1][-1][16] << 8))
							break
			else:
				print("HCIExt_PacketErrorRateCmd try again: %d" % wait_cnt)
				if wait_cnt >= 5:
					print("HCIExt_PacketErrorRateCmd timeout")
					break
		if (conn_del == True):
			self.disconnect()
		if (rsp is None):
			return False
		return rep_tmp

	def HCIExt_ResetSystemCmd(self):
		conn_del = False
		if(self.sock is None):
			conn_del = True
			print('connecting')
			ret = self.connect()
			if(ret== False):
				return False
		
		cmd = [0x01, 0x1D, 0xFC, 0x01, 0x00]
		event = 0x041D
		opcode = 0xFFFF
		
		self.ext_cmd(cmd,event,opcode)
		
		rsp = self.wait_rsp('rsp_extcmd', True, 2)
		
		
		if(conn_del == True):
			self.disconnect()
			
		return False
		if(rsp is None):
			return False
		
		check_rsp = self.check_067f(rsp)
		if(check_rsp):
			print(sys._getframe().f_code.co_name, 'failed, cause:',check_rsp)
			return False
			
		return True
	
	#GAP_DeviceInit(False,False,False,True,0,[0,0,0,0,0,0])
	def GAP_DeviceInit(self, Broadcaster = False, Observer = False, Peripheral = False, Central = True, AddressMode = 0, RandAddr = [0,0,0,0,0,0]):
		
		cmd = [0x01, 0x00, 0xFE, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		event = 0x0600
		opcode = 0xFFFF
		profileRole = 0
		if(Broadcaster):
			profileRole = profileRole | 1
		if(Observer):
			profileRole = profileRole | 2
		if(Peripheral):
			profileRole = profileRole | 4
		if(Central):
			profileRole = profileRole | 8
			
		if(AddressMode > 3 or AddressMode < 0):
			print('AddressMode out of range', AddressMode)
			return False
		
		cmd[4] = profileRole
		cmd[5] = AddressMode
		
		if(len(RandAddr) != 6):
			print('RandAddr format is not correct', RandAddr)
			return False
		5
		for i in range(len(RandAddr)):
			cmd[6+i] = RandAddr[i]
		
		conn_del = False
		if(self.sock is None):
			conn_del = True
			print('connecting')
			ret = self.connect()
			if(ret== False):
				return False

		self.ext_cmd(cmd,event,opcode)
		
		rsp = self.wait_rsp('rsp_extcmd', True, 2)
		
		
		if(conn_del == True):
			self.disconnect()
			
		return False
		if(rsp is None):
			return False
		
		check_rsp = self.check_067f(rsp)
		if(check_rsp):
			print(sys._getframe().f_code.co_name, 'failed, cause:',check_rsp)
			return False
		return True

	
	def GAP_UpdateLinkParamReq(self, ConnHandle=0, IntervalMin = 80,
								IntervalMax = 80, ConnLatency = 0, ConnTimeout = 2000):
		cmd = [0x01, 0x11, 0xFE, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		event = 0x0607
		opcode = 0xFE11
		rep_tmp = [[], [], []]
		cmd[4] = ConnHandle&0xff
		cmd[5] = (ConnHandle>>8)&0xff
		cmd[6] = IntervalMin&0xff
		cmd[7] = (IntervalMin>>8)&0xff
		cmd[8] = IntervalMax&0xff
		cmd[9] = (IntervalMax>>8)&0xff
		cmd[10] = ConnLatency&0xff
		cmd[11] = (ConnLatency>>8)&0xff
		cmd[12] = ConnTimeout&0xff
		cmd[13] = (ConnTimeout>>8)&0xff
		
		conn_del = False
		if(self.sock is None):
			conn_del = True
			print('connecting')
			ret = self.connect()
			if ret == False:
				return False

		self.ext_cmd(cmd,event,opcode)
		wait_cnt = 0
		while (True):
			rsp = self.wait_rsp('rsp_extcmd', True, 5)
			# print(rsp)
			wait_cnt += 1
			if rsp:
				# rep_tmp.append(rsp[2])
				for di in rsp[2]:
					rep_tmp[2].append(di)
				if rep_tmp:
					if ((rep_tmp[-1][-1][5] == 0) and (rep_tmp[-1][-1][3] == 7) and (rep_tmp[-1][-1][4] == 6)):
						print("GAP_UpdateLinkParamReq Success")
						break
					elif len(rep_tmp[-1][-1]) == 9 and rep_tmp[-1][-1][0] == 4 and rep_tmp[-1][-1][1] == 0xFF and \
						rep_tmp[-1][-1][3] == 0x06 and rep_tmp[-1][-1][4] == 0x06 and rep_tmp[-1][-1][8] != 0x16:
						print("BLE disconnected")
						raise Exception("BLE disconnected")
					elif rep_tmp[-1][-1][0] == 4 and rep_tmp[-1][-1][1] == 0xFF and rep_tmp[-1][-1][3] == 0x7F and rep_tmp[-1][-1][4] == 0x06 and rep_tmp[-1][-1][5] != 0:
						print("BLE disconnected when Update link request")
						raise Exception("BLE disconnected when Update link request")
					else:
						print("Not command RSP Data")
						print(rep_tmp[-1])
			else:
				print("LinkReq update try again: %d" % wait_cnt)
				if wait_cnt >= 5:
					print("LinkReq update timeout")
					break
		if(conn_del == True):
			self.disconnect()
		if(rsp is None):
			return False
		return True

	def HCI_LE_SetDataLength(self, ConnHandle=0, TxOctets=251, TxTime=2120):
		conn_del = False
		rsp = ''
		rep_tmp = [[], [], []]
		cmd = [0x01, 0x22, 0x20, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		event = 0xFFFF
		opcode = 0x2022
		cmd[4] = ConnHandle & 0xff
		cmd[5] = (ConnHandle >> 8) & 0xff
		cmd[6] = TxOctets & 0xff
		cmd[7] = (TxOctets >> 8) & 0xff
		cmd[8] = TxTime & 0xff
		cmd[9] = (TxTime >> 8) & 0xff
		conn_del = False
		if (self.sock is None):
			conn_del = True
			print('HCI_LE_SetDataLength connecting')
			ret = self.connect()
			if (ret == False):
				return False
		self.ext_cmd(cmd, event, opcode)
		wait_cnt = 0
		while (True):
			rsp = self.wait_rsp('rsp_extcmd', True, 2)
			print(rsp)
			wait_cnt += 1
			if rsp:
				# rep_tmp.append(rsp[2])
				for di in rsp[2]:
					rep_tmp[2].append(di)
				if ((rep_tmp[-1][-1][1] == 0x0E) and (rep_tmp[-1][-1][4] == 0x22) and (rep_tmp[-1][-1][5] == 0x20) and (
						rep_tmp[-1][-1][6] == 0)):
					print("HCI_LE_SetDataLength Success")
					break
				elif len(rep_tmp[-1][-1]) == 9 and rep_tmp[-1][-1][0] == 4 and rep_tmp[-1][-1][1] == 0xFF and \
						rep_tmp[-1][-1][3] == 0x06 and rep_tmp[-1][-1][4] == 0x06 and rep_tmp[-1][-1][8] != 0x16:
					print("BLE disconnected")
					raise Exception("BLE disconnected")
				elif rep_tmp[-1][-1][0] == 4 and rep_tmp[-1][-1][1] == 0xFF and rep_tmp[-1][-1][3] == 0x7F and \
						rep_tmp[-1][-1][4] == 0x06 and rep_tmp[-1][-1][5] != 0:
					print("BLE disconnected when set datalength")
					raise Exception("BLE disconnected when set datalength")
				else:
					print("Not command RSP Data")
					print(rep_tmp[-1][-1])
			else:
				print("Set data Length again %d" % wait_cnt)
				if wait_cnt >= 5:
					print("Set data Length timeout")
					break
		if (conn_del == True):
			self.disconnect()
		if (rsp is None):
			return None
		return rep_tmp

	def HCI_LE_SetPhy(self, ConnHandle=0, AllPhys=0, TxPhy=1, RxPhy=1, PhyOptions=0):
		conn_del = False
		rsp = ''
		rep_tmp = [[], [], []]
		cmd = [0x01, 0x32, 0x20, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		event = 0xFFFF
		opcode = 0x2032
		cmd[4] = ConnHandle & 0xff
		cmd[5] = (ConnHandle >> 8) & 0xff
		cmd[6] = AllPhys & 0xff
		cmd[7] = TxPhy & 0xff
		cmd[8] = RxPhy & 0xff
		cmd[9] = PhyOptions & 0xff
		cmd[10] = (PhyOptions >> 8) & 0xff
		conn_del = False
		if (self.sock is None):
			conn_del = True
			print('HCI_LE_SetPhy connecting')
			ret = self.connect()
			if (ret == False):
				return False
		self.ext_cmd(cmd, event, opcode)
		wait_cnt = 0
		while True:
			wait_cnt += 1
			rsp = self.wait_rsp('rsp_extcmd', True, 5)
			if rsp:
				for di in rsp[2]:
					rep_tmp[2].append(di)
				if ((rep_tmp[-1][-1][1] == 0x3E) and (rep_tmp[-1][-1][3] == 0x0c) and (rep_tmp[-1][-1][4] == 0)):
					print("HCI_LE_SetPhy Success")
					break
				elif len(rep_tmp[-1][-1]) == 9 and rep_tmp[-1][-1][0] == 4 and rep_tmp[-1][-1][1] == 0xFF and \
						rep_tmp[-1][-1][3] == 0x06 and rep_tmp[-1][-1][4] == 0x06 and rep_tmp[-1][-1][8] != 0x16:
					print("BLE disconnected")
					raise Exception("BLE disconnected")
				elif rep_tmp[-1][-1][0] == 4 and rep_tmp[-1][-1][1] == 0xFF and rep_tmp[-1][-1][3] == 0x7F and \
						rep_tmp[-1][-1][4] == 0x06 and rep_tmp[-1][-1][5] != 0:
					print("BLE disconnected when set phy")
					raise Exception("BLE disconnected when set phy")
			else:
				print("Set Phy Mode again %d" % wait_cnt)
				if wait_cnt >= 5:
					print("Set Phy Mode timeout")
					break
		if (conn_del == True):
			self.disconnect()
		return rep_tmp


	def GAP_Authenticate(self,
						 Connhandle = 0,
						 ioCaps=4,
						 oobAvail=0,
						 oob=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
						 oobConfirm=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
						 locOobAval=0,
						 localOob=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
						 isSCOnlyMod=0,
						 eccKs_isUse=0,
						 eccKs_sK=[0xBD,0x1A,0x3C,0xCD,0xA6,0xB8,0x99,0x58,0x99,0xB7,0x40,0xEB,0x7B,0x60,0xFF,0x4A,0x50,0x3F,0x10,0xD2,0xE3,0xB3,0xC9,0x74,0x38,0x5F,0xC5,0xA3,0xD4,0xF6,0x49,0x3F],
						 eccKs_pK_x=[0xE6,0x9D,0x35,0x0E,0x48,0x01,0x03,0xCC,0xDB,0xFD,0xF4,0xAC,0x11,0x91,0xF4,0xEF,0xB9,0xA5,0xF9,0xE9,0xA7,0x83,0x2C,0x5E,0x2C,0xBE,0x97,0xF2,0xD2,0x03,0xB0,0x20],
						 eccKs_pK_y=[0x8B,0xD2,0x89,0x15,0xD0,0x8E,0x1C,0x74,0x24,0x30,0xED,0x8F,0xC2,0x45,0x63,0x76,0x5C,0x15,0x52,0x5A,0xBF,0x9A,0x32,0x63,0x6D,0xEB,0x2A,0x65,0x49,0x9C,0x80,0xDC],
						 authReq=0x01,
						 maxEKeySize=0x10,
						 keyDist=0x77,
						 pair_enable=0,
						 pair_ioCaps=0x03,
						 pair_oobDFlag=0,
						 pair_authReq=1,
						 pair_maxEKeySiz=0x10,
						 pair_keyDist=0x77):
		cmd =[]
		rep_tmp=[]
		for i in range(164):
			cmd.append(0)
		event = 0x060A
		opcode = 0xFE0B
		cmd[0] = 0x01; cmd[1] = 0x0B; cmd[2] = 0xFE; cmd[3] = 0xA0
		cmd[4] = Connhandle & 0xff
		cmd[5] = (Connhandle >> 8) & 0xff
		cmd[6] = ioCaps; cmd[7] = oobAvail
		for i in range(16):
			cmd[8+i] = oob[i]
		for i in range(16):
			cmd[24+i] = oobConfirm[i]
		cmd[40]=locOobAval
		for i in range(16):
			cmd[41+i] = localOob[i]
		cmd[57] = isSCOnlyMod; cmd[58] = eccKs_isUse
		for i in range(32):
			cmd[59+i] = eccKs_sK[i]
		for i in range(32):
			cmd[91+i] = eccKs_pK_x[i]
		for i in range(32):
			cmd[123+i] = eccKs_pK_y[i]
		cmd[155] = authReq; cmd[156] = maxEKeySize; cmd[157] = keyDist
		cmd[158] = pair_enable;cmd[159] = pair_ioCaps;cmd[160] = pair_oobDFlag
		cmd[161] = pair_authReq;cmd[162] = pair_maxEKeySiz;cmd[163] = pair_keyDist
		conn_del = False
		if (self.sock is None):
			conn_del = True
			print('GAP_Authenticate connecting')
			ret = self.connect()
			if (ret == False):
				return False
		self.ext_cmd(cmd, event, opcode)
		wait_cnt = 0
		while (True):
			wait_cnt += 1
			rsp = self.wait_rsp('rsp_extcmd', True, 10)
			print(rsp)
			if rsp:
				rep_tmp.append(rsp[2])
				if (rep_tmp[-1][-1][3] == 0x0A) and (rep_tmp[-1][-1][4] == 0x06) and (rep_tmp[-1][-1][5] == 0):
					print("GAP_Authenticate Success")
					break
				else:
					print("Not command RSP Data")
					print(rep_tmp[-1][-1])
			else:
				print("GAP_Authenticate again %d" % wait_cnt)
				if wait_cnt >= 3:
					print("GAP_Authenticate timeout")
					break
		if (conn_del == True):
			self.disconnect()
		if (rsp is None):
			return None
		return rep_tmp



	def GapAdv_create(self,
					Properties = 0x0013, # (19)GAP_ADV_PROP_CONNECTABLE+GAP_ADV_PROP_SCANNABLE+GAP_ADV_PROP_LEGACY
					IntervalMin = 0x0000A0, #(160)
					IntervalMax = 0x0000A0, #(160)
					PrimaryChMap = 0x07, # (7) (GAP_ADV_CHAN_37|GAP_ADV_CHAN_38GAP_ADV_CHAN_39)
					PeerAddrType = 0x00, #(0) (PEER_ADDRTYPE_PUBLIC_OR_PUBLIC_ID)
					PeerAddress = [0x00,0x00,0x00,0x00,0x00,0x00],
					FilterPolicy = 0x00, # (0) (AdvFilterPolicy Bit Mask Is Not Set)
					TxPower = 0x7F, #(127)
					PrimaryPHY = 0x01, #(1) (GAP_ADV_PRIM_PHY_1_MBPS)
					SecondaryPHY = 0x01, #(1) (GAP_ADV_SEC_PHY_1_MBPS)
					SID = 0):
		
		cmd = [0x01, 0x3E, 0xFE, 0x15, 0x13, 0x00, 0xA0, 0x00, 0x00, 0xA0, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7F, 0x01, 0x01, 0x00]
		event = 0xFFFF
		opcode = 0xFE3E
		
		cmd[4] = Properties&0xff
		cmd[5] = (Properties>>8)&0xff
		
		cmd[6] = IntervalMin&0xff
		cmd[7] = (IntervalMin>>8)&0xff
		cmd[8] = (IntervalMin>>16)&0xff
		
		cmd[9] = IntervalMax&0xff
		cmd[10] = (IntervalMax>>8)&0xff
		cmd[11] = (IntervalMax>>16)&0xff
		
		cmd[12] = PrimaryChMap&0xff
		
		cmd[13] = PeerAddrType&0xff
		
		for i in range(6):
			cmd[14+i] = PeerAddress[i]
			
		cmd[20] = FilterPolicy&0xff
		cmd[21] = TxPower&0xff
		cmd[22] = PrimaryPHY&0xff
		cmd[23] = SecondaryPHY&0xff
		cmd[24] = SID&0xff
		
		conn_del = False
		if(self.sock is None):
			conn_del = True
			print('connecting')
			ret = self.connect()
			if(ret== False):
				return False

		self.ext_cmd(cmd,event,opcode)
		
		rsp = self.wait_rsp('rsp_extcmd', True, 2)
		
		
		if(conn_del == True):
			self.disconnect()
			
		if(rsp is None):
			return False
		
		check_rsp = self.check_067f(rsp)
		if(check_rsp):
			print(sys._getframe().f_code.co_name, 'failed, cause:',check_rsp)
			return False
		
		#parse command
		return True		
	def test(self):
		#conn_del = False
		#if(self.sock is None):
		#	conn_del = True
		#	print('connecting')
		#	ret = self.connect()
		#	if(ret== False):
		#		return False
		
		cmd = [0x01, 0x11, 0xFE, 0x0A, 0x00, 0x00, 0x64, 0x00, 0x64, 0x00, 0x00, 0x00, 0xD0, 0x07]
		event = 0xFFFF
		opcode = 0xFE11
		
		self.ext_cmd(cmd,event,opcode)
		rsp = self.wait_rsp('rsp_extcmd', True, 2)
		self.disconnect()
		return False
		
		
		#if(conn_del == True):
		#	print('Disconnect sock')
		#	self.disconnect()
			
		return False
		if(rsp is None):
			return False
		
		if(rsp[2] != 0):
			print('HCIExt_ResetSystemCmd failed, cause:',rsp[2])
			return False
		return True	
		
