# import some useful packages
import numpy as np
import matplotlib.pyplot as plt
import seaborn
import networkx as nx
import pandas as pd
import random
import json
import pymongo
import time

import sys
code_path = 'source'
sys.path.append(code_path)
import network_prop
from bson.json_util import dumps
from app import DB_el

def find_drugs_from_hot_genes(Fnew,G_DB,seed_genes,keep_seed_genes =True):
    
    '''
    Function to find drugs associated with hot genes, return a dictionary containing drug info and heat rank
    inputs:
        - Fnew: heat vector from network_prop.network_propagation function
        - G_DB: Bipartite graph with drugs and drug targets (genes) as nodes
        - seed_genes:  seed genes network propagation was started from
        - keep_seed_genes:  decide whether to include seed genes in output drug list (default True)
    
    '''
    
    client = pymongo.MongoClient()
    db = client.dataset

    drug_bank_by_gene = db.drug_bank_by_gene

    # make sure Fnew is sorted
    #Fnew.sort(ascending=False)
    Fnew.sort_values(inplace=True, ascending=False)


    ranked_genes = list(Fnew.index)
    
    if not keep_seed_genes:
        # (Should we only keep non-seed genes??)
        ranked_genes = list(np.setdiff1d(ranked_genes,seed_genes))
        ranked_genes = Fnew[ranked_genes]
        ranked_genes.sort(ascending=False)
        ranked_genes = list(ranked_genes.index)

    gene_drug_dict = dict() # build up a list of genes and drugs that may be related to input list
    start_time = time.time()
    for g in ranked_genes:
        #if g in G_DB.nodes():  # check if g is in drugbank graph
        drug_bank_by_gene_found = drug_bank_by_gene.find_one({'gene': g})
        if(drug_bank_by_gene_found is not None):
            drug_neighs_temp = drug_bank_by_gene_found['drugs'] #list(nx.neighbors(G_DB,g))
        else:
            #print g
            drug_neighs_temp = []

        # add drug neighbors and ranked score to gene_drug_dict
        gene_drug_dict[g] = {'drugs':drug_neighs_temp,'heat_rank':ranked_genes.index(g)}

        #else:
            # fill in dictionary when there are no drugs related to focal gene
        #    gene_drug_dict[g] = {'drugs':[],'heat_rank':ranked_genes.index(g)}
    print 'build up list: ' + str(start_time - time.time())

    # return a sorted dataframe- more useful
    start_time = time.time()
    gene_drug_df = pd.DataFrame(gene_drug_dict).transpose()  # note we have to transpose so index is genes
    gene_drug_df['heat_value'] = Fnew[ranked_genes]
    #gene_drug_df = gene_drug_df.sort(columns='heat_rank')
    gene_drug_df = gene_drug_df.sort_values(by='heat_rank')
    print 'run sorted dataframe: ' + str(start_time - time.time())

    #print gene_drug_df
    return gene_drug_df
            
def drug_gene_heatprop(seed_genes,cluster_x_y_z,plot_flag=False):
    
    '''
    Function to establish drugs potentially related to an input gene list, using network propagation methods
    
    inputs:
        - seed_genes:  genes from which to initiate heat propagation simulation
        - path_to_DB_file:  path to drug bank file, including filename
        - path_to_cluster_file: path to cluster file, including filename
        - plot_flag: should we plot the subnetwork with heat overlaid? Default False
        
    '''
    
    
    # load and parse the drug-bank file into a dict ()
    #DBdict = load_DB_data(path_to_DB_file)
    
    # make a network out of drug-gene interactions
#    DB_el = []
#    for d in DBdict.keys():
#        node_list = DBdict[d]['node_list']
#        for n in node_list:
#            DB_el.append((DBdict[d]['drugbank_id'],n['name']))

    #load_DB_el()
            
    start_time = time.time()
    G_DB = nx.Graph()
    G_DB.add_edges_from(DB_el)

    G_cluster = cluster_x_y_z #load_cluster_data(path_to_cluster_file)
    
    # calculate the degree-normalized adjacency matrix
    Wprime = network_prop.normalized_adj_matrix(G_cluster,weighted=True)

    # run the network_propagation simulation starting from the seed genes
    Fnew = network_prop.network_propagation(G_cluster,Wprime,seed_genes)

    # sort heat vector Fnew
    #Fnew.sort(ascending=False)
    Fnew.sort_values(inplace=True, ascending=False)
    # if plot_flag is on plot the cluster genes with heat overlaid
    if plot_flag:
        pos = nx.spring_layout(G_cluster)

        plt.figure(figsize=(10,10))
        nx.draw_networkx_edges(G_cluster,pos=pos,alpha=.03)
        nx.draw_networkx_nodes(G_cluster,pos=pos,node_size=20,alpha=.8,node_color=Fnew[G_cluster.nodes()],cmap='jet',
                               vmin=0,vmax=np.max(Fnew)/10)
        nx.draw_networkx_nodes(G_cluster,pos=pos,nodelist=seed_genes,node_size=50,alpha=.7,node_color='red',linewidths=2)

        plt.grid('off')
        plt.title('Sample subnetwork: post-heat propagation',fontsize=16)
    
    # find the drugs related to hot genes
    gene_drug_df = find_drugs_from_hot_genes(Fnew,G_DB,seed_genes,keep_seed_genes =True)

    #print gene_drug_df

    return gene_drug_df

