__author__ = 'aarongary'

from collections import Counter
from app import PubMed
from models.TermResolver import TermAnalyzer
from elasticsearch import Elasticsearch
from app import elastic_search_uri
from app import path_to_cluster_file
from app import path_to_DB_file
from app import util
import numpy as np
import networkx as nx
import pandas as pd
import community
import math
import matplotlib.pyplot as plt
import pymongo
import plotly.plotly as py
from plotly.graph_objs import *
from io import StringIO
from pandas import DataFrame
import hashlib
from bson.json_util import dumps
#from RestBroker import start_thumbnail_generator

import matplotlib.pyplot as plt
import matplotlib.colors as mpclrs
import seaborn
import random
import json
import time
from multiprocessing import Pool, cpu_count, Manager, Process
import copy
from random import randint
from app import HeatMaps

from ndex.networkn import NdexGraph
from ndex.client import Ndex

# latex rendering of text in graphs
import matplotlib as mpl
mpl.rc('text', usetex = False)
mpl.rc('font', family = 'serif')

import app.datascience.drug_gene_heatprop
import imp
imp.reload(app.datascience.drug_gene_heatprop)

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=30) # Prod Clustered Server

#============================
#============================
#      CLUSTER VIZ
#============================
#============================

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

    return 0

def get_heat_prop_cluster_viz(seed_genes, esId):
    seed_genes_array = seed_genes.split(',')
    es_id_array = esId.split(',')

    cluster_x_y_z = load_x_y_z_cluster_data(es_id_array[0])
    cluster_heatprop_targets = app.datascience.drug_gene_heatprop.cluster_genes_heatprop(seed_genes_array,cluster_x_y_z)
    if(len(cluster_heatprop_targets.edges()) > 3):
        print 'heat prop'
        main_data_tuples = []
        edge_list_negative_values = []
        for (u,v,d) in cluster_heatprop_targets.edges(data=True):
            main_data_tuples.append((u, v, np.abs(d['weight'])))
            if(d['weight'] < 0):
                edge_list_negative_values.append(u, v)

        result = generate_graph_from_tab_file(main_data_tuples, edge_list_negative_values, 'temp', esId, 'clustering_coefficient') #'community')

        return result['heat_map']
    else:
        print 'no heat prop'
        return get_heatmap_graph_from_es_by_id(es_id_array[0], seed_genes, 'clusters_tcga_louvain', 0.5)

def get_heat_prop_from_gene_list_by_cluster_source(seed_genes, cluster_x_y_z):
    seed_genes_array = seed_genes.split(',')

    gene_drug_df = app.datascience.drug_gene_heatprop.drug_gene_heatprop(seed_genes_array,cluster_x_y_z,plot_flag=False)

    #print gene_drug_df.head(25)

    gene_drug_json = gene_drug_df.reset_index().to_dict(orient='index')

    return gene_drug_json

def get_drugbank_name(db_id, drugbank_mongo_collection):
    drug_bank_found = drugbank_mongo_collection.find_one({'drug_bank_id': db_id})
    drug_bank_desc = ''
    if(drug_bank_found is not None):
        drug_bank_desc = drug_bank_found['drug_desc']
    else:
        drug_bank_desc = db_id

    return drug_bank_desc

def experiment_1(seed_genes, esIds):
    computed_hash = util.compute_query_list_hash(seed_genes)
    #print computed_hash

    return_value_array = []

    client = pymongo.MongoClient()
    db = client.identifiers
    drugbank_collection = db.drugbank
    inferred_drug_search = db.inferred_drug_search

    inferred_drug_search = client.cache.inferred_drug_search

    inferred_drug_search_found = inferred_drug_search.find_one({'searchId': computed_hash})

    if(inferred_drug_search_found is not None):
        return_value_array = inferred_drug_search_found['cached_hits']
    else:
        seed_genes_array = seed_genes.split(',')
        es_id_array = esIds.split(',')

        start_time = time.time()
        print 'Start: ' + str(start_time)
        print '-'
        print '-'
        print '-'
        #================================
        # Run the heat prop in parallel
        #================================
        #manager = Manager()
        #return_dict = manager.dict()
        #jobs = []
        #for es_id in es_id_array:
        #    p = Process(target=get_heat_prop_from_es_id, args=(es_id, seed_genes_array, False, return_dict))
        #    jobs.append(p)
        #    p.start()

        #for proc in jobs:
        #    proc.join()

        #inferred_drug_group_array = return_dict.values()
        return_dict = []

        inferred_drug_group_array = {}
        count = 0
        for es_id in es_id_array:
            # Due to bugs when calling ElasticSearch from Process we are
            # just running the first 2 clusters in serial
            if(count > 1):
                if(len([rd for rd in return_dict if rd is not None]) > 1):
                    break;
            return_dict.append(get_heat_prop_from_es_id(es_id, seed_genes_array, False, None))
            count += 1

        inferred_drug_group_array = [rd for rd in return_dict if rd is not None]

        if(len(inferred_drug_group_array) < 1):
            return [
                {
                    "disease_type": "No results",
                    "genes": [
                    "NONE"
                    ],
                    "gene_count": 1,
                    "value": [
                    {
                      "drug_name": "n/a",
                      "gene": "NONE",
                      "doc_id": "0",
                      "drug_id": "DB00000"
                    }
                    ],
                    "heat_value": 0.004182,
                    "key": "No results",
                    "es_id": "2040020397",
                    "drug_bank_id": "DB00000",
                    "diseases_with_rank": [
                    {
                      "disease": "No results",
                      "rank": 18
                    }
                    ],
                    "heat_rank": 18
                    }
            ]

        #print dumps(inferred_drug_group_array)

        merged_by_rank = []
        annotate_cluster_info = {}
        for a in inferred_drug_group_array:
            for b in a['inferred_drugs']:
                found_match = False
                for c in merged_by_rank:
                    if(c['drug_bank_id'] == b['drug_bank_id']):
                        disease_type_found = False
                        for d in c['diseases_with_rank']:
                            if(d['disease'] == b['disease_type']):
                                disease_type_found = True
                        if(not disease_type_found):
                            c['diseases_with_rank'].append(
                                {
                                    'disease': b['disease_type'],
                                    'rank': b['heat_rank']
                                }
                            )

                        found_match = True

                if(not found_match):
                    b1 =  copy.deepcopy(b)
                    b1['diseases_with_rank'] = [
                        {
                            'disease': b1['disease_type'],
                            'rank': b1['heat_rank']
                        }
                    ]
                    merged_by_rank.append(b1)

            annotate_cluster_info[a['es_id']] = a['annotate_cluster_data']


        return_value_array = {'inferred_drugs': merged_by_rank, 'annotate_cluster_info': annotate_cluster_info} #return_dict.values()

        print '-'
        print '-'
        print '-'
        print 'Finished: ' + str(start_time - time.time())

        inferred_drug_search.save(
            {
                'searchId': computed_hash,
                'cached_hits': return_value_array
            }
        )

    client.close()

    return return_value_array

def get_heat_prop_from_gene_list_loop(seed_genes, esIds):
    seed_genes_array = seed_genes.split(',')
    es_id_array = esIds.split(',')
    return_value_array = []

    start_time = time.time()
    print 'Start: ' + str(start_time)
    print '-'
    print '-'
    print '-'

    for es_id in es_id_array:
        return_value = get_heat_prop_from_es_id(es_id, seed_genes_array)

        if(return_value is not None):
            return return_value

    print '-'
    print '-'
    print '-'
    print 'Finished: ' + str(start_time - time.time())
    return return_value_array


