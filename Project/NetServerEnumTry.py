from win32net import NetServerEnum
from socket import gethostbyname

result = NetServerEnum(None, 100)
for item in result[0]:
    name = item['name']
    try:
        print gethostbyname(name) + " " * 4 + name
    except:
        print name