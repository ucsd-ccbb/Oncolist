
import pandas as pd
import numpy as np
import time, os, shutil, re, community
import networkx as nx
import matplotlib.pyplot as plt
import scipy.spatial.distance as ssd
import scipy.cluster.hierarchy as sch

# import cluster_connect module
import cluster_connect

"""
 -------------------------------------------------------------

Author: Brin Rosenthal (sbrosenthal@ucsd.edu)

 -------------------------------------------------------------
"""

from Utils import HypergeomCalculator
from GO import GOLocusParser

from multiprocessing import Pool
from functools import partial

# import the authomatic GO annotation tools NOTE: CHANGE THIS PATH!!
import sys
#sys.path.append('/Users/brin/Google_Drive/UCSD/cluster_code/go_annotation')
#from HypergeomCalculator import *

def import_TCGA_data(path_file):
    '''
    function to import data and create network- return graph and edge list, input path to file (tsv)
    '''
    D_df = pd.read_csv(path_file, sep='\t', names=['var1', 'var2', 'corr', 'p'])
    nodes = np.union1d(D_df.var1, D_df.var2)

    # don't need to make big network- takes a long time
    edge_list_w = zip(list(D_df['var1']), list(D_df['var2']), list(np.abs(D_df['corr'])))  # try using absolute value of correlations

    return D_df, edge_list_w


def find_edges_thresh(edge_list_total, edge_thresh=0, gamma=1, weight_flag='on'):
    '''
    find edges < threshold and corresponding list of nodes

    find edges with weights less than a given threshold, the corresponding nodes,
    return edges, nodes, and graph constructed from these weighted edges and nodes

    NOTE: gamma and edge_thresh were set after analysis of gamma_scan (see cfncluster_gamma_scan.py), to optimize modularity and overlap fraction, while maintaining a large enough number of groups 5 < size < 500
    UPDATE 1/27/2016: edge_thresh and gamma defaults set to 0 and 1, respectively--> including clusters from multiple gammas


    '''

    if weight_flag == 'on':
        elarge = [(u, v, d**gamma) for (u, v, d) in edge_list_total if d > edge_thresh]
        #esmall=[(u,v,d) for (u,v,d) in edge_list_total if d['weight'] <=edge_thresh]
        # what are the corresponding nodes?
        nodetemp = []
        [nodetemp.append(u) for (u, v, d) in elarge]
        [nodetemp.append(v) for (u, v, d) in elarge]
    else:
        # if no weights, only return connecting nodes
        elarge=[(u, v) for (u, v, d) in edge_list_total if d > edge_thresh]
        # what are the corresponding nodes?
        nodetemp = []
        [nodetemp.append(u) for (u, v) in elarge]
        [nodetemp.append(v) for (u, v) in elarge]

    # how many edges in elarge?
    print('there are ' + str(len(elarge)) + ' edges with weight greater than ' + str(edge_thresh))

    nodetemp = pd.Series(nodetemp)
    nodesmall = list(nodetemp.unique())
    print('there are ' + str(len(nodesmall)) + ' corresponding nodes')

    # make the graph from nodesmall and elarge
    Gtemp = nx.Graph()
    Gtemp.add_nodes_from(nodesmall)
    Gtemp.add_weighted_edges_from(elarge)

    return elarge, nodesmall, Gtemp