def get_heat_prop_from_es_id(es_id, seed_genes_array, include_evidence_graph=False, return_dict=None):
    client = pymongo.MongoClient()
    db = client.identifiers
    drugbank_collection = db.drugbank

    print es_id

    disease_type = get_cluster_disease_by_es_id(es_id)

    cluster_data = load_x_y_z_cluster_data(es_id)
    cluster_x_y_z = cluster_data['cluster']
    print 'start heat prop'
    gene_drug_df = app.datascience.drug_gene_heatprop.drug_gene_heatprop(seed_genes_array,cluster_x_y_z,plot_flag=False)
    print 'finish heat prop'

    gene_drug_json = gene_drug_df.reset_index().to_dict(orient='index')
    #print dumps(gene_drug_json)

    one_gene_many_drugs = []
    hot_genes = []
    hot_genes_with_heat_value = []
    hot_genes_values = []
    annotate_cluster_data = []
    annotate_cluster_min = 9999
    annotate_cluster_max = 0


    for key, value in gene_drug_json.iteritems():

        if(len(value['drugs']) > 0 and value['index'] not in seed_genes_array):
            if(value['heat_value'] > 0.00001):
                one_gene_many_drugs.append({
                    'gene': value['index'],
                    'drugs': value['drugs'],
                    'heat_value': float("{0:f}".format(value['heat_value'])),
                    'heat_rank': value['heat_rank']
                })

        annotate_cluster_data.append({
            'gene': value['index'],
            'drugable': len(value['drugs']) > 0,
            'heat_value': value['heat_value']
        })

        if(value['heat_value'] < annotate_cluster_min):
            annotate_cluster_min = value['heat_value']

        if(value['heat_value'] > annotate_cluster_max):
            annotate_cluster_max = value['heat_value']

        if(value['heat_value'] > 0.00001):
            hot_genes.append(value['index'])
            drugs_array_desc = []
            drugs_for_pop_up = ''

            node_info_for_pop_up = ''#'<span style="font-weight: bold; margin-bottom: 5px;">Drugs associated with ' + str(value['index']) + ':</span><br><div style="margin-left: 10px;">'

            for drug_id in value['drugs']:
                drugs_array_desc.append(get_drugbank_name(drug_id, drugbank_collection))
                drugs_for_pop_up += get_drugbank_name(drug_id, drugbank_collection) + '\n'
                node_info_for_pop_up += get_drugbank_name(drug_id, drugbank_collection) + '<br>'

            node_info_for_pop_up += '</div>'

            #print 'gene_id: ' + value['index'] + ' heat: ' + str(value['heat_value'] * 100000)
            if(value['index'] not in seed_genes_array):
                hot_genes_values.append(value['heat_value'] * 100000)
                hot_genes_with_heat_value.append(
                    {
                        'gene_id': value['index'],
                        'heat_value': value['heat_value'] * 100000,
                        'drugable': len(drugs_for_pop_up) > 0,
                        'seed_gene': False,
                        'drugs': 'do not use',#value['index'] + '\nDrugs targeting this gene:\n\n' + drugs_for_pop_up,
                        'node_info': value['index'],
                        'pop_up_info': node_info_for_pop_up
                    }
                )
            else:
                hot_genes_with_heat_value.append(
                    {
                        'gene_id': value['index'],
                        'heat_value': value['heat_value'] * 100000,
                        'drugable': len(drugs_for_pop_up) > 0,
                        'seed_gene': True,
                        'drugs': 'do not use',#value['index'] + '\n[SEED GENE]\nFor drugs that are directly \ntargeting this query gene \nsee results above', # This is a seed gene.  We are not showing direct drugs only inferred drugs.
                        'node_info': value['index'],
                        'pop_up_info': node_info_for_pop_up
                    }
                )

        else:
            hot_genes_with_heat_value.append(
                {
                    'gene_id': value['index'],
                    'seed_gene': False, # seed genes are intrinsically hot
                    'heat_value': 0.0
                }
            )


        #print annotate_cluster_min
        #annotate_cluster_min = math.log(annotate_cluster_min)
        #annotate_cluster_max = math.log(annotate_cluster_max)

    if((annotate_cluster_max > annotate_cluster_min) and (annotate_cluster_max > 0)):
        for annotate_item in annotate_cluster_data:
            annotate_item['normalized_heat'] = (((annotate_item['heat_value']) * 1.0) - (annotate_cluster_min * 1.0)) / ((annotate_cluster_max * 1.0) - (annotate_cluster_min * 1.0))
    else:
        for annotate_item in annotate_cluster_data:
            annotate_item['normalized_heat'] = 1.0


    if(len(hot_genes_values) < 1):
        max_hot_genes_value = 0
    else:
        max_hot_genes_value = max(hot_genes_values)

    #========================================
    # Results are one to many with drugname
    # as the key.  We need to group by gene
    #========================================
    if(len(one_gene_many_drugs) < 2):
        return None
    else:
        one_drug_many_genes = []
        for gene_drugs in one_gene_many_drugs:
            found_drug = False
            for drug in gene_drugs['drugs']:
                for match_this_drug in one_drug_many_genes:
                    if(drug == match_this_drug['drug_bank_id']):
                        drug_bank_desc = get_drugbank_name(drug, drugbank_collection)

                        match_this_drug['genes'].append(gene_drugs['gene'])
                        max_heat_map_value = match_this_drug['heat_value']
                        if(gene_drugs['heat_value'] > max_heat_map_value):
                            max_heat_map_value = gene_drugs['heat_value']
                        max_heat_rank_value = match_this_drug['heat_rank']
                        if(gene_drugs['heat_rank'] > max_heat_rank_value):
                            max_heat_rank_value = gene_drugs['heat_rank']
                        match_this_drug['gene_count'] += 1
                        match_this_drug['heat_value'] = max_heat_map_value
                        match_this_drug['heat_rank'] = max_heat_rank_value
                        match_this_drug['value'].append({
                                'drug_name': drug_bank_desc,
                                'gene': gene_drugs['gene'],
                                'doc_id': '0',
                                'drug_id': drug
                            })
                        found_drug = True

                        break

                if(not found_drug):
                    drug_bank_desc = get_drugbank_name(drug, drugbank_collection)

                    one_drug_many_genes.append({
                            'drug_bank_id': drug,
                            'heat_value': float("{0:f}".format(gene_drugs['heat_value'])),
                            'heat_rank': gene_drugs['heat_rank'],
                            'genes': [gene_drugs['gene']],
                            'value': [
                                {
                                    'drug_name': drug_bank_desc,
                                    'gene': gene_drugs['gene'],
                                    'doc_id': '0',
                                    'drug_id': drug
                                }
                            ],
                            'key': drug_bank_desc,
                            'gene_count': 1,
                            'disease_type': disease_type,
                            'es_id': es_id
                        })

        top_drugs_sorted_list = one_drug_many_genes #sorted(one_drug_many_genes, key=lambda k: k['gene_count'])

        H = cluster_x_y_z.subgraph(hot_genes)

        nodes = H.nodes()
        numnodes = len(nodes)
        edges=H.edges(data=True)
        numedges = len(edges)

        print 'Edges len: ' + str(len(edges))

        color_list = plt.cm.OrRd(np.linspace(0, 1, 100))

        inferred_drug_graph = {
            'directed':False,
            'nodes':[],
            'links':[]
        }

        if(include_evidence_graph):
            nodes_dict = []
            log_norm_value = mpclrs.LogNorm(0, max_hot_genes_value, clip=False)
            for n in nodes:
                found_hot_gene = False
                for hv in hot_genes_with_heat_value:
                    if(hv['gene_id'] == n):
                        color_list_index = math.ceil((hv['heat_value']/max_hot_genes_value) * 100) - 1
                        font_color = 'black'
                        if(color_list_index > 99):
                            color_list_index = 99

                        if(color_list_index > 40):
                            font_color = 'white'

                        if(hv['drugable']):
                            nodes_dict.append({"id":n,"com":0, "node_type": "DRUGABLE", "drugs": hv['drugs'], 'node_info': hv['node_info'], 'pop_up_info': hv['pop_up_info'], 'seed_gene': hv['seed_gene'], 'font_color': font_color, "degree":H.degree(n),"rfrac":int(color_list[color_list_index][0] * 255),"gfrac":int(color_list[color_list_index][1] * 255),"bfrac":int(color_list[color_list_index][2] * 255)} )
                        else:
                            nodes_dict.append({"id":n,"com":0, "node_type": "NORMAL", "drugs": [], 'node_info': hv['node_info'], 'pop_up_info': 'No drugs available for this gene', 'seed_gene': hv['seed_gene'], 'font_color': font_color, "degree":H.degree(n),"rfrac":int(color_list[color_list_index][0] * 255),"gfrac":int(color_list[color_list_index][1] * 255),"bfrac":int(color_list[color_list_index][2] * 255)} )
                        found_hot_gene = True
                        break

                if(not found_hot_gene):
                    nodes_dict.append({"id":n,"com":0,"degree":H.degree(n),"rfrac":color_list[0][0] * 255,"gfrac":color_list[0][1] * 255,"bfrac":color_list[0][2] * 255} )

            node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges

            edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]], "weight":edges[i][2]['weight']} for i in range(numedges)]

            inferred_drug_graph = {
                'directed':False,
                'nodes':nodes_dict,
                'links':edges_dict
            }

        if(return_dict is not None):
            return_dict[es_id] = es_id

        if(top_drugs_sorted_list is not None):
            if(len(top_drugs_sorted_list) >= 25):
                if(return_dict is not None):
                    return_dict[es_id] = {'inferred_drugs': top_drugs_sorted_list[:24], 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type, 'annotate_cluster_data': annotate_cluster_data, 'es_id': es_id}
                return {'inferred_drugs': top_drugs_sorted_list[:24], 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type, 'annotate_cluster_data': annotate_cluster_data, 'es_id': es_id}
            else:
                if(return_dict is not None):
                    return_dict[es_id] = {'inferred_drugs': top_drugs_sorted_list, 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type, 'annotate_cluster_data': annotate_cluster_data, 'es_id': es_id}
                return {'inferred_drugs': top_drugs_sorted_list, 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type, 'annotate_cluster_data': annotate_cluster_data, 'es_id': es_id}
        else:
            if(return_dict is not None):
                return_dict[es_id] = {'inferred_drugs': [{'nodes': [], 'edges':[]}], 'evidence_graph': {'directed':False,'nodes':[],'links':[]}, 'disease_type': disease_type, 'annotate_cluster_data': annotate_cluster_data, 'es_id': es_id}
            return {'inferred_drugs': [{'nodes': [], 'edges':[]}], 'evidence_graph': {'directed':False,'nodes':[],'links':[]}, 'disease_type': disease_type, 'annotate_cluster_data': annotate_cluster_data, 'es_id': es_id}

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

