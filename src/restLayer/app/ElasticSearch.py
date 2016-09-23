import requests
import tarfile,sys
from app import elastic_search_uri
import urllib2
import json
import time
import pymongo
import nav.api
from itertools import islice
from elasticsearch import Elasticsearch
from bson.json_util import dumps
import json
from collections import Counter
from app import go
from app import PubMed
from app import SearchViz
from app import DrugBank
from app import HeatMaps
from models.TermResolver import TermAnalyzer
from signal import signal, SIGPIPE, SIG_DFL
import numpy as np
from itertools import count
import simplejson
#es = Elasticsearch(send_get_body_as='POST')
#es = Elasticsearch(['http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # Clustered Server
#es = Elasticsearch(['http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200'],send_get_body_as='POST')
#es = Elasticsearch()
es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server
#es = Elasticsearch(['http://ec2-52-27-59-174.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST',timeout=300) # Prod Clustered Server


#===============================================
#===============================================
#===============================================
#===============================================
#           MAIN SEARCH METHOD
#===============================================
#===============================================
#===============================================
#===============================================

def get_geneSuperList(queryTermArray, sorted_query_list):
    returnValue = []

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        #should_match.append( { 'match': {network_info['matchField']: queryTerm} })
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        #should_match.append({"match": {"node_list.node.name":{"query": queryTerm,"boost": boost_value_append}}})
        returnValue.append({'queryTerm': queryTerm, 'boostValue': boost_value_append})

    return returnValue

def get_searchBody(queryTermArray, network_info, disease, sorted_query_list, isStarSearch):
    should_match = []
    must_match = []
    returnBody = {}

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        if(isStarSearch):
            should_match.append({"match": {"node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append( { 'match': {'node_name': queryTerm} })
            #should_match.append( { 'match': {'node_list.node.name': queryTerm} })
        else:
            should_match.append({"match": {"x_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})

    if len(disease) > 0:
        diseaseWithSpaces = '';
        for addThisDisease in disease:
            if len(diseaseWithSpaces) < 1:
                diseaseWithSpaces = addThisDisease
            else:
                diseaseWithSpaces = diseaseWithSpaces + ' ' + addThisDisease

        must_match.append({'match': {'network_name': diseaseWithSpaces}})
    else:
        must_match.append({"match": {"network_name": "LAML ACC BLCA LGG BRCA CESC CHOL COAD ESCA FPPP GBM HNSC KICH KIRC KIRP LIHC LUAD LUSC DLBC MESO OV PAAD PCPG PRAD READ SARC SKCM STAD TGCT THYM THCA UCS UCEC UVM"}})


# REMOVING disease matching until we get that information back in the documents
    if(isStarSearch):
        returnBody = {
                'sort' : [
                    '_score'
                ],
                'query': {
                    'bool': {
                        #'must': must_match,
                        'should': should_match
                    }
                },
                'size': 15
            }
    else:
        returnBody = {
                'sort' : [
                    '_score'
                ],
                'query': {
                    'bool': {
                        #'must': must_match,
                        'should': should_match
                    }
                },
                'size': 12
            }

    return returnBody

#==================================
#==================================
#         STAR SEARCH
#==================================
#==================================
def get_star_search_mapped_old(queryTerms):
    network_information = {
        'searchGroupTitle': 'Star Network',
        'searchTab': 'GENES',
        'network': 'node',
        'matchField': 'node_list.node.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }

    star_network_data = star_search_mapped(network_information)

    return [star_network_data]

def get_star_search_with_disease_mapped_old(queryTerms, disease):
    network_information = {
        'searchGroupTitle': 'Star Network',
        'searchTab': 'GENES',
        'network': 'node',
        'matchField': 'node_list.node.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }
    print disease
    star_network_data = star_search_mapped(network_information, disease)

    return [star_network_data]

def star_search_mapped(network_info, disease=[]):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    queryTermArray = network_info['queryTerms'].split(',')

    unsorted_items = []
    gene_super_list = []
    variants_list = get_variants_by_query_list(queryTermArray)

    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")
    search_body = get_searchBody(queryTermArray, network_info, disease, sorted_query_list, True)

    result = es.search(
        index = 'network',
        doc_type = 'node',
        body = search_body
    )
    print("Got %d Hits:" % result['hits']['total'])

    #==================================
    # PROCESS EACH SEARCH RESULT
    #==================================
    hitCount = 0
    hitMax = 0
    hitMin = 0
    if(result['hits']['total'] < 1):
        print 'no results'

    tr = TermAnalyzer()

    for hit in result['hits']['hits']:
        if(hit["_source"]["node_name"] in queryTermArray):
            if(hitCount == 0):
                hitMax = hit['_score']
            else:
                hitMin = hit['_score']

            geneNeighborhoodArray = [];
            scoreRankCutoff = 0.039

            node_list_name_and_weight = []

            for genehit in hit["_source"]["node_list"]["node"]:
                geneNameDisected = genehit['name'].split(':')
                if(len(geneNameDisected) > 1):
                    geneNeighborhoodArray.append(geneNameDisected[0])
                else:
                    geneNeighborhoodArray.append(genehit['name'])

            x = [set(geneNeighborhoodArray), set(queryTermArray)]

            y = set.intersection(*x)

            emphasizeInfoArrayWithWeights = []

            for genehit in y:
                try:
                    match = (item for item in hit["_source"]["node_list"]['node'] if item["name"] == genehit).next()
                    #match['weight'] = match['weight'] * 70
                    emphasizeInfoArrayWithWeights.append(match)
                except Exception as e:
                    print e.message

            for gene_network_matched in y:
                gene_super_list.append(gene_network_matched)

            searchResultSummaryString = hit["_source"]["source"] + '-' + str(hit["_source"]["degree"])
            wikipedia_cancer_type = tr.get_cancer_description_by_id(hit["_source"]["network_name"]).lower().replace(',','_')
            wikipedia_cancer_type = wikipedia_cancer_type[0].upper() + wikipedia_cancer_type[1:]

            hit_score = float(hit["_score"])
            gene_network_data_items = {
                'searchResultTitle': hit["_source"]["node_name"],
                'hit_id': hit['_id'],
                'diseaseType': tr.get_cancer_description_by_id(hit["_source"]["network_name"]).replace(',',' '),
                'WikipediaDiseaseType': wikipedia_cancer_type,
                'clusterName': hit["_source"]["node_name"],
                'searchResultSummary': searchResultSummaryString,
                'searchResultScoreRank': hit["_score"],
                'luceneScore': hit["_score"],
                'searchResultScoreRankTitle': 'pubmed references ',
                'filterValue': '0.0000000029',
                'emphasizeInfoArray': set(y),
                'emphasizeInfoArrayWithWeights': emphasizeInfoArrayWithWeights,
                'top5': hitCount < 5,
                'hitOrder': hitCount,
                'pubmedCount': 0,
                'queryGenesCount': len(emphasizeInfoArrayWithWeights)
            }

            unsorted_items.append(gene_network_data_items)

            hitCount += 1

    if(hitCount == 0):
        gene_network_data_items = {
                'searchResultTitle': 'No Results',
                'hit_id': 'N/A',
                'diseaseType': "",
                'clusterName': 'No Results',
                'searchResultSummary': 'No Results',
                'searchResultScoreRank': '0',
                'luceneScore': '0',
                'searchResultScoreRankTitle': '',
                'filterValue': '0.0000000029',
                'emphasizeInfoArray': [],
                'emphasizeInfoArrayWithWeights': [],
                'top5': 'true',
                'hitOrder': '0',
                'pubmedCount': 0
            }

        gene_network_data['items'].append(gene_network_data_items)
        return gene_network_data

    print hitCount



    foundHit = False
    for network_data_item in unsorted_items:
        foundHit = False
        for sortedID in sorted_query_list['results']:
            if sortedID['id'] == network_data_item['clusterName']:
                network_data_item['pubmedCount'] = sortedID['count']
                network_data_item['searchResultScoreRank'] = sortedID['normalizedValue']
                for variant_parent in variants_list:
                    if(variant_parent['node_name'] == sortedID['id']):
                        network_data_item['variants'] = variant_parent['variants']
                gene_network_data['items'].append(network_data_item)
                foundHit = True

        if(not foundHit):
            network_data_item['pubmedCount'] = 0
            network_data_item['searchResultScoreRank'] = 0
            gene_network_data['items'].append(network_data_item)

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'queryTerm': key,
                   'boostValue': value}
        #gene_network_data['geneSuperList'].append(kv_item)

    return gene_network_data


#============================
#============================
#      CLUSTER SEARCH
#============================
#============================
def get_cluster_search_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'PATHWAYS',
        'network': 'louvain_cluster',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }

    star_network_data = cluster_search_mapped(network_information)

    return [star_network_data]

def get_cluster_search_with_disease_mapped(queryTerms, disease):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'PATHWAYS',
        'network': 'louvain_cluster',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }
    print disease

    star_network_data = cluster_search_mapped(network_information, disease)

    return [star_network_data]

def cluster_search_mapped(network_info, disease=[]):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []
    gene_super_list = []

    queryTermArray = network_info['queryTerms'].split(',')
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")
    search_body = get_searchBody(queryTermArray, network_info, disease, sorted_query_list, False)

    result = es.search(
        index = 'network',
        doc_type = 'louvain_cluster',
        body = search_body
    )
    print("Got %d Hits:" % result['hits']['total'])

    #==================================
    # PROCESS EACH SEARCH RESULT
    #==================================
    hitCount = 0
    hitMax = 0
    hitMin = 0
    if(result['hits']['total'] < 1):
        print 'no results'

    tr = TermAnalyzer()


    for hit in result['hits']['hits']:
        if(hitCount == 0):
            hitMax = hit['_score']
        else:
            hitMin = hit['_score']

        x_geneNeighborhoodArray = [];
        y_geneNeighborhoodArray = [];
        scoreRankCutoff = 0.039

        node_list_name_and_weight = []

        for genehit in hit["_source"]["x_node_list"]:
            x_geneNeighborhoodArray.append(genehit['name'])

        x_x = [set(x_geneNeighborhoodArray), set(queryTermArray)]

        x_y = set.intersection(*x_x)

        x_emphasizeInfoArrayWithWeights = []

        for genehit in x_y:
            match = (item for item in hit["_source"]["x_node_list"] if item["name"] == genehit).next()
            x_emphasizeInfoArrayWithWeights.append(match)





        for genehit in hit["_source"]["y_node_list"]:
            y_geneNeighborhoodArray.append(genehit['name'])

        y_x = [set(x_geneNeighborhoodArray), set(queryTermArray)]

        y_y = set.intersection(*y_x)

        y_emphasizeInfoArrayWithWeights = []

        for genehit in y_y:
            match = (item for item in hit["_source"]["y_node_list"] if item["name"] == genehit).next()
            y_emphasizeInfoArrayWithWeights.append(match)






#        for gene_network_matched in x_y:
#            gene_super_list.append(gene_network_matched)

        searchResultSummaryString = hit["_source"]["source"] #+ '- [hypergeometric scores coming soon]' #+ hit["_source"]["hypergeometric_scores"]
        searchResultTitle = ''
        hg_q_log_val = 0
        for hg in hit['_source']['hypergeometric_scores']:
            if(hg['qvalueLog'] > hg_q_log_val):
                hg_q_log_val = hg['qvalueLog']
                searchResultTitle = hg['name']

        hit_score = float(hit["_score"])
        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["node_name"].replace('-','') + ' ' + searchResultTitle,
            'hit_id': hit['_id'],
            'diseaseType': tr.get_cancer_description_by_id(hit["_source"]["network_name"]).replace(',',' '),
            'dataSetType': hit["_source"]["network_type"].replace('_', ' '),
            'clusterName': hit["_source"]["node_name"].replace('-',''),
            'searchResultSummary': searchResultSummaryString,
            'hypergeometricScores': hit['_source']['hypergeometric_scores'],
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': len(hit["_source"]["y_node_list"]),
            'emphasizeInfoArray': set(x_y),
            'x_emphasizeInfoArrayWithWeights': x_emphasizeInfoArrayWithWeights,
            'y_emphasizeInfoArrayWithWeights': y_emphasizeInfoArrayWithWeights,
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)

        hitCount += 1

    print hitCount



    foundHit = False
    for network_data_item in unsorted_items:
        foundHit = False
        for sortedID in sorted_query_list['results']:
            if sortedID['id'] == network_data_item['clusterName']:
                network_data_item['pubmedCount'] = sortedID['count']
                network_data_item['searchResultScoreRank'] = sortedID['normalizedValue']
                gene_network_data['items'].append(network_data_item)
                foundHit = True

        if(not foundHit):
            network_data_item['pubmedCount'] = 0
            network_data_item['searchResultScoreRank'] = 0
            gene_network_data['items'].append(network_data_item)

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'queryTerm': key,
                   'boostValue': value}
        #gene_network_data['geneSuperList'].append(kv_item)

    return gene_network_data



#============================
#============================
#      VARIANT SEARCH
#============================
#============================
def get_dbsnp_search_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'VARIANT',
        'network': 'cluster',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }

    phenotype_network_data = dbsnp_search_mapped(network_information)

    return [phenotype_network_data]

def dbsnp_search_mapped(network_info, disease=[]):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []
    gene_super_list = []

    queryTermArray = network_info['queryTerms'].split(',')
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    should_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        #should_match.append({"match": {"node_name": queryTerm}})
        should_match.append({"match": {"node_list.node.name": queryTerm}})




    search_body = {
        'sort' : [
            '_score'
        ],
        'query': {
            'bool': {
                'should': should_match
            }
        },
        'size': 35
    }

    result = es.search(
        index = 'network',
        doc_type = 'dbsnp_network',
        body = search_body
    )

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

        geneNeighborhoodArray = [];
        scoreRankCutoff = 0.039

        node_list_name_and_weight = []

        for geneNodeHit in hit["_source"]["node_list"]:

            for genehit in geneNodeHit["node"]:
                geneNeighborhoodArray.append(genehit['name'])

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithWeights = []

        for genehit in y:
            for node_list_items in hit["_source"]["node_list"]:
                match = (item for item in node_list_items["node"] if item["name"] == genehit).next()
                emphasizeInfoArrayWithWeights.append(match)

        for gene_network_matched in y:
            gene_super_list.append(gene_network_matched)

        searchResultSummaryString = hit["_source"]["source"] + '-' + str(hit["_source"]["total_degree"])

        hit_score = float(hit["_score"])
        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["node_name"],
            'diseaseType': '',
            'clusterName': hit["_source"]["node_name"],
            'searchResultSummary': searchResultSummaryString,
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': set(y),
            'emphasizeInfoArrayWithWeights': emphasizeInfoArrayWithWeights,
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)

        hitCount += 1

    print hitCount



    foundHit = False
    for network_data_item in unsorted_items:
        foundHit = False
        for sortedID in sorted_query_list['results']:
            if sortedID['id'] == network_data_item['clusterName']:
                network_data_item['pubmedCount'] = sortedID['count']
                network_data_item['searchResultScoreRank'] = sortedID['normalizedValue']
                gene_network_data['items'].append(network_data_item)
                foundHit = True

        if(not foundHit):
            network_data_item['pubmedCount'] = 0
            network_data_item['searchResultScoreRank'] = 0
            gene_network_data['items'].append(network_data_item)

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'queryTerm': key,
                   'boostValue': value}
        #gene_network_data['geneSuperList'].append(kv_item)

    return gene_network_data


