__author__ = 'aarongary'

from collections import Counter
from app import PubMed
from app import elastic_search_uri
from app import util
from models.TermResolver import TermAnalyzer
from elasticsearch import Elasticsearch
import numpy as np
import networkx as nx
import pandas as pd
import community
import matplotlib.pyplot as plt
import pymongo
from io import StringIO
from pandas import DataFrame
import hashlib
from bson.json_util import dumps
#from RestBroker import start_thumbnail_generator
from app import SearchViz
from itertools import groupby
import difflib
import time
from elasticsearch_dsl import Search, Q

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server
#es = Elasticsearch(['http://ec2-52-27-59-174.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST',timeout=300) # Prod Clustered Server
#es = Elasticsearch(['http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # PROD
#es = Elasticsearch(['http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com:9200/'],send_get_body_as='POST') # DEV

#============================
#============================
#      CLUSTER SEARCH
#============================
#============================
def get_cluster_search_mapped(queryTerms, pageNumber=99):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'PATHWAYS',
        'diseases': [],
        'network': 'clusters_tcga_louvain',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }
    if(pageNumber == 'undefined'):
        pageNumber = 99

    star_network_data = get_lazy_search(network_information, pageNumber)

    return star_network_data

def get_cluster_search_with_disease_mapped(queryTerms, pageNumber=1, disease=None):
    network_information = {
        'searchGroupTitle': 'Cluster Network',
        'searchTab': 'PATHWAYS',
        'diseases': [],
        'network': 'clusters_tcga_louvain',
        'matchField': 'x_node_list.name',
        'matchCoreNode': 'node_name',
        'cancerType': 'BRCA',
        'queryTerms': queryTerms
    }
    print disease

    star_network_data = get_lazy_search(network_information, pageNumber, disease)

    return star_network_data

def get_lazy_search(network_info, pageNumber=1, disease=[]):
    computed_hash = util.compute_query_list_hash(network_info['queryTerms'])
    #print computed_hash
    if(pageNumber != 99):
        from_page = (int(pageNumber) - 1) * 10
        if(from_page < 0):
            from_page = 0
    else:
        from_page = 0


    client = pymongo.MongoClient()
    db = client.cache

    cluster_search = db.cluster_search

    cluster_search_found = cluster_search.find_one({'searchId': computed_hash, 'disease_type': disease})

    cached_hits = []
    hit_ids = ''
    hit_ids_with_disease = []
    drugable_genes = ['GABRA1','GABRA2','GABRA3','GABRA4','GABRA5','GABRA6','CHRNA4','CHRNA7','GRIA2','GRIK2']
    found_drugable_genes = []
    top_overlap_documents = []
    disease_list = []
    hit_id_node_list = []
    unsorted_items = []
    annotation_array = []
    annotation_dictionary = []

    cluster_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'diseases': [],
        'items': [],
        'grouped_items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1',
        'annotation_filter_all': [],
        'matrix_filter_all': [],
        'disease_filter_all': [],
        'hit_ids': '',
        'hit_ids_with_disease': [],
        'page_number': pageNumber
    }

    cluster_algorithm_hash = {
        'clusters_tcga_oslom': 'OSLM',
        'clusters_geo_oslom': 'OSLM',
        'clusters_tcga_louvain': 'LOUV',
        'clusters_tcga_ivanovska': 'IVAN',
        'clusters_geo_louvain': 'LOUV'

    }

    other_cluster_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': 'OTHER_CLUSTERS',
        'items': [],
        'grouped_items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    other_annotation_dictionary = [{'group_title': 'Other', 'group_members': [], 'topGOId': 'NOGO', 'groupTopQValue': 0, 'topOverlap': 0, 'sort_order': 999, 'group_q_val_total': 0}] #

    queryTermArray = network_info['queryTerms'].split(',')

    sorted_query_list = [] #PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    cluster_network_data['geneSuperList'] = '' #get_geneSuperList(queryTermArray, sorted_query_list)

    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")

    if(cluster_search_found is not None):
        cached_hits = cluster_search_found['cached_hits']
        top_overlap_documents = cluster_search_found['top_overlap_documents']
    else:
        sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
        cluster_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)

        search_body = get_lazy_searchBody(queryTermArray, network_info, disease, sorted_query_list, False, 1) #pageNumber)

        result = es.search(
            index = 'clusters',
            #doc_type = 'clusters_tcga_louvain', clusters_geo_oslom,
            doc_type = ['clusters_geo_oslom', 'clusters_tcga_oslom'],
            body = search_body
        )





