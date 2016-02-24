#python3
import urllib.request
import socket
import json
import time
import threading
import os
import platform
import sys
import re
import copy
import sqlite3
import traceback

global islive
islive=True


roomiddict={'10091':'囚徒','10029':'王师傅','31131':'SOL君','10027':'瓦莉拉','10025':'冰蓝飞狐','10003':'星妈'}

CHATINFOURL = 'http://www.panda.tv/ajax_chatinfo?roomid='
DELIMITER = b'}}'

IGNORE_LEN = 16
FIRST_REQ = b'\x00\x06\x00\x02'
FIRST_RPS = b'\x00\x06\x00\x06'
KEEPALIVE = b'\x00\x06\x00\x00'
RECVMSG = b'\x00\x06\x00\x03'
DANMU_TYPE = '1'
BAMBOO_TYPE = '206'
AUDIENCE_TYPE = '207'
SYSINFO = platform.system()
INIT_PROPERTIES = 'init.properties'
MANAGER = '60'
SP_MANAGER = '120'
HOSTER = '90'


# def loadInit():
#     with open(INIT_PROPERTIES, 'r') as f:
#         init = f.read()
#         init = init.split('\n')
#         roomid = init[0].split(':')[1]
#         #username = init[1].split(':')[1]
#         #password = init[2].split(':')[1]
#         return roomid
def  txtThread(*traceback):
    fadd=open("log.txt",'w')
    fadd.writelines(''.join(traceback))
    fadd.close()


def notify(title, message):
    #about compatibility?
    if SYSINFO == 'Windows':
        pass
    elif SYSINFO == 'Linux':
        os.system('notify-send {}'.format(': '.join([title, message])))
    else:   #for mac
        t = '-title {!r}'.format(title)
        m = '-message {!r}'.format(message)
        os.system('terminal-notifier {} -sound default'.format(' '.join([m, t])))
#             print(nickName + ":" + content)
#             notify(nickName, content)


def initSql(roomid):
        localTime=time.localtime()
        tyear=str(localTime.tm_year)
        tmoon=str(localTime.tm_mon) if len(str(localTime.tm_mon))==2 else '0'+str(localTime.tm_mon)
        tday=str(localTime.tm_mday) if len(str(localTime.tm_mday))==2 else '0'+str(localTime.tm_mday)
        dateNow=tyear+tmoon+tday
        sqlTableName='TM'+dateNow+'RD'+roomid
        conn = sqlite3.connect('pandadanmu.db')
        cursor = conn.cursor()
        try:
            strEx='create table '+sqlTableName+\
            ' (time int(10), name varchar(10), word varchar(50))'
            cursor.execute(strEx)
        except sqlite3.OperationalError:

            print('===数据库表单存在===')
        except :
            addException2logtxt(traceback)
        cursor.close()
        conn.commit()
        conn.close()
        return sqlTableName


def save2Sql(sqlTableName,contentSql,snickSql,LocalTimeSql):
    try:
        conn = sqlite3.connect('pandadanmu.db')
        cursor = conn.cursor()
        while LocalTimeSql:
            strEx='insert into '+sqlTableName+' (time, name, word) values ('\
                +str(LocalTimeSql[0])+',\''+snickSql[0]+'\',\''+contentSql[0]+'\')'
            cursor.execute(strEx)
            del(LocalTimeSql[0],snickSql[0],contentSql[0])
            #print(strEx)
        cursor.close()
        conn.commit()
        conn.close()
        print('===save to sql===')
    except :
        info=sys.exc_info()
        print(info[0],":",info[1])


def keepalive(sock):
    global islive
    while islive:
        print('============sent keepalive msg==============')
        sock.send(KEEPALIVE)
        time.sleep(300)

