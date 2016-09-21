__author__ = 'guorongxu'

import os
import subprocess
import itertools
from datetime import datetime

tumor_types = ["PRAD", "STES"]
#tumor_types = ["ACC", "BLCA", "BRCA", "CESC", "CHOL", "COAD", "COADREAD", "DLBC",
#               "ESCA", "GBM", "GBMLGG", "HNSC", "KICH", "KIPAN", "KIRC", "KIRP",
#               "LAML", "LGG", "LUAD", "LUSC", "MESO", "OV", "PAAD", "PCPG",
#               "PRAD", "READ", "SARC", "SKCM", "STAD", "STES", "TGCT", "THCA",
#               "THYM", "UCEC", "UCS", "UVM"]

## To download raw data from TCGA website.
def download(workspace, data_set, release_year, release_month, release_day):
    root_raw_dir = workspace + "/" + data_set + "/raw_data"

    for tumor_type in tumor_types:
        subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                         workspace + "/codes/" + data_set + "/tcga.sh", "download", root_raw_dir,
                         tumor_type, release_year, release_month, release_day])

## To parse the raw data and output the expression tables
def parse(workspace, data_set, release_year, release_month, release_day):
    root_raw_dir = workspace + "/" + data_set + "/raw_data"
    root_expression_dir = workspace + "/" + data_set + "/expression_files"

    for tumor_type in tumor_types:
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is parsing " + tumor_type + " miRNA data."
        subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                         workspace + "/codes/" + data_set + "/tcga.sh", "parse_mirna", root_raw_dir,
                         root_expression_dir, tumor_type, release_year, release_month, release_day])
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is parsing " + tumor_type + " RNASeq data."
        subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                         workspace + "/codes/" + data_set + "/tcga.sh", "parse_rnaseq", root_raw_dir,
                         root_expression_dir, tumor_type, release_year, release_month, release_day])
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is parsing " + tumor_type + " mutation data."
        subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                         workspace + "/codes/" + data_set + "/tcga.sh", "parse_mutation", root_raw_dir,
                         root_expression_dir, tumor_type, release_year, release_month, release_day])

## To calculate the correlations.
def calculate(workspace, data_set):
    ## Iterate all combinations
    root_expression_dir = workspace + "/" + data_set + "/expression_files"
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    for tumor_type in tumor_types:
        for combination in combinations:
            input_file_0 = root_expression_dir + "/" + tumor_type + "/" + combination[0] + "_matrix.txt"
            input_file_1 = root_expression_dir + "/" + tumor_type + "/" + combination[1] + "_matrix.txt"
            output_file = root_correlation_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + ".cor"

            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))

            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is calculating correlation with " \
                  + tumor_type + ": " + combination[0] + "_vs_" + combination[1] + "."

            threshold = "0.0"
            if combination[0] == "rnaseq" or combination[0] == "mutation":
                subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/tcga.sh", "calculate",
                                 output_file, input_file_0, input_file_1, threshold])
            else:
                subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/tcga.sh", "calculate",
                                 output_file, input_file_0, input_file_1, threshold])

## To filter the correlation edges with less than cutoff.
def filter(workspace, data_set, cut_off=0.5):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    for tumor_type in tumor_types:
        for combination in combinations:
            input_file = root_correlation_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + ".cor"
            output_file = root_correlation_dir + "/" + tumor_type + "/" \
                          + combination[0] + "_vs_" + combination[1] + "_" + str(cut_off) + ".cor"

            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))

            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is filtering " + tumor_type \
                  + ": " + combination[0] + "_vs_" + combination[1]
            subprocess.call(["qsub", "-pe", "smp", "8", "-o", "search_engine.log", "-e", "search_engine.log",
                             workspace + "/codes/" + data_set + "/tcga.sh", "filter", input_file, output_file, str(cut_off)])