def run_lancichinetti_clustering(Gtemp,data_path,code_path,results_folder,algorithm='louvain', num_c_reps = 2,remove_flag=True):

    '''
    This function calculates the clustering algorithm specified by 'algorithm'.  The source code must be downloaded
    and installed from https://sites.google.com/site/andrealancichinetti/software.

    Note, the code failed out of the box.  Had to change line 155 of 'wsarray.h'
    to: 'pair<int, double> * ww = new pair<int, double> [_size_];'

    See Lancichinetti's ReadMe doc for more info on how algorithms work

    beware: oslum algorithms are either VERY slow, or don't work at all

    returns partition
    '''

    # check if Gtemp is bipartite
    is_G_bipartite = nx.bipartite.is_bipartite(Gtemp)

    if is_G_bipartite:
        v1_nodes,v2_nodes = nx.bipartite.sets(Gtemp)
        v1map = dict(zip(v1_nodes,range(len(v1_nodes))))
        v2map = dict(zip(v2_nodes,range(len(v2_nodes))))
        v_all_map = v1map.copy()
        v_all_map.update(v2map)
    else:
        v_all_map = dict(zip(Gtemp.nodes(),range(len(Gtemp.nodes()))))

    Gtemp_mapped = nx.relabel_nodes(Gtemp,v_all_map)
    edge_list_mapped = nx.to_edgelist(Gtemp_mapped)
    e1mapped,e2mapped,weight = zip(*edge_list_mapped)
    weight_list = [x['weight'] for x in weight]

    # pick the right algorithm
    if algorithm=='oslom_undirected':
        # note: oslum is very slow
        pnum=0
    elif algorithm=='oslom_directed':
        pnum=1
    elif algorithm=='infomap_undirected':
        pnum=2
    elif algorithm=='infomap_directed':
        pnum=3
    elif algorithm=='louvain':
        pnum=4
    elif algorithm=='label_propagation':
        pnum=5
    elif algorithm=='hierarchical_infomap_undirected':
        pnum=6
    elif algorithm=='hierarchical_infomap_directed':
        pnum=7
    elif algorithm=='modularity_optimization':
        pnum=8

    edge_list_path = data_path[:-4] + '_edge_list.csv'
    edge_list_df = pd.DataFrame({'v1':e1mapped,'v2':e2mapped,'weight':weight_list})
    edge_list_df.to_csv(edge_list_path,sep=' ',index=False,header=False)

    if remove_flag:
        # check if the directory already exists, delete it if it does.  Otherwise the code throws an error
        if os.path.isdir(results_folder):
            shutil.rmtree(results_folder)

    command_line = "python " + code_path + " -n " + edge_list_path + " -p " + str(pnum) + " -f " +results_folder + " -c " + str(num_c_reps)
    os.system(command_line)

    # parse the results
    partition = parse_results_lancichinetti(results_folder,algorithm=algorithm)

    # translate back to correct ids
    v_all_map_r = {v: k for k, v in v_all_map.items()}
    # replace keys in partition
    partition = dict(partition)
    old_keys = partition.keys()
    for old_key in old_keys:
        new_key = v_all_map_r[old_key]
        partition[new_key] = partition.pop(old_key)
    partition = pd.Series(partition)

    return partition


def parse_results_lancichinetti(results_folder,algorithm='louvain'):
    '''
    This function parses the results from lancichinetti code (doesn't work for OSLOM algorithm yet...
    have to decide what to do about non-unique community membership)

    Returns pandas series object 'partition'
    '''

    results_file = results_folder + '/results_consensus/tp'
    with open(results_file, "r") as ins:
        group_id_dict = dict()
        count = -1
        for line in ins:

            if (algorithm=='hierarchical_infomap_undirected') or (algorithm=='hierarchical_infomap_directed'):
                count = count+1
                # inconsistent file for this algorithm
                line = re.split(r' ', line.rstrip(' '))
            elif (algorithm=='oslom_undirected') or (algorithm=='oslom_directed'):
                is_new_module = (line.find('module')>0)
                if is_new_module:
                    count = count+1
                else:
                    line = re.split(r' ', line.rstrip(' '))
            else:
                count = count+1
                line = re.split(r'\t+', line.rstrip('\t'))
            group_id_dict[count]=line[:-1]  # don't keep trailing \n

    # reverse the group_id_dict
    partition = dict()
    for g in group_id_dict.keys():
        node_list_temp = group_id_dict[g]
        for n in node_list_temp:
            if int(n) in partition.keys():

                partition[int(n)].append(g)
            else:
                partition[int(n)] = [g]
    partition = pd.Series(partition)

    return partition