def get_heat_prop_from_gene_list(seed_genes, esId):
    seed_genes_array = seed_genes.split(',')
    es_id_array = esId.split(',')
    top_drugs_sorted_list = None

    for es_id in es_id_array:
        cluster_x_y_z = load_x_y_z_cluster_data(es_id)
        gene_drug_df = app.datascience.drug_gene_heatprop.drug_gene_heatprop(seed_genes_array,cluster_x_y_z,plot_flag=False)

        #print gene_drug_df.head(25)

        gene_drug_json = gene_drug_df.reset_index().to_dict(orient='index')

        one_gene_many_drugs = []
        for key, value in gene_drug_json.iteritems():
            if(len(value['drugs']) > 0):
                one_gene_many_drugs.append({
                    'gene': value['index'],
                    'drugs': value['drugs'],
                    'heat_value': value['heat_value']
                })

        #=========================================
        # Results are "one to many" with drugname
        # as the key.  We need to group by gene
        #=========================================
        client = pymongo.MongoClient()
        db = client.identifiers
        drugbank_collection = db.drugbank

        one_drug_many_genes = []
        for gene_drugs in one_gene_many_drugs:
            found_drug = False
            for drug in gene_drugs['drugs']:
                for match_this_drug in one_drug_many_genes:
                    if(drug == match_this_drug['drug_bank_id']):
                        drug_bank_found = drugbank_collection.find_one({'drug_bank_id': drug})
                        drug_bank_desc = ''
                        if(drug_bank_found is not None):
                            drug_bank_desc = drug_bank_found['drug_desc']
                        else:
                            drug_bank_desc = drug

                        match_this_drug['genes'].append(gene_drugs['gene'])
                        max_heat_map_value = match_this_drug['heat_value']
                        if(gene_drugs['heat_value'] > max_heat_map_value):
                            max_heat_map_value = gene_drugs['heat_value']
                        match_this_drug['gene_count'] += 1
                        match_this_drug['heat_value'] = max_heat_map_value
                        match_this_drug['value'].append({
                                'drug_name': drug_bank_desc,
                                'gene': gene_drugs['gene'],
                                'doc_id': '0',
                                'drug_id': drug
                            })
                        found_drug = True
                        break

                if(not found_drug):
                    drug_bank_found = drugbank_collection.find_one({'drug_bank_id': drug})
                    drug_bank_desc = ''
                    if(drug_bank_found is not None):
                        drug_bank_desc = drug_bank_found['drug_desc']
                    else:
                        drug_bank_desc = drug

                    one_drug_many_genes.append({
                            'drug_bank_id': drug,
                            'heat_value': gene_drugs['heat_value'],
                            'genes': [gene_drugs['gene']],
                            'value': [
                                {
                                    'drug_name': drug_bank_desc,
                                    'gene': gene_drugs['gene'],
                                    'doc_id': '0',
                                    'drug_id': drug
                                }
                            ],
                            'key': drug_bank_desc,
                            'gene_count': 1
                        })

    #                    {
    #                    'drug': drug,
    #                    'genes': [gene_drugs['gene']],
    #                    'drug_bank_desc': drug_bank_desc
    #                })

        top_drugs_sorted_list = sorted(one_drug_many_genes, key=lambda k: k['gene_count'])

    #print top_drugs_sorted_list[-15:]

    #print dumps(one_drug_many_genes)
    return_value = []

    return top_drugs_sorted_list[-25:]