## To cluster the input correlation file and output to the cluster directory.
def louvain_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"
    root_cluster_dir = workspace + "/" + data_set + "/louvain_cluster_files/"

    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    for tumor_type in tumor_types:
        for combination in combinations:
            input_file = root_correlation_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_0.5.cor"
            for gamma in [1, 4, 7, 11, 14, 17, 20]:
                output_folder = root_cluster_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma)

                output_file = output_folder + "/" + combination[0] + "_vs_" \
                              + combination[1] + "_gamma_" + str(gamma) + ".louvain.tsv"

                if not os.path.exists(os.path.dirname(output_file)):
                    os.makedirs(os.path.dirname(output_file))

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_file
                subprocess.call(["qsub", "-pe", "smp", "2", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/tcga.sh", "louvain_cluster", input_file, output_file, str(gamma)])

## To cluster the input correlation file and output to the cluster directory.
def dedup_louvain_cluster(workspace, data_set):
    root_cluster_dir = workspace + "/" + data_set + "/louvain_cluster_files"
    root_unique_cluster_dir = workspace + "/" + data_set + "/louvain_unique_cluster_files"

    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    for tumor_type in tumor_types:
        for combination in combinations:
            input_folder = root_cluster_dir + "/" + tumor_type
            output_folder = root_unique_cluster_dir + "/" + tumor_type

            if not os.path.exists(os.path.dirname(output_folder)):
                os.makedirs(os.path.dirname(output_folder))

            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_folder
            subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                             workspace + "/codes/" + data_set + "/tcga.sh", "dedup_louvain_cluster", input_folder,
                             output_folder, combination[0] + "_vs_" + combination[1]])

## To cluster the input correlation file and output to the cluster directory.
def oslom_undirected_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"
    root_cluster_dir = workspace + "/" + data_set + "/oslom_undirected_cluster_files/"

    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    for tumor_type in tumor_types:
        for combination in combinations:
            input_file = root_correlation_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_0.5.cor"
            for gamma in [1]:
                output_folder = root_cluster_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma)

                output_file = output_folder + "/" + combination[0] + "_vs_" \
                              + combination[1] + "_gamma_" + str(gamma) + ".oslom_undirected.tsv"

                if not os.path.exists(os.path.dirname(output_file)):
                    os.makedirs(os.path.dirname(output_file))

                if not os.path.exists(output_file):
                    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_file
                    subprocess.call(["qsub", "-pe", "smp", "8", "-o", "search_engine.log", "-e", "search_engine.log",
                                     workspace + "/codes/" + data_set + "/tcga.sh", "oslom_undirected_cluster", input_file, output_file, str(gamma)])

## To cluster the input correlation file and output to the cluster directory.
def ivanovska_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"
    root_cluster_dir = workspace + "/" + data_set + "/cluster_files"

    ## Iterate all combinations
    data_types = ["mirna", "rnaseq"]

    for tumor_type in tumor_types:
        input_file = root_correlation_dir + "/" + tumor_type + "/" + data_types[0] + "_vs_" + data_types[1] + ".cor"
        for gamma in [1]:
            output_file = root_cluster_dir + "/" + tumor_type + "/" + data_types[0] + "_vs_" \
                          + data_types[1] + "_gamma_" + str(gamma) + ".ivanovska.tsv"

            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))

            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_file
            subprocess.call(["qsub", "-pe", "smp", "8", "-o", "search_engine.log", "-e", "search_engine.log",
                             workspace + "/codes/" + data_set + "/tcga.sh", "ivanovska_cluster", input_file, output_file, str(gamma)])

## To replace the correlation values in the cluster RNAseq_vs_RNAseq.
def replace_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"
    root_cluster_dir = workspace + "/" + data_set + "/oslom_undirected_cluster_files"

    ## Iterate all combinations
    data_types = ["rnaseq","rnaseq"]

    for tumor_type in tumor_types:
        input_file = root_correlation_dir + "/" + tumor_type + "/" + data_types[0] + "_vs_" + data_types[1] + "_0.5.cor"
        for gamma in [1]:
            cluster_folder = root_cluster_dir + "/" + tumor_type + "/" + data_types[0] + "_vs_" + data_types[1] + "_gamma_" + str(gamma)

            cluster_file = cluster_folder + "/" + data_types[0] + "_vs_" \
                            + data_types[1] + "_gamma_" + str(gamma) + ".oslom_undirected.tsv"

            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_file
            subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                             workspace + "/codes/" + data_set + "/tcga.sh", "replace_cluster", input_file, cluster_file, str(gamma)])

