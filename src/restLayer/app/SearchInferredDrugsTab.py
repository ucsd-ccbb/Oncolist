__author__ = 'aarongary'

from app import PubMed
from app import elastic_search_uri
from collections import Counter
from elasticsearch import Elasticsearch
from bson.json_util import dumps
import matplotlib.pyplot as plt
import matplotlib.colors as mpclrs
import pymongo
from multiprocessing import Manager, Process
import copy
import app.datascience.drug_gene_heatprop
import imp
imp.reload(app.datascience.drug_gene_heatprop)
import numpy as np
import math
import networkx as nx
import pandas as pd

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server

#TODO: Figure out how to merge/shuffle the drug results
#TODO: Figure out which of the 40 clusters are best for inferred drug searching

#============================
#============================
#      DRUG SEARCH
#============================
#============================
def get_inferred_drug_search(es_id_list):
    es_id_array = es_id_list.split(',')

    #inferred_drugs = get_drugs_from_clusters(es_id_array) #['2010018824','2010011335'])
    inferred_drugs = get_drugs_from_clusters_group_drugs(es_id_array) #['2010018824','2010011335'])

    return inferred_drugs

def get_drugs_from_clusters_group_drugs(es_id_array):
    should_match = []
    for es_id in es_id_array:
        should_match.append({"match": {"node_name": es_id}})

    search_body = {
        'query': {
            'bool': {
                'should': should_match
            }
        },
        'size': len(es_id_array)
    }

    result = es.search(
        index = 'groups',
        doc_type = 'clusters_drugs',
        body = search_body
    )

    if(result['hits']['total'] < 1):
        print 'no results'

    return_data = {
        'drugs': [],
        'grouped_drugs': [],
        'final_grouping': []
    }

    for hit in result['hits']['hits']:
        drug_name_array = []
        for drugNodeHit in hit["_source"]["node_list"][:10]:
            #check if the gene already exists
            if(drugNodeHit['drug_name'] not in return_data['drugs']):
                #if not add initial case
                return_data['drugs'].append(drugNodeHit['drug_name'])
                return_data['grouped_drugs'].append(
                        {
                        'key': drugNodeHit['drug_name'],
                        'drug_bank_id': drugNodeHit['drug_id'],
                        'genes': [drugNodeHit['gene']],
                        'value': [drugNodeHit], #drugNodeHit contains all the information for the drug (ids, doc_id, etc)
                        'gene_count': 1
                        }
                    )
            else:
                #if so append to the existing group
                for grouped_item in return_data['grouped_drugs']:
                    if(drugNodeHit['drug_name'] == grouped_item['key']):
                        if(drugNodeHit['gene'] not in grouped_item['genes']):
                            grouped_item['genes'].append(drugNodeHit['gene'])
                            grouped_item['gene_count'] += 1
                            grouped_item['value'].append(drugNodeHit)

    for drug_node in return_data['grouped_drugs']:
        if(len(drug_node['genes']) > 0):
            return_data['final_grouping'].append(drug_node)


    #print dumps(return_data['final_grouping'])
    #print len(return_data['final_grouping'])

    return return_data['final_grouping']

def get_drugs_from_clusters(es_id_array):
    should_match = []
    for es_id in es_id_array:
        should_match.append({"match": {"node_name": es_id}})

    search_body = {
        'query': {
            'bool': {
                'should': should_match
            }
        },
        'size': 50
    }

    result = es.search(
        index = 'groups',
        doc_type = 'clusters_drugs',
        body = search_body
    )

    if(result['hits']['total'] < 1):
        print 'no results'

    return_data = {
        'genes': [],
        'grouped_genes': []
    }

    for hit in result['hits']['hits']:
        drug_name_array = []
        for geneNodeHit in hit["_source"]["node_list"]:
            #check if the gene already exists
            if(geneNodeHit['gene'] not in return_data['genes']):
                #if not add initial case
                return_data['genes'].append(geneNodeHit['gene'])
                return_data['grouped_genes'].append(
                        {
                        'key': geneNodeHit['gene'],
                        'drug_bank_id': geneNodeHit['drug_id'],
                        'drugs': [geneNodeHit['drug_name']],
                        'value': [geneNodeHit] #geneNodeHit contains all the information for the drug (ids, doc_id, etc)
                        }
                    )
            else:
                #if so append to the existing group
                for grouped_item in return_data['grouped_genes']:
                    if(geneNodeHit['gene'] == grouped_item['key']):
                        if(geneNodeHit['drug_name'] not in grouped_item['drugs']):
                            grouped_item['drugs'].append(geneNodeHit['drug_name'])
                            grouped_item['value'].append(geneNodeHit)
    print dumps(return_data)

    return return_data

