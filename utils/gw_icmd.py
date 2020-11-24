
def parse_time(rsp):
	if(rsp == 'NoRsp'):
		return rsp
	rsp = rsp.split(':')
	rsp = rsp[2]
	#print(rsp)
	#print(rsp[4:6])
	year = int(rsp[4:6],16) + 2000
	month = int(rsp[6:8],16)
	day = int(rsp[8:10],16)
	hour = int(rsp[10:12],16)
	minute = int(rsp[12:14],16)
	second = int(rsp[14:16],16)
	return str(year) + '-' + str(month) + '-' +str(day) + ' ' + str(hour) + ':' + str(minute) + ':' + str(second)
	