__author__ = 'guorongxu'

import subprocess

def download(workspace, data_set):
    with open(workspace + "/" + data_set + "/gene_list.txt") as f:
        content = f.readlines()
        length = len(content)

        for i in range(0, 20):
            subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                             workspace + "/codes/" + data_set + "/pubmed.sh", "download",
                             workspace + "/" + data_set, str(i * length/8), str((i + 1) * length/8 - 1)])

def print_json(workspace, data_set):
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/pubmed.sh", "print_json", workspace + "/" + data_set])

def print_label(workspace, data_set):
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/pubmed.sh", "print_label", workspace + "/" + data_set])

def print_edge(workspace, data_set):
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/pubmed.sh", "print_edge", workspace + "/" + data_set])

def print_schema(workspace, data_set):
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/pubmed.sh", "print_schema", workspace, data_set])

## To append id into json files
def append_id(workspace, data_set):
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/pubmed.sh", "append_id", workspace, data_set])