def expriment_1(seed_genes, esIds):
    client = pymongo.MongoClient()
    db = client.identifiers
    drugbank_collection = db.drugbank

    seed_genes_array = seed_genes.split(',')
    es_id_array = esIds.split(',')

    #seed_genes_array = ['OR2J3','AANAT','KRT80','MACC1','LOC139201','CCDC158','PLAC8L1','CLK1','GLTP','PITPNM2','TRAPPC8','EIF2S2','PNLIP','EHF','FOSB','MTMR4','USP46','CDH11','ENAH','CNOT7','STK39','CAPZA1','STIM2','DLL4','WEE1','MYO1D','TEAD3']
    #es_id_array_debug = ['2020014671','2020004787','2010025212','2010007504','2010020100','2010020273']
    return_value = None
    return_value_array = []

    #================================
    # Run the heat prop in parallel
    #================================
    manager = Manager()
    return_dict = manager.dict()
    jobs = []
    #for es_id in es_id_array:
    #    p = Process(target=get_heat_prop_from_es_id, args=(es_id, seed_genes_array, False, return_dict))
    #    jobs.append(p)
    #    p.start()

    #for proc in jobs:
    #    proc.join()

    #inferred_drug_group_array = return_dict.values()

    for es_id in es_id_array:
        jobs.append(get_heat_prop_from_es_id(es_id, seed_genes_array, False, {}))
    inferred_drug_group_array = jobs
    print dumps(jobs)

    merged_by_rank = []
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

    return_value_array = {'inferred_drugs': merged_by_rank} #return_dict.values()

    return return_value_array

def get_heat_prop_from_es_id(es_id, seed_genes_array, include_evidence_graph=False, return_dict=None):
    client = pymongo.MongoClient()
    db = client.identifiers
    drugbank_collection = db.drugbank

    print es_id

    disease_type = get_cluster_disease_by_es_id(es_id)

    cluster_data = load_x_y_z_cluster_data(es_id)
    cluster_x_y_z = cluster_data['cluster']

    gene_drug_df = app.datascience.drug_gene_heatprop.drug_gene_heatprop(seed_genes_array,cluster_x_y_z,plot_flag=False)

    gene_drug_json = gene_drug_df.reset_index().to_dict(orient='index')
    #print dumps(gene_drug_json)

    one_gene_many_drugs = []
    hot_genes = []
    hot_genes_with_heat_value = []
    hot_genes_values = []
    for key, value in gene_drug_json.iteritems():

        if(len(value['drugs']) > 0 and value['index'] not in seed_genes_array):
            if(value['heat_value'] > 0.00001):
                one_gene_many_drugs.append({
                    'gene': value['index'],
                    'drugs': value['drugs'],
                    'heat_value': float("{0:f}".format(value['heat_value'])),
                    'heat_rank': value['heat_rank']
                })

        if(value['heat_value'] > 0.00001):
            hot_genes.append(value['index'])
            drugs_array_desc = []
            drugs_for_pop_up = ''
            node_info_for_pop_up = '<span style="font-weight: bold; margin-bottom: 5px;">Drugs associated with ' + value['index'] + ':</span><br><div style="margin-left: 10px;">'

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
                        'drugs': value['index'] + '\nDrugs targeting this gene:\n\n' + drugs_for_pop_up,
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
                        'drugs': value['index'] + '\n[SEED GENE]\nFor drugs that are directly \ntargeting this query gene \nsee results above', # This is a seed gene.  We are not showing direct drugs only inferred drugs.
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
                            'disease_type': disease_type
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
                    return_dict[es_id] = {'inferred_drugs': top_drugs_sorted_list[:24], 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type}
                return {'inferred_drugs': top_drugs_sorted_list[:24], 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type}
            else:
                if(return_dict is not None):
                    return_dict[es_id] = {'inferred_drugs': top_drugs_sorted_list, 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type}
                return {'inferred_drugs': top_drugs_sorted_list, 'evidence_graph': inferred_drug_graph, 'disease_type': disease_type}
        else:
            if(return_dict is not None):
                return_dict[es_id] = {'inferred_drugs': [{'nodes': [], 'edges':[]}], 'evidence_graph': {'directed':False,'nodes':[],'links':[]}, 'disease_type': disease_type}
            return {'inferred_drugs': [{'nodes': [], 'edges':[]}], 'evidence_graph': {'directed':False,'nodes':[],'links':[]}, 'disease_type': disease_type}

def get_drugbank_name(db_id, drugbank_mongo_collection):
    drug_bank_found = drugbank_mongo_collection.find_one({'drug_bank_id': db_id})
    drug_bank_desc = ''
    if(drug_bank_found is not None):
        drug_bank_desc = drug_bank_found['drug_desc']
    else:
        drug_bank_desc = db_id

    return drug_bank_desc

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
    index=yValues,    # 1st column as index
    columns=xValues)  # 1st row as the column names

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
        xlist = list(sample_mat.index)
        ylist = list(sample_mat.columns)

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

