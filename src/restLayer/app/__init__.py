import os
#import sys
import logging
import logging.handlers
#import pandas as pd
from pandas import read_pickle as pd_read_pickle
import pymongo
#import itertools



root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
log_path = os.path.join(root, 'logs')
static_path = os.path.join(root, 'static')
dropbox_path = os.path.join(root, 'dropbox')
ingested_path = os.path.join(root, 'ingested')
failed_path = os.path.join(root, 'failed')
mongodb_uri = 'mongodb://localhost'
elastic_search_uri = 'http://ec2-52-32-210-84.us-west-2.compute.amazonaws.com:9200/' # CCBB ElasticSearch (DEV)
#elastic_search_uri = 'http://ec2-52-41-84-103.us-west-2.compute.amazonaws.com:9200/' # CCBB ElasticSearch (PRD)


authors_GB_genes_loaded = '' #pd_read_pickle('authors_GB_genes.txt')
path_to_DB_file = '' #'datascience/drugbank.0.json.new' # set path to drug bank file
path_to_cluster_file = '' #'datascience/sample_matrix.csv' # set path to cluster file

#
#mongodb_uri = 'mongodb://52.26.177.115'

client = pymongo.MongoClient()
db = client.dataset

drug_bank_collection = db.drug_bank

drug_bank_collection_found = drug_bank_collection.find_one({'drug_bank_info_type': 'drug_infer'})

DB_el = []
for kv_pair in drug_bank_collection_found['drug_bank_info']:
    DB_el.append((kv_pair['key'],kv_pair['value']))

#drugs_grouped = []
#for key, group in itertools.groupby(sorted(drug_bank_collection_found['drug_bank_info'], key=lambda k: k['value']), lambda item: item["value"]):
#    group_array = []
#    for group_item in group:
#        group_array.append(group_item['key'])
#    if(len(group_array) > 1):
#        print key + ' val: ' + str(len(group_array))
#    drugs_grouped.append(
#        {
#            'gene': key,
#            'drugs': group_array
#        }
#    )

#    client.dataset.drug_bank_by_gene.save(
#        {
#            'gene': key,
#            'drugs': group_array
#        }
#    )

def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers = []

    formatter = logging.Formatter('%(asctime)s.%(msecs)d ' + name + ' %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

    handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_path, 'app.log'), when='midnight', backupCount=28)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
