import requests
import tarfile,sys
import urllib2
import json
import time
import pymongo

from xml.dom import minidom
from itertools import islice

def get_interpro_data(interproIdList):
    client = pymongo.MongoClient()

    interpro_return_data = {
        'results': []
    }

    interproIdArray = interproIdList.split(',')
    for interpro_item in interproIdArray :
        mystr = "";

        terms = list(client.dataset.interpro.find({'interpro_id': interpro_item}))

        interpro_return_data['results'].append({
            'id': interpro_item,
            'information': terms[0]['interpro_desc']
        })

    return interpro_return_data

def run_interpro_download():
    load_interpro_list(0)

    return 0

def load_interpro_list(file_batch_number):
    url = 'http://localhost:8080/SearchPrototype/interpro-id-desc_all.txt'

    #url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/mirna.txt'

    r = requests.get(url)
    lines = r.iter_lines()

    def parse(lines):
        for line in lines:
            try:
                interproId, interproDesc  = line.split('~')
                yield {
                    'interpro_id': interproId,
                    'interpro_desc': interproDesc
                }
            except Exception as e:
                warningLabel = e.message

    db = pymongo.MongoClient().dataset
    collection = db.interpro
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
        pymongo.IndexModel([('interpro_id', pymongo.ASCENDING)]),
    ])

def main():
    return 0

if __name__ == '__main__':
    sys.exit(main())