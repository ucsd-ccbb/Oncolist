''' This module contains functions for creating and operation on author-gene bipartite networks'''

# import some useful packages

#import pandas as pd
from pandas import read_csv as pd_read_cvs
from pandas import Series as pd_Series
from pandas import DataFrame as pd_DataFrame
import numpy as np
import networkx as nx
import community
import matplotlib.pyplot as plt
import time
import app
import pymongo

def create_author_gene_groupby(input_filename='author_vs_gene.edges.txt'):

    # load author-gene dataframe
    print('loading author gene data...')
    AG_df = pd_read_cvs(input_filename,sep='\t',names=['authors','genes','weight','npubs'])

    # create author-gene groubpy (this takes a few minutes)
    print('grouping authors by genes...')
    #authors_GB_genes = AG_df.authors.groupby(AG_df['genes']).value_counts()

    # create author-weight pair
    authors_weight = zip(AG_df['authors'],AG_df['weight'])
    AG_df['authors_weight'] = authors_weight
    authors_GB_genes = AG_df.authors_weight.groupby(AG_df['genes']).value_counts()


    # save groupby object as pickle
    print('saving output....')
    authors_GB_genes.to_pickle('authors_GB_genes.txt')

def analyze_AG_bipartite_network(genes, authors_GB_genes, pub_thresh=1,
                                 save_file_name = "author_gene_bp.json", plot_flag=False):
    gene_list = genes.split(',')

    t0 = time.time()

    # unpickle groupby object
    #authors_GB_genes = pd.read_pickle(author_gene_GB_fname)
    authors_GB_genes = app.authors_GB_genes_loaded

    # get rid of invalid genes in gene_list
    new_gene_list = []
    for gene in gene_list:
        if gene in authors_GB_genes:
            new_gene_list.append(gene)

    gene_list = new_gene_list

    # create list of all authors/weights who have published on at least one gene in gene_list
    AW_list_total = []
    for gene in gene_list:
        AW_list_total.extend(list(authors_GB_genes[gene].index))
    AW_list_total = zip(*AW_list_total)

    author_list_total = AW_list_total[0]
    weight_list_total = AW_list_total[1]


    print(time.time()-t0)


    author_list_total = pd_Series(author_list_total)
    weight_list_total = pd_Series(weight_list_total,index=author_list_total)

    # take the mean of duplicate entries
    df_temp = pd_DataFrame({'weight':list(weight_list_total),'author':list(author_list_total)},index=range(len(author_list_total)))
    AW_gb_temp = df_temp.weight.groupby(df_temp['author']).mean()

    author_list_total = list(AW_gb_temp.index)
    weight_list_total = list(AW_gb_temp.values)
    weight_list_total = pd_Series(weight_list_total,index=author_list_total)


    # make a dataframe, indexed by authors in author_list_total, with columns = entries in gene_list
    author_gene_df = pd_DataFrame(np.zeros([len(author_list_total),len(gene_list)]),
                                           index = author_list_total,columns=gene_list)


    print(time.time()-t0)

    # fill in the dataframe
    for gene in gene_list:
        #print(gene)
        temp = list(authors_GB_genes[gene].index)
        temp= zip(*temp)
        authors_temp = list(np.unique(temp[0]))
        author_gene_df[gene][authors_temp]=weight_list_total[authors_temp]

    print(time.time()-t0)

    # add a column for total weight
    author_gene_df['total_weight'] = np.sum(np.array(author_gene_df),1)

    author_gene_df.sort('total_weight',inplace=True, ascending=False)

    # next, convert this dataframe into bipartite network
    # make the small bipartite graph
    author_gene_bp = nx.Graph()

    # pick out authors which have published on > pub_thresh genes in gene_list
    index_temp = list(author_gene_df['total_weight'][author_gene_df['total_weight']>pub_thresh].index)

    # only allow 200 authors max
    if len(index_temp)>200:
        author_nodes = index_temp[0:200]
    else:
        author_nodes = index_temp
    #index_temp = list(author_gene_df['total_num'].index)
    #author_nodes = index_temp[0:num_authors]

    print(time.time()-t0)

    for gene in gene_list:
        for author in author_nodes:
            # only add a link if connection exists
            if author_gene_df[gene][author]>0:
                author_gene_bp.add_edge(gene,author)

    # add all genes in gene_list in case none of them come up
    author_gene_bp.add_nodes_from(gene_list)

    # now apply clustering algo to the bipartite graph
    partition = community.best_partition(author_gene_bp)
    partition = pd_Series(partition)
    col_temp_authors = partition[author_nodes]
    col_temp_genes = partition[gene_list]
    col_temp = partition[author_gene_bp.nodes()]

    if plot_flag:
        # plot graph if plot_flag = True
        plt.figure(figsize=[15,15])
        pos = nx.spring_layout(author_gene_bp,k=.3)
        #nx.draw(author_gene_bp,pos=pos,alpha=.5,node_size=100,node_color = col_temp,cmap='Paired')

        gene_list = list(gene_list)
        nx.draw_networkx_nodes(author_gene_bp,nodelist=author_nodes, node_color = col_temp_authors,
                               cmap='Paired',pos=pos,alpha=.5,node_size=100);
        nx.draw_networkx_nodes(author_gene_bp,nodelist=gene_list, node_color = col_temp_genes,
                               cmap='Paired',pos=pos,alpha=.5,node_size=200,node_shape='s');
        nx.draw_networkx_edges(author_gene_bp,pos=pos,alpha=.1);
        node_subset_dict = dict(zip(index_temp[0:20],index_temp[0:20]))
        gene_subset_dict = dict(zip(gene_list,gene_list))
        temp = node_subset_dict.update(gene_subset_dict)
        nx.draw_networkx_labels(author_gene_bp,pos=pos,labels=node_subset_dict);


    # Set up json for saving
    # what should the colors be??
    num_communities = len(np.unique(col_temp))
    color_list = plt.cm.gist_rainbow(np.linspace(0, 1, num_communities))

    # blend the community colors (so that to-nodes are a mixture of all the communities they belong to)
    rfrac,gfrac,bfrac=calc_community_fraction(author_gene_bp,author_nodes,gene_list,partition,color_list)

    # save network in json format
    nodes = author_gene_bp.nodes()
    numnodes = len(nodes)
    edges=author_gene_bp.edges()
    numedges = len(edges)
    #nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n)} for n in nodes]
    nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n),
                  "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]
    node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges
    edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]]} for i in range(numedges)]

    #import json
    json_graph = {"directed": False, "nodes": nodes_dict, "links":edges_dict}
    #json.dump(json_graph,open(save_file_name,'w'))

    print(time.time()-t0)

    return json_graph