#        s = Search(using=client, index="my-index") \
#            .filter("term", network_name="uveal") \
 #           .query("match", title="python")   \
  #          .query(~Q("match", description="beta"))

   #     response = s.execute()



        tr = TermAnalyzer()
        lucene_score_array = []
        for hit in result['hits']['hits']:
            lucene_score_array.append(hit['_score'])

        lucene_score_max = max(lucene_score_array)
        lucene_score_min = min(lucene_score_array)
        for hit in result['hits']['hits']:
            #hit_ids += hit['_id'] + ','
            network_name_s = ''
            gamma_s = ''
            source_s = ''
            network_type_s = ''
            node_name_s = ''
            q_value_i = ''
            go_term_id = ''
            gse_number = ''

            #=============================================
            # Because we are using a "Fields" search in
            # ElasticSearch some of the fields may not
            # exist in each search hit. Therefore we need
            # to check each field first
            #=============================================
            if('network_name' in hit["fields"]):
                if(len(hit["fields"]["network_name"]) > 0):
                    network_name_s = hit["fields"]["network_name"][0]

            if('network_full_name' in hit["fields"]):
                if(len(hit["fields"]["network_full_name"]) > 0):
                    network_full_name_s = hit["fields"]["network_full_name"][0]
                    #if(network_full_name_s not in disease_list):
                    disease_list.append(network_full_name_s)

            if('gse_number' in hit["fields"]):
                if(len(hit["fields"]["gse_number"]) > 0):
                    gse_number = hit["fields"]["gse_number"][0]

            if('gamma' in hit["fields"]):
                if(len(hit["fields"]["gamma"]) > 0):
                    gamma_s = hit["fields"]["gamma"][0]

            if('source' in hit["fields"]):
                if(len(hit["fields"]["source"]) > 0):
                    source_s = hit["fields"]["source"][0]

            if('network_type' in hit["fields"]):
                if(len(hit["fields"]["network_type"]) > 0):
                    network_type_s = hit["fields"]["network_type"][0]

            if('node_name' in hit["fields"]):
                if(len(hit["fields"]["node_name"]) > 0):
                    node_name_s = hit["fields"]["node_name"][0]

            #========================================
            # Get the top annotation from each hit.
            # May not exist for all hits
            #========================================
            if('hypergeometric_scores.qvalueLog' in hit['fields']):
                if(len(hit['fields']['hypergeometric_scores.qvalueLog']) > 0):
                    q_value_i = hit['fields']['hypergeometric_scores.qvalueLog'][0]

            if('hypergeometric_scores.GO_id' in hit['fields']):
                if(len(hit['fields']['hypergeometric_scores.GO_id']) > 0):
                    go_term_id = hit['fields']['hypergeometric_scores.GO_id'][0]

            if('hypergeometric_scores.name' in hit['fields']):
                if(len(hit['fields']['hypergeometric_scores.name']) > 0):
                    if(hit['fields']['hypergeometric_scores.name'][0] not in annotation_array):
                        annotation_array.append(hit['fields']['hypergeometric_scores.name'][0])
                        annotation_dictionary.append({'group_title': hit['fields']['hypergeometric_scores.name'][0], 'topGOId': go_term_id, 'groupTopQValue': 0, 'topOverlap': 0, 'group_members': [], 'sort_order': 1, 'group_q_val_total': 0})


            all_geneNeighborhoodArray = []
            all_geneNeighborhoodStringList = ""
            #========================
            # Get term overlap
            #========================
            #Get All overlap
            #print queryTermArray
            all_nodes_array = []
            for genehit in queryTermArray:
                if(genehit in hit["fields"]["x_node_list.name"] or genehit in hit["fields"]["y_node_list.name"]):
                    all_geneNeighborhoodArray.append(genehit)
                    all_geneNeighborhoodStringList += genehit + ','
            if(len(all_geneNeighborhoodStringList) > 0):
                all_geneNeighborhoodStringList = all_geneNeighborhoodStringList[:-1]

            #'emphasizeInfoArray': all_geneNeighborhoodArray,
            #print hit['fields']

            normalized_score = ((hit['_score'] - lucene_score_min)/(lucene_score_max - lucene_score_min)) * 10.0
            if(normalized_score < 0.7):
                normalized_score = 0.7

            if('hypergeometric_scores.qvalueLog' in hit["fields"]):
                cached_hits.append(
                    {
                        '_index': hit['_index'],
                        '_type': hit['_type'],
                        '_id': hit['_id'],
                        '_score': normalized_score,
                        'overlap_array': all_geneNeighborhoodArray,
                        'overlap_string': all_geneNeighborhoodStringList,
                        'y_count': str(len(hit["fields"]["y_node_list.name"])),
                        'x_count': str(len(hit["fields"]["x_node_list.name"])),
                        'fields': {
                            'hypergeometric_scores_qvalueLog': hit['fields']['hypergeometric_scores.qvalueLog'],
                            'hypergeometric_scores_name': hit['fields']['hypergeometric_scores.name'],
                            'gamma': hit['fields']['gamma'],
                            'source': hit['fields']['source'],
                            'hypergeometric_scores_GO_id': hit['fields']['hypergeometric_scores.GO_id'],
                            'network_name': hit['fields']['network_name'],
                            'network_full_name': hit['fields']['network_full_name'],
                            'gse_number': hit['fields']['gse_number'],
                            'network_type': hit['fields']['network_type']
                        }
                    }
                )
            else:
                cached_hits.append(
                    {
                        '_index': hit['_index'],
                        '_type': hit['_type'],
                        '_id': hit['_id'],
                        '_score': (0.01 * len(all_geneNeighborhoodArray)),#normalized_score,
                        'overlap_array': all_geneNeighborhoodArray,
                        'overlap_string': all_geneNeighborhoodStringList,
                        'y_count': str(len(hit["fields"]["y_node_list.name"])),
                        'x_count': str(len(hit["fields"]["x_node_list.name"])),
                        'fields': {
                            'gamma': hit['fields']['gamma'],
                            'source': hit['fields']['source'],
                            'network_name': hit['fields']['network_name'],
                            'network_full_name': hit['fields']['network_full_name'],
                            'gse_number': hit['fields']['gse_number'],
                            'network_type': hit['fields']['network_type']
                        }
                    }
                )

        cached_hits = sorted(cached_hits, key=lambda k: k['_score'], reverse=True)

        cluster_size_limit = 150
        while((len(top_overlap_documents) < 1) and (cluster_size_limit < 1000)):
            for all_hit in cached_hits:
                network_full_name_s = 'none'
                if('network_full_name' in all_hit["fields"]):
                    if(len(all_hit["fields"]["network_full_name"]) > 0):
                        network_full_name_s = all_hit["fields"]["network_full_name"][0]

                #==================================================
                # This section is temporary until we have a better
                # way of ranking clusters for drug inferrance
                #==================================================
                if(int(all_hit['x_count']) < cluster_size_limit and int(all_hit['y_count']) < cluster_size_limit):
                    top_overlap_documents.append(
                        {
                            'doc_id': all_hit['_id'],
                            'doc_disease': network_full_name_s,
                            'doc_overlap': len(all_hit['overlap_array'])
                        }
                    )
            cluster_size_limit += 50

        client = pymongo.MongoClient()
        db = client.cache

        cluster_search = db.cluster_search

        cluster_search.save(
            {
                'searchId': computed_hash,
                'disease_type': disease,
                'cached_hits': cached_hits,
                'top_overlap_documents': top_overlap_documents
            }
        )

        client.close()

    #============================
    # Compile the filter labels
    #============================
    annotation_filter_all = []
    annotation_filter_all_go_id = []
    matrix_filter_all = []
    disease_filter_all = []
    for hit in cached_hits:
        q_log_value = 0.0

        if('hypergeometric_scores_qvalueLog' in hit['fields']):
            if(len(hit['fields']['hypergeometric_scores_qvalueLog']) > 0):
                q_log_value = hit['fields']['hypergeometric_scores_qvalueLog'][0]
        else:
            #=============================================
            # If no qvaluelog then this is a
            # non-annotated cluster. for filter
            # purposes we give it a passing filter value
            #=============================================
            q_log_value = 99

        if(q_log_value >= 0.5):
            if('network_type' in hit["fields"]):
                if(len(hit["fields"]["network_type"]) > 0):
                    if(hit["fields"]["network_type"][0].replace('_', ' ') not in matrix_filter_all):
                        matrix_filter_all.append(hit["fields"]["network_type"][0].replace('_', ' '))

            if('network_full_name' in hit["fields"]):
                if(len(hit["fields"]["network_full_name"]) > 0):
                    if(hit["fields"]["network_full_name"][0] not in disease_filter_all):
                        disease_filter_all.append(hit["fields"]["network_full_name"][0])


            if('hypergeometric_scores_name' in hit['fields']):
                if(len(hit['fields']['hypergeometric_scores_name']) > 0):
                    if(hit["fields"]["hypergeometric_scores_name"][0] not in annotation_filter_all):
                        annotation_filter_all.append(hit["fields"]["hypergeometric_scores_name"][0])
                        annotation_filter_all_go_id.append(hit["fields"]["hypergeometric_scores_GO_id"][0])
            else:
                if('Other' not in annotation_filter_all):
                    annotation_filter_all.append('Other')

    if(pageNumber != '99'):
        search_these_cached_hits = cached_hits[from_page:from_page + 10]
    else:
        search_these_cached_hits = cached_hits

    for hit in search_these_cached_hits: #result['hits']['hits']:
        #hit_ids += hit['_id'] + ','
        network_name_s = ''
        gamma_s = ''
        source_s = ''
        network_type_s = ''
        node_name_s = ''
        q_value_i = ''
        go_term_id = ''
        gse_number = ''

        #=============================================
        # Because we are using a "Fields" search in
        # ElasticSearch some of the fields may not
        # exist in each search hit. Therefore we need
        # to check and initialize those field
        #=============================================
        if('network_name' in hit["fields"]):
            if(len(hit["fields"]["network_name"]) > 0):
                network_name_s = hit["fields"]["network_name"][0]

        if('network_full_name' in hit["fields"]):
            if(len(hit["fields"]["network_full_name"]) > 0):
                network_full_name_s = hit["fields"]["network_full_name"][0]
                #if(network_full_name_s not in disease_list):
                disease_list.append(network_full_name_s)

        if('gse_number' in hit["fields"]):
            if(len(hit["fields"]["gse_number"]) > 0):
                gse_number = hit["fields"]["gse_number"][0]

        if('gamma' in hit["fields"]):
            if(len(hit["fields"]["gamma"]) > 0):
                gamma_s = hit["fields"]["gamma"][0]

        if('source' in hit["fields"]):
            if(len(hit["fields"]["source"]) > 0):
                source_s = hit["fields"]["source"][0]

        if('network_type' in hit["fields"]):
            if(len(hit["fields"]["network_type"]) > 0):
                network_type_s = hit["fields"]["network_type"][0]

        if('node_name' in hit["fields"]):
            if(len(hit["fields"]["node_name"]) > 0):
                node_name_s = hit["fields"]["node_name"][0]

        #for x_genehit in hit["fields"]["x_node_list.name"]:
        #    if(x_genehit in drugable_genes):
        #        if(x_genehit not in found_drugable_genes):
        #            found_drugable_genes.append(x_genehit)

        #for y_genehit in hit["fields"]["y_node_list.name"]:
        #    if(y_genehit in drugable_genes):
        #        if(y_genehit not in found_drugable_genes):
        #            found_drugable_genes.append(y_genehit)

        all_geneNeighborhoodArray = hit['overlap_array']  #[]
        all_geneNeighborhoodStringList = hit['overlap_string'] #""
        #========================
        # Get term overlap
        #========================
        #Get All overlap

        all_nodes_array = []
        #for genehit in queryTermArray:
        #    if(genehit in hit["fields"]["x_node_list.name"] or genehit in hit["fields"]["y_node_list.name"]):
        #        all_geneNeighborhoodArray.append(genehit)
        #        all_geneNeighborhoodStringList += genehit + ','
        #if(len(all_geneNeighborhoodStringList) > 0):
        #    all_geneNeighborhoodStringList = all_geneNeighborhoodStringList[:-1]


        #for genehit in hit["fields"]["x_node_list.name"]:
        #    all_nodes_array.append(genehit)

        #for genehit in hit["fields"]["y_node_list.name"]:
        #    if(genehit not in all_nodes_array):
        #        all_nodes_array.append(genehit)

        #========================
        # END Get term overlap
        #========================

        #========================================
        # Get the top annotation from each hit.
        # May not exist for all hits
        #========================================
        if('hypergeometric_scores_qvalueLog' in hit['fields']):
            if(len(hit['fields']['hypergeometric_scores_qvalueLog']) > 0):
                q_value_i = hit['fields']['hypergeometric_scores_qvalueLog'][0]

        if('hypergeometric_scores_GO_id' in hit['fields']):
            if(len(hit['fields']['hypergeometric_scores_GO_id']) > 0):
                go_term_id = hit['fields']['hypergeometric_scores_GO_id'][0]

        if('hypergeometric_scores_name' in hit['fields']):
            if(len(hit['fields']['hypergeometric_scores_name']) > 0):
                if(hit['fields']['hypergeometric_scores_name'][0] not in annotation_array):
                    annotation_array.append(hit['fields']['hypergeometric_scores_name'][0])
                    annotation_dictionary.append({'group_title': hit['fields']['hypergeometric_scores_name'][0], 'topGOId': go_term_id, 'groupTopQValue': 0, 'topOverlap': 0, 'group_members': [], 'sort_order': 1, 'group_q_val_total': 0})

        #====================================
        # create a list of nodes in this
        # cluster to be used in dup compare
        #====================================
        hit_id_node_list.append(
            {
                'hit_id': hit['_id'],
                'top_Q': q_value_i,
                'query_nodes': [] #sorted(all_nodes_array)
            }
        )

        gene_network_data_items = {
            'md5hash': 'hash code place holder',
            'searchResultTitle': node_name_s.replace('-','') + ' ' + network_name_s + ' ' + network_type_s + ' gamma:' + gamma_s + ' Q value: ' + str(q_value_i), #+ ' ' + searchResultTitle,
            'QValue': str(q_value_i),
            'Gamma': gamma_s,
            'Source': source_s,
            'hit_id': hit['_id'],
            'diseaseType': network_full_name_s, #tr.get_cancer_description_by_id(network_name_s).replace(',',' '),
            'gse_number': gse_number,
            'dataSetType': network_type_s.replace('_', ' '),
            'clusterName': node_name_s.replace('-',''),
            'hypergeometricScores': [],
            'searchResultScoreRank': hit["_score"],
            'cluster_algorithm': cluster_algorithm_hash[hit["_type"]],
            'luceneScore': hit["_score"],
            'topQValue': q_value_i,
            'topOverlap': len(all_geneNeighborhoodArray),
            'y_count': hit['y_count'], #str(len(hit["fields"]["y_node_list.name"])),
            'x_count': hit['x_count'], #str(len(hit["fields"]["x_node_list.name"])),
            'searchResultScoreRankTitle': 'pubmed references ',
            #'filterValue': str(len(hit["fields"]["y_node_list.name"])) + ' x ' + str(len(hit["fields"]["x_node_list.name"])),
            'emphasizeInfoArray': all_geneNeighborhoodArray,
            'overlapList': all_geneNeighborhoodStringList,
            'x_emphasizeInfoArrayWithWeights': [],
            'y_emphasizeInfoArrayWithWeights': [],
            'pubmedCount': 0
        }

        #==================================================
        # HEAT PROP
        #==================================================
        #cluster_x_y_z = SearchViz.load_x_y_z_cluster_data(hit['_id'])
        #SearchViz.get_heat_prop_from_gene_list_by_cluster_source(all_geneNeighborhoodStringList,cluster_x_y_z)

        #==================================================
        # This section is temporary until we have a better
        # way of ranking clusters for drug inferrance
        #==================================================
