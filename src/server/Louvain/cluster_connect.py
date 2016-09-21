"""
 -----------------------------------------------------------------------

Author: Brin Rosenthal (sbrosenthal@ucsd.edu)

 -----------------------------------------------------------------------
"""


# import some useful packages
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import random
import time

def create_G_core_connected(G_total,num_edges_to_keep=20000,print_flag=True):

    '''
    Function to connect core nodes to periphery nodes by their shortest path

    inputs:
        - G_total: Full graph for a focal cluster
        - num_edges_to_keep: number of top edges to keep which will define the core nodes
        - print_flag: print out progress if true

    outputs:
        - G_core_sps:  Smaller core + periphery node graph
        - G_LCC:  The graph for the core nodes

    Note: if G_total has < num_edges_to_keep edges, G_core_sps and G_LCC will be equal to G_total

    '''
    G_total = G_total.to_undirected()

    print('total number of edges = ' + str(len(G_total.edges())))

    # make sure G_total is fully connected
    if not nx.is_connected(G_total):
        G_total = max(nx.connected_component_subgraphs(G_total), key=len)

    print('total number of edges after extraction = ' + str(len(G_total.edges())))


    # get the list of weights for G_total
    weight_list = [e[2]['weight'] for e in G_total.edges(data=True)]

    # set 1-EL attribute (because SPL algorithm finds lowest weight sum along path)
    n1total,n2total = zip(*G_total.edges())
    one_minus_weight_dict = dict(zip(zip(n1total,n2total),list(1-np.array(weight_list))))
    nx.set_edge_attributes(G_total,'one_minus_weight',one_minus_weight_dict)

    # only keep the top N edges
    idxsort = np.argsort(weight_list)
    idxsort = list(idxsort[::-1])
    #pd.Series(weight_list)[idxsort]

    # create a graph out of the top N edges (start with 100)
    EL_small = [(e[0],e[1],e[2]['weight']) for e in np.array(G_total.edges(data=True))[idxsort[0:num_edges_to_keep]]]

    G_small = nx.Graph()
    G_small.add_weighted_edges_from(EL_small)

    # find the largest connected component
    G_LCC = max(nx.connected_component_subgraphs(G_small), key=len)

    nodes_noncore = list(np.setdiff1d(G_total.nodes(),G_LCC.nodes()))
    nodes_core = list(G_LCC.nodes())

    if print_flag:
        print('there are '+ str(len(nodes_core)) + ' core nodes')
        print('there are '+ str(len(nodes_noncore)) + ' non-core nodes')

    SPs = []
    # loop over noncore nodes to find SPL to core
    for n_focal in nodes_noncore:
        paths = nx.single_source_dijkstra_path(G_total,source=n_focal,weight='one_minus_weight')
        # also measure the path lens so we can keep the shortest one
        path_lens = nx.single_source_dijkstra_path_length(G_total,source=n_focal,weight='one_minus_weight')
        path_lens = pd.Series(path_lens)
        path_lens.sort() # sort it so shortest paths are highest

        path_lens = path_lens[nodes_core] # select only the paths to core nodes

        target_SP_node = list(path_lens.head(1).index)
        target_SP_node = target_SP_node[0]

        shortest_path = paths[target_SP_node]
        for n in range(1,len(shortest_path)):
            n1 = shortest_path[n-1]
            n2 = shortest_path[n]
            weight = G_total.get_edge_data(n1,n2)['weight']

            SPs.append((n1,n2,weight))


    G_core_sps = nx.Graph()
    G_core_sps = G_LCC.copy()
    G_core_sps.add_weighted_edges_from(SPs)

    # temp switch to directed graphs so we can operate on edge sets
    G_LCC = G_LCC.to_directed()
    G_core_sps = G_core_sps.to_directed()

    # add edge attributes (original edge weight) to G_LCC and G_core_sps
    n1core_sps,n2core_sps = zip(*G_core_sps.edges())

    ew_orig_core_sps = [G_total.get_edge_data(n1core_sps[i],n2core_sps[i])['weight_orig'] for i in range(len(n1core_sps))]
    pval_core_sps = [G_total.get_edge_data(n1core_sps[i],n2core_sps[i])['pval'] for i in range(len(n1core_sps))]
    ew_CS_dict = dict(zip(zip(n1core_sps,n2core_sps),ew_orig_core_sps))
    pval_CS_dict = dict(zip(zip(n1core_sps,n2core_sps),pval_core_sps))
    nx.set_edge_attributes(G_core_sps,'weight_orig',ew_CS_dict)
    nx.set_edge_attributes(G_core_sps,'pval',pval_CS_dict)

    n1LCC,n2LCC = zip(*G_LCC.edges())


    ew_orig_LCC = [G_total.get_edge_data(n1LCC[i],n2LCC[i])['weight_orig'] for i in range(len(n1LCC))]
    pval_orig_LCC = [G_total.get_edge_data(n1LCC[i],n2LCC[i])['pval'] for i in range(len(n1LCC))]
    ew_LCC_dict = dict(zip(zip(n1LCC,n2LCC),ew_orig_LCC))
    pval_LCC_dict = dict(zip(zip(n1LCC,n2LCC),pval_orig_LCC))
    nx.set_edge_attributes(G_LCC,'weight_orig',ew_LCC_dict)
    nx.set_edge_attributes(G_LCC,'pval',pval_LCC_dict)

    # add an attribute for core/noncore
    core_attr = dict(zip(G_LCC.edges(), ['core']*len(G_LCC.edges())))
    edges_new = list(set.difference(set(G_core_sps.edges()),set(G_LCC.edges())))
    non_core_attr = dict(zip(edges_new,['noncore']*len(edges_new)))

    core_noncore_attr = core_attr.copy()
    core_noncore_attr.update(non_core_attr)
    nx.set_edge_attributes(G_core_sps,'in_core',core_noncore_attr)

    # back to undirected so we don't have duplicate edges
    G_LCC = G_LCC.to_undirected()
    G_core_sps = G_core_sps.to_undirected()

    return G_core_sps,G_LCC

