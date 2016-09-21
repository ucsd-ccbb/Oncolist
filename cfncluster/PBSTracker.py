__author__ = 'guorongxu'

import re
import time

def trackPBSQueue(ssh_client, minutes, shell_script):

    jobs = 0
    while True:
        time.sleep(minutes * 60)

        is_done = True
        index = 0

        cmd = 'qstat'
        stdin , stdout, stderr = ssh_client.exec_command(cmd)

        #print stdout.read()

        lines = re.split(r'\n+', stdout.read())

        for line in lines:
            if line.find(shell_script) > -1:
                is_done = False
                index = index + 1

        if index > 0:
            if index != jobs:
                jobs = index
                print ""
                print str(index) + " job(s) are running..."

        if is_done:
            print ""
            print "No jobs is running..."
            break

if __name__ == "__main__":
    trackPBSQueue(1, "PBS_Tracker")