#============================
#============================
#      VARIANT LIST
#============================
#============================
def get_variants_by_query_list(queryTerms):
    queryTermArray = queryTerms #.split(',')
    should_match = []

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_name": queryTerm}})

    search_body = {
        'sort' : [
            '_score'
        ],
        'fields': [ 'node_name', 'total_degree', 'node_list.node.name'],
        'query': {
            'bool': {
                'should': should_match
            }
        },
        'size': 35
    }

    result = es.search(
        index = 'network',
        doc_type = 'dbsnp_network',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    #==================================
    # PROCESS EACH SEARCH RESULT
    #==================================
    hitCount = 0
    if(result['hits']['total'] < 1):
        print 'no results'

    return_results = []

    for hit in result['hits']['hits']:
        result_node_name = hit['fields']['node_name'][0]
        variants_array = [];
        field_count = 0
        for geneNodeHit in hit["fields"]["node_list.node.name"]:
            if(field_count < 4):
                variants_array.append(geneNodeHit)
            else:
                break
            field_count += 1

        a = {
            'node_name': result_node_name,
            'variants': variants_array
        }
        return_results.append(a)

        hitCount += 1

    print hitCount

    return return_results




#======================================
#======================================
#   PEOPLE - AUTHOR CENTERED SEARCH
#======================================
#======================================
def get_people_people_pubmed_search_mapped(queryTerms):
    should_match = []
    must_match = []

    queryTermArray = queryTerms.split(',')
    #popular_authors = get_people_pubmed_search_mapped(queryTerms, True)

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.node.name": queryTerm}})
#        should_match.append({"match": {"node_list.node.publications.Keywords": queryTerm}})

    #for popular_author in popular_authors:
    #    should_match.append({"match": {"node_name": popular_author}})


    search_body = {
        'query': {
            'bool': {
                'should': should_match
                #'must': should_match
            }
        },
        'size': 50
    }

    #search_body = {
    #    'query': {
    #        'function_score': {
    #            'query': {
    #                'bool': {
    #                    'should': should_match
    #                }
    #            },
    #            'field_value_factor': {
    #                'field': 'node_list.node.degree',
    #                'factor': 1.0,
    #                'modifier': 'sqrt',
    #                'missing': 1
    #            }
    #        }
    #    }
    #}

    result = es.search(
        index = 'network',
        doc_type = 'author',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    gene_network_data = {
        'searchGroupTitle': 'People pubmed',
        'clusterNodeName': "",
        'searchTab': 'PEOPLE_GENE',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

#    authors_array = []
#    for hit in result['hits']['hits']:
#        for author in hit['_source']['node_list']['node']:
#            if(author['name'] not in authors_array):
#                authors_array.append(author['name'])

#    author_gene_json = []
#    for author in authors_array:
#        author_gene_array = []
#        for hit in result['hits']['hits']:
#            for author in hit['_source']['node_list']['node']:
#                myAuthor = author
#                myAuthorName = author['name']
#                if(author['name'] == author['name']):
#                    author_gene_array.append(hit["_source"]["node_name"])

#        author_gene_json.append({'author': author,
#                                 'genes': author_gene_array})


    for hit in result['hits']['hits']:
        emphasizeInfoArray = []
        #for author in hit['_source']['node_list']['node']:
        #    gene_count = len(author['publications'])
        #    emphasizeInfoArray.append({'author': author,
        #                               'gene_count': gene_count})


        geneNeighborhoodArray = [];
        gene_pub_count = 0
        for geneNodeHit in hit["_source"]["node_list"]["node"]:
            gene_count = len(geneNodeHit['publications'])
            geneNeighborhoodArray.append(geneNodeHit['name'])
            emphasizeInfoArray.append({'gene': geneNodeHit['name'],
                                       'gene_count': gene_count})

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithPublications = []
        genes_overlap = ""
        all_pub_counts = 0
        for geneNodeHit in hit["_source"]["node_list"]["node"]:
            for yhit in y:
                if(yhit == geneNodeHit['name']):
                    all_pub_counts += len(geneNodeHit['publications'])
                    genes_overlap += yhit + ','
                    emphasizeInfoArrayWithPublications.append({'gene': yhit, 'publication_counts': len(geneNodeHit['publications'])})
                    break

        if(len(genes_overlap) > 0):
            genes_overlap = genes_overlap[:-1]


        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["node_name"],
            'hit_id': hit['_id'],
            'diseaseType': '',
            'clusterName': hit['_source']['node_name'],
            'searchResultSummary': 'Pubmed', #(' + str(hit['_source']['degree']) + ')',
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': emphasizeInfoArrayWithPublications,  #set(y),#emphasizeInfoArray,
            'genes_overlap': genes_overlap,
            'emphasizeInfoArrayWithWeights': [],
            'top5': False,
            'hitOrder': 0,
            'all_pub_counts': all_pub_counts,
            'pubmedCount': hit['_source']['degree']
        }
        gene_network_data['items'].append(gene_network_data_items)

    return [gene_network_data]


def get_people_people_pubmed_search_mapped2(queryTerms):
    should_match = []

    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.name": queryTerm}})

    search_body = {
      'query': {
          'filtered': {
             'query': {
                'bool': {
                    'must': [
                    {
                      'nested': {
                        'path': 'node_list',
                        'score_mode': 'sum',
                            'query': {
                                'function_score': {
                                  'query': {
                                       'bool': {
                                            'should': should_match
                                       }
                                  },
                                  'field_value_factor': {
                                    'field': 'node_list.scores',
                                    'factor': 1,
                                    'modifier': 'none',
                                    'missing': 1
                                  },
                                  'boost_mode': 'replace'
                                }
                            }
                      }
                    }
                  ]
                }
             },
             'filter': {
                'or': {
                   'filters': [
                      {'terms': {
                         'network_name': [
                            'pubmed_author'
                         ]
                      }}
                   ]
                }
             }
          }
      }
    }

    result = es.search(
        index = 'network',
        doc_type = 'pubmed_author',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    gene_network_data = {
        'searchGroupTitle': 'People pubmed',
        'clusterNodeName': "",
        'searchTab': 'PEOPLE_GENE',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    for hit in result['hits']['hits']:
        emphasizeInfoArray = []

        geneNeighborhoodArray = [];
        gene_pub_count = 0
        for geneNodeHit in hit["_source"]["node_list"]:
            gene_count = len(geneNodeHit['publications'])
            geneNeighborhoodArray.append(geneNodeHit['name'])
            emphasizeInfoArray.append({'gene': geneNodeHit['name'],
                                       'gene_count': gene_count})

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithPublications = []
        genes_overlap = ""
        all_pub_counts = 0
        for geneNodeHit in hit["_source"]["node_list"]:
            for yhit in y:
                if(yhit == geneNodeHit['name']):
                    all_pub_counts += len(geneNodeHit['publications'])
                    genes_overlap += yhit + ','
                    emphasizeInfoArrayWithPublications.append({'gene': yhit, 'publication_counts': len(geneNodeHit['publications'])})
                    break

        if(len(genes_overlap) > 0):
            genes_overlap = genes_overlap[:-1]


        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["node_name"],
            'hit_id': hit['_id'],
            'diseaseType': '',
            'clusterName': hit['_source']['node_name'],
            'searchResultSummary': 'Pubmed',  #(' + str(hit['_source']['degree']) + ')',
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': emphasizeInfoArrayWithPublications,  #set(y),#emphasizeInfoArray,
            'genes_overlap': genes_overlap,
            'emphasizeInfoArrayWithWeights': [],
            'top5': False,
            'hitOrder': 0,
            'all_pub_counts': all_pub_counts,
            'pubmedCount': hit['_source']['degree']
        }
        gene_network_data['items'].append(gene_network_data_items)

    return [gene_network_data]

#============================
#============================
#   PEOPLE TO GENE BOOST
#============================
#============================
def get_people_gene_boost(queryTerms):
    should_match = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.node.name": queryTerm}})

    search_body = {
        'fields': [ 'node_name', 'total_degree', 'node_list.node.name', 'node_list.node.publications.PMID'],
        'query': {
            'bool': {
                'should': should_match
            }
        },
        'size': 30
    }

    result = es.search(
        index = 'network',
        doc_type = 'author',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    for hit in result['hits']['hits']:
        n_gene_count = len(hit['fields']['node_list.node.name'])
        n_publication_count = len(hit['fields']['node_list.node.publications.PMID'])

        gene_pub_ratio = n_publication_count / n_gene_count

        print "%s - %s" % (hit['fields']['node_name'], gene_pub_ratio)


    return 'success'


#=====================================
#=====================================
#   GENE TO PEOPLE SEARCH FAST (lazy)
#=====================================
#=====================================
def get_people_pubmed_search_fast_lazy_mapped(queryTerms, return_top_hits):
    must_match = []
    popular_authors = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        must_match.append({"match": {"node_name": queryTerm}})

    search_body = {
        'sort' : [
            '_score'
        ],
        'query': {
            'bool': {
                'should': must_match
            }
        },
        'size': 25
    }

    result = es.search(
        index = 'network',
        doc_type = 'pubmed',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    gene_network_data = {
        'searchGroupTitle': 'People pubmed',
        'clusterNodeName': "",
        'searchTab': 'PEOPLE',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

#    authors_array = []
#    for hit in result['hits']['hits']:
#        for author in hit['_source']['node_list']['node']:
#            if(author['name'] not in authors_array):
#                authors_array.append(author['name'])

#    author_gene_json = []
#    for author in authors_array:
#        author_gene_array = []
#        for hit in result['hits']['hits']:
#            for author in hit['_source']['node_list']['node']:
#                myAuthor = author
#                myAuthorName = author['name']
#                if(author['name'] == author['name']):
#                    author_gene_array.append(hit["_source"]["node_name"])

#        author_gene_json.append({'author': author,
#                                 'genes': author_gene_array})


    for hit in result['hits']['hits']:
        emphasizeInfoArray = []
        for author in hit['_source']['node_list']['node']:
            article_count = len(author['publications'])
            if(return_top_hits):
                if(article_count >= 3):
                    if(author['name'] not in popular_authors):
                        popular_authors.append(author['name'])
                    emphasizeInfoArray.append({'author': author['name'],
                                       'article_count': article_count})
            else:
                emphasizeInfoArray.append({'author': author,
                                       'article_count': article_count})


        if(not return_top_hits):
            gene_network_data_items = {
                'searchResultTitle': hit["_source"]["node_name"],
                'hit_id': hit['_id'],
                'diseaseType': '',
                'clusterName': hit['_source']['node_name'],
                'searchResultSummary': 'Pubmed (' + str(hit['_source']['degree']) + ')',
                'searchResultScoreRank': hit["_score"],
                'luceneScore': hit["_score"],
                'searchResultScoreRankTitle': 'pubmed references ',
                'filterValue': '0.0000000029',
                'emphasizeInfoArray': emphasizeInfoArray,
                'emphasizeInfoArrayWithWeights': [],
                'top5': False,
                'hitOrder': 0,
                'pubmedCount': hit['_source']['degree']
            }
            gene_network_data['items'].append(gene_network_data_items)

    if(return_top_hits):
        return popular_authors
    else:
        return [gene_network_data]


#============================
#============================
#   GENE TO PEOPLE SEARCH
#============================
#============================
def get_people_pubmed_search_mapped(queryTerms, return_top_hits):
    must_match = []
    popular_authors = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        must_match.append({"match": {"node_name": queryTerm}})

    search_body = {
        'sort' : [
            '_score'
        ],
        'query': {
            'bool': {
                'should': must_match
            }
        },
        'size': 25
    }

    result = es.search(
        index = 'network',
        doc_type = 'pubmed',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    gene_network_data = {
        'searchGroupTitle': 'People pubmed',
        'clusterNodeName': "",
        'searchTab': 'PEOPLE',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

#    authors_array = []
#    for hit in result['hits']['hits']:
#        for author in hit['_source']['node_list']['node']:
#            if(author['name'] not in authors_array):
#                authors_array.append(author['name'])

#    author_gene_json = []
#    for author in authors_array:
#        author_gene_array = []
#        for hit in result['hits']['hits']:
#            for author in hit['_source']['node_list']['node']:
#                myAuthor = author
#                myAuthorName = author['name']
#                if(author['name'] == author['name']):
#                    author_gene_array.append(hit["_source"]["node_name"])

#        author_gene_json.append({'author': author,
#                                 'genes': author_gene_array})


    for hit in result['hits']['hits']:
        emphasizeInfoArray = []
        for author in hit['_source']['node_list']['node']:
            article_count = len(author['publications'])
            if(return_top_hits):
                if(article_count >= 3):
                    if(author['name'] not in popular_authors):
                        popular_authors.append(author['name'])
                    emphasizeInfoArray.append({'author': author['name'],
                                       'article_count': article_count})
            else:
                emphasizeInfoArray.append({'author': author,
                                       'article_count': article_count})


        if(not return_top_hits):
            gene_network_data_items = {
                'searchResultTitle': hit["_source"]["node_name"],
                'hit_id': hit['_id'],
                'diseaseType': '',
                'clusterName': hit['_source']['node_name'],
                'searchResultSummary': 'Pubmed (' + str(hit['_source']['degree']) + ')',
                'searchResultScoreRank': hit["_score"],
                'luceneScore': hit["_score"],
                'searchResultScoreRankTitle': 'pubmed references ',
                'filterValue': '0.0000000029',
                'emphasizeInfoArray': emphasizeInfoArray,
                'emphasizeInfoArrayWithWeights': [],
                'top5': False,
                'hitOrder': 0,
                'pubmedCount': hit['_source']['degree']
            }
            gene_network_data['items'].append(gene_network_data_items)

    if(return_top_hits):
        return popular_authors
    else:
        return [gene_network_data]



#===================================
#===================================
#   PEOPLE && GENE TARGETED SEARCH
#===================================
#===================================
def get_people_gene_targeted_search(author, genes):
    return_value = []
    queryTermArray = genes.split(',')
    for gene in queryTermArray:
        must_match = []
        must_match.append({"match": {"node_list.node.name": gene}})
        must_match.append({"match": {"node_name": author}})

        g_value = {
            'gene': gene,
            'author': author,
            'publications': []
        }
        publications = []

        search_body = {
            'query': {
                'bool': {
                    'should': must_match
                }
            },
            'size': 1
        }

        result = es.search(
            index = 'network',
            doc_type = 'pubmed_author',
            body = search_body
        )

        print("Got %d Hits:" % result['hits']['total'])

        for hit in result['hits']['hits']:
            for found_gene in hit['_source']['node_list']:
                if(found_gene['name'] == gene):
                    publications = found_gene['publications']
                    break

        g_value['publications'] = publications
        return_value.append(g_value)

    return return_value






#============================
#============================
#      DRUG SEARCH
#============================
#============================
def get_drug_network_search_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'DRUG',
        'network': 'drug_network',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }

    phenotype_network_data = drug_network_search_mapped(network_information)

    return [phenotype_network_data]

def drug_network_search_mapped(network_info, disease=[]):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []
    gene_super_list = []

    queryTermArray = network_info['queryTerms'].split(',')
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    should_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        should_match.append({"match": {"node_list.node.name": queryTerm}})


    search_body = {
        'sort' : [
            '_score'
        ],
        'query': {
            'bool': {
                'should': should_match
            }
        },
        'size': 50
    }

    result = es.search(
        index = 'network',
        doc_type = 'drugbank',
        body = search_body
    )

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

        geneNeighborhoodArray = [];
        scoreRankCutoff = 0.039

        node_list_name_and_weight = []

        for geneNodeHit in hit["_source"]["node_list"]['node']:
            geneNeighborhoodArray.append(geneNodeHit['name'])

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithWeights = []

        for genehit in y:
            node_list_items = hit["_source"]["node_list"]
            match = (item for item in node_list_items["node"] if item["name"] == genehit).next()
            emphasizeInfoArrayWithWeights.append(match)

        for gene_network_matched in y:
            gene_super_list.append(gene_network_matched)

        searchResultSummaryString = 'drugbank-' + str(hit["_source"]["degree"])
        #searchResultSummaryString = hit["_source"]["source"] + '-' + str(hit["_source"]["total_degree"])

        hit_score = float(hit["_score"])

        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["node_name"], #DrugBank.get_drugbank_synonym(hit["_source"]["node_name"]),
            'diseaseType': '',
            'clusterName': hit["_source"]["drugbank_id"],
            'searchResultSummary': searchResultSummaryString,
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': list(y),
            'emphasizeInfoArrayWithWeights': emphasizeInfoArrayWithWeights,
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)

        hitCount += 1

    print hitCount



    foundHit = False
    for network_data_item in unsorted_items:
        foundHit = False
        for sortedID in sorted_query_list['results']:
            if sortedID['id'] == network_data_item['clusterName']:
                network_data_item['pubmedCount'] = sortedID['count']
                network_data_item['searchResultScoreRank'] = sortedID['normalizedValue']
                gene_network_data['items'].append(network_data_item)
                foundHit = True

        if(not foundHit):
            network_data_item['pubmedCount'] = 0
            network_data_item['searchResultScoreRank'] = 0
            gene_network_data['items'].append(network_data_item)

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'queryTerm': key,
                   'boostValue': value}
        #gene_network_data['geneSuperList'].append(kv_item)



    #===============================
    # GROUP DRUGS BY TARGETED GENE
    #===============================
    drug_gene_grouping = []

    for drug_hit in gene_network_data['items']:
        match_found = False
        # After first item is already added (need to append to existing array)
        for gene_loop_item in drug_gene_grouping:
            if(len(drug_hit['emphasizeInfoArray']) > 0):
                if(gene_loop_item['gene_name'] == drug_hit['emphasizeInfoArray'][0]):
                    gene_loop_item['searchResultTitle'].append({'drug_name': drug_hit['searchResultTitle'],
                                               'drugbank_id': drug_hit['clusterName']})
                    match_found = True

        # First item added
        if(not match_found):
            if(len(drug_hit['emphasizeInfoArray']) > 0):
                drug_gene_grouping.append(
                    {
                        'gene_name': drug_hit['emphasizeInfoArray'][0],
                        'searchResultTitle': [{'drug_name': drug_hit['searchResultTitle'],
                                               'drugbank_id': drug_hit['clusterName']}]
                    }
                )
            else:
                drug_gene_grouping.append(
                    {
                        'gene_name': 'unknown',
                        'searchResultTitle': [{'drug_name': drug_hit['searchResultTitle'],
                                               'drugbank_id': drug_hit['clusterName']}]
                    }
                )

    for drug_gene_no_count_item in drug_gene_grouping:
        drug_gene_no_count_item['gene_count'] = len(drug_gene_no_count_item['searchResultTitle'])


    #drug_gene_dumped = dumps(drug_gene_grouping)

    gene_network_data['grouped_items'] = drug_gene_grouping

    return gene_network_data

#============================
#============================
#   COEXPRESSION SEARCH
#============================
#============================
def get_coexpression_network_search_mapped(queryTerms, genome=None):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'GENES',
        'network': 'Co-expression',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms,
        'genome': ''
    }

    coexpression_network_data = coexpression_network_search_mapped(network_information, genome)

    return [coexpression_network_data]

def coexpression_network_search_mapped(network_info, genome):
    genome_lookup = ''

    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []
    gene_super_list = []

    queryTermArray = network_info['queryTerms'].split(',')
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    should_match = []
    must_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        should_match.append({"match": {"node_list.name": queryTerm}})
        should_match.append({"match": {"node_name": queryTerm}})

    must_match.append({'match': {'network_name': 'Co-expression'}})

    if(genome):
        if(genome == 'RAT'):
            genome_lookup = 'rattus_norvegicus'
        elif(genome == 'MOUSE'):
            genome_lookup = 'mus_musculus'
        elif(genome == 'HUMAN'):
            genome_lookup = 'human'

        must_match.append({'match': {'species': genome_lookup}})

    #must_match.append({'match': {'species': 'human'}})

    search_body = {
        'sort' : [
            '_score'
        ],
        'query': {
            'bool': {
                'must': must_match,
                'should': should_match
            }
        },
        'size': 15
    }

    result = es.search(
        index = 'network',
        doc_type = 'genemania',
        body = search_body
    )

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

        geneNeighborhoodArray = [];
        scoreRankCutoff = 0.039

        node_list_name_and_weight = []

        for geneNodeHit in hit["_source"]["node_list"]:

            for genehit in geneNodeHit["node"]:
                geneNeighborhoodArray.append(genehit['name'].upper())

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithWeights = []

        for genehit in y:
            for node_list_items in hit["_source"]["node_list"]:
                match = (item for item in node_list_items["node"] if item["name"].upper() == genehit).next()
                #match['weight'] = match['weight'] * 10
                emphasizeInfoArrayWithWeights.append(match)

        for gene_network_matched in y:
            gene_super_list.append(gene_network_matched)

        searchResultSummaryString = hit["_source"]["source"] + '-' + str(hit["_source"]["total_degree"])

        hit_score = float(hit["_score"])
        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["node_name"].upper(),
            'diseaseType': '[Species = ' + hit['_source']['species'] + ']',
            'clusterName': hit["_source"]["node_name"].upper(),
            'searchResultSummary': searchResultSummaryString,
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': set(y),
            'emphasizeInfoArrayWithWeights': emphasizeInfoArrayWithWeights,
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)

        hitCount += 1

    print hitCount



    foundHit = False
    for network_data_item in unsorted_items:
        foundHit = False
        for sortedID in sorted_query_list['results']:
            if sortedID['id'] == network_data_item['clusterName']:
                network_data_item['pubmedCount'] = sortedID['count']
                network_data_item['searchResultScoreRank'] = sortedID['normalizedValue']
                gene_network_data['items'].append(network_data_item)
                foundHit = True

        if(not foundHit):
            network_data_item['pubmedCount'] = 0
            network_data_item['searchResultScoreRank'] = 0
            gene_network_data['items'].append(network_data_item)

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'queryTerm': key,
                   'boostValue': value}
        #gene_network_data['geneSuperList'].append(kv_item)

    return gene_network_data



def get_boost_value(boostArray, idToCheck):
    for boostItem in boostArray:
        if(boostItem['id'] == idToCheck):
            returnThisValue = boostItem['normalizedValue']
            return boostItem['normalizedValue']

    return 0

def star_search_mapped_2_0(network_info):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []

    gene_super_list = []

    sorted_query_list = PubMed.get_gene_pubmed_counts(network_info['queryTerms'])

    queryTermArray = network_info['queryTerms'].split(',')
    should_match = [] #[{ 'match': {'network_name': network_info['cancerType']}}]

    for queryTerm in queryTermArray:
        should_match.append( { 'match': {network_info['matchField']: queryTerm} })

    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    es_body = {
            'fields': ['node_ame'],
            'query': {
                'bool': {
                    'should': should_match,
                }
            }
        }

    #es_body_json = dumps(es_body)

    result = es.search(
        index='network',
        doc_type=network_info['network'], # node
        body={
            'fields': ['node_name'],
            'query': {
                'bool': {
                    'should': should_match,
                    #"must_not" : { "term" : {"degree" : "1"} },
                    #'should': [{ 'match': {network_info['matchField']: network_info['queryTerms']} }]
                }
            }
            ,'size': 100
        }
    )
    #should_json = dumps(should_match)
    #result_json = dumps(result)
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

        geneNeighborhoodArray = [];
        scoreRankCutoff = 0.039

        searchResultSummaryString = hit["_source"]["source"] + '-' + hit["_source"]["degree"]

        hit_score = float(hit["_score"])
        gene_network_data_items = {
            #'searchResultTitle': hit["_source"]["source"] + '-' + hit["_source"]["degree"] + '-' + hit["_source"]["nodeName"],
            'searchResultTitle': hit["_source"]["node_name"],
            'clusterName': hit["_source"]["node_name"],
            'searchResultSummary': searchResultSummaryString,
            'searchResultScoreRank': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': [],
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)
        hitCount += 1


    gene_network_data['items'] = unsorted_items
    #print('%s ' % dumps(gene_network_data))

    return gene_network_data


def star_prep_for_cytoscape_js(clusterName):
    cytoscape_elements = []
    cytoObj = []

    result = es.search(
        index='network',
        doc_type='node', # node
        body={
            'query': {
                'bool': {
                    'must': [
                        { 'match': {'network_name': 'BRCA'} },
                        { 'match': {'node_name': clusterName}}
                    ],
                }
            },
            "size": 2
        }
    )

    print("Got %d Hits:" % result['hits']['total'])
    for hit in result['hits']['hits']:
        node_list = hit['_source']['node_list']['node']
        i = 0

        cytoscape_init_model = {
            'group': 'nodes',
            'data': {
                'id': str(i),
                'nodeName': hit['_source']['node_name'],
                'shortName': hit['_source']['node_name'],
                'address': '',
                'centerNode': 'true',
                'score': 100
            }
        }
        i += 1
        cytoObj.append(cytoscape_init_model)

        for node_item in node_list:
            if(float(node_item['weight']) > 0.59):
                shortName = node_item['name'].split(':')

                cytoscape_model = {
                    'group': 'nodes',
                    'data': {
                        'id': str(i),
                        'nodeName': node_item['name'],
                        'shortName': shortName[0] + '\n\n' + shortName[1] if len(shortName) > 1 else '',
                        'address': shortName[1] if len(shortName) > 1 else '',
                        'centerNode': 'false',
                        'score': float(node_item['weight']) * 10
                    }
                }

                cytoscape_edge_model = {
                    'group': 'edges',
                    'data': {
                        'id': 'e' + str(i),
                        'source': str(i),
                        'weight': float(node_item['weight']) * 10,
                        'target': '0'
                    }
                }

                cytoObj.append(cytoscape_model)
                cytoObj.append(cytoscape_edge_model)

                i += 1

#        while i >= 1:
            #{data: { id: 'e1', source: 'SLC24A6:12-113772827', target: 'CDKN1C:11-2907332'},group: 'edges'}
#            cytoscape_edge_model = {
#                'group': 'edges',
#                'data': {
##                    'id': 'e' + str(i),
#                    'source': str(i),
#                    'target': '0'
#                }
#            }

#            cytoObj.append(cytoscape_edge_model)

#            i -= 1
    #print(dumps(cytoObj))

    return cytoObj


def get_single_star_search(term_name):
    neighborhood = [];

    es_body = {
        'fields': ['node_name', 'source', 'degree', 'node_list.node.name'],
        'query': {
            'bool': {
                'should': [{ 'match': {'node_name': term_name} }]
            }
        },
        'size': 2
        }

    #es_body_json = dumps(es_body)

    results = es.search(
        index='network',
        doc_type='node', # node
        body={
        #'fields': ['nodeName', 'source', 'degree', 'node_list.node.name'],
        'query': {
            'bool': {
                'must': [{'match': {'network_name': 'BRCA'}}],
                'should': [{ 'match': {'node_name': term_name} }]
            }
        },
        'size': 2
        }
    )


    #result_json = dumps(results)
    print("Got %d Hits:" % results['hits']['total'])

    return results




def get_star_pvalue(queryTerms):
    queryTermArray = queryTerms.split(',')

    result = es.search(
        index='network',
        doc_type='node',
        body={
            'sort' : ['_score'],
            "fields": [ "node_name", "node_list.node.name" ],
            'query': {
                'bool': {
                    'must': [{ 'match': {'network_name': 'BRCA'} }],
                    "must_not" : { 'term' : {'degree' : '1'} },
                    'should': [{ 'match': {'node_list.node.name': queryTerms}}]
                }
            }#,
            #"size": 4
        }
    )

    for hit in result['hits']['hits']:
        geneNeighborhoodArray = [];
        for genehit in hit["fields"]["node_list.node.name"]:
            geneNameDisected = genehit.split(':')
            if(len(geneNameDisected) > 1):
                geneNeighborhoodArray.append(geneNameDisected[0])
            else:
                geneNeighborhoodArray.append(genehit['name'])

        for geneRefined in geneNeighborhoodArray:
            print('%s' % geneRefined)


def get_all_searches(queryTerms):

    return [get_gene_network_search_mapped(queryTerms), get_pathway_network_search_mapped(queryTerms), get_protein_network_search_mapped(queryTerms)]

def get_gene_network_search_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Gene Networks',
        'searchTab': 'GENESX',
        'network': 'gene_network',
        'matchField': 'gene_neighborhood.neighbors.name'

    }

    gene_network_data = get_genemania_generic_network_search_mapped(queryTerms, network_information)

    return gene_network_data

def get_pathway_network_search_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Pathway Networks',
        'searchTab': 'PATHWAYSX',
        'network': 'pathway_network',
        'matchField': 'gene_neighborhood.neighbors.name'

    }

    pathway_network_data = get_genemania_generic_network_search_mapped(queryTerms, network_information)

    return pathway_network_data