def results_TCGA_cluster(data_path,code_path,results_path, algorithm='louvain',edge_thresh=0,gamma=1,cluster_size_min=5, cluster_size_max=2000, write_file_name='cluster_results.csv', print_flag=True):
    '''
    Function to process and cluster TCGA correlation files

    Inputs:
        - data_path:  path to the correlation file, including file, example: '/home/ec2-user/data/LIHC/mirna_vs_rnaseq.cor'
        - code_path:  path to location of 'select.py' function, example: '/home/ec2-user/code/clustering_programs_5_2'
        - results_path: path to storage of results, example:  '/home/ec2-user/results'
        - algorithm:  name of clustering algorithm to use.  Can be one of:
            - 'oslom_undirected'
            - 'infomap_undirected'
            - 'louvain'
            - 'label_propagation'
            - 'hierarchical_infomap_undirected'
            - 'modularity_optimization'
            (see https://sites.google.com/site/andrealancichinetti/software for more details)
        - edge_thresh:  edge weight cutoff (default= 0)
        - gamma:  tuning parameter for weights (default = 1--> works with all algorithms)
        - cluster_size_min:  minimum cluster size to include (default = 5)
        - cluster_size_max:  maximum cluster size to include (default = 2000)
        - write_file_name:  path and name to store results (example:  '/home/ec2-user/results/louvain_cluster_results.csv')
        - print_flag:  decide whether to print out progress (default = True)
    '''

    # import the data
    print('importing the data...')
    D_df, edge_list_total = import_TCGA_data(data_path)

    # calculate louvain clusters
    print('thresholding edges...')
    elarge,nodesmall,Gtemp = find_edges_thresh(edge_list_total, edge_thresh = edge_thresh,gamma=gamma)
    print('calculating optimal community partitions using modularity maximization...')
    #partition = community.best_partition(Gtemp)

    # check if Gtemp is bipartite
    is_G_bipartite = nx.bipartite.is_bipartite(Gtemp)

    results_folder = results_path + '/results_'+algorithm+'_temp'

    code_select = code_path+'/select.py'
    partition = run_lancichinetti_clustering(Gtemp,data_path,code_select,results_folder,algorithm=algorithm,num_c_reps=5)
    
    # calculate the true value counts (flatten the list of lists first)
    flat_part_values = [item for sublist in partition.values for item in sublist]
    flat_part_VC = pd.Series(flat_part_values).value_counts()

    # switch partition values to tuples, so value_counts() works
    part_values = [tuple(x) for x in partition.values]
    partition = pd.Series(part_values,list(partition.index))
    partition_VC = partition.value_counts()

    # set low co-occurence nodes to group -1
    keylist = partition.keys()
    allnodes = []
    allnodes.extend(D_df['var1'])
    allnodes.extend(D_df['var2'])
    allnodes = list(np.unique(allnodes))
    setdiff_nodes = np.setdiff1d(allnodes,keylist)
    for s in range(len(setdiff_nodes)):
        partition[setdiff_nodes[s]]=[-1]

    # setup data for output- only save within community edges
    partition = dict(partition)

    numedges = len(D_df.var1)
    numnodes = len(partition)

    node1list, node2list, corrlist, pvallist, groupidlist = [],[],[],[],[]
    for i in range(numedges):

        # print out some progress if print_flag True
        if print_flag:
            if (i%100000)==0:
                print('%.2f percent written' % (i/float(numedges)))

        key1 = D_df.var1[i]
        key2 = D_df.var2[i]

        # check how many groups key1 and key2 belong to
        num_groups_1 = len(partition[key1])
        num_groups_2 = len(partition[key2])

        groups_both = []
        groups_both.extend(partition[key1])
        groups_both.extend(partition[key2])
        groups_both = list(np.unique(groups_both))

        # fill in lists if node 1 and node 2 are in the same group
        for g in groups_both:
            if (g in partition[key1]) and (g in partition[key2]) and (g>-1) and (flat_part_VC[g]>=cluster_size_min) and (flat_part_VC[g]<=cluster_size_max):
                node1list.append(key1)
                node2list.append(key2)
                corrlist.append(D_df['corr'][i])
                pvallist.append(D_df['p'][i])
                groupidlist.append(g)

    # wrap results in a dataframe
    D_with_groups = pd.DataFrame({'var1':node1list,'var2':node2list,'corr':corrlist,'p':pvallist,'group_id':groupidlist})

    # trim the groups (connect periphery nodes to core nodes)
    D_trimmed = cluster_connect.trim_cluster_df(D_with_groups,num_edges_to_keep=20000)
    D_trimmed.index = range(len(D_trimmed))

    # sort the groups
    D_with_groups_sorted = sort_clusters(D_trimmed,partition,is_bipartite=is_G_bipartite,print_flag=print_flag)

    # write results to file
    D_with_groups_sorted.to_csv(write_file_name,sep='\t',index=False)


