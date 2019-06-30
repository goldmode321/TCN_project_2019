import subprocess
import time

subprocess.Popen('python teststm.py')
i = 0
while True:
    i+=1
    print('a'+str(i))
    time.sleep(0.1)