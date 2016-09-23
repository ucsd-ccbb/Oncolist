__author__ = 'aarongary'
import requests
import tarfile,sys
import urllib2
import json
import time
import pymongo
import nav.api
from itertools import islice
from elasticsearch import Elasticsearch
from bson.json_util import dumps
from collections import Counter
from app import go
from app import PubMed

#es = Elasticsearch(send_get_body_as='POST')
es = Elasticsearch(['http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # Clustered Server
#es = Elasticsearch(['http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200'],send_get_body_as='POST')
#es = Elasticsearch()


def star_search_mapped_2_0(query_terms):
    gene_network_data = {
        'searchGroupTitle': "Star Results",
        'clusterNodeName': "Lucene score",
        'searchTab': "GENES",
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []

    gene_super_list = []

    sorted_query_list = PubMed.get_gene_pubmed_counts(query_terms)#PubMed.get_gene_pubmed_counts_normalized(query_terms, 10)

    sorted_query_list_json = dumps(sorted_query_list)

    boostValue = get_boost_value(sorted_query_list['results'], 'AANAT')

    queryTermArray = query_terms.split(',')
    should_match = [] #[{ 'match': {'networkName': network_info['cancerType']}}]

    for queryTerm in queryTermArray:
        #should_match.append( { 'match': {network_info['matchField']: queryTerm} })
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        should_match.append({"match": {"node_list.node.name":{"query": queryTerm,"boost": boost_value_append}}})
        gene_network_data['geneSuperList'].append({'queryTerm': queryTerm, 'boostValue': boost_value_append})

    query_terms = query_terms.replace(",", "*")

    es_body = {
            'fields': ['nodeName'],
            'query': {
                'bool': {
                    'should': should_match,
                }
            }
        }

    es_body_json = dumps(es_body)

    result = es.search(
        index='network',
        doc_type='node', # node
        body={
            'fields': ['nodeName', 'source', 'degree', 'node_list.node.name'],
            'query': {
                'bool': {
                    'must': [{'match': {'networkName': 'BRCA'}}],
                    'should': should_match,
                }
            }
            ,'size': 50
        }
    )
    should_json = dumps(should_match)
    result_json = dumps(result)
    print("Got %d Hits:" % result['hits']['total'])

    #==================================
    # PROCESS EACH SEARCH RESULT
    #==================================
    hitCount = 0
    hitMax = 0
    hitMin = 0
    if(result['hits']['total'] < 1):
        print 'no results'

    for hit in result['hits']['hits']:
        if(hitCount == 0):
            hitMax = hit['_score']
        else:
            hitMin = hit['_score']

        searchResultSummaryString = hit["fields"]["source"][0] + '-' + hit["fields"]["degree"][0]

        geneNeighborhoodArray = [];

        for genehit in hit["fields"]["node_list.node.name"]:
            geneNameDisected = genehit.split(':')
            if(len(geneNameDisected) > 1):
                geneNeighborhoodArray.append(geneNameDisected[0])
            else:
                geneNeighborhoodArray.append(genehit)

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        hit_score = float(hit["_score"])
        gene_network_data_items = {
            #'searchResultTitle': hit["_source"]["source"] + '-' + hit["_source"]["degree"] + '-' + hit["_source"]["nodeName"],
            'searchResultTitle': hit["fields"]["nodeName"][0],
            'clusterName': hit["fields"]["nodeName"][0],
            'searchResultSummary': searchResultSummaryString,
            'luceneScore': hit["_score"],
            'boostValue': get_boost_value(sorted_query_list['results'], hit["fields"]["nodeName"][0]),
            'searchResultScoreRankTitle': 'lucene boosted score ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': set(y),
            #'emphasizeInfoArray': [],
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)
        hitCount += 1


    gene_network_data['items'] = unsorted_items
    #print('%s ' % dumps(gene_network_data))

    return [gene_network_data]

def get_boost_value(boostArray, idToCheck):
    for boostItem in boostArray:
        if(boostItem['id'] == idToCheck):
            returnThisValue = boostItem['normalizedValue']
            return boostItem['normalizedValue']

    return 0