def get_heatmap_graph_from_es_by_id(elasticId, gene_list, search_type, cut_off_filter_value):
    filter_count_setting1 = 400
    client = pymongo.MongoClient()
    db = client.cache

    gene_list_array = gene_list.split(',')

    query_list_found = []

    x_edge_overlap = []
    y_edge_overlap = []

    x_edge_non_overlap = []
    y_edge_non_overlap = []

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
#            doc_type = search_type,
            body = search_body
        )

        if(len(results['hits']['hits']) > 0):
            result = results['hits']['hits'][0]['_source']

            #if(result['correlation_matrix_degree'] > 300000):
            if(len(result['correlation_matrix']) < 1):
                resultx = {
                    'directed':False,
                    'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                    'links':[{'source':0,'target':1,'weight':1}]
                }

                return resultx

            calculated_cut_off = 0.5
            #if(len(result['correlation_matrix']) > 1000):
            #    calculated_cut_off = 0.87
            #else:
            #    calculated_cut_off = 0.5 + (0.37 * (len(result['correlation_matrix'])/1000))

            cluster_IO = "corr	group_id	p	var1	var2 \n"

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
            print calculated_cut_off

            #=================================
            # GET QUERY LIST OVERLAP
            #=================================
            for gene_list_item in gene_list_array:
                x_node_index = findIndexByKeyValue(result['x_node_list'], 'name', gene_list_item)
                y_node_index = findIndexByKeyValue(result['y_node_list'], 'name', gene_list_item)
                if(x_node_index >= 0):
                    query_list_found.append(gene_list_item + '_' + result['x_node_list_type'])
                else:
                    if(y_node_index >= 0):
                        query_list_found.append(gene_list_item + '_' + result['y_node_list_type'])
                        x_edge_overlap.append(x_node_index)

                #===================================
                # GET QUERY LIST OVERLAP FOR EDGES
                # i.e. EDGE INDEX from:0 to:1
                #===================================
                if(x_node_index >= 0):
                    x_edge_overlap.append(x_node_index)

                if(y_node_index >= 0):
                    y_edge_overlap.append(y_node_index)


            #===================================
            # GENERATE NODES & EDGES DATAFRAME
            # BASED ON EDGE CUT_OFF
            #===================================
            main_data_tuples = []
            all_data_tuples = []
            query_nodes_data_tuples = []
            subG_nodes_data_tuples = []
            found_x_query_node_edge = []
            found_y_query_node_edge = []
            core_nodes = []
            edge_counter = 0

            edge_list_negative_values = []
            for correlation_record in result['correlation_matrix']:
                correlation_value = correlation_record['correlation_value']
                all_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
                if( (abs(correlation_value) >= calculated_cut_off) and edge_counter < filter_count_setting1): #150):
                    edge_counter += 1
                    #if(edge_counter % 20 == 0):
                    #    print edge_counter
                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))

                    if(result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'] not in core_nodes):
                        core_nodes.append(result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'])
                    if(result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'] not in core_nodes):
                        core_nodes.append(result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'])

                    if(correlation_value < 0):
                        edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))
                else:
                    if((correlation_record['x_loc'] in x_edge_overlap) or (correlation_record['y_loc'] in y_edge_overlap)):
                        #edge_counter += 1
                        #if(edge_counter % 20 == 0):
                        #    print edge_counter
                        #main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'], result['y_node_list'][correlation_record['y_loc']]['name'], np.abs(correlation_record['correlation_value'])))
                        query_nodes_data_tuples.append(correlation_record)
                        if(correlation_value < 0):
                            edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))

            print 'main_data_tuples: ' + str(len(main_data_tuples))

            for correlation_record in query_nodes_data_tuples:
                correlation_value = correlation_record['correlation_value']
                if((correlation_record['x_loc'] in x_edge_overlap) and (correlation_record['x_loc'] not in found_x_query_node_edge)):
                    found_x_query_node_edge.append(correlation_record['x_loc'])
                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))

                if((correlation_record['y_loc'] in y_edge_overlap) and (correlation_record['y_loc'] not in found_y_query_node_edge)):
                    found_y_query_node_edge.append(correlation_record['y_loc'])
                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))

            #===============================
            # CUTOFF was too stringent.
            # no edges produced.  Recompute
            #===============================
            #if(len(data['corr']) < 1):
            if(len(main_data_tuples) < 1):
                for correlation_record in result['correlation_matrix']:
                    correlation_value = correlation_record['correlation_value']
                    if((abs(correlation_value) >= 0.5)):
                        main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['y_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
                        if(correlation_value < 0):
                            edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))

            #subG = nx.Graph()
            #subG.add_nodes_from()
            #subG.add_weighted_edges_from(main_data_tuples)
            #subG_minimum = nx.minimum_spanning_tree(subG)
            #subG_nodes = subG.nodes()
            #mainG = nx.Graph()
            #mainG.add_weighted_edges_from(all_data_tuples)

            #main_subG = mainG.subgraph(subG_nodes)
            #for edges_subG in subG_minimum.edges(data=True):
            #    subG_nodes_data_tuples.append((edges_subG[0], edges_subG[1], edges_subG[2]['weight']))

            result = generate_graph_from_tab_file(main_data_tuples, edge_list_negative_values, gene_list_array, elasticId, 'clustering_coefficient')
            #result = generate_graph_from_tab_file(subG_nodes_data_tuples, edge_list_negative_values, gene_list_array, elasticId, 'community')

            #================================
            # INSERT QUERY NODE IF NOT FOUND
            # IN RESULTING NETWORK
            #================================
            for xy_item in query_list_found:
                foundItem = False
                for node in result['heat_map']['nodes']:
                    if(node['id'] == xy_item):
                        foundItem = True
                        break

                if(not foundItem):
                    result['heat_map']['nodes'].append(
                        {
                          'bfrac': 207,
                          'degree': 0,
                          'gfrac': 120,
                          'rfrac': 0,
                          'com': 999,
                          'id': xy_item
                        }
                    )

            return result['heat_map']
        else:
            result = {
                'directed':False,
                'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                'links':[{'source':0,'target':1,'weight':1}]
            }

            return result

        print("Got %d Hits:" % results['hits']['total'])

        if(results['hits']['total'] < 1):
            print 'no results'

    #return return_value

def filter_edges_to_tuples(result, calculated_cut_off, x_edge_overlap, y_edge_overlap, number_of_edges, for_heat_prop_use=False):
    main_data_tuples = []
    all_data_tuples = []
    query_nodes_data_tuples = []
    edge_counter = 0
    non_core_counts = {}
    edge_list_negative_values = []
    #calculated_cut_off = 0.5

    for correlation_record in result['correlation_matrix']:
        correlation_value = correlation_record['correlation_value']
        all_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
        if( (abs(correlation_value) >= calculated_cut_off) and edge_counter < number_of_edges):
            main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
            edge_counter += 1
            #print 'Core: ' + str(edge_counter) + ' out of ' + str(number_of_edges)
            if(correlation_value < 0):
                edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))
        else:
            if((correlation_record['x_loc'] in x_edge_overlap) or (correlation_record['y_loc'] in y_edge_overlap)):
                max_reached = False
                if(correlation_record['x_loc'] in non_core_counts):
                    non_core_counts[correlation_record['x_loc']] += 1
                    if((non_core_counts[correlation_record['x_loc']] > 10) and not for_heat_prop_use):
                        max_reached = True
                elif(correlation_record['y_loc'] in non_core_counts):
                    non_core_counts[correlation_record['y_loc']] += 1
                    if(non_core_counts[correlation_record['y_loc']] > 10 and not for_heat_prop_use):
                        max_reached = True

                elif((correlation_record['x_loc'] in x_edge_overlap)):
                    non_core_counts[correlation_record['x_loc']] = 1
                elif((correlation_record['y_loc'] in y_edge_overlap)):
                    non_core_counts[correlation_record['y_loc']] = 1

                #print 'Non-core: ' + str(edge_counter)
                if(not max_reached):
                    edge_counter += 1
                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
                    query_nodes_data_tuples.append(correlation_record)
                    if(correlation_value < 0):
                        edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))

    return_obj = {
        'main_data_tuples': main_data_tuples,
        'edge_list_negative_values': edge_list_negative_values,
        'all_data_tuples': all_data_tuples
    }


    #print dumps(non_core_counts)
    return return_obj


