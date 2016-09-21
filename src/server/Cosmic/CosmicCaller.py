__author__ = 'guorongxu'

import subprocess

def print_json(workspace, data_set):
    subprocess.call(["qsub", "-o", "search_engine.log", "-e", "search_engine.log",
                     workspace + "/codes/" + data_set + "/cosmic.sh", "print_json", workspace + "/" + data_set])

## To print schema
def print_schema(workspace, data_set):
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/cosmic.sh", "print_schema", workspace, data_set])

## To append id into json files
def append_id(workspace, data_set):
    subprocess.call(["qsub", "-pe", "smp", "1", "-o", "search_engine.log", "-e", "search_engine.log",
                    workspace + "/codes/" + data_set + "/cosmic.sh", "append_id", workspace, data_set])