def local_modularity(G,node_list,weighted_tf=False):
    ''' Calculate the local modularity of a group of nodes.  Sum of all partition Lmods = total modularity'''
    # is graph weighted?

    if weighted_tf:
        degree_G = G.degree(G.nodes(),weight='weight')
    else:
        degree_G = G.degree(G.nodes())
    sub_G = G.subgraph(node_list)

    m2 = np.sum(degree_G.values()) # total number of edges in subgraph
    L_mod = 0
    for i in range(len(node_list)):
        for j in range(len(node_list)):
            nodei = node_list[i]
            nodej = node_list[j]
            # does the edge exist?
            if sub_G.has_edge(nodei,nodej):
                edge_data = sub_G.get_edge_data(nodei,nodej)
                if weighted_tf:
                    weight = edge_data['weight']
                else:
                    weight = 1
            else:
                weight = 0

            L_mod = L_mod + weight - degree_G[nodei]*degree_G[nodej]/float(m2)
    L_mod = L_mod/m2  # normalize it

    return L_mod


def sort_clusters(D_with_groups,partition,is_bipartite=False,print_flag=True,plot_flag=False):
    # input D_with_groups and partition from results_TCGA_cluster
    # is the network symmetric or bipartite? --> import this from Gtemp in 'results_TCGA_cluster'
    # return sorted dataframe

    # how many groups are there?
    groups = D_with_groups['group_id'].unique()
    num_groups = len(groups)
    v1temp = D_with_groups['var1']
    v2temp = D_with_groups['var2']
    v1temp = np.unique(v1temp)
    v2temp = np.unique(v2temp)
    num_overlap = np.intersect1d(v1temp,v2temp)

    # sort group_ids by corr, re-order dataframe
    corr_sorted_total,p_sorted_total = [],[]
    v1total,v2total = [],[]
    group_total = []
    group_count = 0
    for focal_group in groups:

        group_count += 1
        if print_flag:
            print('sorting group ' + str(group_count) + ' out of ' + str(num_groups))
        c_idx = list(D_with_groups[D_with_groups['group_id']==focal_group].index)

        vrow = D_with_groups['var1'][c_idx]
        vrow = np.unique(vrow)
        num_nodes_r = len(vrow)

        vcol = D_with_groups['var2'][c_idx]
        vcol = np.unique(vcol)
        num_nodes_c = len(vcol)

        vtot = []
        vtot.extend(vrow)
        vtot.extend(vcol)
        v_unique = np.unique(vtot)
        num_nodes_t = len(v_unique)
        v_map_tot = dict(zip(v_unique,range(len(v_unique))))
        v_map_tot_r = dict(zip(range(len(v_unique)),v_unique))

        v_map_row = dict(zip(vrow,range(num_nodes_r)))
        v_map_row_r = dict(zip(range(num_nodes_r),vrow))

        v_map_col = dict(zip(vcol,range(num_nodes_c)))
        v_map_col_r = dict(zip(range(num_nodes_c),vcol))

        # make corr_mat and p_mat symmetric if there is overlap between vrow and vcol
        if is_bipartite:
            corr_mat = np.zeros((num_nodes_r,num_nodes_c))
            p_mat = np.ones((num_nodes_r,num_nodes_c))

        else:
            corr_mat = np.zeros((num_nodes_t,num_nodes_t))
            p_mat = np.ones((num_nodes_t, num_nodes_t))

        for i in c_idx:
            v1 = D_with_groups['var1'][i]
            v2 = D_with_groups['var2'][i]

            # make it symmetric if there is overlap between vrow and vcol
            if is_bipartite:
                corr_mat[v_map_row[v1],v_map_col[v2]] = D_with_groups['corr'][i]
                p_mat[v_map_row[v1],v_map_col[v2]] = D_with_groups['p'][i]

            else:
                corr_mat[v_map_tot[v1],v_map_tot[v2]] = D_with_groups['corr'][i]
                p_mat[v_map_tot[v1],v_map_tot[v2]] = D_with_groups['p'][i]
                corr_mat[v_map_tot[v2],v_map_tot[v1]] = D_with_groups['corr'][i]  # make it symmetric
                p_mat[v_map_tot[v2],v_map_tot[v1]] = D_with_groups['p'][i]  # make it symmetric


        if (not is_bipartite) and len(v_map_tot)>1:
            #DRmat = ssd.squareform(ssd.pdist(np.abs(corr_mat)))
            DRmat = slow_dist_mat(np.abs(corr_mat))  # replaced dist mat calc because indices were wrong

            row_Z = sch.linkage(DRmat)
            row_idx = sch.leaves_list(row_Z)
        elif is_bipartite and len(v_map_row)>1:
            #DRmat = ssd.squareform(ssd.pdist(np.abs(corr_mat)))
            DRmat = slow_dist_mat(np.abs(corr_mat))

            row_Z = sch.linkage(DRmat)
            row_idx = sch.leaves_list(row_Z)
        else:
            # don't sort if there is only one row
            row_idx=0


        if (not is_bipartite) and len(v_map_tot)>1:
            #DCmat = ssd.squareform(ssd.pdist(np.abs(np.transpose(corr_mat))))
            DCmat = slow_dist_mat(np.transpose(np.abs(corr_mat)))

            col_Z = sch.linkage(DCmat)
            col_idx = sch.leaves_list(col_Z)
        elif is_bipartite and len(v_map_col)>1:
            #DCmat = ssd.squareform(ssd.pdist(np.abs(np.transpose(corr_mat))))
            DCmat = slow_dist_mat(np.transpose(np.abs(corr_mat)))

            col_Z = sch.linkage(DCmat)
            col_idx = sch.leaves_list(col_Z)
        else:
            # don't sort if there is only one column
            col_idx = 0

        corr_shape = np.shape(corr_mat)
        print(corr_shape)
        numrows = corr_shape[0]
        numcols = corr_shape[1]

        corr_mat_sorted = corr_mat
        p_mat_sorted = p_mat
        if (numrows>1) and (numcols>1):
            # only need to sort if corr_mat has more than one row/col
            corr_mat_sorted = corr_mat_sorted[row_idx,:]
            corr_mat_sorted = corr_mat_sorted[:,col_idx]


            p_mat_sorted = p_mat_sorted[row_idx,:]
            p_mat_sorted = p_mat_sorted[:,col_idx]

        # reshape sorted corr_mat, save to new df?
        corr_mat_sorted_flat = np.ravel(corr_mat_sorted)
        p_mat_sorted_flat = np.ravel(p_mat_sorted)

        if plot_flag:
            plt.matshow(corr_mat_sorted,cmap='bwr',vmin=-1,vmax=1)

        # also save row/col gene ids
        mgrid_test = np.mgrid[0:numrows,0:numcols]
        mgrid_rows = mgrid_test[0]
        mgrid_cols = mgrid_test[1]
        row_flat = np.ravel(mgrid_rows)
        col_flat = np.ravel(mgrid_cols)

        # then translate to gene ids
        v1list = []
        v2list = []

        # handle symmetry
        if is_bipartite:
            if numrows>1:
                v1list = [v_map_row_r[row_idx[r]] for r in row_flat]
            else:
                v1list = [v_map_row_r[r] for r in row_flat]
            if numcols>1:
                v2list = [v_map_col_r[col_idx[c]] for c in col_flat]
            else:
                v2list = [v_map_col_r[c] for c in col_flat]

        else:
            v1list = [v_map_tot_r[row_idx[r]] for r in row_flat]
            v2list = [v_map_tot_r[col_idx[c]] for c in col_flat]

        # also save group ids
        group_list = (np.ones((1,len(v1list)))*focal_group)
        group_list = list(group_list[0])

        corr_sorted_total.extend(corr_mat_sorted_flat)
        p_sorted_total.extend(p_mat_sorted_flat)
        v1total.extend(v1list)
        v2total.extend(v2list)
        group_total.extend(group_list)

    D_with_groups_sorted = pd.DataFrame({'corr':corr_sorted_total,'p':p_sorted_total,
                                              'var1':v1total,'var2':v2total,'group_id':group_total})

    return D_with_groups_sorted

