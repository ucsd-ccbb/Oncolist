__author__ = 'aarongary'

from itertools import groupby
from elasticsearch import Elasticsearch
from app import elastic_search_uri
from bson.json_util import dumps
from models.ConditionSearchModel import ConditionSearchResults
import pymongo
from app import util
from operator import itemgetter

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server

def get_condition_search(queryTerms, pageNumber=1):
    myConditionSearchResults = ConditionSearchResults()
    myConditionSearchResults.name = 'my name'

    cosmic_grouped_items = get_cosmic_search(queryTerms, pageNumber)
    basic_results = get_cosmic_grouped_by_tissues_then_diseases(queryTerms, pageNumber) #get_cosmic_grouped_by_disease_tissue(queryTerms, pageNumber)

    myConditionSearchResults.add_simplified_cosmic_item(cosmic_grouped_items)
    myConditionSearchResults.add_basic_cosmic_list(basic_results)

    result = myConditionSearchResults.to_JSON()

    return result

#    for c_g_i in cosmic_grouped_items[0]['grouped_items']:
#        for c_g_i_p in c_g_i['phenotypes']:
#            #myConditionSearchResults.addGroupedCosmicConditions(c_g_i['gene_name']['name'], c_g_i_p)#['phenotype_name'])
#            myConditionSearchResults.addGroupedCosmicConditionsGene(c_g_i_p['phenotype_name'], c_g_i['gene_name']['name'], c_g_i_p['group_info'])#, c_g_i_p['variants'])

#    clinvar_grouped_items = get_clinvar_search(queryTerms, pageNumber)

#    for c_g_i in clinvar_grouped_items[0]['grouped_items']: #phenotype_name': hit["_source"]["node_name"], 'gene_name': genehit, 'resources
        #for c_g_i_p in c_g_i['searchResultTitle']:
            #myConditionSearchResults.addGroupedClinvarConditions(c_g_i['gene_name']['name'], c_g_i_p)#['phenotype_name'])
         #   myConditionSearchResults.addGroupedClinvarConditionsGene(c_g_i_p['phenotype_name'], c_g_i['gene_name']['name'], c_g_i_p['resources'])#['phenotype_name'])

#        for c_g_i_p in c_g_i['phenotype_name']:
            #myConditionSearchResults.addGroupedClinvarConditions(c_g_i['gene_name']['name'], c_g_i_p)#['phenotype_name'])
#            myConditionSearchResults.addGroupedClinvarConditionsGene(c_g_i_p, c_g_i['gene_name'], c_g_i['resources'])#['phenotype_name'])



#    myConditionSearchResults.group_items_by_conditions()
#    myConditionSearchResults.updateCounts()

#    result = myConditionSearchResults.to_JSON()

#    return result


def get_cosmic_grouped_items(queryTerms, phenotypes=None):
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
        index = 'conditions',
        doc_type = 'conditions_clinvar',
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



