import requests
import tarfile,sys
import urllib2
import json
import time
import pymongo
from itertools import islice

def run_mirbase_download():
    load_mirbase_list(0)

    return 0

def get_mir_data(mirna):
    client = pymongo.MongoClient()

    mirna_data = {
        'results': []
    }

    mirnaarray = mirna.split(',')
    for mirna_item in mirnaarray :
        mystr = "";

        terms = list(client.dataset.mirbase.find({'mId': mirna_item}))
        if(len(terms) > 0):
            mirna_data['results'].append({
                'id': mirna_item,
                'information': terms[0]['mirna_information']
            })

    return mirna_data

def get_mir_name_converter(term_id):
    client = pymongo.MongoClient()

    terms = list(client.dataset.mirbase.find({'mId': term_id}))
    if(len(terms) > 0):
        return terms[0]['mirna_id']
    else:
        return "UNKNOWN"

def get_mirbase_info(mirna_id): # EXT
    mir_resolved_id = get_mir_name_converter(mirna_id)

    if(mir_resolved_id is not "UNKNOWN"):
        url = 'http://mygene.info/v2/query?q=' + mir_resolved_id

        r = requests.get(url)
        r_json = r.json()
        if 'hits' in r_json and len(r_json['hits']) > 0:
            entrezgene_id = r_json['hits'][0]['entrezgene']
            url2 = 'http://mygene.info/v2/gene/' + str(entrezgene_id)
            r2 = requests.get(url2)
            r2_json = r2.json()
            return r2_json

        return r
    else:
        return "UNKNOWN TERM"

def load_mirbase_list(file_batch_number):
    url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/mirna.txt'

    r = requests.get(url)
    lines = r.iter_lines()

    def parse(lines):
        for line in lines:
            try:
                c1, mirna_id, mId, c2, c3, c4, mirna_information, c5  = line.split('\t')
                yield {
                    'mirna_id': mirna_id,
                    'mId': mId,
                    'mirna_information': mirna_information
                }
            except Exception as e:
                warningLabel = e.message

    db = pymongo.MongoClient().dataset
    collection = db.mirbase
    collection.drop()

    count = 0
    iterator = parse(lines)
    while True:
        records = [record for record in islice(iterator, 1000)]
        if len(records) > 0:
            count += len(collection.insert_many(records).inserted_ids)
        else:
            break

    collection.create_indexes([
        pymongo.IndexModel([('mirna_id', pymongo.ASCENDING)]),
        pymongo.IndexModel([('mId', pymongo.ASCENDING)])
    ])


def main():
    return 0

if __name__ == '__main__':
    sys.exit(main())