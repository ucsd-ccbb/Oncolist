__author__ = 'aarongary'
import pymongo
import sys
import requests
import os
import json

def populate_gene_db():
    client = pymongo.MongoClient()
    db = client.identifiers
    genemania = db.genemania
    genemania_pubmed = db.genemania_pubmed

    genemania_pubmed.drop()

    genemania_items = genemania.find({'source': 'Gene Name'})
    loop_count = 0
    for item in genemania_items:
        if(loop_count < 200):
            pubmed_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + item['name'] + '&retmode=json&retmax=2000'

            r_json = requests.get(pubmed_url).json()

            if('esearchresult' in r_json):
                #print r_json['esearchresult']['count']

                genemania_pubmed.save(
                    {
                        'gene':item['name'],
                        'idlist': r_json['esearchresult']['idlist']
                     }

                )
            print item['name']
        #else:
            #break
        print loop_count
        loop_count += 1

    genemania_pubmed.ensure_index([("gene" , pymongo.ASCENDING)])
    genemania_pubmed.ensure_index([("idlist" , pymongo.ASCENDING)])

def read_pubmed_files():
    client = pymongo.MongoClient()
    db = client.identifiers
    genemania_pubmed = db.genemania_pubmed

    file_list = os.listdir("../pubmed_json_files")

    for file_item in file_list:
        found_gene_record = genemania_pubmed.find_one({'idlist': file_item.replace('.json','')})

        if(found_gene_record is not None):
            print found_gene_record['gene']

        #print file_item

def run_sample():


    client = pymongo.MongoClient()
    db = client.identifiers
    genemania = db.genemania # ret collection
    gene_pubmed = db.gene_pubmed
    gene_abstract = db.gene_abstract

    genemania_items = genemania.find({'source':'Gene Name'}) # ret cursor
    gene_pubmed_items = gene_pubmed.find()


    count = 0
#    for item in genemania_items:
#       if count > 200:
#           break
#       pubmed_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s&retmode=json&retmax=2000' % item['name']
#       json_obj = requests.get(pubmed_url).json()

       # validate
#       if 'esearchresult' in json_obj:
#           print json_obj['esearchresult']['count']
#           id_list = json_obj['esearchresult']['idlist']
#           print(id_list)
#           gene_pubmed.save(
#               {'gene':item['name'],
#                'idlist':id_list}
#           )
           # update document with idlist

       # print item['name']
#       count += 1

    # create index for gene field
#    gene_pubmed.ensure_index([("gene", pymongo.ASCENDING)])

    # test find by index on gene field
    print gene_pubmed.find_one({'gene':'NFYA'})

    # read in pubmed files from directory and search in gene database
    for filename in os.listdir("../pubmed_json_files/"):
       filepath = "../pubmed_json_files/" + filename

       try:
           json_pubmed = json.loads(open(filepath).read())
       except ValueError as e:
           break

       filename = filename.replace('.json', "")
       print filename

       # look up genes in gene_pubmed database that have same pub med id
       for gene in gene_pubmed_items:
           print gene['gene']
           if filename in gene['idlist']:
               # if pub med id matches, save gene name and pub med abstract to gene_abstract database
               print " - FOUND GENE: " + gene['gene']
               gene_abstract.save(
                   {'gene': gene['name'],
                    'abstract': json_pubmed['abstract']}
               )



if __name__ == '__main__':
    #populate_gene_db()
    #read_pubmed_files()
    run_sample()