def analyze_AG_bipartite_network_exp(genes, authors_GB_genes, pub_thresh=1,
                                 save_file_name = "author_gene_bp.json", plot_flag=False):

    gene_list = genes.split(',')

    t0 = time.time()

    # unpickle groupby object
    #authors_GB_genes = pd.read_pickle(author_gene_GB_fname)
    authors_GB_genes = app.authors_GB_genes_loaded

    # get rid of invalid genes in gene_list
    new_gene_list = []
    for gene in gene_list:
        if gene in authors_GB_genes:
            new_gene_list.append(gene)

    gene_list = new_gene_list

    # create list of all authors who have published on at least one gene in gene_list
    author_list_total = []
    for gene in gene_list:
        author_list_total.extend(list(authors_GB_genes[gene].index))

    print(time.time()-t0)


    author_list_total = pd_Series(author_list_total)
    authors_unique = np.unique(author_list_total)

    print(time.time()-t0)

    # make a dataframe, indexed by authors in author_list_total, with columns = entries in gene_list
    author_gene_df = pd_DataFrame(np.zeros([len(authors_unique),len(gene_list)]),
                                           index = authors_unique,columns=gene_list)

    print(time.time()-t0)

    # fill in the dataframe
    for gene in gene_list:
        #print(gene)
        authors_temp = list(authors_GB_genes[gene].index)
        author_gene_df[gene][authors_temp]=1

    print(time.time()-t0)

    # add a column for total number of genes
    num_genes = author_list_total.value_counts()
    author_gene_df['total_num'] = num_genes

    author_gene_df.sort('total_num',inplace=True, ascending=False)

    # next, convert this dataframe into bipartite network
    # make the small bipartite graph
    author_gene_bp = nx.Graph()

    # pick out authors which have published on > pub_thresh genes in gene_list
    index_temp = list(author_gene_df['total_num'][author_gene_df['total_num']>pub_thresh].index)

    # only allow 200 authors max
    if len(index_temp)>200:
        author_nodes = index_temp[0:200]
    else:
        author_nodes = index_temp
    #index_temp = list(author_gene_df['total_num'].index)
    #author_nodes = index_temp[0:num_authors]

    print(time.time()-t0)

    for gene in gene_list:
        for author in author_nodes:
            # only add a link if connection exists
            if author_gene_df[gene][author]==1:
                author_gene_bp.add_edge(gene,author)

    # add all genes in gene_list in case none of them come up
    author_gene_bp.add_nodes_from(gene_list)

    # now apply clustering algo to the bipartite graph
    partition = community.best_partition(author_gene_bp)
    partition = pd_Series(partition)
    col_temp_authors = partition[author_nodes]
    col_temp_genes = partition[gene_list]
    col_temp = partition[author_gene_bp.nodes()]

    if plot_flag:
        # plot graph if plot_flag = True
        plt.figure(figsize=[15,15])
        pos = nx.spring_layout(author_gene_bp,k=.3)
        #nx.draw(author_gene_bp,pos=pos,alpha=.5,node_size=100,node_color = col_temp,cmap='Paired')

        gene_list = list(gene_list)
        nx.draw_networkx_nodes(author_gene_bp,nodelist=author_nodes, node_color = col_temp_authors,
                               cmap='Paired',pos=pos,alpha=.5,node_size=100);
        nx.draw_networkx_nodes(author_gene_bp,nodelist=gene_list, node_color = col_temp_genes,
                               cmap='Paired',pos=pos,alpha=.5,node_size=200,node_shape='s');
        nx.draw_networkx_edges(author_gene_bp,pos=pos,alpha=.1);
        node_subset_dict = dict(zip(index_temp[0:20],index_temp[0:20]))
        gene_subset_dict = dict(zip(gene_list,gene_list))
        temp = node_subset_dict.update(gene_subset_dict)
        nx.draw_networkx_labels(author_gene_bp,pos=pos,labels=node_subset_dict);


    # Set up json for saving
    # what should the colors be??
    num_communities = len(np.unique(col_temp))
    color_list = plt.cm.gist_rainbow(np.linspace(0, 1, num_communities))

    # blend the community colors (so that to-nodes are a mixture of all the communities they belong to)
    rfrac,gfrac,bfrac=calc_community_fraction(author_gene_bp,author_nodes,gene_list,partition,color_list)

    # save network in json format
    nodes = author_gene_bp.nodes()
    numnodes = len(nodes)
    edges=author_gene_bp.edges()
    numedges = len(edges)
    #nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n)} for n in nodes]
    nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n),
                  "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]
    node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges
    edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]]} for i in range(numedges)]

    import json
    json_graph = {"directed": False, "nodes": nodes_dict, "links":edges_dict}
    json.dump(json_graph,open(save_file_name,'w'))

    print(time.time()-t0)

    return json_graph

