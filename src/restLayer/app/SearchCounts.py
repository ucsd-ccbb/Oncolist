__author__ = 'aarongary'

from collections import Counter
from app import PubMed
from models.TermResolver import TermAnalyzer
from elasticsearch import Elasticsearch
from app import elastic_search_uri

#es = Elasticsearch(['http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # Clustered Server
es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server

#==================================
#==================================
#         GENE SEARCH
#==================================
#==================================
def get_counts_gene(queryTerms, disease=[]):
#    network_info = {
#        'searchGroupTitle': 'Star Network',
#        'searchTab': 'GENES',
#        'network': 'node',
#        'matchField': 'node_list.node.name',
#        'matchCoreNode': 'node_name',
#        'cancerType': 'BRCA',
#        'queryTerms': queryTerms
#    }

#    gene_network_data = {
#        'searchGroupTitle': network_info['searchGroupTitle'],
#        'clusterNodeName': "",
#        'searchTab': network_info['searchTab'],
#        'items': [],
#        'geneSuperList': [],
#        'geneScoreRangeMax': '100',
#        'geneScoreRangeMin': '5',
#        'geneScoreRangeStep': '0.1'
#    }

#    queryTermArray = queryTerms.split(',')

#    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
#    gene_network_data['geneSuperList'] = get_geneSuperList_gene(queryTermArray, sorted_query_list)
#    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")
#    search_body = get_searchBody_count_gene(queryTermArray, network_info, disease, sorted_query_list, True)

#    result = es.count(
#        index = 'network',
#        doc_type = 'node',
#        body = search_body
#    )

    return 0

def get_searchBody_count_gene(queryTermArray, network_info, disease, sorted_query_list, isStarSearch):
    should_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value_gene(sorted_query_list['results'], queryTerm)
        if(isStarSearch):
            should_match.append({"match": {"node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append( { 'match': {'node_name': queryTerm} })
        else:
            should_match.append({"match": {"x_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})

    returnBody = {
        'query': {
            'bool': {
                'should': should_match
            }
        }
    }

    return returnBody

def get_geneSuperList_gene(queryTermArray, sorted_query_list):
    returnValue = []

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        #should_match.append( { 'match': {network_info['matchField']: queryTerm} })
        boost_value_append = get_boost_value_gene(sorted_query_list['results'], queryTerm)
        #should_match.append({"match": {"node_list.node.name":{"query": queryTerm,"boost": boost_value_append}}})
        returnValue.append({'queryTerm': queryTerm, 'boostValue': boost_value_append})

    return returnValue

def get_boost_value_gene(boostArray, idToCheck):
    for boostItem in boostArray:
        if(boostItem['id'] == idToCheck):
            returnThisValue = boostItem['normalizedValue']
            return boostItem['normalizedValue']

    return 0


#==================================
#==================================
#         CLUSTERS SEARCH
#==================================
#==================================
def get_counts_cluster(queryTerms, disease=[]):
    network_info = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'PATHWAYS',
        'network': 'cluster',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }
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
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList_cluster(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")
    search_body = get_searchBody_count_cluster(queryTermArray, network_info, disease, sorted_query_list, False)

    result = es.count(
        index = 'clusters',
        doc_type = ['clusters_geo_oslom', 'clusters_tcga_oslom'],
        body = search_body
    )

    return result['count']

def get_searchBody_count_cluster(queryTermArray, network_info, disease, sorted_query_list, isStarSearch):
    should_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value_cluster(sorted_query_list['results'], queryTerm)
        if(isStarSearch):
            should_match.append({"match": {"node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append( { 'match': {'node_name': queryTerm} })
        else:
            should_match.append({"match": {"x_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})

    returnBody = {
        'query': {
            'bool': {
                'should': should_match
            }
        }
    }

    return returnBody

def get_geneSuperList_cluster(queryTermArray, sorted_query_list):
    returnValue = []

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        #should_match.append( { 'match': {network_info['matchField']: queryTerm} })
        boost_value_append = get_boost_value_cluster(sorted_query_list['results'], queryTerm)
        #should_match.append({"match": {"node_list.node.name":{"query": queryTerm,"boost": boost_value_append}}})
        returnValue.append({'queryTerm': queryTerm, 'boostValue': boost_value_append})

    return returnValue

def get_boost_value_cluster(boostArray, idToCheck):
    for boostItem in boostArray:
        if(boostItem['id'] == idToCheck):
            returnThisValue = boostItem['normalizedValue']
            return boostItem['normalizedValue']

    return 0

#==================================
#==================================
#         CONDITIONS SEARCH
#==================================
#==================================
def get_counts_condition(queryTerms, phenotypes=None):
    should_match = []
    must_match = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.name": queryTerm}})

    if(phenotypes is not None):
        phenotypeTermArray = phenotypes.split('~')

        for phenotypeTerm in phenotypeTermArray:
            must_match.append({"match": {"node_name": phenotypeTerm}})

            search_body = {
               'query': {
                    'bool': {
                        'must': must_match,
                        'should': should_match
                    }
                }
            }
    else:
        search_body = {
           'query': {
                'bool': {
                    'should': should_match
                }
            }
        }

    result = es.count(
        index = 'conditions',
        doc_type = 'conditions_clinvar',
        body = search_body
    )

    return result['count']

#==================================
#==================================
#         AUTHORS SEARCH
#==================================
#==================================
def get_counts_author(queryTerms):
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
                            'authors_pubmed'
                         ]
                      }}
                   ]
                }
             }
          }
      }
    }

    result = es.count(
        index = 'authors',
        doc_type = 'authors_pubmed',
        body = search_body
    )

    return result['count']

#==================================
#==================================
#         DRUGS SEARCH
#==================================
#==================================
def get_counts_drug(queryTerms, disease=[]):
    network_info = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'DRUG',
        'network': 'drug_network',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }

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
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList_drug(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    should_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value_drug(sorted_query_list['results'], queryTerm)
        should_match.append({"match": {"node_list.name": queryTerm}})

    search_body = {
        'query': {
            'bool': {
                'should': should_match
            }
        }
    }

    result = es.count(
        index = 'drugs',
        doc_type = 'drugs_drugbank',
        body = search_body
    )

    return result['count']

def get_geneSuperList_drug(queryTermArray, sorted_query_list):
    returnValue = []

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        #should_match.append( { 'match': {network_info['matchField']: queryTerm} })
        boost_value_append = get_boost_value_drug(sorted_query_list['results'], queryTerm)
        #should_match.append({"match": {"node_list.node.name":{"query": queryTerm,"boost": boost_value_append}}})
        returnValue.append({'queryTerm': queryTerm, 'boostValue': boost_value_append})

    return returnValue

def get_boost_value_drug(boostArray, idToCheck):
    for boostItem in boostArray:
        if(boostItem['id'] == idToCheck):
            returnThisValue = boostItem['normalizedValue']
            return boostItem['normalizedValue']

    return 0
