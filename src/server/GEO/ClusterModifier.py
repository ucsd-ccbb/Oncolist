__author__ = 'guorongxu'

import os
import re
import sys

## deduplicate the cluster files.
def modify_cluster(cluster_file):
    print "cluster_file: " + cluster_file

    modified_cluster_file = cluster_file + ".mod"
    filewriter = open(modified_cluster_file, "a")

    with open(cluster_file) as fp:
        lines = fp.readlines()

        for line in lines:
            if line.startswith("corr"):
                filewriter.write(line)
                continue

            fields = re.split(r'\t', line)
            ## if two nodes are the same, then the correlation value should be 0.
            if fields[3] == fields[4].rstrip():
                filewriter.write(line.replace(fields[0], "0.0"))
            else:
                filewriter.write(line)

    fp.closed
    filewriter.close()

    os.rename(cluster_file, cluster_file + ".old")
    os.rename(modified_cluster_file, modified_cluster_file[:-4])

## Main entry
if __name__ == "__main__":
    cluster_file = sys.argv[1]
    #cluster_file = "/Users/guorongxu/Desktop/SearchEngine/GEO/louvain_json_files/rnaseq_vs_rnaseq_gamma_11.tsv"

    modify_cluster(cluster_file)