def analyze_AG_bipartite_network_working_jan_20_2016(genes, authors_GB_genes, pub_thresh=1,
                                 save_file_name = "author_gene_bp.json", plot_flag=False):
    gene_list = genes.split(',')
    #if(len(gene_list) )

    t0 = time.time()

    # unpickle groupby object
    #authors_GB_genes = pd.read_pickle(author_gene_GB_fname)
    authors_GB_genes = app.authors_GB_genes_loaded

    # create list of all authors who have published on at least one gene in gene_list
    author_list_total = []
    for gene in gene_list:
        if(gene in authors_GB_genes):
            author_list_total.extend(list(authors_GB_genes[gene].index))

    print(time.time()-t0)


    author_list_total = pd_Series(author_list_total)
    authors_unique = np.unique(author_list_total)

    print(time.time()-t0)

    # make a dataframe, indexed by authors in author_list_total, with columns = entries in gene_list
    author_gene_df = pd_DataFrame(np.zeros([len(authors_unique),len(gene_list)]),
                                           index = authors_unique,columns=gene_list)

    print(time.time()-t0)

    # fill in the dataframe
    for gene in gene_list:
        #print(gene)
        if(gene in authors_GB_genes):
            authors_temp = list(authors_GB_genes[gene].index)
            author_gene_df[gene][authors_temp]=1

    print(time.time()-t0)

    # add a column for total number of genes
    num_genes = author_list_total.value_counts()
    author_gene_df['total_num'] = num_genes

    author_gene_df.sort('total_num',inplace=True, ascending=False)
    
    # next, convert this dataframe into bipartite network
    # make the small bipartite graph
    author_gene_bp = nx.Graph()
    
    # pick out authors which have published on > pub_thresh genes in gene_list
    index_temp = list(author_gene_df['total_num'][author_gene_df['total_num']>pub_thresh].index)
    
    # only allow 200 authors max
    if len(index_temp)>200:
        author_nodes = index_temp[0:200]
    else:
        author_nodes = index_temp
    #index_temp = list(author_gene_df['total_num'].index)
    #author_nodes = index_temp[0:num_authors]

    print(time.time()-t0)
    
    for gene in gene_list:
        for author in author_nodes:
            # only add a link if connection exists
            if author_gene_df[gene][author]==1:
                author_gene_bp.add_edge(gene,author)

    # add all genes in gene_list in case none of them come up
    author_gene_bp.add_nodes_from(gene_list)
    
    # now apply clustering algo to the bipartite graph
    partition = community.best_partition(author_gene_bp)
    partition = pd_Series(partition)
    col_temp_authors = partition[author_nodes]
    col_temp_genes = partition[gene_list]
    col_temp = partition[author_gene_bp.nodes()]
    
    if plot_flag:
        # plot graph if plot_flag = True
        plt.figure(figsize=[15,15])
        pos = nx.spring_layout(author_gene_bp,k=.3)
        #nx.draw(author_gene_bp,pos=pos,alpha=.5,node_size=100,node_color = col_temp,cmap='Paired')

        gene_list = list(gene_list)
        nx.draw_networkx_nodes(author_gene_bp,nodelist=author_nodes, node_color = col_temp_authors,
                               cmap='Paired',pos=pos,alpha=.5,node_size=100);
        nx.draw_networkx_nodes(author_gene_bp,nodelist=gene_list, node_color = col_temp_genes,
                               cmap='Paired',pos=pos,alpha=.5,node_size=200,node_shape='s');
        nx.draw_networkx_edges(author_gene_bp,pos=pos,alpha=.1);
        node_subset_dict = dict(zip(index_temp[0:20],index_temp[0:20]))
        gene_subset_dict = dict(zip(gene_list,gene_list))
        temp = node_subset_dict.update(gene_subset_dict)
        nx.draw_networkx_labels(author_gene_bp,pos=pos,labels=node_subset_dict);
        
        
    # Set up json for saving
    # what should the colors be??
    num_communities = len(np.unique(col_temp))
    color_list = plt.cm.gist_rainbow(np.linspace(0, 1, num_communities))
    
    # blend the community colors (so that to-nodes are a mixture of all the communities they belong to)
    rfrac,gfrac,bfrac=calc_community_fraction(author_gene_bp,author_nodes,gene_list,partition,color_list)
    
    # save network in json format
    nodes = author_gene_bp.nodes()
    numnodes = len(nodes)
    edges=author_gene_bp.edges()
    numedges = len(edges)
    #nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n)} for n in nodes]
    nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n),
                  "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]
    node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges
    edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]]} for i in range(numedges)]

    import json
    json_graph = {"directed": False, "nodes": nodes_dict, "links":edges_dict}
    json.dump(json_graph,open(save_file_name,'w'))
    
    print(time.time()-t0)
        
    return json_graph
        
        
