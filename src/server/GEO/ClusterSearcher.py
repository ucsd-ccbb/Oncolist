__author__ = 'Guorong Xu<g1xu@ucsd.edu>'

import os
import sys
import subprocess

def search_cluster(cluster_file_folder):
    for dirpath, directories, filenames in os.walk(cluster_file_folder):
        for filename in filenames:
            if filename.endswith(".tsv"):
                input_file = os.path.join(dirpath, filename)
                subprocess.call(["qsub", "-pe", "smp", "1", "/shared/workspace/SearchEngineProject/GEO/ClusterModifier.py", input_file])

## Main entry
if __name__ == "__main__":
    cluster_file_folder = sys.argv[1]

    search_cluster(cluster_file_folder)