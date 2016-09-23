import json
import sys
import pymongo
import requests
import argparse
from itertools import islice

mongodb_uri = 'mongodb://localhost'


def ScratchIt():
    json_string = '{"first_name": "Guido", "last_name":"Rossum"}'
    parsed_json = json.loads(json_string)
    print(parsed_json['first_name'])

    return

def lookup_name(lookforthisname):
    c = pymongo.MongoClient(mongodb_uri).ontologies.icd10

    query = ({"name": {"$regex": ".*" + lookforthisname + ".*"}})

    cursor = c.find(query)

    print(cursor.count())

    map = {it['name']: it['id'] for it in c.find(query)}

    for k, v in map.items():
        print k, " ", v

    return map



def icd10it():
    client = pymongo.MongoClient(mongodb_uri)
    db = client.ontologies

    # collection ICD 10 codes
    icd10collection = db.icd10

    f = open('/Users/aarongary/Development/DataSets/ICD_10/icd10_codes.txt', 'r')
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
