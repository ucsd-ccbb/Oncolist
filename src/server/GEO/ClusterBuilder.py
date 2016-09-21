__author__ = 'guorongxu'

import os
import sys
import logging
from Louvain import cluster_analysis_module

def calculate_louvain_c_plus(input_file, code_path, temp_path, output_file, gamma, algorithm):
    cluster_analysis_module.results_TCGA_cluster(input_file, code_path, temp_path, algorithm, edge_thresh=0.0,
           gamma=int(gamma), cluster_size_min=2, cluster_size_max=10000, write_file_name=output_file, print_flag=False)
    #cluster_analysis_module.results_TCGA_cluster(input_file, gamma=int(gamma), cluster_size_min=2, cluster_size_max=10000,
    #                                             write_file_name = output_file, print_flag=True)

def calculate_ivanovska(input_file, output_file, gamma):
    cluster_analysis_module.save_ivanovska_clusters(input_file,edge_thresh=.5,gamma=int(gamma),qthresh=10, cluster_size_min=2,
                    print_flag=True,plot_flag=False,write_file_name=output_file)

if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    temp_path = output_file[:output_file.rfind('/')]
    gamma = sys.argv[3]
    operation = sys.argv[4]
    code_path = "/shared/workspace/SearchEngineProject/software/clustering_programs_5_2"

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Input file: " + input_file)
    logging.info("Output file: " + output_file)
    logging.info("gamma: " + gamma)

    if operation == "louvain_cluster" and os.path.exists(input_file) and not os.path.exists(output_file):
        calculate_louvain_c_plus(input_file, code_path, temp_path, output_file, gamma, algorithm='louvain')

    if operation == "oslom_undirected_cluster" and os.path.exists(input_file) and not os.path.exists(output_file):
        calculate_louvain_c_plus(input_file, code_path, temp_path, output_file, gamma, algorithm='oslom_undirected')
