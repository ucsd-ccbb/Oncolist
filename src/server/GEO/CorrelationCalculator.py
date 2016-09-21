__author__ = 'guorongxu'

import sys
import logging
import correlator

def calculate(output_file, input_file_0, input_file_1, threshold):
    if threshold > 0:
        correlator.correlate(output_file, input_file_0, input_file_1, spearman="spearman", rho_threshold = threshold)
    else:
        correlator.correlate(output_file, input_file_0, input_file_1, spearman="spearman")

if __name__ == "__main__":

    output_file = sys.argv[1]
    input_file_0 = sys.argv[2]
    input_file_1 = sys.argv[3]
    threshold = float(sys.argv[4])

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)

    logging.info("Input file 0: " + input_file_0)
    logging.info("Input file 1: " + input_file_1)
    logging.info("Output file: " + output_file)

    calculate(output_file, input_file_0, input_file_1, threshold)
