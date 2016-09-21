__author__ = 'guorongxu'

import sys
import re
import math
import logging

## Main entry
if __name__ == "__main__":

    correlation_file = sys.argv[1]
    output_file = sys.argv[2]
    cut_off = float(sys.argv[3])

    logging.info("correlation file: " + correlation_file)
    logging.info("output file: " + output_file)
    logging.info("cut_off: " + str(cut_off))

    filewriter = open(output_file, "a")

    with open(correlation_file) as fp:
        lines = fp.readlines()
        for line in lines:
            fields = re.split(r'\t+', line)
            if math.fabs(float(fields[2])) >= cut_off:
                filewriter.write(line)

    fp.close()
    filewriter.close()