#        if(int(hit['x_count']) <= 200 and int(hit['y_count']) <= 200):
#            top_overlap_documents.append(
#                {
#                    'doc_id': hit['_id'],
#                    'doc_disease': network_full_name_s,
#                    'doc_overlap': len(all_geneNeighborhoodArray)
#                }
#            )
        #==================================================
        # END temporary section
        #==================================================

        unsorted_items.append(gene_network_data_items)

        annotation_found = False

        for ann_dict_item in annotation_dictionary:
            if('hypergeometric_scores_name' in hit['fields']):
                if(len(hit['fields']['hypergeometric_scores_name']) > 0):
                    if(ann_dict_item['group_title'] == hit['fields']['hypergeometric_scores_name'][0]):
                        ann_dict_item['group_q_val_total'] += gene_network_data_items['topQValue']
                        ann_dict_item['group_members'].append(gene_network_data_items)
                        # cumulate the q value scores
                        annotation_found = True

        if(not annotation_found):
            for ann_dict_item in other_annotation_dictionary:
                if(ann_dict_item['group_title'] == 'Other'):
                    ann_dict_item['group_members'].append(gene_network_data_items)

    #print 'Process hits: ' + str(start_time - time.time())
    #start_time = time.time()
    #=================================================
    # Calculate the average Q value for each group
    # Also determine the highest Q value in the group
    #=================================================
    master_group_dups = []
    master_group_dups_membership = []
    for ann_dict_item in annotation_dictionary:

        if(len(ann_dict_item['group_members']) > 0):
            average_q_value = float(ann_dict_item['group_q_val_total']) / float(len(ann_dict_item['group_members']))
            ann_dict_item['average_q_value'] = average_q_value

            group_top_q_value_array = []
            group_top_overlap_array = []
            for group_item in ann_dict_item['group_members']:
                group_top_q_value_array.append(group_item['topQValue'])
                group_top_overlap_array.append(len(group_item['emphasizeInfoArray']))

            #==============================================
            # Find cluster dups DISABLED (see line below)
            #==============================================
            if(len(group_top_q_value_array) > 0 and ann_dict_item['group_title'] != 'Other'):
                ann_dict_item['groupTopQValue'] = max(group_top_q_value_array)
                dup_ids = [] #DISABLED  determine_cluster_duplicates(group_top_q_value_array, hit_id_node_list)

                if(len(dup_ids) > 0):
                    for dup in dup_ids:
                        if dup not in master_group_dups_membership:
                            master_group_dups_membership.append(dup)

                ann_dict_item['topOverlap'] = max(group_top_overlap_array)
            elif(ann_dict_item['group_title'] == 'Other'):
                ann_dict_item['topOverlap'] = max(group_top_overlap_array)


        else:
            ann_dict_item['average_q_value'] = 0

    #print master_group_dups_membership
    #print 'Average Q: ' + str(start_time - time.time())
    #start_time = time.time()

    top_documents_sorted_list = sorted(top_overlap_documents, key=lambda k: k['doc_overlap'])
    #print dumps(top_documents_sorted_list[-3:])

    for top_docs in reversed(top_documents_sorted_list[-8:]):
        hit_ids += top_docs['doc_id'] + ','
        hit_ids_with_disease.append(
            {
                'id': top_docs['doc_id'],
                'disease': top_docs['doc_disease']
            }
        )

    if(len(hit_ids) > 0):
        hit_ids = hit_ids[:-1]
        #start_thumbnail_generator(hit_ids)

        cluster_network_data['hit_ids'] = hit_ids
        cluster_network_data['hit_ids_with_disease'] = hit_ids_with_disease


    for ann_dict_item in annotation_dictionary:
        replace_group_with_this = []
        for group_item in ann_dict_item['group_members']:
            if(group_item['hit_id'] in master_group_dups_membership):
                #ann_dict_item['group_members'].remove(group_item)
                group_item['Source'] += '_dup'
            else:
                replace_group_with_this.append(group_item)
        ann_dict_item['group_members'] = replace_group_with_this

    cluster_network_data['grouped_items'] = annotation_dictionary

    return_disease_list = []
    disease_list_grouped =  [list(j) for i, j in groupby(sorted(disease_list))]
    for disease_group in disease_list_grouped:
        return_disease_list.append(
            {
                'disease_title': disease_group[0],
                'count': len(disease_group)
            }
        )

    cluster_network_data['diseases'] = return_disease_list
    #print 'Other: ' + str(start_time - time.time())
    #start_time = time.time()

    if(len(other_annotation_dictionary) > 0):
        cluster_network_data['grouped_items'].append(other_annotation_dictionary[0])

        cluster_network_data['annotation_filter_all'] = annotation_filter_all
        cluster_network_data['annotation_filter_all_go_id'] = annotation_filter_all_go_id
        cluster_network_data['matrix_filter_all'] = matrix_filter_all
        cluster_network_data['disease_filter_all'] = disease_filter_all


    other_cluster_network_data['grouped_items'] = other_annotation_dictionary

    #print 'Everything else: ' + str(start_time - time.time())

    #print found_drugable_genes

    return [cluster_network_data] #, other_cluster_network_data]