def cluster_genes_heatprop(seed_genes,cluster_x_y_z):

    '''
    Function to establish drugs potentially related to an input gene list, using network propagation methods

    inputs:
        - seed_genes:  genes from which to initiate heat propagation simulation
        - path_to_DB_file:  path to drug bank file, including filename
        - path_to_cluster_file: path to cluster file, including filename
        - plot_flag: should we plot the subnetwork with heat overlaid? Default False

    '''

    #G_DB = nx.Graph()
    #G_DB.add_edges_from(DB_el)

    G_cluster = cluster_x_y_z #load_cluster_data(path_to_cluster_file)

    # calculate the degree-normalized adjacency matrix
    Wprime = network_prop.normalized_adj_matrix(G_cluster['cluster'],weighted=True)

    # run the network_propagation simulation starting from the seed genes
    Fnew = network_prop.network_propagation(G_cluster['cluster'],Wprime,seed_genes)

    # sort heat vector Fnew
    Fnew.sort(ascending=False)

    H = G_cluster['cluster'].subgraph(Fnew.head(500).keys())

    return H

def load_DB_el():
    client = pymongo.MongoClient()
    db = client.dataset

    drug_bank_collection = db.drug_bank

    drug_bank_collection_found = drug_bank_collection.find_one({'drug_bank_info_type': 'drug_infer'})

    DB_el = []
    for kv_pair in drug_bank_collection_found['drug_bank_info']:
        DB_el.append((kv_pair['key'],kv_pair['value']))

    return DB_el

def load_DB_data(fname):
    '''
    Function to load drug bank data (in format of this file 'drugbank.0.json.new')
    '''

    with open(fname, 'r') as f:
        read_data = f.read()
    f.closed

    si = read_data.find('\'\n{\n\t"source":')
    sf = read_data.find('\ncurl')

    DBdict = dict()

    # fill in DBdict
    while si > 0:

        db_temp = json.loads(read_data[si+2:sf-2])
        DBdict[db_temp['drugbank_id']]=db_temp

        # update read_data
        read_data = read_data[sf+10:]

        si = read_data.find('\'\n{\n\t"source":')
        sf = read_data.find('\ncurl')


    #of = open('drug_bank.json', 'w')

    #of.write(dumps(DBdict))

    #of.close()


#    db = pymongo.MongoClient().dataset
#    collection = db.drug_bank
#    collection.drop()

#    count = 0

#    DB_el = []
#    for k, v in DBdict.iteritems():
#        node_list = v['node_list']
#        for n in node_list:
#            DB_el.append(
#                {
#                    'key': k,
#                    'value': n['name']
#                 }
#            )

#    insert_this_gene_record = {
#        'drug_bank_info_type': 'drug_infer',
#        'drug_bank_info': DB_el
#    }
#    collection.insert_one(insert_this_gene_record)
#    count += 1
#    print('%s' % count)


#    DB_el = []
#    for d in DBdict.keys():
#        node_list = DBdict[d]['node_list']
#        for n in node_list:
#            DB_el.append((DBdict[d]['drugbank_id'],n['name']))




#    collection.create_indexes([
#        pymongo.IndexModel([('db_id', pymongo.ASCENDING)])
#    ])

#    db.close()

    return DBdict

def load_cluster_data(fname):
    # NOTE: THIS ONLY WORKS FOR SYMMETRIC CLUSTERS FOR NOW

    cluster_result =  {'xValues': '','yValues': '','zValues': ''}

    xValues = cluster_result.xValues;
    yValues = cluster_result.yValues;
    zValues = cluster_result.zValues;

    sample_mat = pd.DataFrame(data=zValues,    # values
    index=yValues,    # 1st column as index
    columns=xValues)  # 1st row as the column names

    idx_to_node = dict(zip(range(len(sample_mat)),list(sample_mat.index)))

    sample_mat = np.array(sample_mat)
    sample_mat = sample_mat[::-1,0:-1] # reverse the indices for use in graph creation

    G_cluster = nx.from_numpy_matrix(np.abs(sample_mat))
    G_cluster = nx.relabel_nodes(G_cluster,idx_to_node)

    return G_cluster

