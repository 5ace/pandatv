import sys
from pandaTV import PandaTV


if __name__ == '__main__':
    idolid= sys.argv[1] if len(sys.argv)>1 else '66666'
    panda=PandaTV(idolid)
    panda.getChatInfo()
    #python3 pandaTVDanmu.py 10091
