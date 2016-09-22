__author__ = 'aarongary'

import requests
import tarfile,sys
import urllib2
import json

from itertools import islice
from bson.json_util import dumps
from collections import Counter

def getEntrezGeneInfoByID(gene_id):
    if(len(gene_id) > 0):
        try:
            entrez_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=" + str(gene_id) + "&retmode=json"

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

def getESPubMedByID(gene_id):
    if(len(gene_id) > 0):
        try:
            entrez_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=" + str(gene_id) + "&retmode=json"

            entrez_content = "";
            entrez_data = {
                'hits': []
            }
#http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubchem&term=DB03585



            for line in urllib2.urlopen(entrez_url):
                entrez_content += line.rstrip() + " "

            hit = {
                    'name': entrez_content,
                    '_score': 0,
                    'symbol': gene_id
                }

            entrez_data['hits'].append(hit)
        except Exception as e:
            print e.message
            return {'hits': [{'symbol': gene_id, 'name': 'unable to return data'}]}

        return entrez_data
    else :
        return {'hits': [{'symbol': gene_id, 'name': 'not vailable'}]}

def getTribeTermResolution(terms):
    import requests

    TRIBE_URL = "http://tribe.greenelab.com"

    query_terms = terms.split(',')

    gene_list = []

    for term in query_terms:
        gene_list.append(term)

    payload = {'from_id': 'Entrez', 'to_id': 'Symbol', 'gene_list': gene_list, 'organism': 'Homo sapiens'}

    r = requests.post(TRIBE_URL + '/api/v1/gene/xrid_translate', data=payload)
    result_dictionary = r.json()

    for gene_query, search_result in result_dictionary.iteritems():
        print(gene_query + ": " + str(search_result))

    return result_dictionary

def start_thumbnail_generator(es_id_list):
    import requests

    r = requests.get('http://localhost:3000/setThumbnailList/' + es_id_list)

    return {'message': 'success'}



