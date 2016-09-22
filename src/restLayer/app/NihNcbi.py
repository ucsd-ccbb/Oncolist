__author__ = 'aarongary'
import requests
import tarfile,sys
import urllib2
import json
import time
import app.genemania
import pymongo
from itertools import islice
from bson.json_util import dumps

def lookup_id(name):
    '''
    :param name: gene id, symbol, or synonym to find in the name column (case insensitive)
    :return: ensembl ID (or None)
    '''
    c = pymongo.MongoClient().datasets.nih
    results = c.find({'Symbol': 'FOSB'})
    for result in results:
        print result['description']

    return None if results is None else results

def load_gene_info():
    client = pymongo.MongoClient()
    db = client.datasets

    # collection stores metadata about source networks
    nih = db.nih

    url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/gene_info_small3b.txt'
    #url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/gene_info_small3c.txt'
    #url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/gene_info_smallx.txt'

    r = requests.get(url)
    lines = r.iter_lines()
    lines.next() # ignore header row

    def parse(lines):
        for line in lines:
        #for line in lines:
            try:
                field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15 = line.split('\t')
                yield {
                    'Symbol': field3.upper(),
                    'GeneID': field2.upper(),
                    'Synonyms': field5.upper(),
                    'description': field9,
                    'type_of_gene': field10
                }
            except Exception as e:
                print e.message

    count = 0
    iterator = parse(lines)
    while True:
        records = [record for record in islice(iterator, 1000)]
        if len(records) > 0:
            count += len(nih.insert_many(records).inserted_ids)
            print('inserted %d identifiers (%d total)', len(records), count)
        else:
            break

    nih.create_indexes([
        pymongo.IndexModel([('Symbol', pymongo.ASCENDING)]),
        pymongo.IndexModel([('GeneID', pymongo.ASCENDING)])
    ])