def log2server(ftag):
    data = ftag.read().decode('utf-8')
    chatInfo = json.loads(data)
    chatAddr = chatInfo['data']['chat_addr_list'][0]
    socketIP = chatAddr.split(':')[0]
    socketPort = int(chatAddr.split(':')[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socketIP,socketPort))
    rid      = str(chatInfo['data']['rid']).encode('utf-8')
    appid    = str(chatInfo['data']['appid']).encode('utf-8')
    authtype = str(chatInfo['data']['authtype']).encode('utf-8')
    sign     = str(chatInfo['data']['sign']).encode('utf-8')
    ts       = str(chatInfo['data']['ts']).encode('utf-8')
    msg  = b'u:' + rid + b'@' + appid + b'\nk:1\nt:300\nts:' + ts + b'\nsign:' + sign + b'\nauthtype:' + authtype
    msgLen = len(msg)
    sendMsg = FIRST_REQ + int.to_bytes(msgLen, 2, 'big') + msg
    s.sendall(sendMsg)
    return s



def getChatInfo(roomid):
    roomiddict[roomid]=roomiddict[roomid] if roomiddict.get(roomid) else  roomid
    print('这里是主播：',roomiddict[roomid],'的直播间')
    with urllib.request.urlopen(CHATINFOURL + roomid) as f:
        s =  log2server(f)
        recvMsg = s.recv(4)
        if recvMsg == FIRST_RPS:
            print('成功连接弹幕服务器')
            recvLen = int.from_bytes(s.recv(2), 'big')

        threading.Thread(target=keepalive,args=(s,)).start()

        sqlTableName=initSql(roomid)

        contentMsg=list()
        snickMsg=list()
        LocalMsgTime=list()
        global islive
        while islive:
            try:
                recvMsg = s.recv(4)
            except ConnectionAbortedError :
                getChatInfo(roomid)
            if recvMsg == RECVMSG:
                recvLen = int.from_bytes(s.recv(2), 'big')
                recvMsg = s.recv(recvLen)   #ack:0
                #print(recvMsg)
                recvLen = int.from_bytes(s.recv(4), 'big')
                s.recv(IGNORE_LEN)
                recvLen -= IGNORE_LEN
                recvMsg = s.recv(recvLen)#chat msg
                #print(recvMsg)
                recvMsg =recvMsg.split(b'{\"type\":')
                #print(recvMsg)
                for chatmsg in recvMsg[1:]:
                    typeContent = re.search(b'\"(\d+)\"',chatmsg)
                    #print(typeContent)
                    if typeContent:
                        if typeContent.group(1) == b'1':
                            try:
                                contentMsg.append(b''.join(re.findall(b'\"content\":\"(.*?)\"',chatmsg)).decode('unicode_escape'))
                                snickMsg.append(b''.join(re.findall(b'\"nickName\":\"(.*?)\"',chatmsg)).decode('unicode_escape'))
                                LocalMsgTime.append(int(time.time()))
                                print(snickMsg[-1]+':'+contentMsg[-1])
                            except :
                                threading.Thread(target=txtThread, args=(traceback,)).start()
                        elif typeContent.group(1) == b'207':
                            contentSql=copy.deepcopy(contentMsg)
                            snickSql=copy.deepcopy(snickMsg)
                            LocalTimeSql=copy.deepcopy(LocalMsgTime)
                            contentMsg.clear()
                            snickMsg.clear()
                            LocalMsgTime.clear()
                            if len(contentSql):
                                threading.Thread(target=save2Sql, args=(sqlTableName,contentSql,snickSql,LocalTimeSql,)).start()
                        elif typeContent.group(1) == b'206':
                            goldNum=b''.join(re.findall(b'\"content\":\"(.*?)\"',chatmsg)).decode('unicode_escape')
                            goldNikname=b''.join(re.findall(b'\"nickName\":\"(.*?)\"',chatmsg)).decode('unicode_escape')
                            strprint=goldNikname+'送给主播'+goldNum+'个竹子'
                            print(strprint)

        s.close()


def main(idolid):

    try:
        getChatInfo(idolid)
    except Exception as e:
        threading.Thread(target=txtThread, args=(traceback,)).start()


if __name__ == '__main__':
    idolid= sys.argv[1] if len(sys.argv)>1 else '10091'
    main(idolid)
    #python3 pandaTVDanmu.py 10091

