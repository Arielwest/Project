from ComputerDatabase import ComputerDatabase
from WakeOnLan import shutdown
from socket import gethostbyaddr

db = ComputerDatabase()
computers = db.read()
for computer in computers:
    try:
        print gethostbyaddr(computer.ip)[0]
    except:
        print computer.ip