def get_protein_network_search_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Protein Networks',
        'searchTab': 'PROTEIN',
        'network': 'protein_network',
        'matchField': 'gene_neighborhood.neighbors.name'

    }

    protein_network_data = get_genemania_generic_network_search_mapped(queryTerms, network_information)

    return protein_network_data






############################
## Methods that support
## Search Page Link Clicks
############################

def get_gene_network_by_nodeName(queryTerms):
    network_information = {
        'searchGroupTitle': 'Gene Networks',
        'searchTab': 'GENES',
        'network': 'gene_network',
        'matchField': 'gene_neighborhood.neighbors.name'

    }

    gene_network_data = get_generic_network_by_nodeName(queryTerms)

    return gene_network_data


def get_generic_network_by_nodeName(queryTerm):
    network_info = {
        'searchGroupTitle': 'Gene Networks',
        'searchTab': 'GENES',
        'network': 'gene_network',
        'matchField': 'gene_neighborhood.neighbors.name'
    }

    result = es.search(
        index='network',
        doc_type=network_info['network'],
        body={
                "fields": [ "source", "node_name", "gene_neighborhood.neighbors.name" ],
                "query" : {
                       "match": {
                           "node_name": queryTerm #"OR2H1"
                        }
                },
            "size": 2
        }
    )
    print("Got %d Hits:" % result['hits']['total'])

    return result['hits']['hits']



