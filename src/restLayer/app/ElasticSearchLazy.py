import sys
from elasticsearch import Elasticsearch
from bson.json_util import dumps

es = Elasticsearch(['http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # Clustered Server

#==============================
#==============================
#   PEOPLE SEARCH - GENE KEYED
#============================
#============================
def get_people_gene_center_search(queryTerms):
    queryTermArray = queryTerms.split(',')

    search_body = {
        'sort' : [
            '_score'
        ],
        'query': {
            'filtered': {
                'filter': {
                    'terms': {
                        'node_name': queryTermArray
                    }
                }
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

    for hit in result['hits']['hits']:
        emphasizeInfoArray = []
        for author in hit['_source']['node_list']['node']:
            article_count = len(author['publications'])

            emphasizeInfoArray.append({'author': author,
                                       'article_count': article_count})

        top5 = sorted(emphasizeInfoArray, key=lambda k: k['article_count'], reverse=True)[:3]

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
            'emphasizeInfoArray': top5, #emphasizeInfoArray,
            'emphasizeInfoArrayWithWeights': [],
            'top5': False,
            'hitOrder': 0,
            'pubmedCount': hit['_source']['degree']
        }
        gene_network_data['items'].append(gene_network_data_items)

    return [gene_network_data]

#===============================
#===============================
#   PEOPLE SEARCH - GENE KEYED
#   LOAD THE DATA WHEN REQUESTED
#===============================
#===============================
def get_people_gene_center_fill_in(gene):

    search_body = {
        'query': {
            'bool': {
                'must': [
                    {'match': {'node_name': gene}}
                ]
            }
        },
        'size': 1
    }

    result = es.search(
        index = 'network',
        doc_type = 'pubmed',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    emphasizeInfoArray = []
    for hit in result['hits']['hits']:
        for author in hit['_source']['node_list']['node']:
            article_count = len(author['publications'])
            emphasizeInfoArray.append({'author': author,
                                       'article_count': article_count})

    return emphasizeInfoArray

#============================
#============================
#   PEOPLE TO GENE SEARCH
#============================
#============================
def get_people_author_center_search(queryTerms):
    should_match = []
    must_match = []

    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.node.name": queryTerm}})

    search_body = {
        'query': {
            'filtered': {
                'filter': {
                    'terms': {
                        'node_list.node.name': queryTermArray
                    }
                }
            }
        },
        'size': 50
    }




#    search_body = {
#        'query': {
#            'bool': {
#                'should': should_match
#            }
#        },
#        'size': 50
#    }

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

    for hit in result['hits']['hits']:
        emphasizeInfoArray = []

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
            'searchResultSummary': 'Pubmed (' + str(hit['_source']['degree']) + ')',
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




def main():
    return 0

if __name__ == '__main__':
    sys.exit(main())