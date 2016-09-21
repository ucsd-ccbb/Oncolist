__author__ = 'guorongxu'

import time
import logging
from subprocess import Popen, PIPE, STDOUT

def trackPBSQueue(minutes, shell_script):
    jobs = 0
    while True:
        time.sleep(minutes * 60)

        is_done = True
        index = 0

        cmd = 'qstat'
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for line in p.stdout:
            line = line.rstrip()
            if line.find(shell_script) > -1:
                is_done = False
            index = index + 1

        if index > 2:
            if index - 2 != jobs:
                jobs = index -2
                logging.info("")
                logging.info(str(index - 2) + " job(s) are running...")

        if is_done:
            logging.info("")
            logging.info("No jobs is running...")
            break

if __name__ == "__main__":
    trackPBSQueue(1, "PBS_Tracker")