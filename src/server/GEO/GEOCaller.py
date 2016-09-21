__author__ = 'guorongxu'

import os
import subprocess
import logging
from datetime import datetime

## To download the raw files.
def download(workspace, data_set, s3_input_files_address, disease_name):
    root_raw_dir = workspace + "/" + data_set + "/raw_files"

    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is downloading raw files."
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/geo.sh", "download", s3_input_files_address, root_raw_dir, disease_name])

## To preprocess the raw files.
def preprocess(workspace, data_set):
    root_raw_dir = workspace + "/" + data_set + "/raw_files"

    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is preprocessing raw files."
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/geo.sh", "preprocess", root_raw_dir])

## To calculate the correlations.
def calculate(workspace, data_set):
    threshold = "0.0"
    root_raw_dir = workspace + "/" + data_set + "/raw_files"
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    print root_raw_dir
    print root_correlation_dir

    if not os.path.exists(os.path.dirname(root_correlation_dir)):
        os.makedirs(os.path.dirname(root_correlation_dir))

    for dirpath, directories, filenames in os.walk(root_raw_dir):
        for filename in filenames:
            if filename.endswith(".txt"):
                input_file = os.path.join(dirpath, filename)

                print input_file

                input_folder = filename[:-4]
                output_file = os.path.join(dirpath.replace("raw_files", "correlation_files") + "/" + input_folder, "rnaseq_vs_rnaseq.cor")

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is calculating correlation with " + input_file + "."
                subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/geo.sh", "calculate",
                                 output_file, input_file, input_file, threshold])

## To cluster the input correlation file and output to the cluster directory.
def louvain_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    for dirpath, dirs, files in os.walk(root_correlation_dir):
        for filename in files:
            input_file = os.path.join(dirpath, filename)
            for gamma in [1, 4, 7, 11, 14, 17, 20]:
                output_folder = dirpath + "_gamma_" + str(gamma)
                output_folder = output_folder.replace("correlation_files", "louvain_cluster_files")
                output_file = os.path.join(output_folder, filename[:-4]) + "_gamma_" + str(gamma) + ".tsv"

                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_file
                if not os.path.exists(output_file):
                    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                        workspace + "/codes/" + data_set + "/geo.sh", "louvain_cluster", input_file, output_file, str(gamma)])

def dedup_louvain_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    for dir_name in os.listdir(root_correlation_dir):
        correlation_dir = os.path.join(root_correlation_dir, dir_name)
        if os.path.isdir(correlation_dir):
            for project_name in os.listdir(correlation_dir):

                input_cluster_folder = correlation_dir.replace("correlation_files", "louvain_cluster_files")
                output_unique_folder = correlation_dir.replace("correlation_files", "unique_louvain_cluster_files")
                if not os.path.exists(output_unique_folder):
                    os.makedirs(output_unique_folder)

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is deduplicating louvain cluster " + input_cluster_folder
                if os.path.exists(input_cluster_folder):
                    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                        workspace + "/codes/" + data_set + "/geo.sh", "dedup_louvain_cluster", input_cluster_folder, output_unique_folder, project_name])

## To cluster the input correlation file and output to the cluster directory.
def oslom_undirected_cluster(workspace, data_set):
    root_correlation_dir = workspace + "/" + data_set + "/correlation_files"

    for dirpath, dirs, files in os.walk(root_correlation_dir):
        for filename in files:
            input_file = os.path.join(dirpath, filename)
            for gamma in [1]:
                output_folder = dirpath + "_gamma_" + str(gamma)
                output_folder = output_folder.replace("correlation_files", "oslom_cluster_files")
                output_file = os.path.join(output_folder, filename[:-4]) + "_gamma_" + str(gamma) + ".tsv"

                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is clustering " + input_file
                if not os.path.exists(output_file):
                    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                        workspace + "/codes/" + data_set + "/geo.sh", "oslom_undirected_cluster", input_file, output_file, str(gamma)])

## To parse the star file and then print star json file.
def print_star_json(workspace, data_set):
    root_cluster_dir = workspace + "/" + data_set + "/correlation_files"

    network_type = "rnaseq_vs_rnaseq"

    for dirpath, directories, filenames in os.walk(root_cluster_dir):
        for filename in filenames:
            input_file = os.path.join(dirpath, filename)
            output_file = input_file.replace("correlation_files", "json_files")[:-4] + ".star.json"

            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))

            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing " + input_file
            if not os.path.exists(output_file):
                subprocess.call(["qsub", "-pe", "smp", "2", "-o", "search_engine.log", "-e", "search_engine.log",
                             workspace + "/codes/" + data_set + "/geo.sh", "print_star_json", workspace, input_file,
                             output_file, network_type])

## To parse the cluster file and then print cluster json file.
def print_louvain_cluster_json(workspace, data_set):
    root_cluster_dir = workspace + "/" + data_set + "/unique_louvain_cluster_files"

    network_type = "rnaseq_vs_rnaseq"

    for dirpath, directories, filenames in os.walk(root_cluster_dir):
        for filename in filenames:
            input_file = os.path.join(dirpath, filename)
            output_file = input_file.replace("unique_louvain_cluster_files", "louvain_json_files")[:-4] + ".cluster.json"

            if input_file.endswith(".tsv") and not os.path.exists(output_file):
                if not os.path.exists(os.path.dirname(output_file)):
                    os.makedirs(os.path.dirname(output_file))
                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing " + input_file
                subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/geo.sh", "print_louvain_cluster_json", workspace, input_file,
                                 output_file, network_type])

## To parse the cluster file and then print cluster json file.
def print_oslom_cluster_json(workspace, data_set):
    root_cluster_dir = workspace + "/" + data_set + "/oslom_cluster_files"

    network_type = "rnaseq_vs_rnaseq"

    for dirpath, directories, filenames in os.walk(root_cluster_dir):
        for filename in filenames:
            input_file = os.path.join(dirpath, filename)
            output_file = input_file.replace("oslom_cluster_files", "oslom_json_files")[:-4] + ".cluster.json"

            if input_file.endswith(".tsv") and not os.path.exists(output_file):
                if not os.path.exists(os.path.dirname(output_file)):
                    os.makedirs(os.path.dirname(output_file))
                print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing " + input_file
                subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                                 workspace + "/codes/" + data_set + "/geo.sh", "print_oslom_cluster_json", workspace, input_file,
                                 output_file, network_type])

## To print schema
def print_schema(workspace, data_set):
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/geo.sh", "print_schema", workspace, data_set])

## To append id into json files
def append_id(workspace, data_set):
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/geo.sh", "append_id", workspace, data_set])

## To upload the resuling files.
def upload(workspace, data_set, s3_output_files_address, disease_name):
    root_dir = workspace + "/" + data_set + "/"

    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is uploading resulting files."
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/geo.sh", "upload", s3_output_files_address, root_dir, disease_name])

if __name__ == "__main__":

    logging.basicConfig(filename='/Users/guorongxu/Desktop/SearchEngine/GEO/search_engine.log',level=logging.DEBUG)

    workspace = "/Users/guorongxu/Desktop/SearchEngine"
    data_set = "GEO"
    dedup_louvain_cluster(workspace, data_set)