def get_heatmap_graph_from_es_by_id_using_neighbors(elasticId, gene_list, number_of_edges = 200):

    client = pymongo.MongoClient()
    db = client.cache

    gene_list_array = gene_list.split(',')

    query_list_found = []

    x_edge_overlap = []
    y_edge_overlap = []
    cluster_annotations = []

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
#            doc_type = search_type,
            body = search_body
        )

        if(len(results['hits']['hits']) > 0):
            result = results['hits']['hits'][0]['_source']
            cluster_annotations = result['hypergeometric_scores']

            if(len(result['correlation_matrix']) < 1):
                resultx = {
                    'directed':False,
                    'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                    'links':[{'source':0,'target':1,'weight':1}],
                    'annotations': []
                }

                return resultx

            total_edges = len(result['correlation_matrix'])
            calculated_cut_off = get_top_200_weight(result['correlation_matrix'], number_of_edges)
            print calculated_cut_off

            #=================================
            # GET QUERY LIST OVERLAP
            #=================================
            for gene_list_item in gene_list_array:
                if(gene_list_item == 'WEE1'):
                    my_test_str = ''
                x_node_index = findIndexByKeyValue(result['x_node_list'], 'name', gene_list_item)
                y_node_index = findIndexByKeyValue(result['y_node_list'], 'name', gene_list_item)
                if(x_node_index >= 0):
                    query_list_found.append(gene_list_item)
                else:
                    if(y_node_index >= 0):
                        query_list_found.append(gene_list_item)
                        x_edge_overlap.append(x_node_index)

                #===================================
                # GET QUERY LIST OVERLAP FOR EDGES
                # i.e. EDGE INDEX from:0 to:1
                #===================================
                if(x_node_index >= 0):
                    x_edge_overlap.append(x_node_index)

                if(y_node_index >= 0):
                    y_edge_overlap.append(y_node_index)

            #===========================
            # GENERATE NODES EXPRESSION
            # DICTIONARY
            #===========================
            node_expression_dict = {}
            expression_value_list = []
            for x_node_item in result['x_node_list']:
                node_expression_dict[x_node_item['name']] =  x_node_item['value']
                expression_value_list.append(x_node_item['value'])

            for y_node_item in result['y_node_list']:
                if(y_node_item['name'] not in node_expression_dict):
                    node_expression_dict[y_node_item['name']] =  y_node_item['value']
                    expression_value_list.append(x_node_item['value'])

            expression_max = max(expression_value_list)
            expression_min = min(expression_value_list)

            #===================================
            # GENERATE NODES & EDGES DATAFRAME
            # BASED ON EDGE CUT_OFF
            #===================================
            filtered_graph_data = filter_edges_to_tuples(result, calculated_cut_off, x_edge_overlap, y_edge_overlap, number_of_edges, for_heat_prop_use=True)

            main_data_tuples = filtered_graph_data['main_data_tuples']#[]
            all_data_tuples = filtered_graph_data['all_data_tuples']#[]
            query_nodes_data_tuples = []
            edge_counter = 0
            non_core_counts = {}
            edge_list_negative_values = filtered_graph_data['edge_list_negative_values']#[]

#            for correlation_record in result['correlation_matrix']:
#                correlation_value = correlation_record['correlation_value']
#                all_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
#                if( (abs(correlation_value) >= calculated_cut_off) and edge_counter < number_of_edges):
#                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
#                    edge_counter += 1
#                    #print 'Core: ' + str(edge_counter)
#                    if(correlation_value < 0):
#                        edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))
#                else:
#                    if((correlation_record['x_loc'] in x_edge_overlap) or (correlation_record['y_loc'] in y_edge_overlap)):
#                        max_reached = False
#                        if(correlation_record['x_loc'] in non_core_counts):
#                            non_core_counts[correlation_record['x_loc']] += 1
#                            if(non_core_counts[correlation_record['x_loc']] > 10):
#                                max_reached = True
#                        elif(correlation_record['y_loc'] in non_core_counts):
#                            non_core_counts[correlation_record['y_loc']] += 1
#                            if(non_core_counts[correlation_record['y_loc']] > 10):
#                                max_reached = True

#                        elif((correlation_record['x_loc'] in x_edge_overlap)):
#                            non_core_counts[correlation_record['x_loc']] = 1
#                        elif((correlation_record['y_loc'] in y_edge_overlap)):
#                            non_core_counts[correlation_record['y_loc']] = 1

                        #print 'Non-core: ' + str(edge_counter)
#                        if(not max_reached):
#                            edge_counter += 1
#                            main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
##                            query_nodes_data_tuples.append(correlation_record)
#                            if(correlation_value < 0):
#                                edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))
            #print dumps(non_core_counts)

            print 'main_data_tuples: ' + str(len(main_data_tuples))

#            for correlation_record in query_nodes_data_tuples:
#                correlation_value = correlation_record['correlation_value']
#                if((correlation_record['x_loc'] in x_edge_overlap) and (correlation_record['x_loc'] not in found_x_query_node_edge)):
#                    found_x_query_node_edge.append(correlation_record['x_loc'])
#                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'], result['y_node_list'][correlation_record['y_loc']]['name'], np.abs(correlation_record['correlation_value'])))#

#                if((correlation_record['y_loc'] in y_edge_overlap) and (correlation_record['y_loc'] not in found_y_query_node_edge)):
#                    found_y_query_node_edge.append(correlation_record['y_loc'])
#                    main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'], result['y_node_list'][correlation_record['y_loc']]['name'], np.abs(correlation_record['correlation_value'])))

            #===============================
            # CUTOFF was too stringent.
            # no edges produced.  Recompute
            #===============================
            if(len(main_data_tuples) < 1):
                for correlation_record in result['correlation_matrix']:
                    correlation_value = correlation_record['correlation_value']
                    if((abs(correlation_value) >= 0.5)):
                        main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type'], np.abs(correlation_record['correlation_value'])))
                        if(correlation_value < 0):
                            edge_list_negative_values.append((result['x_node_list'][correlation_record['x_loc']]['name'] + '_' + result['x_node_list_type'], result['y_node_list'][correlation_record['y_loc']]['name'] + '_' + result['y_node_list_type']))

            mainG = nx.Graph()
            mainG.add_weighted_edges_from(all_data_tuples)

            adjacency_matrix = nx.adjacency_matrix(mainG)


            for neighbor_edges in mainG.edges_iter(gene_list_array, data=True):
                main_data_tuples.append((neighbor_edges[0],neighbor_edges[1],neighbor_edges[2]['weight']))

            result = generate_graph_from_tab_file(main_data_tuples, edge_list_negative_values, gene_list_array, elasticId, 'clustering_coefficient')

            result['heat_map']['filter_message'] = 'Showing top %d edges out of %d' % (len(result['heat_map']['links']), total_edges)
            result['heat_map']['annotations'] = cluster_annotations

            #================================
            # INSERT QUERY NODE IF NOT FOUND
            # IN RESULTING NETWORK
            #================================
            for xy_item in query_list_found:
                foundItem = False
                for node in result['heat_map']['nodes']:
                    if(node['id'].replace('_g', '').replace('_v', '').replace('_m', '') == xy_item):
                        foundItem = True
                        break

                if(not foundItem):
                    result['heat_map']['nodes'].append(
                        {
                          'bfrac': 207,
                          'degree': 0,
                          'gfrac': 120,
                          'rfrac': 0,
                          'com': 999,
                          'id': xy_item
                        }
                    )


            #================================
            # ADD EXPRESSION VALUE TO THE
            # NODES (Normalize)
            #================================
            for node in result['heat_map']['nodes']:
                if(node['id'].replace('_g', '').replace('_v', '').replace('_m', '') in node_expression_dict):
                    if(expression_max != expression_min):
                        node['expression_value'] = (node_expression_dict[node['id'].replace('_g', '').replace('_v', '').replace('_m', '')] - expression_min)/ (expression_max - expression_min)
                    else:
                        node['expression_value'] = 1.0

            return result['heat_map']
        else:
            result = {
                'directed':False,
                'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                'links':[{'source':0,'target':1,'weight':1}],
                'annotations':[]
            }

            return result

        print("Got %d Hits:" % results['hits']['total'])

        if(results['hits']['total'] < 1):
            print 'no results'

    #return return_value

