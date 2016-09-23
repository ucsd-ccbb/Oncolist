__author__ = 'aarongary'

from collections import Counter
from app import PubMed
from models.TermResolver import TermAnalyzer
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # Clustered Server

#==================================
#==================================
#         STAR SEARCH
#==================================
#==================================
def get_star_search_mapped(queryTerms):
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

def get_star_search_with_disease_mapped(queryTerms, disease):
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
    if(len(disease) > 0): #isStarSearch):
        returnBody = {
#                'sort' : [
#                    '_score'
#                ],
                'query': {
                    'bool': {
                        'must': must_match,
                        'should': should_match
                    }
                },
                'size': 15
            }
    else:
        returnBody = {
#                'sort' : [
#                    '_score'
#                ],
                'query': {
                    'bool': {
                        #'must': must_match,
                        'should': should_match
                    }
                },
                'size': 15
            }

    return returnBody

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
        print result_node_name
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

def get_geneSuperList(queryTermArray, sorted_query_list):
    returnValue = []

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        #should_match.append( { 'match': {network_info['matchField']: queryTerm} })
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        #should_match.append({"match": {"node_list.node.name":{"query": queryTerm,"boost": boost_value_append}}})
        returnValue.append({'queryTerm': queryTerm, 'boostValue': boost_value_append})

    return returnValue

def get_boost_value(boostArray, idToCheck):
    for boostItem in boostArray:
        if(boostItem['id'] == idToCheck):
            returnThisValue = boostItem['normalizedValue']
            return boostItem['normalizedValue']

    return 0