def get_gene_gene_json(cluster_id):
    client = pymongo.MongoClient()
    db = client.cache

    heat_map_graph = db.heat_map_graph
    cluster_id_no_zero = str(cluster_id).replace('.0', '')

    heat_map_found = heat_map_graph.find_one({'clusterId': 'cluster' + cluster_id_no_zero})

    if(heat_map_found is not None):
        return heat_map_found['heat_map']
    else:
        return {'directed': False, 'nodes': [], 'links': []}

def save_gene_gene_json(input_file_name, out_file_start, cluster_id, color_type='clustering_coefficient', colormap='OrRd'):
    '''
    this function takes a processed cluster file ('input_file_name': output of process clustering results in cluster_analysis_module)
    and saves a json file for every community in the file, starting with 'out_file_start'.  'input_file_name' and 'out_file_start'
    should be prepended with location.
    '''

    # first load in a network (edge list)
    edge_list_df = pd_read_csv(input_file_name,sep='\t')

    group_ids = np.unique(edge_list_df['group_id'])

    for focal_group in group_ids:
        print focal_group

        save_file_name = out_file_start + '_' + str(int(focal_group)) + '.json'

        idx_group = (edge_list_df['group_id']==focal_group)
        idx_group = list(edge_list_df['group_id'][idx_group].index)

        # make a network out of it

        #edge_list = [(edge_list_df['var1'][i], edge_list_df['var2'][i], np.abs(edge_list_df['corr'][i])) for i in idx_group if edge_list_df['corr'][i] !=0]
        edge_list = [(edge_list_df['var1'][i], edge_list_df['var2'][i], edge_list_df['corr'][i]) for i in idx_group if edge_list_df['corr'][i] !=0]

        Gsmall = nx.Graph()
        Gsmall.add_weighted_edges_from(edge_list)

        nodes = Gsmall.nodes()
        numnodes = len(nodes)
        edges=Gsmall.edges(data=True)
        numedges = len(edges)
        if color_type=='community':
            partition = community.best_partition(Gsmall)

            partition = pd_Series(partition)
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






        # save network in json format
        #nodes = Gsmall.nodes()
        #numnodes = len(nodes)
        #edges=Gsmall.edges(data=True)
        #numedges = len(edges)
        #nodes_dict = [{"id":n,"com":col_temp[n],"degree":author_gene_bp.degree(n)} for n in nodes]
        #nodes_dict = [{"id":n,"com":col_temp[n],"degree":Gsmall.degree(n),
        #              "rfrac":rfrac[n]*255,"gfrac":gfrac[n]*255,"bfrac":bfrac[n]*255} for n in nodes]



        node_map = dict(zip(nodes,range(numnodes)))  # map to indices for source/target in edges
        edges_dict = [{"source":node_map[edges[i][0]], "target":node_map[edges[i][1]], "weight":edges[i][2]['weight']} for i in range(numedges)]

        import json
        json_graph = {"directed": False, "nodes": nodes_dict, "links":edges_dict}


        client = pymongo.MongoClient()
        db = client.cache

        heat_maps = db.heat_map_graph

        a = {
            'clusterId': 'cluster' + str(int(focal_group)),
            'heat_map': json.dumps(json_graph) #heat_map_ordered_transposed
        }

        #heat_maps.save(a)

        #json.dump(json_graph,open(save_file_name,'w'))