def trim_cluster_df(D_cluster,num_edges_to_keep=20000,print_flag = True):
    '''
    - This function inputs a cluster dataframe (with columns for var1,var2,corr,p,group_id)

    - Trims edges from clusters which are bigger than num_edges_to_keep
    - Returns a new trimmed cluster dataframe, with a new column for core/noncore nodes

    '''

    D_cluster.index = D_cluster['group_id']

    # make sure we keep track of original weights

    group_ids = D_cluster['group_id'].unique()
    num_groups = len(group_ids)

    D_full_trimmed = pd.DataFrame()
    c_count = 0
    for c_focal in group_ids: # loop over clusters
        c_count = c_count+1

        # check if there are enough edges in cluster

        if len(D_cluster.loc[c_focal])>25:

            if print_flag:
                print('trimming cluster ' + str(float(c_count)) + ' out of ' + str(len(group_ids)))

            D_c_focal = D_cluster.loc[c_focal]

            var1_D_c_focal = list(np.unique(D_c_focal['var1']))  # list used below to check new var1 matches old var1

            G_c = create_graph_from_DF_cluster(D_c_focal)

            # trim excess edges
            G_core_sps,G_core = create_G_core_connected(G_c,num_edges_to_keep=num_edges_to_keep,print_flag=print_flag)

            nodes1,nodes2,edata = zip(*nx.to_edgelist(G_core_sps))
            ezip = [(e['weight_orig'],e['pval'],e['in_core']) for e in edata]
            corr_c,pval_c,core_c = zip(*ezip)

            group_c = c_focal + np.zeros((len(nodes1)))

            # MAKE SURE NEW var1 MATCHES OLD var1
            # need to loop to make sure all are correct....
            var1,var2 = [],[]
            for i in range(len(nodes1)):

                n1 = nodes1[i]
                n2 = nodes2[i]
                if n1 in var1_D_c_focal:
                    var1.append(n1)
                    var2.append(n2)
                else:
                    var1.append(n2)
                    var2.append(n1)

            D_c_trimmed = pd.DataFrame({'var1':var1,'var2':var2,'corr':corr_c,'p':pval_c,
                                        'group_id':group_c,'core_status':core_c})

            D_full_trimmed = pd.concat([D_full_trimmed,D_c_trimmed])

    return D_full_trimmed



def create_graph_from_DF_cluster(D_c_focal):
    '''
    Helper function to return a graph from a focal cluster dataframe
    '''

    corr_list_abs = D_c_focal['corr'].abs()
    D_c_focal['abs_corr'] = corr_list_abs

    # extract the top 300k edges, for memory constraints
    if len(D_c_focal)>300000:
        D_c_focal = D_c_focal.sort('abs_corr',ascending=False)  # sort by absolute value of correlation
        D_c_focal = D_c_focal.head(300000)

    D_c_focal = D_c_focal.loc[D_c_focal['abs_corr']>0] # only keep non-zero edges


    n1list = D_c_focal['var1']
    n2list = D_c_focal['var2']
    corr_list = D_c_focal['corr']
    pval_list = D_c_focal['p']

    G_c = nx.DiGraph()
    G_c.add_weighted_edges_from(zip(n1list,n2list,np.abs(corr_list)))

    weight_no_abs_dict = dict(zip(zip(n1list,n2list),corr_list))
    pval_dict = dict(zip(zip(n1list,n2list),pval_list))

    nx.set_edge_attributes(G_c,'weight_orig',weight_no_abs_dict)
    nx.set_edge_attributes(G_c,'pval',pval_dict)

    return G_c

