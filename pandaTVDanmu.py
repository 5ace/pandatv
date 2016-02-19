#!/usr/bin/env python3
#author=707
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

global islive
islive=True


dict={10091:'囚徒',10029:'王师傅',31131:'SOL君',10027:'瓦莉拉',10025:'冰蓝飞狐',10003:'星妈'}

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


def notify(title, message):
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

def save2Sql(sqlTableName,contentSql,snickSql,LocalTimeSql):
    try:
        conn = sqlite3.connect('pandadanmu.db')
        cursor = conn.cursor()
        #writefile = open(txtName,"w")
        while LocalTimeSql:
            strEx='insert into '+sqlTableName+' (time, name, word) values ('\
                +str(LocalTimeSql[0])+',\''+snickSql[0]+'\',\''+contentSql[0]+'\')'
            cursor.execute(strEx)
            #writefile.writelines([time.ctime(LocalTimeSql[0]),':',snickSql[0],':',contentSql[0]],'\n',)
            del(LocalTimeSql[0],snickSql[0],contentSql[0])
            #print(strEx)
        #writefile.close()
        cursor.close()
        conn.commit()
        conn.close()
        print('===save===')
    except :
        info=sys.exc_info()  
        print(info[0],":",info[1])
        
def keepalive(sock):
    global islive
    while islive:
        print('============sent keepalive msg==============')
        sock.send(KEEPALIVE)
        time.sleep(300)


        

def getChatInfo(roomid):
    with urllib.request.urlopen(CHATINFOURL + roomid) as f:
        data = f.read().decode('utf-8')
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
        recvMsg = s.recv(4)
        if recvMsg == FIRST_RPS:
            print('成功连接弹幕服务器')
            recvLen = int.from_bytes(s.recv(2), 'big')
        #s.send(b'\x00\x06\x00\x00')
        #print(s.recv(4))
        threading.Thread(target=keepalive,args=(s,)).start()

        startTime=str(int(1440*(int(time.time())/1440)))
        conn = sqlite3.connect('pandadanmu.db')
        cursor = conn.cursor()
        sqlTableName='TM'+startTime+'RD'+roomid
        strEx='create table '+sqlTableName+\
        ' (time int(10), name varchar(10), word varchar(50))'
        cursor.execute(strEx)
        cursor.close()
        conn.commit()
        conn.close()
        txtGet='时间：'+time.ctime()+'房间号：'+roomid+'\n'+\
        '完整弹幕获取代码，请粘贴后右键到CMD：\n'+\
        'python '+sqlTableName
        writefile = open('log.txt',"w")
        writefile.writelines(txtGet)
        writefile.close()
        contentMsg=list()
        snickMsg=list()
        LocalMsgTime=list()
        global islive
        while islive:
            try:
                recvMsg = s.recv(4)
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
                                    if snickMsg[-1]=='丁果' and contentMsg[-1][:4]=='exit':
                                        print('==========get break target======')
                                        whileCodition=False
                                    print(snickMsg[-1]+':'+contentMsg[-1])
                                except :
                                    print('===GBK encode error, perhaps special string ===')
                            elif typeContent.group(1) == b'207':
                                contentSql=copy.deepcopy(contentMsg)
                                snickSql=copy.deepcopy(snickMsg)
                                LocalTimeSql=copy.deepcopy(LocalMsgTime)
                                contentMsg=list()
                                snickMsg=list()
                                LocalMsgTime=list()
                                if len(contentSql):
                                    threading.Thread(target=save2Sql, args=(sqlTableName,contentSql,snickSql,LocalTimeSql,)).start()
                            elif typeContent.group(1) == b'206':
                                goldNum=b''.join(re.findall(b'\"content\":\"(.*?)\"',chatmsg)).decode('unicode_escape')
                                goldNikname=b''.join(re.findall(b'\"nickName\":\"(.*?)\"',chatmsg)).decode('unicode_escape')
                                strprint=goldNikname+'送给主播'+goldNum+'个竹子'
                                print(strprint)
            except Exception as e:
                raise e


                
            



def main(idolid):

    getChatInfo(idolid)

if __name__ == '__main__':
    idolid= sys.argv[1] if len(sys.argv)>1 else '10013'
    main(idolid)
    #python3 pandaTVDanmu.py 10091

