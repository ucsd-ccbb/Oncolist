__author__ = 'aarongary'

from elasticsearch import Elasticsearch
from app import elastic_search_uri
from app import util
import pymongo

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server

def get_people_people_pubmed_search_mapped2(queryTerms, pageNumber=1):
    """Searches the authors index in ElasticSearch.

    :param queryTerms: comma delimited string containing query terms
    :param pageNumber: integer used for specifying which paged result is being requested

    :return: : a list of search results
    """

    computed_hash = util.compute_query_list_hash(queryTerms)
    #print computed_hash

    should_match = []
    gene_network_data = {}

    if(pageNumber != 99):
        from_page = (int(pageNumber) - 1) * 10
        if(from_page < 0):
            from_page = 0
    else:
        from_page = 0

    queryTermArray = queryTerms.split(',')

    client = pymongo.MongoClient()
    db = client.cache

    cluster_search = db.author_search

    cluster_search_found = cluster_search.find_one({'searchId': computed_hash, 'author_type': 'none'})

    if(cluster_search_found is not None):
        gene_network_data = cluster_search_found['cached_hits']
    else:
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
          },
            "from": 0,
            "size": 40,
        }

        result = es.search(
            index = 'authors',
            doc_type = 'authors_pubmed',
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
            'geneScoreRangeStep': '0.1',
            'overlap_counts': []
        }

        overlap_counts_array = []
        overlap_found = False

        lucene_score_array = []
        for hit in result['hits']['hits']:
            lucene_score_array.append(hit['_score'])

        lucene_score_max = max(lucene_score_array)
        lucene_score_min = min(lucene_score_array)
        all_genes = {}

        for hit in result['hits']['hits']:
            emphasizeInfoArray = []

            geneNeighborhoodArray = [];
            gene_pub_count = 0
            for geneNodeHit in hit["_source"]["node_list"]:
                gene_count = len(geneNodeHit['publications'])
                geneNeighborhoodArray.append(geneNodeHit['name'])
                emphasizeInfoArray.append({'gene': geneNodeHit['name'],
                                           'gene_count': gene_count})
                if(geneNodeHit['name'] in queryTermArray):
                    if(geneNodeHit['name'] not in all_genes):
                        all_genes[geneNodeHit['name']] = 0

            x = [set(geneNeighborhoodArray), set(queryTermArray)]

            y = set.intersection(*x)

            for gene_network_matched in y:
                for match_this_overlap in overlap_counts_array:
                    if(gene_network_matched == match_this_overlap['gene']):
                        match_this_overlap['count'] += 1
                        overlap_found = True
                        break

                if(not overlap_found):
                    overlap_counts_array.append(
                        {
                            'gene': gene_network_matched,
                            'count': 1
                        }
                    )

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

            normalized_score = ((hit['_score'] - lucene_score_min)/(lucene_score_max - lucene_score_min)) * 10.0
            if(normalized_score < 0.7):
                normalized_score = 0.7

            gene_network_data_items = {
                'searchResultTitle': hit["_source"]["node_name"],
                'hit_id': hit['_id'],
                'diseaseType': '',
                'clusterName': hit['_source']['node_name'],
                'searchResultSummary': 'Pubmed',  #(' + str(hit['_source']['degree']) + ')',
                'searchResultScoreRank': normalized_score, #hit["_score"],
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
            gene_network_data['overlap_counts'] = overlap_counts_array

        for item in gene_network_data['items']:
            for gene in item['emphasizeInfoArray']:
                all_genes[gene['gene']] += 1

        gene_network_data['geneSuperList'] = all_genes

        client = pymongo.MongoClient()
        db = client.cache

        cluster_search = db.author_search

        cluster_search.save(
            {
                'searchId': computed_hash,
                'author_type': 'none',
                'cached_hits': gene_network_data
            }
        )

        client.close()

    if(pageNumber != 99):
        gene_network_data['items'] = gene_network_data['items'][from_page:from_page + 10]


    return [gene_network_data]

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
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    if(result['hits']['total'] < 1):
        print 'no results'

    return result['hits']['hits'][0]["_source"]

