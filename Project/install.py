import subprocess
import sys
from Constants import *

print "installing..."
print "Please wait that might take a while."
subprocess.call([sys.executable, "get-pip.py"])
pip_path = "\\".join(sys.executable.split("\\")[:-1] + ["Scripts", "pip"])
for module in MODULES_TO_INSTALL:
    print "installing " + module
    subprocess.call([pip_path, "install", module])
    print module + " installed"
print "installation finished!"
check = sys.stdin.readable()
if check:
    input_data = sys.stdin.readline()
    subprocess.Popen([sys.executable, input_data])