def get_heatmap_graph_from_es_by_id_no_processing(elasticId, gene_list):

    client = pymongo.MongoClient()
    db = client.cache

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
#            doc_type = search_type,
            body = search_body
        )

        if(len(results['hits']['hits']) > 0):
            result = results['hits']['hits'][0]['_source']

            #if(result['correlation_matrix_degree'] > 300000):
            if(len(result['correlation_matrix']) < 1):
                resultx = {
                    'directed':False,
                    'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                    'links':[{'source':0,'target':1,'weight':1}]
                }

                return resultx

            #===================================
            # GENERATE NODES & EDGES DATAFRAME
            # BASED ON EDGE CUT_OFF
            #===================================
            main_data_tuples = []

            edge_list_negative_values = []
            for correlation_record in result['correlation_matrix']:
                correlation_value = correlation_record['correlation_value']
                main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'], result['y_node_list'][correlation_record['y_loc']]['name'], correlation_record['correlation_value']))

            Gsmall = nx.Graph()

            Gsmall.add_weighted_edges_from(main_data_tuples)

            cluster_edges = Gsmall.edges(data=True)
            cluster_nodes = Gsmall.nodes()
            cluster_edges_array = []
            cluster_data_frame = 'source\t target\t weight\n'
            for edge in cluster_edges:
                cluster_edges_array.append({'source': edge[0], 'target': edge[1], 'weight': edge[2]['weight']})
                #cluster_data_frame += '%s\t%s\t%s\n' % (edge[0],edge[1],str(edge[2]['weight']))

            #return {'node_count': len(cluster_nodes), 'edge_count': len(cluster_edges_array), 'nodes': cluster_nodes, 'edges': cluster_edges_array}
            return {'edges': cluster_edges_array}
        else:
            result = {
                'directed':False,
                'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                'links':[{'source':0,'target':1,'weight':1}]
            }

            return result

        print("Got %d Hits:" % results['hits']['total'])

        if(results['hits']['total'] < 1):
            print 'no results'

    #return return_value


def convert_cluster_to_cx_es_by_id(elasticId):
    print elasticId
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
        body = search_body
    )

    if(len(results['hits']['hits']) > 0):
        result = results['hits']['hits'][0]['_source']

        if(len(result['correlation_matrix']) < 1):
            resultx = {
                'directed':False,
                'nodes':[],
                'links':[]
            }

            return resultx

        #===================================
        # GENERATE NODES & EDGES DATAFRAME
        # BASED ON EDGE CUT_OFF
        #===================================
        main_data_tuples = []

        edge_list_negative_values = []
        for correlation_record in result['correlation_matrix']:
            correlation_value = correlation_record['correlation_value']
            main_data_tuples.append((result['x_node_list'][correlation_record['x_loc']]['name'], result['y_node_list'][correlation_record['y_loc']]['name'], correlation_record['correlation_value']))

        Gsmall = nx.Graph()

        Gsmall.add_weighted_edges_from(main_data_tuples)

        export_edges = Gsmall.edges()
        export_nodes = Gsmall.nodes()

        #ndex_gsmall = NdexGraph(networkx_G=Gsmall)
        ndex_gsmall = NdexGraph()
        ndex_nodes_dict = {}

        for export_node in export_nodes:
            ndex_nodes_dict[export_node] = ndex_gsmall.add_new_node(export_node)

        for export_edge in export_edges:
            ndex_gsmall.add_edge_between(ndex_nodes_dict[export_edge[0]],ndex_nodes_dict[export_edge[1]])
            #print export_edge[0] + ' ' + export_edge[1]
            #print str(ndex_nodes_dict[export_edge[0]]) + ' ' + str(ndex_nodes_dict[export_edge[1]])

        ndex_gsmall.write_to('../../cx/' + elasticId + '_manual.cx')

        #cx_from_networkn = ndex_gsmall.to_cx()

        #print dumps(cx_from_networkn)

        cluster_edges = Gsmall.edges(data=True)
        cluster_nodes = Gsmall.nodes()
        cluster_edges_array = []
        cluster_data_frame = 'source\t target\t weight\n'
        for edge in cluster_edges:
            cluster_edges_array.append({'source': edge[0], 'target': edge[1], 'weight': edge[2]['weight']})
            #cluster_data_frame += '%s\t%s\t%s\n' % (edge[0],edge[1],str(edge[2]['weight']))

        #return {'node_count': len(cluster_nodes), 'edge_count': len(cluster_edges_array), 'nodes': cluster_nodes, 'edges': cluster_edges_array}
        return {'edges': cluster_edges_array}
    else:
        result = {
            'directed':False,
            'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
            'links':[{'source':0,'target':1,'weight':1}]
        }

        return result

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

def get_top_200_weight(cor_matrix, number_of_edges):
    cor_values_array = [];
    for correlation_record in cor_matrix:
        cor_values_array.append(correlation_record['correlation_value'])

    cor_values_array_sorted = sorted(cor_values_array, reverse=True)[:number_of_edges]

    return cor_values_array_sorted[-1]

def generate_filtered_matrix(elasticId, gene_list, number_of_edges):
    client = pymongo.MongoClient()
    db = client.cache

    gene_list_array = gene_list.split(',')

    query_list_found = []
    return_array_string = '[]'
    x_edge_overlap = []
    y_edge_overlap = []

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
            body = search_body
        )

        if(len(results['hits']['hits']) > 0):
            result = results['hits']['hits'][0]['_source']
            x_axis_type = '_' + result['x_node_list_type']
            y_axis_type = '_' + result['y_node_list_type']
            x_axis_index = []
            y_axis_index = []

            if(len(result['correlation_matrix']) < 1):
                resultx = {
                    'directed':False,
                    'nodes':[{'bfrac':40.800000000000004,'degree':138,'gfrac':0,'rfrac':255,'com':0,'id':'WNT2B_v'},{'bfrac':191.25,'degree':2,'gfrac':0,'rfrac':255,'com':1,'id':'SLC6A6'}],
                    'links':[{'source':0,'target':1,'weight':1}]
                }

                return resultx

            calculated_cut_off = get_top_200_weight(result['correlation_matrix'], number_of_edges)
            print calculated_cut_off

            #=================================
            # GET QUERY LIST OVERLAP
            #=================================
            for gene_list_item in gene_list_array:
                if(gene_list_item == 'WEE1'):
                    my_test_str = ''
                x_node_index = findIndexByKeyValue(result['x_node_list'], 'name', gene_list_item)
                y_node_index = findIndexByKeyValue(result['y_node_list'], 'name', gene_list_item)
                if(x_node_index >= 0):
                    query_list_found.append(gene_list_item)
                else:
                    if(y_node_index >= 0):
                        query_list_found.append(gene_list_item)
                        x_edge_overlap.append(x_node_index)

                #===================================
                # GET QUERY LIST OVERLAP FOR EDGES
                # i.e. EDGE INDEX from:0 to:1
                #===================================
                if(x_node_index >= 0):
                    x_edge_overlap.append(x_node_index)

                if(y_node_index >= 0):
                    y_edge_overlap.append(y_node_index)

            #===================================
            # GENERATE NODES & EDGES DATAFRAME
            # BASED ON EDGE CUT_OFF
            #===================================
            filtered_graph_data = filter_edges_to_tuples(result, calculated_cut_off, x_edge_overlap, y_edge_overlap, number_of_edges)

            main_data_tuples = filtered_graph_data['main_data_tuples']#[]
            all_data_tuples = filtered_graph_data['all_data_tuples']#[]
            query_nodes_data_tuples = []
            edge_counter = 0
            non_core_counts = {}
            edge_list_negative_values = filtered_graph_data['edge_list_negative_values']#[]

            Gsmall = nx.Graph()

            Gsmall.add_weighted_edges_from(main_data_tuples)
            nodes = Gsmall.nodes()
            #=======================================================================================
            # Because the adjacency matrix combines both axes we need to do some post-filtering
            # to limit the output to the respective node type.  This only applies to non-symetrical
            # clusters, but works for symetrical types as well.
            # Determine which rows/cols have nodes for their respective axis
            # i.e. if the y axis is type '_v' then we want a list of all the indexes with
            # nodes of type '_v' so we can remove them from the x axis
            #=======================================================================================

            node_index = 0
            xValues = []
            yValues = []
            for node in nodes:
                if(node.endswith(x_axis_type)):
                    x_axis_index.append(node_index)
                    xValues.append(node)

                if(node.endswith(y_axis_type)):
                    yValues.append(node)
                    y_axis_index.append(node_index)

                node_index += 1

            edges=Gsmall.edges(data=True)

            myMatrix = nx.adjacency_matrix(Gsmall, nodes, weight='weight')

            raw_matrix_array = np.array(myMatrix.todense())

            clustered_matrix = HeatMaps.cluster_heat_map_2D({'zValues': raw_matrix_array, 'xValues': xValues, 'yValues': yValues})#cluster_heat_map({'zValues': raw_matrix_array, 'xValues': xValues, 'yValues': yValues})

            matrix_array = clustered_matrix['zValues']

            #matrix_array = raw_matrix_array

            return_array_string = '['
            row_index = 0
            for row in matrix_array:
                col_index = 0
                if(row_index in x_axis_index):
                    return_array_string += '['
                    for col in row:
                        if(col_index in y_axis_index):
                            return_array_string += str(col) + ','
                        col_index += 1
                    if(return_array_string[-1] == ','):
                        return_array_string = return_array_string[:-1]
                    return_array_string += '],'
                row_index += 1

            #print return_array_string[-1]
            if(return_array_string[-1] == ','):
                return_array_string = return_array_string[:-1]
            return_array_string += ']'