#========================================================================
# If 2 or more clusters share 95% of the same nodes we will flag them as
# duplicates.  In a group of duplicates we will keep the first one and
# recommend removing the others
#========================================================================
def determine_cluster_duplicates(group_item_ids, group_items):
    return_ids = []
    simularity_array = [list(j) for i, j in groupby(sorted(group_item_ids))]
    for simular_items in simularity_array:
        group_dup_ids = []
        if(len(simular_items) > 1):
            compare_these_objs = []
            last_list = []
            last_id = ''
            first_id = None
            for compare_this in group_items:
                if(compare_this['top_Q'] == simular_items[0]):
                    if first_id is None:
                        first_id = compare_this['hit_id']

                    #print compare_this['hit_id'] + ' query nodes size: ' + str(len(compare_this['query_nodes']))

                    this_list = compare_this['query_nodes']
                    this_id = compare_this['hit_id']

                    if(len(last_list) > 0):
                        sm=difflib.SequenceMatcher(None,last_list,this_list)
                        if(sm.ratio() > 0.95):
                            if(last_id not in return_ids):
                                group_dup_ids.append(last_id)
                                #print last_id
                            if(this_id not in return_ids):
                                group_dup_ids.append(this_id)
                                #print this_id

                    last_list = this_list
                    last_id = compare_this['hit_id']

            for dup_item in group_dup_ids[1:]:
                return_ids.append(dup_item)

            #print simular_items[0]
    return return_ids


def load_x_y_z_cluster_data(result_source):
    #result_source = results['hits']['hits'][0]['_source']
    xValues = []
    yValues = []

    result = result_source
    for x_label in result['x_node_list']:
        xValues.append(x_label['name'])

    for y_label in result['y_node_list']:
        yValues.append(y_label['name'])

    data = []
    for correlation_record in result['correlation_matrix']:

        correlation_value = correlation_record['correlation_value']

        data.append([correlation_record['x_loc'], correlation_record['y_loc'], correlation_value])

    array = np.zeros((len(result['x_node_list']), len(result['y_node_list'])))

    for row, col, val in data:
        index = (row, col)
        array[index] = val

    zValues = array;

    sample_mat = pd.DataFrame(data=zValues,    # values
    index=yValues,    # 1st column as index
    columns=xValues)  # 1st row as the column names

    idx_to_node = dict(zip(range(len(sample_mat)),list(sample_mat.index)))

    sample_mat = np.array(sample_mat)
    sample_mat = sample_mat[::-1,::-1] # reverse the indices for use in graph creation

    G_cluster = nx.Graph()
    G_cluster = nx.from_numpy_matrix(np.abs(sample_mat))
    G_cluster = nx.relabel_nodes(G_cluster,idx_to_node)

    return G_cluster

