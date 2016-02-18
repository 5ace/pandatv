recvMsg=b'{"type":"1","time":1455792804,"data":{"from":{"identity":"30","rid":"3053498"\
,"__plat":"pc_web","nickName":"\\u54b8\\u5473\\u515c\\u98ce","level":"4","userNa\
me":"PandaTv3053498"},"to":{"toqid":1,"toroom":"10091"},"content":"33333333333"}\
}A\xf5S?*a*\x00\x01\x15-?\x00\x00\x01\x15{"type":"1","time":1455792804,"data":{"\
from":{"identity":"30","rid":"24237990","__plat":"pc_web","nickName":"\\u9648CiC\
i","level":"5","userName":"PandaTv24237990"},"to":{"toqid":1,"toroom":"10091"},"\
content":"\\u5c31\\u662f\\u673a\\u68b0\\u6cd5\\u7684\\u8282\\u594f\\u554a\\u3002\
\\u3002"}}'
import re
import json
# print(recvMsg)
# recvMsg =recvMsg.split(b'{\"type\":')
# print(recvMsg)
# for chatmsg in recvMsg[1:]:
#     typeContent = re.search(b'\"(\d+)\"',chatmsg)
#     print(typeContent)
#     if typeContent:
#         if typeContent.group(1) == b'1':
#         	print('1')
#         elif typeContent.group(1)==b'0':
#         	print('0')
recvMsgLst=recvMsg.split(b'\x00\x01\x15')
for recvMsg in recvMsgLst:
	print(recvMsg)
	recvMsg=recvMsg.decode('utf-8')
	print(recvMsg)
	recvMsg=json.loads(recvMsg)
	print(recvMsg)
	recvMsg=eval(recvMsg)
	print(recvMsg)
	print(type(recvMsg))