#        zz = np.matrix([[str(ele) for ele in a] for a in np.array(myMatrix.todense())])

    #return_string = '{"zValues": ' + return_array_string + ', "yValues": ' + dumps(clustered_matrix['xValues']) + ', "xValues": ' + dumps(clustered_matrix['yValues']) +  '}'
    return_string = '{"zValues": ' + return_array_string + ', "yValues": ' + dumps(clustered_matrix['xValues']) + ', "xValues": ' + dumps(clustered_matrix['yValues']) +  '}'

    return return_string




def generate_graph_from_tab_file(edge_list_prerendered, edge_list_negative_values, query_genes, cluster_id, color_type='betweenness_centrality', colormap='spring_r'):
    '''
    this function takes a processed cluster file ('input_file_name': output of process clustering results in cluster_analysis_module)
    and saves a json file for every community in the file, starting with 'out_file_start'.  'input_file_name' and 'out_file_start'
    should be prepended with location.
    '''

    # first load in a network (edge list)

    #edge_list_df = cluster_IO #pd.read_csv(cluster_IO,sep='\t')

    group_ids = 'X' #np.unique(edge_list_df['group_id'])

    for focal_group in group_ids:

        #print focal_group

        #save_file_name = out_file_start + '_' + str(int(focal_group)) + '.json'

        #idx_group = (edge_list_df['group_id']==focal_group)
        #idx_group = list(edge_list_df['group_id'][idx_group].index)

        # make a network out of it

        #edge_list = [(edge_list_df['var1'][i], edge_list_df['var2'][i], np.abs(edge_list_df['corr'][i])) for i in idx_group if edge_list_df['corr'][i] !=0]


        Gsmall = nx.Graph()

        Gsmall.add_weighted_edges_from(edge_list_prerendered)
        permaGsmall = Gsmall

        #Gsmall.add_weighted_edges_from(edge_list)

        #outdeg = Gsmall.degree()
        outdeg = Gsmall.degree()
        edges_count = Gsmall.size()
#        to_remove = [n for n in outdeg if outdeg[n] == 1]
#        to_remove_count = len(to_remove)

#        if((edges_count - to_remove_count) >= 5):
#            Gsmall.remove_nodes_from(to_remove)
#            permaGsmall = Gsmall
#            outdeg = Gsmall.degree()
#            to_remove = [n for n in outdeg if outdeg[n] == 0]
#            Gsmall.remove_nodes_from(to_remove)
#            if(Gsmall.size() < 5):
#                Gsmall = permaGsmall

        nodes = Gsmall.nodes()
        numnodes = len(nodes)
        edges=Gsmall.edges(data=True)
        numedges = len(edges)

        data = []
#        for correlation_record in result['correlation_matrix']:

#            correlation_value = correlation_record['correlation_value']
#            if( (abs(correlation_value) >= calculated_cut_off) and edge_counter < 2000):
#                data.append([correlation_record['x_loc'], correlation_record['y_loc'], correlation_value])#abs(correlation_value)])

#        array = np.zeros((len(result['x_node_list']), len(result['y_node_list'])))

#        for row, col, val in data:
#            index = (row, col)
#            array[index] = val

#        return_array_string = '['
#        for row in array:
#            return_array_string += '['
#            for col in row:
#                return_array_string += str(col) + ','
#            return_array_string += '],'

#        return_array_string += ']'






        # pre-calculate the node positions (multiply by 1000 below... may need to change this)
#        node_pos = nx.spring_layout(Gsmall, k=0.2, iterations=5)

        print 'Edges len: ' + str(len(edges))
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



            pos_x_y = {}
            communities_counter = []
            for debug_node in nodes:
                r_color = int(rfrac[debug_node]*255) + randint(0,19)
                r_color = 10 if r_color < 5 else r_color
                g_color = int(gfrac[debug_node]*255) + randint(0,19)
                g_color = 10 if g_color < 5 else g_color
                b_color = int(bfrac[debug_node]*255) + randint(0,19)
                b_color = 10 if b_color < 5 else b_color
                pos_x_y[debug_node] = (r_color, b_color)
                #print str(r_color) + ', ' + str(b_color)
                community_color_concat = str(rfrac[debug_node]) + str(gfrac[debug_node]) + str(bfrac[debug_node])
                if(community_color_concat not in communities_counter):
                    communities_counter.append(community_color_concat)

            # pre-calculate the node positions (multiply by 1000 below... may need to change this)
            if(len(communities_counter) >= 3):
                node_pos = nx.spring_layout(Gsmall, k=0.02, pos=pos_x_y, iterations=5)
                for node_pos_item in node_pos:
                    print node_pos_item
            else:
                node_pos = nx.spring_layout(Gsmall, k=0.02, iterations=5)

            nodes_dict = [{"id":n,"com":col_temp[n],"degree":Gsmall.degree(n),
                        "rfrac":int(rfrac[n]*255),"gfrac":int(gfrac[n]*255),"bfrac":int(bfrac[n]*255),
                        "x":node_pos[n][0]*1000,
                        "y":node_pos[n][1]*1000} for n in nodes]
        elif color_type=='expression_value':
            mystr = ''
        elif color_type=='clustering_coefficient':
            # pre-calculate the node positions (multiply by 1000 below... may need to change this)
            #node_pos = nx.spring_layout(Gsmall, k=0.04)
            #node_pos = nx.spring_layout(Gsmall, k=0.04)

            cmap= plt.get_cmap(colormap)
            rfrac,gfrac,bfrac,local_cc=calc_clustering_coefficient(Gsmall,cmap)
            nodes_dict = [{"id":n,"com":0,"degree":Gsmall.degree(n),
                        "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255,
                        "local_cc": local_cc[n],
                        #"x":node_pos[n][0]*1000,
                        #"y":node_pos[n][1]*1000
                           } for n in nodes]

        elif color_type=='betweenness_centrality':
            # pre-calculate the node positions (multiply by 1000 below... may need to change this)
            node_pos = nx.spring_layout(Gsmall, k=0.2, iterations=5)

            cmap= plt.get_cmap(colormap)
            rfrac,gfrac,bfrac=calc_betweenness_centrality(Gsmall,cmap)
            nodes_dict = [{"id":n,"com":0,"degree":Gsmall.degree(n),
                        "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255,
                        "x":node_pos[n][0]*1000,
                        "y":node_pos[n][1]*1000} for n in nodes]

        node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges

        edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]], "weight":edges[i][2]['weight']} for i in range(numedges)]

        #==========================================
        # Restore the correlation sign (+/-)
        #
        # create a list of edges that should be
        # negative using [source, target] format
        #==========================================
        edge_list_negative_values_adjusted = [(node_map[neg_edge_item[0]], node_map[neg_edge_item[1]]) for neg_edge_item in edge_list_negative_values if((neg_edge_item[0] in node_map) and (neg_edge_item[1] in node_map))]

        for edge_dict_item in edges_dict:  #AVMGJVnyRXVvO0gLpdDP
            for e_neg in edge_list_negative_values_adjusted:
                if(e_neg[0] == edge_dict_item['source'] and e_neg[1] == edge_dict_item['target']) or (e_neg[1] == edge_dict_item['source'] and e_neg[0] == edge_dict_item['target']):
                    edge_dict_item['weight'] = -1 * np.abs(edge_dict_item['weight'])

        import json
        json_graph = {"directed": False, "nodes": nodes_dict, "links":edges_dict}
        print 'Edge count: ' + str(len(edges_dict))

        #client = pymongo.MongoClient()
        #db = client.cache

        #heat_maps = db.heat_map_graph

        a = {
            'clusterId': focal_group,
            'heat_map': json_graph
        }

        return a

