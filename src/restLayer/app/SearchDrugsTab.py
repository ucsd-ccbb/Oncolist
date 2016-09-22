__author__ = 'aarongary'

from app import PubMed
from app import elastic_search_uri
from collections import Counter
from elasticsearch import Elasticsearch

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300)

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
    #phenotype_network_data = drug_network_search_gene_centric(network_information)

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
        'geneScoreRangeStep': '0.1',
        'document_ids': [],
        'inferred_drugs': [],
        'overlap_counts': []
    }

    unsorted_items = []
    gene_super_list = []
    overlap_counts_array = []
    overlap_found = False

    queryTermArray = network_info['queryTerms'].split(',')
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    should_match = []

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        should_match.append({"match": {"node_list.name": queryTerm}})


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
        index = 'drugs',
        doc_type = 'drugs_drugbank',
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
            geneNeighborhoodArray.append(geneNodeHit['name'])

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithWeights = []

        for genehit in y:
            node_list_items = hit["_source"]["node_list"]
            match = (item for item in node_list_items if item["name"] == genehit).next()
            emphasizeInfoArrayWithWeights.append(match)

        for gene_network_matched in y:
            gene_super_list.append(gene_network_matched)








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
            'pubmedCount': 0,
            'hit_id': hit['_id']
        }
        gene_network_data['document_ids'].append(hit['_id'])

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
    gene_network_data['overlap_counts'] = overlap_counts_array

    return gene_network_data


def drug_network_search_gene_centric(network_info, disease=[]):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1',
        'document_ids': [],
        'inferred_drugs': []
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
        should_match.append({"match": {"node_list.name": queryTerm}})


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
        index = 'drugs',
        doc_type = 'drugs_drugbank',
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

    search_results_for_grouping = []
    for hit in result['hits']['hits']:
        geneNeighborhoodArray = [];

        for geneNodeHit in hit["_source"]["node_list"]:
            geneNeighborhoodArray.append(geneNodeHit['name'])

        x = [set(geneNeighborhoodArray), set(queryTermArray)]

        y = set.intersection(*x)

        emphasizeInfoArrayWithWeights = []

        for genehit in y:
            search_results_for_grouping.append(
                {
                    'drugbank_id': hit['_source']['drugbank_id'],
                    'drug_name': hit['_source']['node_name'],
                    'gene_overlap': genehit,
                    'hit_id': hit['_id']
                }
            )

            node_list_items = hit["_source"]["node_list"]
            match = (item for item in node_list_items if item["name"] == genehit).next()
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
            'pubmedCount': 0,
            'hit_id': hit['_id']
        }
        gene_network_data['document_ids'].append(hit['_id'])

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