def slow_dist_mat(C):
    '''
    Helper function to calculate the distance matrix (using squareform and pdist resulted in re-ordering indices)

    '''
    dist = np.zeros((len(C),len(C)))
    for i in range(len(C)-1):
        p1 = C[i,:]
        for j in range(i+1,len(C)):
            p2 = C[j,:]
            dist[i,j] = ssd.cdist([p1],[p2])[0][0]
            dist[j,i] = dist[i,j]
    return dist

def cal_mirna_enrichment(Gtemp, GO_ID_list, total_unique_gene, GO_Term_list, focal_node):
    enrichment_mirna = dict()
    # find neighbors of focal_node
    if focal_node in Gtemp.nodes():
        f_neighbors = Gtemp.neighbors(focal_node)
        if len(f_neighbors)>20:
            print(focal_node + ' has ' + str(len(f_neighbors)) + ' neighbors')

            # annotate this list
            enriched_list = HypergeomCalculator.calc_enrichment(f_neighbors, GO_ID_list, total_unique_gene, GO_Term_list)

            GO_temp = dict()
            for enriched_item in enriched_list:
                if enriched_item['qvalue'] > 10:
                    GO_temp[enriched_item['go_id']] = enriched_item['qvalue']
                    if True:
                        print(enriched_item['name'] + ': q-value = ' + str(enriched_item['qvalue']))

            # only create a key for focal node if it has some significant entries
            if len(GO_temp) > 0:
                enrichment_mirna[focal_node] = GO_temp

    return enrichment_mirna

