import sys
import pymongo
import requests
import urllib2

from app.util import set_status, create_edges_index
from app.status import Status
from bson.json_util import dumps

__author__ = 'aarongary'


def get_gene_info_by_id(gene_id):
    #return ["UNKNOWN"]

    alt_term_id = []
    if(len(gene_id) > 2):
        r_json = {}
        try:
            url = 'http://mygene.info/v3/query?q=' + gene_id

            r = requests.get(url)
            r_json = r.json()
            if 'hits' in r_json and len(r_json['hits']) > 0:
                for alt_term in r_json['hits']:
                    if(isinstance(alt_term['symbol'], list)):
                        alt_term_id.append(alt_term['symbol'][0].upper())
                    else:
                        alt_term_id.append(alt_term['symbol'].upper())

                #gene_symbol = r_json['hits'][0]['symbol'].upper()
                return alt_term_id
        except Exception as e:
            print e.message
            return {'hits': [{'symbol': gene_id, 'entrezgene': '', 'name': 'Entrez results: 0'}]}

        return ["UNKNOWN"]
    else :
        return ["UNKNOWN"]

def get_entrezgene_info_by_symbol(gene_id):
    if(len(gene_id) > 0):
        try:
            url = 'http://mygene.info/v3/query?q=' + gene_id

            r = requests.get(url)
            r_json = r.json()
            if 'hits' in r_json and len(r_json['hits']) > 0:
                for alt_term in r_json['hits']:
                    if(isinstance(alt_term['entrezgene'], list)):
                        return str(alt_term['entrezgene'][0])
                    else:
                        return str(alt_term['entrezgene'])

        except Exception as e:
            print e.message
            return {'hits': [{'symbol': gene_id, 'entrezgene': '', 'name': 'Entrez results: 0'}]}

        return ["UNKNOWN"]
    else :
        return ["UNKNOWN"]




def getMyGeneInfoByID(gene_id):
    if(len(gene_id) > 0):
        try:
            mir_resolved_id = get_mir_name_converter(gene_id)

            if(mir_resolved_id is not "UNKNOWN"):
                url = 'http://mygene.info/v3/query?q=' + mir_resolved_id

                r = requests.get(url)
                r_json = r.json()
                if 'hits' in r_json and len(r_json['hits']) > 0:
                    for alt_hit in r_json['hits']:
                        entrezgene_id = alt_hit['entrezgene']
                        url2 = 'http://mygene.info/v3/gene/' + str(entrezgene_id)
                        r2 = requests.get(url2)
                        r2_json = r2.json()
                        return r2_json

                return r
            else:
                return "UNKNOWN TERM"

            entrez_url = "http://mygene.info/v3/query?q=" + str(gene_id)

            entrez_content = "";
            entrez_data = {
                'hits': []
            }


            for line in urllib2.urlopen(entrez_url):
                entrez_content += line.rstrip() + " "

            hit = {
                    'name': entrez_content,
                    '_score': 0,
                    'symbol': gene_id,
                    'source': 'Entrez'
                }

            entrez_data['hits'].append(hit)
        except Exception as e:
            print e.message
            return {'hits': [{'symbol': gene_id, 'name': 'Entrez results: 0'}]}

        return entrez_data
    else :
        return {'hits': [{'symbol': gene_id, 'name': 'not vailable'}]}

def get_mir_name_converter(mirna_id):
    return "UNKNOWN"