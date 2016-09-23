import sys, numpy, scipy
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist
from bson.json_util import dumps
#import app.ElasticSearch
#import networkx as nx

def cluster_heat_map_2D(es_data_matrix):
    colHeaders = es_data_matrix['xValues']
    rowHeaders = es_data_matrix['yValues']
    dataMatrix = es_data_matrix['zValues']

    #===============================
    # Need to account for asymmetry
    # if asymmetric then return
    #===============================
    if(len(colHeaders) != len(rowHeaders)):
        return es_data_matrix
    else:
        distanceMatrix = dist.pdist(dataMatrix)
        distanceSquareMatrix = dist.squareform(distanceMatrix)

        linkageMatrix = hier.linkage(distanceSquareMatrix)

        heatmapOrder = hier.leaves_list(linkageMatrix)

        orderedDataMatrix = dataMatrix[heatmapOrder,:]
        orderedOrderedDataMatrix = orderedDataMatrix[:,heatmapOrder]
        rowHeaders = numpy.array(rowHeaders)
        orderedRowHeaders = rowHeaders[heatmapOrder]

        colHeaders = numpy.array(colHeaders)
        orderedColHeaders = colHeaders[heatmapOrder]

        return_json = {
            'xValues': orderedColHeaders,
            'yValues': orderedRowHeaders,
            'zValues': orderedOrderedDataMatrix
            }

        return return_json