def cluster_search_mapped(network_info, disease=[]):
    gene_network_data = {
        'searchGroupTitle': network_info['searchGroupTitle'],
        'clusterNodeName': "",
        'searchTab': network_info['searchTab'],
        'items': [],
        'grouped_items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '100',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    unsorted_items = []
    gene_super_list = []
    annotation_array = []
    annotation_dictionary = [{'group_title': 'Other', 'group_members': [], 'sort_order': 999}]

    queryTermArray = network_info['queryTerms'].split(',')
    sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)
    gene_network_data['geneSuperList'] = get_geneSuperList(queryTermArray, sorted_query_list)
    network_info['queryTerms'] = network_info['queryTerms'].replace(",", "*")
    search_body = get_searchBody(queryTermArray, network_info, disease, sorted_query_list, False)

    result = es.search(
        #index = 'network',
        #doc_type = 'louvain_cluster',
        index = 'clusters',
        doc_type = 'clusters_tcga_louvain',
        #doc_type = 'clusters_tcga_louvain, clusters_tcga_oslom',
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
        if(len(hit['_source']['hypergeometric_scores']) > 0):
            if(hit['_source']['hypergeometric_scores'][0]['name'] not in annotation_array):
                annotation_array.append(hit['_source']['hypergeometric_scores'][0]['name'])
                annotation_dictionary.append({'group_title': hit['_source']['hypergeometric_scores'][0]['name'], 'group_members': [], 'sort_order': 1})

        if(hitCount == 0):
            hitMax = hit['_score']
        else:
            hitMin = hit['_score']

        all_geneNeighborhoodArray = [];
        #========================
        # Get term overlap
        #========================
        #Get All overlap
        for genehit in hit["_source"]["query_node_list"]:
            all_geneNeighborhoodArray.append(genehit['name'])

        all_all = [set(all_geneNeighborhoodArray), set(queryTermArray)]

        all_intersect = set.intersection(*all_all)
        #========================
        # END Get term overlap
        #========================

        searchResultSummaryString = hit["_source"]["source"] #+ '- [hypergeometric scores coming soon]' #+ hit["_source"]["hypergeometric_scores"]
        searchResultTitle = ''
        hg_q_log_val = 5.0
        for hg in hit['_source']['hypergeometric_scores']:
            if(hg['qvalueLog'] >= hg_q_log_val):
                hg_q_log_val = hg['qvalueLog']
                searchResultTitle = hg['name']

        hit_score = float(hit["_score"])

        #=================================================
        # Compute a hash code to identify if 2 (or more)
        # clusters are the same
        #=================================================
        hash_array = []
        h = hashlib.new('ripemd160')
        h.update(hit["_source"]["network_name"] + hit["_source"]["network_type"] + str(len(hit["_source"]["y_node_list"])) + 'x' + str(len(hit["_source"]["x_node_list"])))
        all_geneNeighborhoodString = ''.join(sorted(all_geneNeighborhoodArray))
        h.update(all_geneNeighborhoodString)
        computed_hash = h.hexdigest()
        #=================================================
        # END HASH COMPUTE
        #=================================================

        hash_array.append(computed_hash)

        gene_network_data_items = {
            'md5hash': computed_hash,
            'searchResultTitle': hit["_source"]["node_name"].replace('-','') + ' ' + hit["_source"]["network_name"] + ' ' + hit["_source"]["network_type"] + ' gamma:' + hit["_source"]["gamma"], #+ ' ' + searchResultTitle,
            'hit_id': hit['_id'],
            'diseaseType': tr.get_cancer_description_by_id(hit["_source"]["network_name"]).replace(',',' '),
            'dataSetType': hit["_source"]["network_type"].replace('_', ' '),
            'clusterName': hit["_source"]["node_name"].replace('-',''),
            'searchResultSummary': searchResultSummaryString,
            'hypergeometricScores': hit['_source']['hypergeometric_scores'],
            'searchResultScoreRank': hit["_score"],
            'luceneScore': hit["_score"],
            'searchResultScoreRankTitle': 'pubmed references ',
            'filterValue': str(len(hit["_source"]["y_node_list"])) + ' x ' + str(len(hit["_source"]["x_node_list"])),
            'emphasizeInfoArray': set(all_intersect),
            'x_emphasizeInfoArrayWithWeights': [],
            'y_emphasizeInfoArrayWithWeights': [],
            'top5': hitCount < 5,
            'hitOrder': hitCount,
            'pubmedCount': 0
        }

        unsorted_items.append(gene_network_data_items)
        gene_network_data['items'].append(gene_network_data_items)

        annotation_found = False
        for ann_dict_item in annotation_dictionary:
            if(len(hit['_source']['hypergeometric_scores']) > 0):
                if(ann_dict_item['group_title'] == hit['_source']['hypergeometric_scores'][0]['name']):
                    ann_dict_item['group_members'].append(gene_network_data_items) #hit['_id'])  #hit["_source"]["node_name"].replace('-','') + ' ' + hit["_source"]["network_name"] + ' ' + hit["_source"]["network_type"] + ' gamma:' + hit["_source"]["gamma"] + ' ' + searchResultTitle)
                    annotation_found = True

        if(not annotation_found):
            for ann_dict_item in annotation_dictionary:
                if(ann_dict_item['group_title'] == 'Other'):
                    mystr1 = ann_dict_item['group_members'].append(gene_network_data_items) #hit['_id'])  #hit["_source"]["node_name"].replace('-','') + ' ' + hit["_source"]["network_name"] + ' ' + hit["_source"]["network_type"] + ' gamma:' + hit["_source"]["gamma"] + ' ' + searchResultTitle)



        hitCount += 1

    print hitCount

    #for network_data_item in unsorted_items:

    gene_network_data['grouped_items'] = annotation_dictionary


#    foundHit = False
#    for network_data_item in unsorted_items:
#        foundHit = False
#        for sortedID in sorted_query_list['results']:
#            if sortedID['id'] == network_data_item['clusterName']:
#                network_data_item['pubmedCount'] = sortedID['count']
#                network_data_item['searchResultScoreRank'] = sortedID['normalizedValue']
#                gene_network_data['items'].append(network_data_item)
#                foundHit = True

#        if(not foundHit):
#            network_data_item['pubmedCount'] = 0
#            network_data_item['searchResultScoreRank'] = 0
#            gene_network_data['items'].append(network_data_item)

    counter_gene_list = Counter(gene_super_list)

    for key, value in counter_gene_list.iteritems():
        kv_item = {'queryTerm': key,
                   'boostValue': value}
        #gene_network_data['geneSuperList'].append(kv_item)



    return gene_network_data

def get_document_overlaps(queryTerms, elasticId):
    queryTermArray = queryTerms.split(',')
    search_body = {
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
        body = search_body
    )

    if(len(results) > 0):
        result = results['hits']['hits'][0]['_source']

        data = {
            'corr': [],
            'group_id': [],
            'p': [],
            'var1': [],
            'var2': []
        }
        print 'got results'
        main_data_tuples = []
        #===================================
        # GENERATE NODES & EDGES DATAFRAME
        # BASED ON EDGE CUT_OFF
        #===================================
        for correlation_record in result['correlation_matrix']:
            data['corr'].append(correlation_record['correlation_value'])
            data['group_id'].append(elasticId)
            data['p'].append(correlation_record['p_value'])
            data['var1'].append(result['x_node_list'][correlation_record['x_loc']]['name'])
            data['var2'].append(result['y_node_list'][correlation_record['y_loc']]['name'])
            main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'], result['y_node_list'][correlation_record['y_loc']]['name'], correlation_record['correlation_value']))

        #print 'x1'
        #print main_data_tuples
#        edge_list_1 = [(data['var1'], data['var2'], data['corr'])]
#        Gsmall_1 = nx.Graph()
        #print 'x2'
#        Gsmall_1.add_weighted_edges_from(edge_list_1)
        #print 'x3'

#        for query_term in queryTermArray:
#            print Gsmall_1.neighbors(query_term)



        #print 'edge list created'
        #edge_list_df = pd.DataFrame(data, columns=['corr', 'group_id','p','var1','var2'])
        #print 'data frame created'

        Gsmall = nx.Graph()
        #print 'edge list created 4'
        Gsmall.add_weighted_edges_from(main_data_tuples)
        #print 'edges added'

        for query_term in queryTermArray:
            print Gsmall.neighbors(query_term)



        #group_ids = np.unique(edge_list_df['group_id'])

        #for focal_group in group_ids:
        #    idx_group = (edge_list_df['group_id']==focal_group)
        #    idx_group = list(edge_list_df['group_id'][idx_group].index)

            # make a network out of it
        #    print 'edge list created 2'
        #    edge_list = [(edge_list_df['var1'][i], edge_list_df['var2'][i], edge_list_df['corr'][i]) for i in idx_group if edge_list_df['corr'][i] !=0]
        #    print 'edge list created 3'
        #    Gsmall = nx.Graph()
        #    print 'edge list created 4'
        #    Gsmall.add_weighted_edges_from(edge_list)
        #    print 'edges added'

        #    for query_term in queryTermArray:
        #        print Gsmall.neighbors(query_term)

def get_searchBody(queryTermArray, network_info, disease, sorted_query_list, isStarSearch):
    should_match = []
    must_match = []
    returnBody = {}

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)

    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)
        if(boost_value_append < 0.0001):
            boost_value_append = 0.0001
        if(isStarSearch):
            should_match.append({"match": {"node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append( { 'match': {'node_name': queryTerm} })
            #should_match.append( { 'match': {'node_list.node.name': queryTerm} })
        else:
            #should_match.append({"match": {"query_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append({"match": {"x_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append({"match": {"y_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})

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
                'size': 12
            }

    return returnBody

def get_lazy_searchBody(queryTermArray, network_info, disease, sorted_query_list, isStarSearch, pageNumber=1):
    should_match = []
    should_match_experiment =[]
    must_match_experiment = []
    filter_match = []
    must_match = []
    returnBody = {}
    if(pageNumber != 99):
        from_page = (int(pageNumber) - 1) * 40
        if(from_page < 0):
            from_page = 0
    else:
        from_page = 0

    #sorted_query_list = PubMed.get_gene_pubmed_counts_normalized(network_info['queryTerms'], 1)


    for queryTerm in queryTermArray:
        boost_value_append = get_boost_value(sorted_query_list['results'], queryTerm)

        if(boost_value_append < 0.001):
            boost_value_append = 0.001

        if(isStarSearch):
            should_match.append({"match": {"node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            should_match.append( { 'match': {'node_name': queryTerm} })
            #should_match.append( { 'match': {'node_list.node.name': queryTerm} })
        else:
            #should_match_experiment.append({"constant_score": {"query":{"match": {"query_node_list.name":queryTerm}}}})
            should_match_experiment.append({"constant_score": {"filter":{"term": {"query_node_list.name":queryTerm}}}})

            should_match.append({"match": {"query_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            filter_match.append(queryTerm)
            #should_match.append({"match": {"x_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})
            #should_match.append({"match": {"y_node_list.name":{"query": queryTerm,"boost": boost_value_append}}})

    if len(disease) > 0:
        diseaseWithSpaces = '';
        for addThisDisease in disease:
            must_match_experiment.append({"constant_score": {"filter":{"term": {"network_name":addThisDisease.lower()}}}})

            if len(diseaseWithSpaces) < 1:
                diseaseWithSpaces = addThisDisease
            else:
                diseaseWithSpaces = diseaseWithSpaces + ' ' + addThisDisease


        must_match.append({'match': {'network_name': diseaseWithSpaces}})
        print 'Filter disease: '
        print disease
    else:
        must_match.append({"match": {"network_name": "LAML ACC BLCA LGG BRCA CESC CHOL COAD ESCA FPPP GBM HNSC KICH KIRC KIRP LIHC LUAD LUSC DLBC MESO OV PAAD PCPG PRAD READ SARC SKCM STAD TGCT THYM THCA UCS UCEC UVM"}})

    experimental_search_body2 = {}
    if(len(disease) > 0):
        experimental_search_body2 = {
            'fields': ['network_type', 'network_name', 'network_full_name', 'gse_number', 'gamma', 'hypergeometric_scores.name', 'hypergeometric_scores.qvalueLog', 'hypergeometric_scores.GO_id', 'x_node_list.name', 'y_node_list.name', 'source'],
            'size': 40,
            'from': from_page,
            'query': {
                'filtered': {
                    'filter': {'term': {'network_name': disease}},
                    'query': {
                        'function_score': {
                            'query': {
                                'bool': {
                                    'should': should_match_experiment
                                }
                            },
                            'field_value_factor': {
                                'field': 'max_annotation_conf',
                                'factor': 0.00001,
                                'modifier': 'log2p',
                                'missing': 1
                            },
                            'score_mode': 'sum',
                            'boost_mode': 'sum'
                        }
                    }
                }
            }
        }

        returnBody = {
            #'sort': [{'_score': {'order': 'desc'}}, {'hypergeometric_scores.qvalueLog': {'order': 'desc'}}],
            'fields': ['network_type', 'network_name', 'network_full_name', 'gse_number', 'gamma', 'hypergeometric_scores.name', 'hypergeometric_scores.qvalueLog', 'hypergeometric_scores.GO_id', 'x_node_list.name', 'y_node_list.name', 'source'],
            'filtered':{
                'query' : {
                    'bool': {
                        'should': should_match
                    }
                },
                'filter': must_match
            },
            'from': from_page,
            'size': 10
        }

        #s = Search.from_dict(experimental_search_body2)
        #s.filter('term', network_name='uveal')
        #experimental_search_body2 = s.to_dict()
        #print dumps(experimental_search_body2)

    else:
        returnBodyx = {
            'fields': ['network_type', 'network_name', 'network_full_name', 'gse_number', 'gamma', 'hypergeometric_scores.name', 'hypergeometric_scores.qvalueLog', 'hypergeometric_scores.GO_id', 'x_node_list.name', 'y_node_list.name', 'source'],
            'query': {
                'filtered': {
                    'query': {
                        'function_score': {
                            'query': {
                                'bool': {
                                    'should': should_match_experiment
                                }

                            },
                            'functions': [
                                {
                                    'script_score': {
                                        'file': 'pathwayFunctions'
                                    }
                                }
                            ],
                            'score_mode': 'multiply'
                        },
                        'filter': {
                            'bool': {
                                'should': [
                                    {
                                        'terms': {
                                            'query_node_list.name': filter_match
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            'highlight': {
                'pre_tags': [''],
                'post_tags': [''],
                'fields': {
                    'query_node_list.name': {}
                }
            },
            'from': from_page,
            'size': 10
        }

        experimental_search_body2 = {
            'highlight': {
                'pre_tags': [''],
                'fields': {
                    'query_node_list.name': {}
                },
                'post_tags': ['']
            },
            'fields': ['network_type', 'network_name', 'network_full_name', 'gse_number', 'gamma', 'hypergeometric_scores.name', 'hypergeometric_scores.qvalueLog', 'hypergeometric_scores.GO_id', 'x_node_list.name', 'y_node_list.name', 'source'],
            'size': 40,
            'from': from_page,
            'query': {
                'function_score': {
                    'query': {
                        'bool': {
                            'should': should_match_experiment
                        }
                    },
                    'field_value_factor': {
                        'field': 'max_annotation_conf',
                        'factor': 0.00001,
                        'modifier': 'log2p',
                        'missing': 1
                    },
                    'score_mode': 'sum',
                    'boost_mode': 'sum'
                }
            }
        }


        returnBody = {
            #'sort': [{'_score': {'order': 'desc'}}, {'hypergeometric_scores.qvalueLog': {'order': 'desc'}}],
            'fields': ['network_type', 'network_name', 'network_full_name', 'gse_number', 'gamma', 'hypergeometric_scores.name', 'hypergeometric_scores.qvalueLog', 'hypergeometric_scores.GO_id', 'x_node_list.name', 'y_node_list.name', 'source'],
            'query' : {
                'bool': {
                    'should': should_match
                }
            },
            'from': from_page,
            'size': 10
        }

    return experimental_search_body2 #returnBody


def convert_network_type(network_type):
    switcher = {
        'mutation_vs_mutation': 'DNA x DNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
        'rnaseq_vs_rnaseq': 'RNA x RNA',
    }
    return switcher.get(network_type, network_type)

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

    return 0.0001

def get_heatmap_graph_from_es_by_id(elasticId, gene_list, search_type, cut_off_filter_value):

    client = pymongo.MongoClient()
    db = client.cache

    gene_list_array = gene_list.split(',')

    query_list_found = []

    heat_map_graph = db.heat_map_graph

    heat_map_found = heat_map_graph.find_one({'clusterId': elasticId})

    if(heat_map_found is not None):
        return heat_map_found['heat_map']
    else:
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
            doc_type = search_type,
            body = search_body
        )

        if(len(results['hits']['hits']) > 0):
            result = results['hits']['hits'][0]['_source']
            calculated_cut_off = 0.5
            #if(len(result['correlation_matrix']) > 1000):
            #    calculated_cut_off = 0.87
            #else:
            #    calculated_cut_off = 0.5 + (0.37 * (len(result['correlation_matrix'])/1000))

            cluster_IO = "corr  group_id    p   var1    var2 \n"

            x_matrix_width = len(result['x_node_list'])-1
            y_matrix_width = len(result['y_node_list'])-1

            data = {
                'corr': [],
                'group_id': [],
                'p': [],
                'var1': [],
                'var2': []
            }

            calculated_cut_off = get_top_200_weight(result['correlation_matrix'])

            for gene_list_item in gene_list_array:
                x_node_index = findIndexByKeyValue(result['x_node_list'], 'name', gene_list_item)
                if(x_node_index >= 0):
                    query_list_found.append(gene_list_item)
                else:
                    y_node_index = findIndexByKeyValue(result['y_node_list'], 'name', gene_list_item)
                    if(y_node_index >= 0):
                        query_list_found.append(gene_list_item)

            for correlation_record in result['correlation_matrix']:
                correlation_value = correlation_record['correlation_value']
                if( (abs(correlation_value) >= calculated_cut_off)): #or (correlation_record['x_loc'] in x_query_list_found) or (correlation_record['y_loc'] in y_query_list_found) ):
                    #if( (correlation_record['x_loc'] in x_query_list_found) and abs(correlation_value) < calculated_cut_off ):
                    #    x_query_list_found.remove(correlation_record['x_loc'])

                    #if( (correlation_record['y_loc'] in y_query_list_found) and abs(correlation_value) < calculated_cut_off ):
                    #    y_query_list_found.remove(correlation_record['y_loc'])

                #if(abs(correlation_value) >= calculated_cut_off):
                    data['corr'].append(correlation_value)
                    data['group_id'].append(elasticId)
                    data['p'].append(correlation_record['p_value'])
                    data['var1'].append(result['x_node_list'][correlation_record['x_loc']]['name'])
                    data['var2'].append(result['y_node_list'][correlation_record['y_loc']]['name'])

            #===============================
            # CUTOFF was too stringent.
            # no edges produced.  Recompute
            #===============================
            if(len(data['corr']) < 1):
                for correlation_record in result['correlation_matrix']:
                    correlation_value = correlation_record['correlation_value']
                    if((abs(correlation_value) >= 0.5)):
                        data['corr'].append(correlation_value)
                        data['group_id'].append(elasticId)
                        data['p'].append(correlation_record['p_value'])
                        data['var1'].append(result['x_node_list'][correlation_record['x_loc']]['name'])
                        data['var2'].append(result['y_node_list'][correlation_record['y_loc']]['name'])

            df = pd.DataFrame(data, columns=['corr', 'group_id','p','var1','var2'])


            result = generate_graph_from_tab_file(df, 'temp', elasticId, 'community')

            for xy_item in query_list_found:
                foundItem = False
                for node in result['heat_map']['nodes']:
                    if(node['id'] == xy_item):
                        foundItem = True
                        break

                if(not foundItem):
                    result['heat_map']['nodes'].append(
                        {
                          'bfrac': 80,
                          'degree': 0,
                          'gfrac': 80,
                          'rfrac': 80,
                          'com': 999,
                          'id': xy_item
                        }
                    )

            return result['heat_map']
        print("Got %d Hits:" % results['hits']['total'])

        if(results['hits']['total'] < 1):
            print 'no results'

    #return return_value

def findIndexByKeyValue(obj, key, value):
    mystr = ''
    for i in range(0,len(obj)):
        if (obj[i][key] == value):
            return i

    return -1

def get_top_200_weight(cor_matrix):
    cor_values_array = [];
    for correlation_record in cor_matrix:
        cor_values_array.append(correlation_record['correlation_value'])

    cor_values_array_sorted = sorted(cor_values_array, reverse=True)[:200]

    #print cor_values_array_sorted
    print cor_values_array_sorted[-1]

    return cor_values_array_sorted[-1]

def get_enrichment_from_es_by_id(elasticId):
    search_body = {
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
        body = search_body
    )

    if(len(results) > 0):
        result = results['hits']['hits'][0]['_source']


        hyper_geo_results = result['hypergeometric_scores']

        if(len(hyper_geo_results) > 0):
            return hyper_geo_results;
        else:
            return [{
                'name': 'no results found',
                'GO_id': '',
                'pvalue': 0,
                'qvalueLog': 0,
                'overlap': 0,
                'genes_from_list': 0,
                'genes_from_GO': 0,
                'description': 'no results found'
            }]

def generate_graph_from_tab_file(cluster_IO,out_file_start, cluster_id, color_type='community', colormap='OrRd'):
    '''
    this function takes a processed cluster file ('input_file_name': output of process clustering results in cluster_analysis_module)
    and saves a json file for every community in the file, starting with 'out_file_start'.  'input_file_name' and 'out_file_start'
    should be prepended with location.
    '''

    # first load in a network (edge list)

    edge_list_df = cluster_IO #pd.read_csv(cluster_IO,sep='\t')

    group_ids = np.unique(edge_list_df['group_id'])

    for focal_group in group_ids:

        print focal_group

        #save_file_name = out_file_start + '_' + str(int(focal_group)) + '.json'

        idx_group = (edge_list_df['group_id']==focal_group)
        idx_group = list(edge_list_df['group_id'][idx_group].index)

        # make a network out of it

        edge_list = [(edge_list_df['var1'][i], edge_list_df['var2'][i], np.abs(edge_list_df['corr'][i])) for i in idx_group if edge_list_df['corr'][i] !=0]
        #edge_list = [(edge_list_df['var1'][i], edge_list_df['var2'][i], edge_list_df['corr'][i]) for i in idx_group if edge_list_df['corr'][i] !=0]

        Gsmall = nx.Graph()
        Gsmall.add_weighted_edges_from(edge_list)


        nodes = Gsmall.nodes()
        numnodes = len(nodes)
        edges=Gsmall.edges(data=True)
        numedges = len(edges)



        if color_type=='community':
            partition = community.best_partition(Gsmall)

            partition = pd.Series(partition)
            col_temp = partition[Gsmall.nodes()]

            # Set up json for saving
            # what should the colors be??
            num_communities = len(np.unique(col_temp))
            color_list = plt.cm.gist_rainbow(np.linspace(0, 1, num_communities))

            # blend the community colors (so that to-nodes are a mixture of all the communities they belong to)
            rfrac,gfrac,bfrac=calc_community_fraction(Gsmall,Gsmall.nodes(),Gsmall.nodes(),partition,color_list)

            #nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n)} for n in nodes]
            nodes_dict = [{"id":n,"com":col_temp[n],"degree":Gsmall.degree(n),
                        "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]
        elif color_type=='clustering_coefficient':
            cmap= plt.get_cmap(colormap)
            rfrac,gfrac,bfrac=calc_clustering_coefficient(Gsmall,cmap)
            nodes_dict = [{"id":n,"com":0,"degree":Gsmall.degree(n),
                        "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]

        elif color_type=='betweenness_centrality':
            cmap= plt.get_cmap(colormap)
            rfrac,gfrac,bfrac=calc_betweenness_centrality(Gsmall,cmap)
            nodes_dict = [{"id":n,"com":0,"degree":Gsmall.degree(n),
                        "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]




#        partition = community.best_partition(Gsmall)

#        partition = pd.Series(partition)
#        col_temp = partition[Gsmall.nodes()]

        # Set up json for saving
        # what should the colors be??
#        num_communities = len(np.unique(col_temp))
#        color_list = plt.cm.gist_rainbow(np.linspace(0, 1, num_communities))

        # blend the community colors (so that to-nodes are a mixture of all the communities they belong to)
#        rfrac,gfrac,bfrac=calc_community_fraction(Gsmall,Gsmall.nodes(),Gsmall.nodes(),partition,color_list)

        # save network in json format
#        nodes = Gsmall.nodes()
#        numnodes = len(nodes)
#        edges=Gsmall.edges(data=True)
#        numedges = len(edges)
        #nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n)} for n in nodes]
#        nodes_dict = [{"id":n,"com":col_temp[n],"degree":Gsmall.degree(n),
#                      "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]









        node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges

        edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]], "weight":edges[i][2]['weight']} for i in range(numedges)]

        #==========================================
        # Restore the correlation sign (+/-)
        #
        # create a list of edges that should be
        # negative using [source, target] format
        #==========================================
        edge_list_negative_values = [(node_map[edge_list_df['var1'][i]], node_map[edge_list_df['var2'][i]]) for i in idx_group if edge_list_df['corr'][i] < 0]

        for edge_dict_item in edges_dict:
            for e_neg in edge_list_negative_values:
                if(e_neg[0] == edge_dict_item['source'] and e_neg[1] == edge_dict_item['target']) or (e_neg[1] == edge_dict_item['source'] and e_neg[0] == edge_dict_item['target']):
                    edge_dict_item['weight'] = -1 * np.abs(edge_dict_item['weight'])

        import json
        json_graph = {"directed": False, "nodes": nodes_dict, "links":edges_dict}
        print 'Edge count: ' + str(len(edges_dict))

        client = pymongo.MongoClient()
        db = client.cache

        heat_maps = db.heat_map_graph

        a = {
            'clusterId': focal_group,
            'heat_map': json_graph#json.dumps(json_graph) #heat_map_ordered_transposed
        }

        #heat_maps.save(a)

        return a

        #json.dump(json_graph,open(save_file_name,'w'))

def calc_clustering_coefficient(G,cmap):
    # this function calculates the clustering coefficient of each node, and returns colors corresponding to these values
    local_CC = nx.clustering(G,G.nodes())
    local_CC_scale = [round(local_CC[key]*float(255)) for key in local_CC.keys()]
    local_CC_scale = pd.Series(local_CC_scale,index=G.nodes())
    rfrac = [cmap(int(x))[0] for x in local_CC_scale]
    gfrac = [cmap(int(x))[1] for x in local_CC_scale]
    bfrac = [cmap(int(x))[2] for x in local_CC_scale]
    rfrac = pd.Series(rfrac,index=G.nodes())
    gfrac = pd.Series(gfrac,index=G.nodes())
    bfrac = pd.Series(bfrac,index=G.nodes())

    return rfrac,gfrac,bfrac

def calc_betweenness_centrality(G,cmap):
    # this function calculates the betweenness centrality of each node, and returns colors corresponding to these values
    local_BC = nx.betweenness_centrality(G)
    local_BC_scale = [round(local_BC[key]*float(255)) for key in local_BC.keys()]
    local_BC_scale = pd.Series(local_BC_scale,index=G.nodes())
    rfrac = [cmap(int(x))[0] for x in local_BC_scale]
    gfrac = [cmap(int(x))[1] for x in local_BC_scale]
    bfrac = [cmap(int(x))[2] for x in local_BC_scale]
    rfrac = pd.Series(rfrac,index=G.nodes())
    gfrac = pd.Series(gfrac,index=G.nodes())
    bfrac = pd.Series(bfrac,index=G.nodes())

    return rfrac,gfrac,bfrac



# this function calculates fraction of to-node connections belonging to each community
def calc_community_fraction(G,to_nodes,from_nodes, from_nodes_partition, color_list):
    # set color to most populous community
    degree = G.degree(to_nodes)
    rfrac,gfrac,bfrac=pd.Series(index=G.nodes()),pd.Series(index=G.nodes()),pd.Series(index=G.nodes())
    for t in to_nodes:
        t_neighbors = G.neighbors(t)
        t_comms = [from_nodes_partition[i] for i in t_neighbors]
        t_comms = pd.Series(t_comms)

        unique_comms = t_comms.unique()
        num_unique_comms = len(unique_comms)

        num_n = pd.Series(index=unique_comms)
        for n in unique_comms:
            num_n[n] = sum(t_comms==n)

        # find max num_n
        color_max = color_list[num_n.argmax()][0:3]

        # how much is shared by other colors?
        #print(num_n)
        frac_shared = 1-np.max(num_n)/np.sum(num_n)

        # darken the color by this amount
        #color_dark = shade_color(color_max,-frac_shared*100)
        color_dark = (color_max[0]*(1-frac_shared), color_max[1]*(1-frac_shared), color_max[2]*(1-frac_shared))

        rfrac[t] = color_dark[0]
        gfrac[t] = color_dark[1]
        bfrac[t] = color_dark[2]

    # fill in the from_nodes colors
    for f in from_nodes:
        f_group = from_nodes_partition[f]
        rfrac[f] = color_list[f_group][0]
        gfrac[f] = color_list[f_group][1]
        bfrac[f] = color_list[f_group][2]



    return rfrac,gfrac,bfrac

def get_all_cluster_ids():
    search_body = {
        'fields': ['_id'],
        'query' : {
            'match_all': {}
        },
        'size': 70000
    }

    result = es.search(
        index = 'clusters',
        doc_type = 'clusters_tcga_louvain',
        body = search_body
    )

    print("Got %d Hits:" % result['hits']['total'])

    hit_ids = ''
    hit_ids_array = []
    for hit in result['hits']['hits']:
        hit_ids += '"' + hit['_id'] + '",'
        hit_ids_array.append(hit['_id'])


    if(len(hit_ids) > 0):
        hit_ids = hit_ids[:-1]


    of = open('all_cluster_ids.json', 'w')
    i = 0
    for cluster_id in hit_ids_array:
        of.write(cluster_id + '\n')


    of.write('\n')
    of.write('\n')
    of.write('\n')
    of.write('\n')
    of.write('\n')
    of.write('\n')
    of.write(hit_ids + '\n')

    of.close()

    #print hit_ids_array



def get_remaining_thumbnails():

    all_thumbs = [];
    with open("thumbs_master_list.txt", "r") as f:
      for line in f:
        all_thumbs.append(line)

    partial_thumbs = [];
    with open("thumbs_partial_list.txt", "r") as f:
      for line in f:
        partial_thumbs.append(line)



    #all_all = [set(all_thumbs), set(partial_thumbs)]

    leftovers = list(set(all_thumbs) - set(partial_thumbs))

    print len(leftovers)

    of = open('thumbnails_leftovers.txt', 'w')
    i = 0
    id_array_string = ''
    for cluster_id in leftovers:

        id_array_string += '"' + cluster_id.rstrip() + '",'

    of.write(id_array_string)
    of.close()


def transform_matrix_to_graph():
    my_matrix = [
    [-0.37340000000000001, 0.0, -0.37459999999999999, -0.39660000000000001, -0.4123, -0.36890000000000001],
    [0.0, 0.31709999999999999, 0.31340000000000001, 0.34210000000000002, 0.0, 0.32429999999999998],
    [-0.32690000000000002, -0.40189999999999998, 0.50939999999999996, 0.54959999999999998, 0.57179999999999997, 0.57179999999999997],
    [-0.31030000000000002, -0.41099999999999998, -0.38729999999999998, 0.0, -0.30990000000000001, 0.0],
    [0.30869999999999997, 0.0, 0.30330000000000001, 0.0, 0.0, 0.0, 0.34000000000000002, 0.0, 0.34210000000000002],
    [-0.43240000000000001, -0.3896, -0.39900000000000002, 0.74729999999999996, 0.85919999999999996, 0.78000000000000003]
    ]

    for d1 in my_matrix:
        for d2 in d1:
            d2 = 200 - d2 * 100


    my_matrix2 = [
        [1, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 1, 0],
        [1, 0, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 0],
        [1, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 0]
        ]

    A = np.array(my_matrix2)
    G = nx.DiGraph(A)

    x_nodes = ['A','B','C','D','E','F',]


def test_cluster_search_helper(expected_annotation):
    tr = TermAnalyzer()
    #expected_annotation = 'GO:0050877'
    client = pymongo.MongoClient()
    db = client.go

    go_search = db.genes

    go_search_found = go_search.find({'go': expected_annotation})

    query_genes = ''
    if go_search_found is not None:
        for go_gene in go_search_found:
            termsClassified = tr.identify_term(go_gene['gene'])

            for item_type in termsClassified:
                if(item_type['type'] == 'GENE'):
                    if('geneSymbol' in item_type):
                        termGeneSymbol = item_type['geneSymbol']
                        query_genes += termGeneSymbol.upper() + ','

    if(len(query_genes) > 0):
        query_genes = query_genes[0:-1]

    test_template = {
        'query_genes': query_genes,
        'expected_annotation': expected_annotation
    }

    search_results = get_cluster_search_mapped(query_genes, 99)

    print dumps(search_results)

    return_result = False;

    for search_tab in search_results:
        if(search_tab['searchTab'] == 'PATHWAYS'):
            if(expected_annotation in search_tab['annotation_filter_all_go_id']):
                return_result = True;
                print('found it')
                print search_tab['annotation_filter_all_go_id']
            else:
                return_result = False;
                print('No')
                print search_tab['annotation_filter_all_go_id']

    return return_result