def get_cosmic_searchx(queryTerms, pageNumber):
    hitCount = 0
    from_page = (pageNumber - 1) * 50
    if(from_page < 0):
        from_page = 0
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

    search_body = {
        'sort' : [
            '_score'
        ],
       'query': {
            'bool': {
                'should': should_match
            }
        },
        'from': from_page,
        'size': 50
    }

    result = es.search(
        index = 'conditions',
        doc_type = 'conditions_clinvar',
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

def get_clinvar_search(queryTerms, pageNumber):
    hitCount = 0
    from_page = (pageNumber - 1) * 200
    if(from_page < 0):
        from_page = 0
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

    hits_by_condition = []
    should_match = []
    must_match = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
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
        'from': from_page,
        'size': 100
    }

    result = es.search(
        index = 'conditions',
        doc_type = 'conditions_clinvar',
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

            for genehit in queryTermArray:
                for item in hit["_source"]["node_list"]:
                    if(item["name"] == genehit):
                        hit_resources = []
                        for phenotype_id in hit['_source']['phenotype_id_list']:
                            ids_split = phenotype_id['name'].split(':')
                            if(len(ids_split) > 1):
                                hit_resources.append({ids_split[0]:ids_split[1]})

                        hits_by_condition.append({'phenotype_name': [hit["_source"]["node_name"]], 'gene_name': genehit, 'resources': hit_resources})


        phenotype_network_data['grouped_items'] = hits_by_condition; #phenotype_gene_grouping

    return [phenotype_network_data]

def get_cosmic_search(queryTerms, pageNumber):
    computed_hash = util.compute_query_list_hash(queryTerms)
    #print computed_hash

    search_size = 15
    from_page = 0
    hitCount = 0

    if(pageNumber == 99):
        search_size = 60
        from_page = 0
    else:
        search_size = 15
        from_page = (pageNumber - 1) * 15
        if(from_page < 0):
            from_page = 0

    phenotype_network_data = {
        'searchGroupTitle': 'Cosmic Phenotypes',
        'clusterNodeName': "Cosmic",
        'searchTab': 'PHENOTYPES',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    gene_condition_array = []

    should_match = []
    must_match = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.name": queryTerm}})
        gene_condition_array.append({queryTerm: []})

    search_body = {
        'sort' : [
            '_score'
        ],
        'fields': ['node_list.description','node_list.tissue','node_list.name', 'node_list.cosmic_id', 'node_list.pubmed'], #, 'node_name'],
        'query': {
            'bool': {
                'should': should_match,
                'must_not': [{'match': {'node_list.description': 'NS'}}]
            }
        },
        #'from': 0,
        #'size': 60
        'from': from_page,
        'size': search_size
    }

    result = es.search(
        index = 'conditions',
        doc_type = 'conditions_cosmic_mutant',
        body = search_body
    )



    #client = pymongo.MongoClient()
    #db = client.cache

    #cluster_search = db.condition_search

    #cluster_search.save(
    #    {
    #        'searchId': computed_hash,
    #        'condition_type': 'none',
    #        'cached_hits': cached_hits
    #    }
    #)

    #client.close()



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
        gene_network_data_items = {
            'hit_id': 'unknown',
            'diseaseType': '', #"[Phenotype = " + hit["_source"]["node_name"] + "]",
        }

        gene_condition_unique = []
        sorted_list = sorted(result['hits']['hits'], key=lambda k: k['fields']['node_list.name']) # sort by gene symbol

        all_doc_json = []

        for key, group in groupby(sorted_list, lambda item: item['fields']['node_list.name']):
            groups = []
            groups_for_set = []
            groups_for_set_dict = []
            groups.append(list(group))
            #print key[0]
            sorted_list = sorted(result['hits']['hits'], key=lambda k: k['fields']['node_list.name'])
            for group_item in groups[0]:
                groups_for_set.append(group_item['fields']['node_list.tissue'][0] + '|' + group_item['fields']['node_list.description'][0]) # + '~' + group_item['fields']['node_list.cosmic_id'][0])
                groups_for_set_dict.append(
                    {
                        'title': group_item['fields']['node_list.tissue'][0] + '|' + group_item['fields']['node_list.description'][0],
                        'cosmic_id': group_item['fields']['node_list.cosmic_id'][0],
                        'pubmed_id': group_item['fields']['node_list.pubmed'][0],
                        'gene': group_item['fields']['node_list.name'][0],
                        'tissue': group_item['fields']['node_list.tissue'][0],
                        'disease': group_item['fields']['node_list.description'][0],
                        'esId': group_item['_id'],
                        'score': group_item['_score']
                        #'variant_gene': {
                        #    'variant': group_item['fields']['node_name'][0],
                        #    'gene': group_item['fields']['node_list.name'][0]
                        #}
                    }
                )
                all_doc_json.append(
                    {
                        'title': group_item['fields']['node_list.tissue'][0] + '|' + group_item['fields']['node_list.description'][0],
                        'cosmic_id': group_item['fields']['node_list.cosmic_id'][0],
                        'pubmed_id': group_item['fields']['node_list.pubmed'][0],
                        'gene': group_item['fields']['node_list.name'][0],
                        'tissue': group_item['fields']['node_list.tissue'][0],
                        'disease': group_item['fields']['node_list.description'][0],
                        'esId': group_item['_id'],
                        'score': group_item['_score']
                            #'variant_gene': {
                        #    'variant': group_item['fields']['node_name'][0],
                        #    'gene': group_item['fields']['node_list.name'][0]
                        #}
                    }
                )


            #print key, groups
            #for groups_for_set_item in set(groups_for_set):
            #    print groups_for_set_item

            sorted_expanded_phenotypes = []
            sorted_phenotype_titles = sorted(set(groups_for_set))

            sorted_phenotype_titles_dict = sorted(groups_for_set_dict, key=lambda k: k['title'])

            for sorted_title in sorted_phenotype_titles:
                sorted_title_parts = sorted_title.split('~')
                cosmic_ids = []
                variant_ids = []
                pubmed_ids = []
                for sorted_phenotype_cosmic_id in sorted_phenotype_titles_dict:
                    if(sorted_phenotype_cosmic_id['title'] == sorted_title):
                        if(sorted_phenotype_cosmic_id['cosmic_id'] not in cosmic_ids):
                            cosmic_ids.append(sorted_phenotype_cosmic_id['cosmic_id'])
                            #variant_ids.append(sorted_phenotype_cosmic_id['variant_gene'])
                        if((sorted_phenotype_cosmic_id['pubmed_id'] not in pubmed_ids) and len(sorted_phenotype_cosmic_id['pubmed_id']) > 0):
                            pubmed_ids.append(sorted_phenotype_cosmic_id['pubmed_id'])

                sorted_expanded_phenotypes.append(
                    {
                        'phenotype_name': sorted_title, #sorted_title_parts[0],
                        'group_info': {
                            'cosmic_ids': cosmic_ids,
                            'pubmed_ids': pubmed_ids
                        },
                        #'variants': variant_ids,
                        #'cosmic_id': sorted_title_parts[1],
                        'hit_id': 'unknown'
                    }
                )

            gene_condition_unique.append(
                {
                    'gene_name': {'name': key[0]},
                    'phenotypes': sorted_expanded_phenotypes,
                    'phenotypecount': len(sorted_expanded_phenotypes)
                }
            )

        sorted_list2 = sorted(all_doc_json, key=lambda k: k['disease'])
        disease_group_by = []
        for disease_key, tissue_group in groupby(sorted_list2, lambda item: item['disease']):
            tissues = list(tissue_group)
            sorted_list3 = sorted(tissues, key=lambda k: k['tissue'])
            tissue_group_by = []
            genes_in_group = []
            for tissue_key, item_group in groupby(sorted_list3, lambda item2: item2['tissue']):
                gene_list = []
                pubmed_list = []
                cosmic_list = []
                item_group_list = list(item_group)
                for gene_check in item_group_list:
                    if(gene_check['gene'] not in gene_list):
                        gene_list.append(gene_check['gene'])

                for gene_check in item_group_list:
                    if(gene_check['pubmed_id'] not in pubmed_list):
                        if(len(gene_check['pubmed_id']) > 0):
                            pubmed_list.append(gene_check['pubmed_id'])

                for gene_check in item_group_list:
                    if(gene_check['cosmic_id'] not in cosmic_list):
                        if(len(gene_check['cosmic_id']) > 0):
                            cosmic_list.append(gene_check['cosmic_id'])

                tissue_group_by.append(
                    {
                        'tissue': tissue_key,
                        'genes': gene_list,
                        'pubmed_ids': pubmed_list,
                        'cosmic_ids': cosmic_list,
                        'items': item_group_list,

                    }
                )

            disease_group_by.append(
                {
                    'disease': disease_key,
                    'data_source': 'COSMIC',
                    'tissues': tissue_group_by,
                    'grouped_by_conditions_count': len(tissue_group_by)
                }
            )

        #sorted_list3 = sorted(disease_group_by, key=lambda k: k['title'])
        #disease_group_by = []
        #for disease_key, disease_group in itertools.groupby(sorted_list2, lambda item: item['disease']):
        #    disease_group_by.append(
        #        {
        #            'disease': disease_key,
        #            'tissues': list(disease_group)
        #        }
        #    )

        phenotype_network_data['grouped_items'] = gene_condition_unique


    #print dumps([phenotype_network_data])

    return disease_group_by









def get_cosmic_grouped_by_disease_tissue(queryTerms, pageNumber):
    #grouped_diseases = get_cosmic_grouped_by_disease(queryTerms, pageNumber)
    grouped_tissues = get_cosmic_grouped_by_tissues(queryTerms, pageNumber)

    disease_groups = []
    for disease in grouped_diseases:
        sorted_list = sorted(disease['tissues'], key=lambda k: k['fields']['node_list.tissue']) # sort by tissues

        #===============================
        # GROUP BY TISSUE
        #===============================
        tissue_groups = []
        for key, group in groupby(sorted_list, lambda item: item['fields']['node_list.tissue']):
            gene_list = []
            info_page_list = ''
            dedup_reference = []
            gene_string_list = []
            for tissue_gene in list(group):
                if(tissue_gene['fields']['node_list.name'][0] not in gene_string_list):
                    gene_string_list.append(tissue_gene['fields']['node_list.name'][0])

                dedup_signature = tissue_gene['fields']['node_list.name'][0] + tissue_gene['fields']['node_list.cosmic_id'][0]
                if(dedup_signature not in dedup_reference):
                    dedup_reference.append(dedup_signature)
                    gene_item = {
                        'gene': tissue_gene['fields']['node_list.name'][0],
                        'cosmic_id': tissue_gene['fields']['node_list.cosmic_id'][0],
                        'pubmed_id': tissue_gene['fields']['node_list.pubmed'][0],
                        'es_id': tissue_gene['_id'],
                        'disease': tissue_gene['fields']['node_list.description'][0],
                        'tissue': tissue_gene['fields']['node_list.tissue'][0],
                        '_score': tissue_gene['_score'],
                        'info_page': tissue_gene['fields']['node_list.cosmic_id'][0] + '~' + tissue_gene['fields']['node_list.name'][0]
                    }
                    info_page_list += tissue_gene['fields']['node_list.cosmic_id'][0] + '~' + tissue_gene['fields']['node_list.name'][0] + ','

                    gene_list.append(gene_item)

            if(len(info_page_list) > 0):
                info_page_list = info_page_list[:-1]

            tissue_group_item = {
                'tissue': key[0],
                'genes': gene_list,
                'info_page_list': info_page_list,
                'gene_list': gene_string_list
            }
            tissue_groups.append(tissue_group_item)


        disease_group_item = {
            'disease': disease['disease'][0],
            'tissues': tissue_groups,
            'grouped_by_conditions_count': len(tissue_groups)
        }
        disease_groups.append(disease_group_item)

    return disease_groups

def get_cosmic_grouped_by_tissues_then_diseases(queryTerms, pageNumber):
    computed_hash = util.compute_query_list_hash(queryTerms)
    #print computed_hash

    hitCount = 0
    if(pageNumber != 99):
        from_page = (int(pageNumber) - 1) * 5
        if(from_page < 0):
            from_page = 0
    else:
        from_page = 0

    phenotype_network_data = {
        'searchGroupTitle': 'Cosmic Phenotypes',
        'clusterNodeName': "Cosmic",
        'searchTab': 'PHENOTYPES',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    gene_condition_array = []
    search_these_cached_hits = []
    should_match = []
    must_match = []
    queryTermArray = queryTerms.split(',')

    cached_hits = []
    conditions_dict = {}
    conditions_array = []
    tissue_filter_array = []
    disease_filter_array = []

    client = pymongo.MongoClient()
    db = client.cache

    conditions_search = db.conditions_search

    conditions_search_found = conditions_search.find_one({'searchId': computed_hash})

    if(conditions_search_found is not None):
        cached_hits = conditions_search_found['cached_hits']
    else:
        for queryTerm in queryTermArray:
            should_match.append({"match": {"node_list.name": queryTerm}})
            gene_condition_array.append({queryTerm: []})

        search_body = {
            'sort' : [
                '_score'
            ],
            #'fields': ['node_list.description','node_list.tissue','node_list.name', 'node_list.cosmic_id', 'node_list.pubmed'], #, 'node_name'],
            'query': {
                'bool': {
                    'should': should_match,
                    'must_not': [{'match': {'node_list.description': 'NS'}}]
                }
            },
            'from': 0,
            'size': 120
            #'from': from_page,
            #'size': 15
        }

        result = es.search(
            index = 'conditions',
            doc_type = 'conditions_cosmic_mutant',
            body = search_body
        )

        if(result['hits']['total'] < 1):
            print 'no results'

            return []
        else:
            hit_list = []
            for hit in result['hits']['hits']:
                for node_list_item in hit['_source']['node_list']:
                    node_list_item['_score'] = hit['_score']
                    hit_list.append(node_list_item)

            sorted_hits = sorted(hit_list, key=lambda k: k['_score'], reverse=True)

        tissue_grouper = itemgetter("tissue")
        disease_grouper = itemgetter("description")

        for tissue, group in groupby(sorted(sorted_hits, key = tissue_grouper), tissue_grouper):
            if(tissue not in tissue_filter_array):
                tissue_filter_array.append(tissue)
            conditions_dict[tissue] = {'diseases': []}
            inner_count = 0
            for disease, inner_group in groupby(sorted(group, key = disease_grouper), disease_grouper):
                if(disease not in disease_filter_array):
                    disease_filter_array.append(disease)

                inner_count += 1
                inner_group_list = list(inner_group)
                gene_list = []
                for gene_item in inner_group_list:
                    if(gene_item['name'] not in gene_list):
                        gene_list.append(gene_item['name'])

                conditions_dict[tissue]['diseases'].append({'disease_desc': disease, 'disease_content': {'condition_item': inner_group_list, 'genes': gene_list}})

            conditions_dict[tissue]['disease_count'] = inner_count

        #print dumps(conditions_dict)

        for k, v in conditions_dict.iteritems():
            top_gene_overlap = 0
            for disease in v['diseases']:
                if(len(disease['disease_content']['genes']) > top_gene_overlap):
                    top_gene_overlap = len(disease['disease_content']['genes'])

            conditions_array.append({'tissue': k, 'top_gene_overlap': top_gene_overlap, 'disease_count': v['disease_count'], 'disease_group': v})

        sorted_cached_hits = sorted(conditions_array, key=lambda k: k['disease_count'], reverse=True)

        cached_hits = {'hits': sorted_cached_hits, 'tissue_filters': tissue_filter_array, 'disease_filters': disease_filter_array}

        conditions_search.save(
            {
                'searchId': computed_hash,
                'condition': 'none specified',
                'cached_hits': cached_hits
            }
        )

        client.close()

    if(pageNumber != 99):
        temp_search_these_cached_hits = cached_hits['hits'][from_page:from_page + 5]
        cached_hits['hits'] = temp_search_these_cached_hits
        search_these_cached_hits = cached_hits
    else:
        search_these_cached_hits = cached_hits

    return search_these_cached_hits

def get_cosmic_grouped_by_disease(queryTerms, pageNumber):
    computed_hash = util.compute_query_list_hash(queryTerms)
    #print computed_hash

    hitCount = 0
    from_page = (pageNumber - 1) * 15
    if(from_page < 0):
        from_page = 0
    phenotype_network_data = {
        'searchGroupTitle': 'Cosmic Phenotypes',
        'clusterNodeName': "Cosmic",
        'searchTab': 'PHENOTYPES',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    gene_condition_array = []

    should_match = []
    must_match = []
    queryTermArray = queryTerms.split(',')

    for queryTerm in queryTermArray:
        should_match.append({"match": {"node_list.name": queryTerm}})
        gene_condition_array.append({queryTerm: []})

    search_body = {
        'sort' : [
            '_score'
        ],
        'fields': ['node_list.description','node_list.tissue','node_list.name', 'node_list.cosmic_id', 'node_list.pubmed'], #, 'node_name'],
        'query': {
            'bool': {
                'should': should_match,
                'must_not': [{'match': {'node_list.description': 'NS'}}]
            }
        },
        'from': 0,
        'size': 60
        #'from': from_page,
        #'size': 15
    }

    result = es.search(
        index = 'conditions',
        doc_type = 'conditions_cosmic_mutant',
        body = search_body
    )

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
        sorted_list = sorted(result['hits']['hits'], key=lambda k: k['fields']['node_list.description']) # sort by disease

        #===============================
        # GROUP BY DISEASE
        #===============================
        disease_groups = []
        for key, group in groupby(sorted_list, lambda item: item['fields']['node_list.description']):
            disease_group_item = {
                'disease': key,
                'tissues': list(group)
            }
            disease_groups.append(disease_group_item)

    return disease_groups


def upcase_first_letter(s):
    return s[0].upper() + s[1:]