def save_ivanovska_clusters(data_path,edge_thresh=.5,gamma=1,qthresh=10, cluster_size_min=5,
                    print_flag=True,plot_flag=False,write_file_name='GO_clusters_temp.csv'):

    '''

    This is a function that implements the Ivanovska clustering method of annotating var2 terms which are highly associated
    with var1 terms, annotating against the gene ontology, then clustering this matrix.

    Saves an edge list which contains var1 terms with significant annotations, the terms they annotate to, their q-value,
    and the group they belong to.  The edge list has been sorted so that the top annotating terms/genes appear highest in
    each cluster.

    arguments:
        - data_path: path to correlation edge list (example: data_path = '/Users/brin/Documents/TCGA_data/LIHC/mirna_vs_rnaseq.cor')
        - edge_thresh: cutoff for how highly associated var2 genes must be to each var1 (default = .5)
        - gamma:  parameter to scale correlations (default = 1.. probably don't want to change this)
        - qthresh:  cutoff for significance of enriched GO terms (default = 10)
        - cluster_size_min:  minimum cluster size to save
        - print_flag:  print some diagnostics? (default = True)
        - plot_flag:  plot the total heatmap? (default = False)
        - write_file_name:  where should we write the final file?  (default = 'GO_clusters_temp.csv')

    returns: None

    '''
    #data_path = '/Users/brin/Documents/TCGA_data/LIHC/mirna_vs_rnaseq.cor'
    #edge_thresh = .5
    #gamma = 1
    #qthresh = 10  # minimum enrichment significance to record
    #print_flag = True
    #plot_flag = False
    #write_file_name = 'GO_clusters_temp.csv'
    #cluster_size_min = 5

    OV_df, edge_list = import_TCGA_data(data_path) # import the data

    elarge, nodesmall, Gtemp = find_edges_thresh(edge_list,edge_thresh=edge_thresh,gamma=gamma) # build the graph

    # import GO annotation tools (this takes a little time) NOTE: CHANGE THESE PATHS
    go_gene_file = '/shared/workspace/SearchEngineProject/GO/GO2all_locus.txt'
    gene_info_file = '/shared/workspace/SearchEngineProject/GO/Homo_sapiens.gene_info'
    go_term_file = '/shared/workspace/SearchEngineProject/GO/go.obo'
    GO_ID_list, total_unique_gene, GO_Term_list = GOLocusParser.parse(go_gene_file, gene_info_file, go_term_file)

    # write a function to annotate genes which correlate highly with any mirna (e.g. neighbors in the graph)
    #nodes_A,nodes_B = nx.bipartite.sets(Gtemp)
    nodes_A = list(OV_df['var1'].unique())
    nodes_B = list(OV_df['var2'].unique())

    test_nodes = nodes_A[-5:]
    func = partial(cal_mirna_enrichment, Gtemp, GO_ID_list, total_unique_gene, GO_Term_list)
    pool = Pool(processes=2)
    enrichment_list = pool.map(func, test_nodes)

    pool.close()
    pool.join()

    enrichment_mirna = {}
    for result in enrichment_list:
        for key in result:
            enrichment_mirna.update({key:result.get(key)})

    if len(enrichment_mirna)>2:
        GO_unique = [enrichment_mirna[n].keys() for n in enrichment_mirna.keys()]
        # flatten the list
        GO_unique = [item for sublist in GO_unique for item in sublist]
        GO_unique = np.unique(GO_unique)

        print(len(GO_unique))
        # make a dictionary to map from GO_unique to index, and mirna to index
        GO_map = dict(zip(GO_unique,range(len(GO_unique))))
        GO_map_r = dict(zip(range(len(GO_unique)),GO_unique))
        mirna_map = dict(zip(enrichment_mirna.keys(),range(len(enrichment_mirna.keys()))))
        mirna_map_r = dict(zip(range(len(enrichment_mirna.keys())),enrichment_mirna.keys()))

        # now make the correlation matrix: GO_mirna
        GO_mirna = np.zeros((len(GO_map),len(mirna_map)))
        # loop over mirnas
        for n in enrichment_mirna.keys():
            mirna_idx = mirna_map[n]
            # loop over GO terms in each mirna
            for g in enrichment_mirna[n].keys():
                GO_idx = GO_map[g]

                qtemp = enrichment_mirna[n][g]

                # fill in the matrix
                GO_mirna[GO_idx,mirna_idx] = qtemp

            # now try clustering using louvain- what do we get?
            go_mirna_for_graph = dict()
            qvec = []
            for n in enrichment_mirna.keys():
                # loop over GO terms in each mirna
                dict_temp = dict()
                for g in enrichment_mirna[n].keys():

                    qtemp = enrichment_mirna[n][g]
                    qvec.append(qtemp)

                    #qtemp = np.exp(-qtemp**2)
                    #qtemp = round(qtemp*5)
                    qtemp = qtemp**gamma
                    # fill in the dict
                    dict_temp[g]={'weight':qtemp}
                go_mirna_for_graph[n] = dict_temp
            G_go_mirna = nx.from_dict_of_dicts(go_mirna_for_graph)

        #partition = community.best_partition(G_go_mirna)
        dendo = community.generate_dendrogram(G_go_mirna)
        partition = community.partition_at_level(dendo, 0)
        partition = pd.Series(partition)


        partition_sort = partition.sort(axis=0,inplace=False)
        idx_sort = list(partition_sort.index)
        idx_mirna = np.array([m for m in idx_sort if (m in mirna_map.keys())]) # np.intersect1d(idx_sort,mirna_map.keys())
        grp_mirna = np.array([partition_sort[m] for m in idx_sort if (m in mirna_map.keys())])
        idx_GO = np.array([g for g in idx_sort if (g in GO_map.keys())])
        grp_GO = np.array([partition[g] for g in idx_sort if (g in GO_map.keys())])

        group_ids = list(np.unique(partition_sort))
        col_idx = []
        row_idx = []
        corr_sorted_total, gene_list_total,GO_term_list_total,group_total = [],[],[],[]
        for g in group_ids:
            # sort individual groups by mean GO value in each row/column
            idx_mirna_focal = idx_mirna[grp_mirna==g]
            col_temp = np.array([mirna_map[i] for i in idx_mirna_focal])
            mean_mirna_focal = np.mean(GO_mirna[:,col_temp],0)
            mean_sort = np.argsort(mean_mirna_focal)
            mean_sort = mean_sort[::-1] # sort descending
            col_temp = col_temp[mean_sort]

            # append to col_idx
            col_idx.extend(col_temp)

            idx_GO_focal = idx_GO[grp_GO==g]
            row_temp = np.array([GO_map[i] for i in idx_GO_focal])
            print "break point!!!!"
            print idx_mirna_focal
            if len(row_temp)>0:
                # check that row_temp isn't empty
                mean_GO_focal = np.mean(GO_mirna[row_temp,:],1)
                mean_sort = np.argsort(mean_GO_focal)
                mean_sort = mean_sort[::-1]  # sort descending
                row_temp = row_temp[mean_sort]

            # append to col_idx
            row_idx.extend(row_temp)

            # save out flattened sections of correlation matrix as clusters
            # only save if there are more than cluster_size_min items in cluster
            cluster_size = np.sum(partition==g)
            if cluster_size>cluster_size_min:
                corr_mat_focal = GO_mirna
                corr_mat_focal = corr_mat_focal[row_temp,:]
                corr_mat_focal = corr_mat_focal[:,col_temp]

                corr_mat_focal_flat = np.ravel(corr_mat_focal)

                corr_shape = np.shape(corr_mat_focal)
                print(corr_shape)
                numrows = corr_shape[0]
                numcols = corr_shape[1]

                mgrid_test = np.mgrid[0:numrows,0:numcols]
                mgrid_rows = mgrid_test[0]
                mgrid_cols = mgrid_test[1]
                row_flat = np.ravel(mgrid_rows)
                col_flat = np.ravel(mgrid_cols)

                # then translate to gene ids/ GO term names
                gene_list = []
                gene_list = [mirna_map_r[col_temp[i]] for i in col_flat]
                GO_term_list = [GO_map_r[row_temp[i]] for i in row_flat]

                # also save the group list
                group_list = (np.ones((1,len(gene_list)))*g)
                group_list = list(group_list[0])

                corr_sorted_total.extend(corr_mat_focal_flat)
                gene_list_total.extend(gene_list)
                GO_term_list_total.extend(GO_term_list)
                group_total.extend(group_list)

        GO_name_list_total=[GO_Term_list[x][0] for x in GO_term_list_total]
        D_with_groups_sorted = pd.DataFrame({'qvalue':corr_sorted_total,'gene_name':gene_list_total,
                                            'GO_term':GO_term_list_total,'GO_name':GO_name_list_total,
                                             'group_id':group_total})
    else:
        # save out dummy dataframe if there are not enough enriched terms
        D_with_groups_sorted = pd.DataFrame({'qvalue':np.nan,'gene_name':np.nan,
                                            'GO_term':np.nan, 'GO_name':np.nan,
                                            'group_id':np.nan},index=[0])

    # write results to file
    D_with_groups_sorted.to_csv(write_file_name,sep='\t',index=False)

    go_mirna_L = GO_mirna
    go_mirna_L = go_mirna_L[row_idx,:]
    go_mirna_L = go_mirna_L[:,col_idx]

    if plot_flag:
        plt.figure(figsize=(20,50))
        plt.matshow(go_mirna_L,fignum=False,cmap='jet',aspect='auto',vmin=0,vmax=30)
        xtick_labels = [mirna_map_r[i] for i in col_idx]
        ytick_labels = [GO_map_r[i] for i in row_idx]
        plt.xticks(range(len(xtick_labels)),xtick_labels,rotation=90)
        plt.yticks(range(len(ytick_labels)),ytick_labels,fontsize=6)
        plt.grid('off')

        #plt.savefig('/Users/brin/Google_Drive/UCSD/update_16_01/LIHC_go_mirna_louvain.png',dpi=150)