def calc_clustering_coefficient(G,cmap):
    # this function calculates the clustering coefficient of each node, and returns colors corresponding to these values
    local_CC = nx.clustering(G,G.nodes())
    local_CC_scale = [round(local_CC[key]*float(255)) for key in G.nodes()]
    local_CC_scale = pd.Series(local_CC_scale,index=G.nodes())
    rfrac = [cmap(int(x))[2] for x in local_CC_scale]
    gfrac = [cmap(int(x))[1] for x in local_CC_scale]
    bfrac = [cmap(int(x))[0] for x in local_CC_scale]
    rfrac = pd.Series(rfrac,index=G.nodes())
    gfrac = pd.Series(gfrac,index=G.nodes())
    bfrac = pd.Series(bfrac,index=G.nodes())

    return rfrac,gfrac,bfrac,local_CC

def calc_betweenness_centrality(G,cmap):
    # this function calculates the betweenness centrality of each node, and returns colors corresponding to these values
    local_BC = nx.betweenness_centrality(G)
    local_BC_scale = [round(local_BC[key]*float(255)) for key in G.nodes()]
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

def get_cluster_document_from_elastic_by_id2(elasticId):
    xValues = []
    yValues = []

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
        body = search_body
    )

    if(len(results) > 0):
        result = results['hits']['hits'][0]['_source']
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

    #==========================================
    # Because the z matrix is transposed we
    # will switch the labels for X and Y coord.
    #==========================================
    return_value = {
        'xValues': yValues,
        'yValues': xValues,
        'zValues': array
    }

    print("Got %d Hits:" % results['hits']['total'])

    if(results['hits']['total'] < 1):
        print 'no results'

    return return_value

def get_cluster_document_from_elastic_by_id3(elasticId):
    client = pymongo.MongoClient()
    db = client.cache

    heat_maps = db.heat_maps

    heat_map_found = heat_maps.find_one({'elasticId': elasticId})

    if(heat_map_found is not None):
        print 'Get cached heatmap'
        return heat_map_found['heat_map']
    else:
        es_data_matrix = get_cluster_document_from_elastic_by_id2(elasticId)
        return dumps(es_data_matrix) #heat_map_ordered_transposed

def get_heatmap_export(esId):
    cluster_result = get_cluster_document_from_elastic_by_id3('2020035052')
    exportArray = []
    xValues = cluster_result.xValues;
    yValues = cluster_result.yValues;
    zValues = cluster_result.zValues;

    tempHeader = ','
    for xVal in xValues:
        tempHeader += xVal + ','
    exportArray.append(tempHeader)

    for i in range(len(yValues)):
        tempRowString = yValues[i] + ','
        for j in range(len(xValues)):
            tempRowString += zValues[i][j] + ','
        exportArray.append(tempRowString)




#    var exportArrayString = "data:text/csv;charset=utf-8,";
#    for (var k = 0; k <= $scope.plotlyData.yValues.length; k++) {
#        exportArrayString += $scope.plotlyData.exportArray[k] + '\n';
#    }



def load_x_y_z_cluster_data(esId):
#    results = get_cluster_document_from_elastic_by_id3('2020035052')

    xValues = []
    yValues = []
    cluster_info = ''

    search_body = {
       'query': {
            'bool': {
                'must': [
                   {'match': {
                      '_id': esId
                   }}
                ]
            }
        }
    }

    results = es.search(
        index = 'clusters',
        body = search_body
    )

    if(len(results) > 0):
        result = results['hits']['hits'][0]['_source']
        cluster_info = result['network_full_name']
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
    index=xValues,    # 1st column as index
    columns=yValues)  # 1st row as the column names

    numrows = len(sample_mat)
    numcols = len(sample_mat.columns)

    # check if symmetric
    if numrows==numcols:
        idx_to_node = dict(zip(range(len(sample_mat)),list(sample_mat.index)))

        sample_mat = np.array(sample_mat)
        sample_mat = sample_mat[::-1,::-1] # reverse the indices for use in graph creation
    else:
        zmat = np.array(sample_mat)
        zmat = zmat[::-1,0:-1] # reverse the indices for use in graph creation
        ylist = list(sample_mat.index)
        xlist = list(sample_mat.columns)

        zsym,xsym,ysym = symmetrize_matrix(zmat,xlist,ylist)

        sample_mat = zsym
        idx_to_node = dict(zip(range(len(sample_mat)),xlist))

    #G_cluster = nx.Graph()
    G_cluster = nx.from_numpy_matrix(np.abs(sample_mat))
    G_cluster = nx.relabel_nodes(G_cluster,idx_to_node)

    return {'cluster': G_cluster, 'cluster_info': cluster_info}

def symmetrize_matrix(zmat,xlist,ylist):
    '''
    Simple helper function to symmetrize an assymmetric matrix

    inputs:
        - zmat: a 2d matrix (dimensions r x c)
        - xlist: ordered list of row names (length r)
        - ylist: ordered list of column names (length c)

    outputs:
        - zsym: symmetrized matrix (dimensions (r+c) x (r+c))
        - xsym: [xlist, ylist]
        - ysim: [xlist, ylist] (Note: ysim = xsim)

    '''

    numrows,numcols = zmat.shape

    # initialize the symmetric version of zmat
    zsym = np.zeros((numrows+numcols,numrows+numcols))
    # fill diagonal with 1s
    np.fill_diagonal(zsym,1)

    zsym[0:numrows,numrows:]=zmat
    zsym[numrows:,0:numrows]=np.transpose(zmat)

    xsym = []
    xsym.extend(xlist)
    xsym.extend(ylist)

    ysym = []
    ysym.extend(xlist)
    ysym.extend(ylist)

    return zsym,xsym,ysym

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

def plot_cluster():
    G=nx.random_geometric_graph(200,0.125)
    pos=nx.get_node_attributes(G,'pos')

    dmin=1
    ncenter=0
    for n in pos:
        x,y=pos[n]
        d=(x-0.5)**2+(y-0.5)**2
        if d<dmin:
            ncenter=n
            dmin=d

    p=nx.single_source_shortest_path_length(G,ncenter)

    print p