################
#########################






def get_genemania_generic_network_search_mapped(queryTerms, network_info):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    gene_super_list = []

    queryTermArray = queryTerms.split(',')

    result = es.search(
        index='network',
        doc_type=network_info['network'],
        body={
            'sort' : [
                '_score'
            ],
            'query': {
                'match': {
                    network_info['matchField']: queryTerms
                }
            },
            "size": 10
        }
    )
    print("Got %d Hits:" % result['hits']['total'])

    #==================================
    # PROCESS EACH SEARCH RESULT
    #==================================
    hitCount = 0
    hitMax = 0
    hitMin = 0
    for hit in result['hits']['hits']:
        if(hitCount == 0):
            hitMax = hit['_score']
        else:
            hitMin = hit['_score']

        geneNeighborhoodArray = [];
        scoreRankCutoff = 0.039

        for genehit in hit["_source"]["gene_neighborhood"]["neighbors"]:
            geneNeighborhoodArray.append(genehit['name'])

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        for gene_network_matched in y:
            gene_super_list.append(gene_network_matched)

        searchResultSummaryString = 'Gene Neighborhood (' + str(len(hit["_source"]["gene_neighborhood"]["neighbors"])) + ') '
        if('pathway_neighborhood' in hit["_source"]):
            searchResultSummaryString += 'Pathway Neighborhood (' + str(len(hit["_source"]["pathway_neighborhood"]["neighbors"])) + ') '
        if('protein_neighborhood' in hit["_source"]):
            searchResultSummaryString += 'Protein Neighborhood (' + str(len(hit["_source"]["protein_neighborhood"]["neighbors"])) + ') '
        if('trxfactor_neighborhood' in hit["_source"]):
            searchResultSummaryString += 'TRx Neighborhood (' + str(len(hit["_source"]["trxfactor_neighborhood"]["neighbors"])) + ') '


        hit_score = float(hit["_score"])
        gene_network_data_items = {
            'searchResultTitle': hit["_source"]["source"] + '-' + hit["_source"]["total_degree"] + '-' + hit["_source"]["node_name"],
            'searchResultSummary': searchResultSummaryString,
            #'searchResultScoreRank': hit["_score"],
            'searchResultScoreRankTitle': 'score ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': set(y),
            'luceneScore': hit["_score"],
            'top5': hitCount < 5,
            'hitOrder': hitCount
        }

        #print('%s ' % gene_network_data_items["searchResultTitle"])
        #print('%s ' % y)

        gene_network_data['items'].append(gene_network_data_items)
        hitCount += 1

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'geneId': key,
                   'geneCount': value}
        gene_network_data['geneSuperList'].append(kv_item)


    #print('%s ' % dumps(counter_gene_list))

    #print('%s ' % dumps(gene_network_data))

    return gene_network_data