def calc_clustering_coefficient(G,cmap):
    # this function calculates the clustering coefficient of each node, and returns colors corresponding to these values
    local_CC = nx.clustering(G,G.nodes())
    local_CC_scale = [round(local_CC[key]*float(255)) for key in local_CC.keys()]
    local_CC_scale = pd_Series(local_CC_scale,index=G.nodes())
    rfrac = [cmap(int(x))[0] for x in local_CC_scale]
    gfrac = [cmap(int(x))[1] for x in local_CC_scale]
    bfrac = [cmap(int(x))[2] for x in local_CC_scale]
    rfrac = pd_Series(rfrac,index=G.nodes())
    gfrac = pd_Series(gfrac,index=G.nodes())
    bfrac = pd_Series(bfrac,index=G.nodes())

    return rfrac,gfrac,bfrac

def calc_betweenness_centrality(G,cmap):
    # this function calculates the betweenness centrality of each node, and returns colors corresponding to these values
    local_BC = nx.betweenness_centrality(G)
    local_BC_scale = [round(local_BC[key]*float(255)) for key in local_BC.keys()]
    local_BC_scale = pd_Series(local_BC_scale,index=G.nodes())
    rfrac = [cmap(int(x))[0] for x in local_BC_scale]
    gfrac = [cmap(int(x))[1] for x in local_BC_scale]
    bfrac = [cmap(int(x))[2] for x in local_BC_scale]
    rfrac = pd_Series(rfrac,index=G.nodes())
    gfrac = pd_Series(gfrac,index=G.nodes())
    bfrac = pd_Series(bfrac,index=G.nodes())

    return rfrac,gfrac,bfrac



# this function calculates fraction of to-node connections belonging to each community
def calc_community_fraction(G,to_nodes,from_nodes, from_nodes_partition, color_list):
    # set color to most populous community
    degree = G.degree(to_nodes)
    rfrac,gfrac,bfrac=pd_Series(index=G.nodes()),pd_Series(index=G.nodes()),pd_Series(index=G.nodes())
    for t in to_nodes:
        t_neighbors = G.neighbors(t)
        t_comms = [from_nodes_partition[i] for i in t_neighbors]
        t_comms = pd_Series(t_comms)
        
        unique_comms = t_comms.unique()
        num_unique_comms = len(unique_comms)
        
        num_n = pd_Series(index=unique_comms)
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

from matplotlib.colors import colorConverter
from matplotlib.colors import rgb_to_hsv
from matplotlib.colors import hsv_to_rgb
def shade_color(color, percent):
    """
    A color helper utility to either darken or lighten given color.
    This color utility function allows the user to easily darken or lighten a color for
    plotting purposes.  This function first converts the given color to RGB using 
    ColorConverter and then to HSL.  The saturation is modified according to the given 
    percentage and converted back to RGB.
    Parameters
    ----------
    color : string, list, hexvalue
        Any acceptable Matplotlib color value, such as 'red', 'slategrey', '#FFEE11', (1,0,0)
    percent :  the amount by which to brighten or darken the color.
    Returns
    -------
    color : tuple of floats
        tuple representing converted rgb values
    """

    rgb = colorConverter.to_rgb(color)

    h, l, s = rgb_to_hsv([rgb[0],rgb[1],rgb[2]])

    l *= 1 + float(percent)/100

    l = np.clip(l, 0, 1)

    r, g, b = hsv_to_rgb([h, l, s])

    return r, g, b