## To parse the cluster file and then print json file.
def print_louvain_json(workspace, data_set):
    prefix = "clusters_tcga_louvain"
    root_cluster_dir = workspace + "/" + data_set + "/louvain_unique_cluster_files"
    root_louvain_json_dir = workspace + "/" + data_set + "/louvain_json_files"
    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    print "printing louvain json..."
    for tumor_type in tumor_types:
        ## Print cluster json files
        for combination in combinations:
            for gamma in [1, 4, 7, 11, 14, 17, 20]:
                input_folder = root_cluster_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma)
                input_file = input_folder + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma) + ".louvain.unique.tsv"
                output_folder = root_louvain_json_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma)
                output_file = output_folder + "/" + combination[0] + "_vs_" + combination[1] \
                              + "_gamma_" + str(gamma) + ".json"

                if os.path.exists(os.path.dirname(input_file)):
                    if not os.path.exists(os.path.dirname(output_file)):
                        os.makedirs(os.path.dirname(output_file))

                    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing " + input_file
                    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                                     workspace + "/codes/" + data_set + "/tcga.sh", "print_louvain_json", workspace, input_file,
                                     output_file, tumor_type, combination[0] + "_vs_" + combination[1], prefix])

        ## Print star json files
        #print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing " + tumor_type
        #subprocess.call(["qsub", "-pe", "smp", "4", "-o", "search_engine.log", "-e", "search_engine.log",
        #                workspace + "/codes/" + data_set + "/tcga.sh", "print_star_json", workspace, data_set, tumor_type])

## To parse the cluster file and then print json file.
def print_oslom_undirected_json(workspace, data_set):
    prefix = "clusters_tcga_oslom"
    root_cluster_dir = workspace + "/" + data_set + "/oslom_undirected_cluster_files"
    root_louvain_json_dir = workspace + "/" + data_set + "/oslom_undirected_json_files"
    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]
    combinations = list(itertools.combinations_with_replacement(data_types, 2))

    for tumor_type in tumor_types:
        ## Print cluster json files
        for combination in combinations:
            for gamma in [1]:
                input_folder = root_cluster_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma)
                input_file = input_folder + "/" + combination[0] + "_vs_" + combination[1] + "_gamma_" + str(gamma) + ".oslom_undirected.tsv"
                output_file = root_louvain_json_dir + "/" + tumor_type + "/" + combination[0] + "_vs_" + combination[1] \
                              + "_gamma_" + str(gamma) + ".json"

                if not os.path.exists(os.path.dirname(output_file)):
                    os.makedirs(os.path.dirname(output_file))

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing " + input_file
                subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/tcga.sh", "print_oslom_json", workspace, input_file,
                                 output_file, tumor_type, combination[0] + "_vs_" + combination[1], prefix])

        ## Print star json files
        #print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing " + tumor_type
        #subprocess.call(["qsub", "-pe", "smp", "4", "-o", "search_engine.log", "-e", "search_engine.log",
        #                workspace + "/codes/" + data_set + "/tcga.sh", "print_star_oslom_json", workspace, data_set, tumor_type])

## To parse the cluster file and then print json file.
def print_ivanovska_json(workspace, data_set):
    prefix = "clusters_tcga_ivanovska"
    root_cluster_dir = workspace + "/" + data_set + "/cluster_files"
    root_ivanovska_json_dir = workspace + "/" + data_set + "/ivanovska_json_files"
    ## Iterate all combinations
    data_types = ["mirna", "rnaseq"]

    for tumor_type in tumor_types:
        ## Print cluster json files
        for gamma in [1]:
            input_file = root_cluster_dir + "/" + tumor_type + "/" + data_types[0] + "_vs_" \
                         + data_types[1] + "_gamma_" + str(gamma) + ".tsv"
            output_file = root_ivanovska_json_dir + "/" + tumor_type + "/" + data_types[0] + "_vs_" + data_types[1] \
                          + "_gamma_" + str(gamma) + ".ivanovska.json"

            if os.path.exists(os.path.dirname(input_file)):
                if not os.path.exists(os.path.dirname(output_file)):
                    os.makedirs(os.path.dirname(output_file))

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing " + input_file
                subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/tcga.sh", "print_ivanovska_json", workspace, input_file,
                                 output_file, tumor_type, data_types[0] + "_vs_" + data_types[1], prefix])

## To print labels
def print_label(workspace, data_set):
    ## Iterate all combinations
    data_types = ["mirna", "rnaseq", "mutation"]

    for tumor_type in tumor_types:
        for data_type in data_types:
            ## Print label
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing labels of " + tumor_type
            subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                            workspace + "/codes/" + data_set + "/tcga.sh", "print_label", workspace, data_set, tumor_type, data_type])

## To print schema
def print_schema(workspace, data_set):

    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing schema of TCGA"
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/tcga.sh", "print_schema", workspace, data_set])

## To append id into json files
def append_id(workspace, data_set):
    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into TCGA json files"
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/tcga.sh", "append_id", workspace, data_set])