#def get_star_search_mapped_2_0(queryTerms):
#    network_information = {
#        'searchGroupTitle': 'Star Network',
#        'searchTab': 'GENES',
#        'network': 'node',
#        'matchField': 'nodeName',
#        'matchCoreNode': 'nodeName',
#        'cancerType': 'BRCA',
#        'queryTerms': queryTerms
#    }

#    star_network_data = star_search_mapped_2_0(network_information)

#    return [star_network_data]

def get_star_search_neighborhood_mapped(queryTerms):
    network_information = {
        'searchGroupTitle': 'Star Network',
        'searchTab': 'GENES',
        'network': 'node',
        'matchField': 'node_list.node.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }

    star_network_data = star_search_mapped_2_0(network_information)

    return [star_network_data]

def generate_search_results():
    return 0

def get_genes_from_elastic_by_id(elasticId, search_type):
    search_body = {
        'sort' : [
            '_score'
        ],
       'query': {
            'bool': {
                'must': [
                   {'match': {
                      '_id': elasticId
                   }}
                ]
            }
        },
        'size': 1
    }

    result = es.search(
        index = 'network',
        doc_type = search_type,
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    #==================================
    # PROCESS EACH SEARCH RESULT
    #==================================
    hitCount = 0
    geneNeighborhoodArray = [];
    if(result['hits']['total'] < 1):
        print 'no results'

    hit = result['hits']['hits'][0]
    for geneNodeHit in hit["_source"]['node_list']['node']:
        geneNeighborhoodArray.append(geneNodeHit['name'])

    return geneNeighborhoodArray

def get_clinvar_phenotypes():
    phenotypes = []

    search_body = {
        'fields': ['node_name'],
       'query': {
            'match_all': {}
        },
        'size': 40000
    }

    result = es.search(
        index = 'network',
        doc_type = 'clinvar',
        body = search_body
    )

    if(result['hits']['total'] < 1):
        print 'no results'
    else:
        for hit in result['hits']['hits']:
            hit_name_array = hit['fields']['node_name']
            for hit_name in hit_name_array:
                phenotypes.append(hit_name)

    return phenotypes

def get_clinvar_phenotypes():
    phenotypes = []

    search_body = {
        'fields': ['node_name'],
       'query': {
            'match_all': {}
        },
        'size': 40000
    }

    result = es.search(
        index = 'network',
        doc_type = 'clinvar',
        body = search_body
    )

    if(result['hits']['total'] < 1):
        print 'no results'
    else:
        for hit in result['hits']['hits']:
            hit_name_array = hit['fields']['node_name']
            for hit_name in hit_name_array:
                phenotypes.append(hit_name)

    return phenotypes

def get_clinvar_search(queryTerms, phenotypes=None):
    hitCount = 0
    phenotype_network_data = {
        'searchGroupTitle': 'Phenotypes',
        'clusterNodeName': "",
        'searchTab': 'PHENOTYPES',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    should_match = []
    must_match = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.node.name": queryTerm}})

    if(phenotypes is not None):
        phenotypeTermArray = phenotypes.split('~')

        for phenotypeTerm in phenotypeTermArray:
            must_match.append({"match": {"node_name": phenotypeTerm}})

            search_body = {
                'sort' : [
                    '_score'
                ],
               'query': {
                    'bool': {
                        'must': must_match,
                        'should': should_match
                    }
                },
                'size': 15
            }


    else:
        search_body = {
            'sort' : [
                '_score'
            ],
           'query': {
                'bool': {
                    'should': should_match
                }
            },
            'size': 15
        }

    result = es.search(
        index = 'network',
        doc_type = 'clinvar',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    if(result['hits']['total'] < 1):
        print 'no results'

        gene_network_data_items = {
                'searchResultTitle': 'No Results',
                'hit_id': 'N/A',
                'diseaseType': "",
                'clusterName': 'No Results',
                'searchResultSummary': 'No Results',
                'searchResultScoreRank': '0',
                'luceneScore': '0',
                'searchResultScoreRankTitle': '',
                'filterValue': '0.0000000029',
                'emphasizeInfoArray': [],
                'emphasizeInfoArrayWithWeights': [],
                'top5': 'true',
                'hitOrder': '0',
                'pubmedCount': 0
            }

        phenotype_network_data['items'].append(gene_network_data_items)
        return [phenotype_network_data]
    else:
        for hit in result['hits']['hits']:
            hitCount += 1
            type_counts = {}#{'genes': len(hit["_source"]["node_list"]['node'])}#'indel': 0, 'insertion': 0, 'deletion': 0, 'duplication': 0, 'single nucleotide variant': 0}
            emphasizeInfoArrayWithWeights = []
            searchResultSummaryString = hit["_source"]["source"] + '-' + str(hit["_source"]["degree"])

            for genehit in queryTermArray:
                for item in hit["_source"]["node_list"]['node']:
                    if(item["name"] == genehit):
                        emphasizeInfoArrayWithWeights.append(item)
                        break

            for variant_hit in hit['_source']['variant_list']['node']:
                # indel, insertion, deletion, duplication, single nucleotide variant
                if(upcase_first_letter(variant_hit['variant_type']) in type_counts):
                    type_counts[upcase_first_letter(variant_hit['variant_type'])] += 1
                else:
                    type_counts[upcase_first_letter(variant_hit['variant_type'])] = 1

            phenotype_ids = []
            for phenotype_id in hit['_source']['phenotype_id_list']['node']:
                ids_split = phenotype_id['name'].split(':')
                if(len(ids_split) > 1):
                    phenotype_ids.append({ids_split[0]:ids_split[1]})

            gene_network_data_items = {
                'searchResultTitle': hit["_source"]["node_name"],
                'hit_id': hit['_id'],
                'diseaseType': '', #"[Phenotype = " + hit["_source"]["node_name"] + "]",
                'clusterName': hit["_source"]["node_name"],
                'searchResultSummary': searchResultSummaryString,
                'searchResultScoreRank': hit["_score"],
                'luceneScore': hit["_score"],
                'searchResultScoreRankTitle': 'pubmed references ',
                'filterValue': '0.0000000029',
                'emphasizeInfoArray': emphasizeInfoArrayWithWeights,
                'emphasizeInfoArrayWithWeights': emphasizeInfoArrayWithWeights,
                'phenotype_ids': phenotype_ids,
                'node_type_counts': type_counts,
                'top5': hitCount < 5,
                'hitOrder': hitCount,
                'pubmedCount': 0,
                'queryGenesCount': len(emphasizeInfoArrayWithWeights)
            }
            phenotype_network_data['items'].append(gene_network_data_items)



        #==================================
        # GROUP PHENOTYPE BY TARGETED GENE
        #==================================
        phenotype_gene_grouping = []

        for phenotype_hit in phenotype_network_data['items']:
            match_found = False
            # After first item is already added (need to append to existing array)
            for gene_loop_item in phenotype_gene_grouping:
                if(len(phenotype_hit['emphasizeInfoArray']) > 0):
                    if(gene_loop_item['gene_name'] == phenotype_hit['emphasizeInfoArray'][0]):
                        gene_loop_item['searchResultTitle'].append({'phenotype_name': phenotype_hit['searchResultTitle'],
                                                   'hit_id': phenotype_hit['hit_id']})
                        match_found = True

            # First item added
            if(not match_found):
                if(len(phenotype_hit['emphasizeInfoArray']) > 0):
                    phenotype_gene_grouping.append(
                        {
                            'gene_name': phenotype_hit['emphasizeInfoArray'][0],
                            'searchResultTitle': [{'phenotype_name': phenotype_hit['searchResultTitle'],
                                                   'hit_id': phenotype_hit['hit_id']}]
                        }
                    )
                else:
                    phenotype_gene_grouping.append(
                        {
                            'gene_name': 'unknown',
                            'searchResultTitle': [{'phenotype_name': phenotype_hit['searchResultTitle'],
                                                   'hit_id': phenotype_hit['hit_id']}]
                        }
                    )

        for phenotype_gene_no_count_item in phenotype_gene_grouping:
            phenotype_gene_no_count_item['gene_count'] = len(phenotype_gene_no_count_item['searchResultTitle'])


        #drug_gene_dumped = dumps(drug_gene_grouping)

        phenotype_network_data['grouped_items'] = phenotype_gene_grouping



    return [phenotype_network_data]

def upcase_first_letter(s):
    return s[0].upper() + s[1:]

def get_document_from_elastic_by_id(elasticId, search_type):
    search_body = {
        'sort' : [
            '_score'
        ],
       'query': {
            'bool': {
                'must': [
                   {'match': {
                      '_id': elasticId
                   }}
                ]
            }
        },
        'size': 1
    }

    result = es.search(
        index = 'clusters',
        #doc_type = search_type,
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])
    signal(SIGPIPE,SIG_DFL)

    if(result['hits']['total'] < 1):
        print 'no results'

    return result['hits']['hits'][0]["_source"]

def get_information_page_data_phenotypes(elasticId):
    hit = get_document_from_elastic_by_id(elasticId, 'clinvar')

    ptype_id_array = []

    for ptype_id in hit['phenotype_id_list']['node']:
        ptype_id_split = ptype_id['name'].split(':')
        if(len(ptype_id_split) > 1):
            if(ptype_id_split[0] == 'MedGen'):
                ptype_id_array.append({'url': 'http://www.ncbi.nlm.nih.gov/medgen/' + ptype_id_split[1],
                                       'type': 'MEDGEN',
                                       'title': 'MedGen'})
            elif(ptype_id_split[0] == 'SNOMED CT'):
                ptype_id_array.append({'url': 'https://mq.b2i.sg/snow-owl/#!terminology/snomed/' + ptype_id_split[1],
                                       'type': 'SNOMED',
                                       'title': 'SNOMED'})
            elif(ptype_id_split[0] == 'OMIM'):
                ptype_id_array.append({'url': 'http://www.omim.org/entry/' + ptype_id_split[1],
                                       'type': 'OMIM',
                                       'title': 'OMIM (must open in new window)'})

    return_result = {
        'Phenotype_ids': ptype_id_array
    }

    return return_result

def get_information_page_data_gene(geneId):
    client = pymongo.MongoClient()
    db = client.identifiers
    print geneId
    collection = db.variants

    variant_results = collection.find({'geneSymbol': geneId})

    for variant in variant_results:
        print variant['term']

    return_result = {
        'variant_ids': []
    }

    return return_result

def get_information_page_data_people_centered(elasticId, genes):
    hit = get_document_from_elastic_by_id(elasticId, 'pubmed_author')

    genes_array = genes.split(',')

    gene_pubs = []

    for node_list_item in hit['node_list']:
        if(node_list_item['name'] in genes_array):
            for pub in node_list_item['publications']:
                pub['date'] = pub['date'][4:6] + '-' + pub['date'][6:8] + '-' + pub['date'][0:4]
            gene_pubs.append(node_list_item)



    return_result = {
        'publications': gene_pubs
    }

    return return_result

def get_document_from_elastic_by_id2(elasticId, search_type):
    xValues = []

    yValues = []
    yValuesTemp = []

    zValues = []

    search_body = {
       'query': {
            'bool': {
                'must': [
                   {'match': {
                      '_id': elasticId
                   }}
                ]
            }
        }
    }

    results = es.search(
        index = 'clusters',
        #doc_type = search_type,
        body = search_body
    )

    if(len(results) > 0):
        isSymetric = False
        result = results['hits']['hits'][0]['_source']
        matrix_width = len(result['x_node_list'])
        for x_label in result['x_node_list']:
            xValues.append(x_label['name'])

        for y_label in result['y_node_list']:
            #yValuesTemp.append(y_label['name'])
            yValues.append(y_label['name'])

        #if(result['x_node_list_type'] == result['y_node_list_type']):
        #    isSymetric = True

        #for reverse_y_label in reversed(yValuesTemp):
        #    yValues.append(reverse_y_label)

        calculated_cut_off = SearchViz.get_top_200_weight(result['correlation_matrix'])
        print calculated_cut_off
        data = []
        edge_counter = 0
        for correlation_record in result['correlation_matrix']:

            #===========================
            # If the matrix is symetric
            # the cor. is 1 for x = y
            #===========================
            #if(isSymetric):
            #    if(correlation_record['x_loc'] == correlation_record['y_loc']):
            #        correlation_value = 1.0
            #    else:
            #        correlation_value = correlation_record['correlation_value']
            #else:
            #    correlation_value = correlation_record['correlation_value']
            correlation_value = correlation_record['correlation_value']
            if( (abs(correlation_value) >= calculated_cut_off) and edge_counter < 2000):
                #data.append([correlation_record['x_loc'], (matrix_width - correlation_record['y_loc'] - 1), correlation_value])#abs(correlation_value)])
                data.append([correlation_record['x_loc'], correlation_record['y_loc'], correlation_value])#abs(correlation_value)])
            #elif(result['x_node_list'][correlation_record['x_loc']]['name'] in )

        #for i in range(0,matrix_width):
        #    data.append([i,matrix_width - i - 1,1.0])

        array = np.zeros((len(result['x_node_list']), len(result['y_node_list'])))

        for row, col, val in data:
            index = (row, col)
            array[index] = val

        return_array_string = '['
        for row in array:
            return_array_string += '['
            for col in row:
                return_array_string += str(col) + ','
            return_array_string += '],'

        return_array_string += ']'
    #==========================================
    # Because the z matrix is transposed we
    # will switch the labels for X and Y coord.
    #==========================================
    return_value = {
        'xValues': yValues,
        'yValues': xValues,
        'zValues': array
    }

    return_string = '{"zValues": ' + return_array_string + ', "yValues": ' + dumps(xValues) + ', "xValues": ' + dumps(yValues) +  '}'

    print("Got %d Hits:" % results['hits']['total'])

    if(results['hits']['total'] < 1):
        print 'no results'

    return return_string #return_value

def convert_name_to_index(node_list, node_list_source):
    return_array = []
    node_list_array = node_list.split(',')
    for node_item in node_list_array:
        for i, j in enumerate(node_list_source):
            if j['name'] == node_item:
                return_array.append(i)
                break;

    return return_array

def get_heatmap_filtered_by_id(elasticId, node_list):
    #es_data_matrix = get_document_from_elastic_by_id2(elasticId, 'clusters_tcga_louvain')

    xValues = []

    yValues = []
    filter_genes_index_x = []
    filter_genes_index_y = []

    zValues = []

    search_body = {
       'query': {
            'bool': {
                'must': [
                   {'match': {
                      '_id': elasticId
                   }}
                ]
            }
        }
    }

    results = es.search(
        index = 'clusters',
        #doc_type = search_type,
        body = search_body
    )

    if(len(results) > 0):
        isSymetric = False
        result = results['hits']['hits'][0]['_source']

        filter_genes_index_x = convert_name_to_index(node_list, result['x_node_list'])
        filter_genes_index_y = convert_name_to_index(node_list, result['y_node_list'])

        matrix_width = len(result['x_node_list'])
        for x_label in result['x_node_list']:
            xValues.append(x_label['name'])

        for y_label in result['y_node_list']:
            #yValuesTemp.append(y_label['name'])
            yValues.append(y_label['name'])

        #if(result['x_node_list_type'] == result['y_node_list_type']):
        #    isSymetric = True

        #for reverse_y_label in reversed(yValuesTemp):
        #    yValues.append(reverse_y_label)

        calculated_cut_off = SearchViz.get_top_200_weight(result['correlation_matrix'])
        #print calculated_cut_off
        data = []
        edge_counter = 0
        for correlation_record in result['correlation_matrix']:

            #===========================
            # If the matrix is symetric
            # the cor. is 1 for x = y
            #===========================
            #if(isSymetric):
            #    if(correlation_record['x_loc'] == correlation_record['y_loc']):
            #        correlation_value = 1.0
            #    else:
            #        correlation_value = correlation_record['correlation_value']
            #else:
            #    correlation_value = correlation_record['correlation_value']
            correlation_value = correlation_record['correlation_value']
            #if( (abs(correlation_value) >= calculated_cut_off) and edge_counter < 2000):
            if(correlation_record['x_loc'] in filter_genes_index_x or correlation_record['y_loc'] in filter_genes_index_y):
                #data.append([correlation_record['x_loc'], (matrix_width - correlation_record['y_loc'] - 1), correlation_value])#abs(correlation_value)])
                data.append([correlation_record['x_loc'], correlation_record['y_loc'], correlation_value])#abs(correlation_value)])
            #elif(result['x_node_list'][correlation_record['x_loc']]['name'] in )

        #for i in range(0,matrix_width):
        #    data.append([i,matrix_width - i - 1,1.0])

        array = np.zeros((len(result['x_node_list']), len(result['y_node_list'])))

        for row, col, val in data:
            index = (row, col)
            array[index] = val

        return_array_string = '['
        for row in array:
            return_array_string += '['
            for col in row:
                return_array_string += str(col) + ','
            return_array_string += '],'

        return_array_string += ']'
    #==========================================
    # Because the z matrix is transposed we
    # will switch the labels for X and Y coord.
    #==========================================
    return_value = {
        'xValues': yValues,
        'yValues': xValues,
        'zValues': array
    }

    return_string = '{"zValues": ' + return_array_string + ', "yValues": ' + dumps(xValues) + ', "xValues": ' + dumps(yValues) +  '}'

    print("Got %d Hits:" % results['hits']['total'])

    if(results['hits']['total'] < 1):
        print 'no results'

    return return_string #return_value

def get_document_from_elastic_by_id3(elasticId, search_type):
    client = pymongo.MongoClient()
    db = client.cache

    heat_maps = db.heat_maps

    heat_map_found = heat_maps.find_one({'elasticId': elasticId})

    if(heat_map_found is not None):
        print 'Get cached heatmap'
        return heat_map_found['heat_map']
    else:

        es_data_matrix = get_document_from_elastic_by_id2(elasticId, 'clusters_tcga_louvain')

        #heat_map_json_1D = HeatMaps.cluster_heat_map(es_data_matrix)

        #zValues = heat_map_json_1D['zValues'].transpose()
        #xValues = heat_map_json_1D['yValues'] # switch the order (x --> y)
        #yValues = heat_map_json_1D['xValues'] # switch the order (y --> x)

        #transposed_matrix_json = {
        #    'xValues': xValues,
        #    'yValues': yValues,
        #    'zValues': zValues
        #}

        #heat_map_ordered_transposed = dumps(HeatMaps.cluster_heat_map(transposed_matrix_json))

        a = {
            'elasticId': elasticId,
            'heat_map': es_data_matrix #heat_map_ordered_transposed
        }

        #heat_maps.save(a)

        #f = open("pickle.txt", "w")
        #return_dump = home_brew(es_data_matrix)
        #f.close()
        return es_data_matrix #return_dump #heat_map_ordered_transposed
        #return dumps(HeatMaps.cluster_heat_map(es_data_matrix))

def get_document_from_elastic_by_id_raw(elasticId, search_type):
    search_body = {
        'sort' : [
            '_score'
        ],
       'query': {
            'bool': {
                'must': [
                   {'match': {
                      '_id': elasticId
                   }}
                ]
            }
        },
        'size': 1
    }

    results = es.search(
        index = 'clusters',
        #doc_type = search_type,
        body = search_body
    )

    return results


def get_cluster_disease_by_es_id(es_id):

    search_body = {
        'fields': [
           'network_full_name'
        ],
       'query': {
          'bool': {
            'must': [
            { 'match': {'_id': es_id} }
            ]
          }
       }
    }

    result = es.search(
        index = 'clusters',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])
    if(len(result['hits']['hits']) > 0):
        hit = result['hits']['hits'][0]
        if('network_full_name' in hit["fields"]):
            if(len(hit["fields"]["network_full_name"]) > 0):
                return hit["fields"]["network_full_name"][0]
            else:
                return 'unknown'

def get_condition_variants(gene, condition, tissue):
    return_results = []
    search_body = {
        'sort' : [
            '_score'
        ],
        'fields': ['node_list.description','node_list.tissue','node_list.name', 'node_name', 'node_list.cosmic_id'],
        'query': {
            'bool': {
                'must': [
                    {'match': {'node_list.name': gene}}, #'GATA3'
                    {'match': {'node_list.description': condition}}, #'ER-PR-positive carcinoma'
                    {'match': {'node_list.tissue': tissue}} #'breast'
                ]
            }
        }
    }

    result = es.search(
        index = 'conditions',
        doc_type = 'conditions_cosmic_mutant',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    if(result['hits']['total'] > 0):
        for condition_hit in result['hits']['hits']:
            if(condition_hit['fields']['node_list.tissue'][0] == tissue and condition_hit['fields']['node_list.description'][0] == condition):
                return_results.append({
                    'variant': condition_hit['fields']['node_name'][0],
                    'gene': condition_hit['fields']['node_list.name'][0],
                    'cosmicid': condition_hit['fields']['node_list.cosmic_id'][0]
                })
    else:
        print 'no results'

    return return_results

def get_disease_types_from_ES():
    client = pymongo.MongoClient()
    db = client.identifiers
    disease_collection = db.disease_lookup

    disease_types = []

    search_body = {
        'size': 0,
        'aggs' : {
            'diseases_agg' : {
                'terms' : { 'field' : 'network_name', 'size': 100 }
            }
        }
    }

    result = es.search(
        index = 'clusters',
        body = search_body
    )
    count = 0
    disease_keys = []
    if(result['aggregations']['diseases_agg']['buckets'] < 1):
        print 'no results'
    else:
        for hit in result['aggregations']['diseases_agg']['buckets']:
            disease_keys.append(hit['key'])
            print hit['key']


    for disease_key in disease_keys:
        search_body = {
            'size': 1,
            'query' : {
                'bool': {
                    'must': [{ 'match': {'network_name': disease_key} }]
                }
            }
        }

        result = es.search(
            index = 'clusters',
            body = search_body
        )

        if(len(result) > 0):
            result = result['hits']['hits'][0]['_source']
            #disease_collection.save(
            #    {
            #        'id': disease_key,
            #        'desc': result['network_full_name'],
            #        'synonym': disease_key
            #    }
            #)

            print result['network_full_name'] + '\t' + disease_key

    return 'success'

def main():
    return 0

if __name__ == '__main__':
    sys.exit(main())