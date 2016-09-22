import sys
import pymongo
import requests
import argparse
from itertools import islice

from app.util import set_status, create_edges_index
from app.status import Status
import app

log = app.get_logger('icd10')

def load_icd10():
    client = pymongo.MongoClient()
    db = client.ontologies

    # collection ICD 10 codes
    icd10collection = db.icd10

    #url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/DataSets/icd10_codes.txt'
    #log.info('reading network list from %s', url)
    #r = requests.get(url)

    f = open('/home/ec2-user/data/cytoscapenav/app/icd10_codes.txt', 'r')
    #f = open('/Users/aarongary/Development/DataSets/ICD_10/icd10_codes.txt', 'r')

    #r = requests.get(url)
    #lines = list(r.iter_lines())[1:] # ignore header line



    print('starting...')
    for line in f.readlines():
        field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14  = line.split(';')
        icd10line = {
            'nodetype': field2.rstrip().lstrip().lower(),
            'id': field7.rstrip().lstrip().lower(),
            'name': field9.rstrip().lstrip().lower()
        }

        #print('{"nodetype":"%s","id":"%s","name":"%s"}' % (field2.rstrip().lstrip(), field7.rstrip().lstrip(), field9.rstrip().lstrip()))

        _id = icd10collection.insert_one(icd10line).inserted_id

    print('finished...')
    f.close()

    return


def main():
    return 0


if __name__ == '__main__':
    sys.exit(main())