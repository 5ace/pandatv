import sqlite3
import time
import re
import sys

IDdict={'10091':'囚徒','10029':'王师傅','31131':'SOL君','10027':'瓦莉拉','10025':'冰蓝飞狐','10003':'星妈'}

def data(sqlTableName,findstr):
	#sqlTableName='TM1455793646RD10091'
	# 查询记录：
	timeStart=sqlTableName.split('RD')[0].split('TM')[1]
	roomid=sqlTableName.split('RD')[1]
	conn = sqlite3.connect('pandadanmu.db')
	cursor = conn.cursor()
	# 执行查询语句:
	strEx='select * from '+sqlTableName#+' where time=?'
	print(strEx)
	cursor.execute(strEx)#, timex)
	# 获得查询结果集:
	values = cursor.fetchall()
	cursor.close()
	conn.close()
	datadict=dict()
	datalist=list()
	ttNum=0
	if not IDdict.get(roomid):
		IDdict[roomid]=roomid
	txtName=time.ctime(int(timeStart))[4:10]+'日'+IDdict[roomid]+'弹幕汇总.txt'

	if values:
		writefile=open(txtName,"w")
		print(len(values),'抓取开始时间:',time.ctime(int(values[0][0])))
		for v in values:
			writefile.writelines(['时间:',time.ctime(v[0])[4:19],':',v[1],':',v[2],'\n'])
			if v[2].find(findstr)>0:
				v0=int(int(v[0]/60)*60)
				if datadict.get(v0,0):
					datadict[v0]=datadict[v0]+1
				else:
					datadict[v0]=1
				ttNum=ttNum+1



		# sortedlist=sorted(datadict.items(), key=lambda e:e[1], reverse=True)
		print('总共出现',ttNum,'条弹幕包含‘',findstr,'’')
		# for x in sortedlist:
		# 	if x[1]>2:
		# 		print('时间：',time.ctime(60*x[0]),'次数:',x[1])


		writefile.close()
	return datadict




def main(findstr,date):
	con = sqlite3.connect('pandadanmu.db')
	cursor = con.cursor()
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	tableLst=cursor.fetchall()
	cursor.close()
	con.close()
	retDict=dict()
	print(tableLst)
	for table in tableLst:
		tableStr=''.join(table)
		ctime=time.ctime(int(tableStr[2:12]))
		print(ctime)
		if ctime[4:10] == date:

			print(ctime,':',tableStr)
			datadict=data(tableStr,findstr)
			roomid=tableStr.split('RD')[1]
			for k,v in datadict.items():
				retKey=str(k)+'RD'+roomid
				if retDict.get(retKey,0):
					retDict[retKey]=retDict[retKey]+v
				else:
					retDict[retKey]=v
	sortedlist=sorted(retDict.items(), key=lambda e:e[1], reverse=True)
	#timeStart=sqlTableName.split('RD')[0].split('TM')[1]
	txtName=date+'日单位时间内获得‘'+findstr+'’个数的总排名.txt'
	writefile=open(txtName,"w")	

	for k,v in sortedlist:
		if v>2:
			#print('总共出现',v,'条弹幕包含‘',findstr,'’')
			strlist=str(k).split('RD')
			if not IDdict.get(strlist[1]):
				IDdict[strlist[1]]=strlist[1]
			writefile.writelines([time.ctime(int(strlist[0])),IDdict[roomid],':',str(v),'\n'])
			print(k,v)
	
	writefile.close()



if __name__=='__main__':
	#sqlTableName= sys.argv[2] if len(sys.argv)>1 else 'TM1455794040RD10091'
	findstr= sys.argv[1] if len(sys.argv)>1 else '666'
	date= sys.argv[2] if len(sys.argv)>1 else 'Feb 19'
	main(findstr,date)

#python3 dataOutT.py 666 TM1455794040RD10091

