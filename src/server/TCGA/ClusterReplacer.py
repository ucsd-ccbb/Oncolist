__author__ = 'guorongxu'

import sys
import re
import math
import logging

def parse_correlation(correlation_file):
    correlation_list = {}
    with open(correlation_file) as fp:
        lines = fp.readlines()
        for line in lines:
            fields = re.split(r'\t+', line)
            correlation_list.update({fields[0] + "_" + fields[1]:fields})

    return correlation_list

def parse_cluster(cluster_file, correlation_list):

    filewriter = open(cluster_file + ".rep", "a")

    with open(cluster_file) as fp:
        lines = fp.readlines()
        for line in lines:
            fields = re.split(r'\t+', line)
            if fields[0] == "cor":
                filewriter.write(line)

            if (fields[3] + "_" + fields[4]) in correlation_list:
                edge = correlation_list.get(fields[3] + "_" + fields[4])
                filewriter.write(edge[2] + "\t" + fields[1] + "\t" + edge[3] + "\t" + fields[3] + "\t" + fields[4])
            if (fields[4] + "_" + fields[3]) in correlation_list:
                edge = correlation_list.get(fields[4] + "_" + fields[3])
                filewriter.write(edge[2] + "\t" + fields[1] + "\t" + edge[3] + "\t" + fields[3] + "\t" + fields[4])

    filewriter.close()

## Main entry
if __name__ == "__main__":

    correlation_file = sys.argv[1]
    cluster_file = sys.argv[2]

    print correlation_file

    logging.info("correlation file: " + correlation_file)
    logging.info("cluster file: " + cluster_file)

    correlation_list = parse_correlation(correlation_file)

    parse_cluster(cluster_file, correlation_list)

