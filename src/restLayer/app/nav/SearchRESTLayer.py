# -*- coding: utf-8 -*-
import pymongo
from bottle import Bottle, request, response, HTTPError
from collections import defaultdict
from bson import ObjectId

import app
from app import genemania

import requests
import json
import math
from PIL import Image
#from job_queue import JobQueue

log = app.get_logger('nav api')
api = Bottle()

#jobQueue = JobQueue()
#jobQueue.start()

from bson.json_util import dumps
from bottle import route, run
from app import go
from app import MirBase
from app import InterPro
from app import ElasticSearch
from app import PubMed
from app import RestBroker
from app import NeighborhoodSearch
from app import TermIdentifier
from app import ElasticSearchLazy
from app import author_gene_clustering_module
from app import SearchGeneTab
from app import SearchPathwaysTab
from app import SearchConditionsTab
from app import SearchAuthorsTab
from app import SearchDrugsTab
from app import SearchCounts
from app import util
from app import SearchViz
from app import SearchInferredDrugsTab
from app import ESearch

@route('/w3')
def w3Go():
    return "<h4>start</h4>"

@api.get('/api/nav/aaron/:name')
def get_gene(name):
    client = pymongo.MongoClient(app.mongodb_uri)
    c = client.identifiers.genemania

    id = genemania.lookup_id(name)
    if id is None:
        return HTTPError(404)

    myResults = {result['source']: result['name'] for result in c.find({'preferred': id, 'source': {'$ne': 'Synonym'}})};
    myResults2 = json.dumps(myResults)
    myResults2 = myResults2.replace("u\"","\"").replace("u\'","\'")

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, myResults2)

    return {result['source']: result['name'] for result in c.find({'preferred': id, 'source': {'$ne': 'Synonym'}})}

@api.get('/ontologies/icd10/findbyname/:lookforthisname')
def get_icd10_by_name(lookforthisname):
    c = pymongo.MongoClient(app.mongodb_uri).ontologies.icd10

    query = ({"name": {"$regex": ".*" + lookforthisname + ".*"}})

    cursor = c.find(query)

    print(cursor.count())

    map = {it['name']: it['id'] for it in c.find(query)}

    myResults2 = dumps(c.find(query).limit(15))
    myResults2 = myResults2.replace("u\"", "\"").replace("u\'", "\'")

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, myResults2)

    return dumps(c.find(query))


#http://localhost:8182/nav/pubmed/genecounts/BRCA1
@api.get('/nav/pubmed/genecounts/:geneList')
def get_pubmed_counts(geneList):
    return_value = dumps(app.PubMed.get_gene_pubmed_counts(geneList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value


#http://localhost:8182/nav/pubmed/genecounts/normalized/OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,PITPNM2,TRAPPC8,EIF2S2
@api.get('/nav/pubmed/genecounts/normalized/:geneList')
def get_pubmed_counts_normalized(geneList):
    return_value = dumps(app.PubMed.get_gene_pubmed_counts_normalized(geneList, 1))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value


#http://localhost:8182/nav/interpro/info/IPR000001
@api.get('/nav/interpro/info/:interproIdList')
def get_interpro_info(interproIdList):
    return_value = dumps(app.InterPro.get_interpro_data(interproIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/map/:geneIdList')
def get_elasticsearch_mapping(geneIdList):
    return_value = dumps(app.ElasticSearch.get_all_searches(geneIdList)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value


#http://localhost:8182/nav/elasticsearch/star/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/star/search/map/:geneIdList')
def get_elasticsearch_star_search_mapping(geneIdList):
    #return_value = dumps(app.ElasticSearch.get_star_search_mapped(geneIdList)) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchGeneTab.get_star_search_mapped(geneIdList)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/star/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/star/search/map/:geneIdList/:disease')
def get_elasticsearch_star_search_with_disease_mapping(geneIdList, disease):
    #return_value = dumps(app.ElasticSearch.get_star_search_with_disease_mapped(geneIdList, [disease])) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchGeneTab.get_star_search_with_disease_mapped(geneIdList, [disease])) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value


#http://localhost:8182/nav/elasticsearch/dbsnp/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/dbsnp/search/map/:geneIdList')
def get_elasticsearch_dbsnp_search_mapping(geneIdList):
    return_value = dumps(app.ElasticSearch.get_dbsnp_search_mapped(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/dbsnp/variants/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/dbsnp/variants/:geneIdList')
def get_variants_by_query_list_api(geneIdList):
    return_value = dumps(app.ElasticSearch.get_variants_by_query_list(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value


#http://localhost:8182/nav/elasticsearch/coexpression_network/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/coexpression_network/search/map/:geneIdList')
def get_elasticsearch_coexpression_network_search_mapping(geneIdList):
    return_value = dumps(app.ElasticSearch.get_coexpression_network_search_mapped(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/coexpression_network/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/coexpression_network/search/map/:geneIdList/:genome')
def get_elasticsearch_coexpression_network_search_mapping(geneIdList, genome):
    return_value = dumps(app.ElasticSearch.get_coexpression_network_search_mapped(geneIdList, genome))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/cluster/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/cluster/search/map/:geneIdList')
def get_elasticsearch_star_search_mapping(geneIdList):
    #return_value = dumps(app.ElasticSearch.get_cluster_search_mapped(geneIdList)) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchPathwaysTab.get_cluster_search_mapped(geneIdList)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/cluster/search/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/cluster/search/map/:geneIdList/:disease')
def get_elasticsearch_star_search_with_disease_mapping(geneIdList, disease):
    #return_value = dumps(app.ElasticSearch.get_cluster_search_with_disease_mapped(geneIdList, [disease])) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchPathwaysTab.get_cluster_search_with_disease_mapped(geneIdList, [disease])) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/go/enrich/ENSG00000012048,ENSG00000233636,ENSG00000129673,ENSG00000163749,ENSG00000173261,ENSG00000013441,ENSG00000139433,ENSG00000090975
@api.get('/nav/elasticsearch/getheatmap/:elasticId')
def get_heatmap_from_elastic_search(elasticId):
    cluster_result = dumps(ElasticSearch.get_document_from_elastic_by_id(elasticId, 'cluster'))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

#http://localhost:8182/nav/elasticsearch/go/enrich/ENSG00000012048,ENSG00000233636,ENSG00000129673,ENSG00000163749,ENSG00000173261,ENSG00000013441,ENSG00000139433,ENSG00000090975
@api.get('/nav/elasticsearch/getheatmap2/:elasticId')
def get_heatmap_from_elastic_search2(elasticId):
    cluster_result = dumps(ElasticSearch.get_document_from_elastic_by_id2(elasticId, 'cluster'))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

# get document by id - Raw
@api.get('/nav/elasticsearch/fileByIdRaw/:searchType/:elasticId')
def get_doc_by_id_from_elastic_search_raw(searchType, elasticId):
    cluster_result = dumps(ElasticSearch.get_document_from_elastic_by_id_raw(elasticId, searchType))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

@api.get('/nav/elasticsearch/getheatmap3/:elasticId')
def get_heatmap_from_elastic_search3(elasticId):
    cluster_result = ElasticSearch.get_document_from_elastic_by_id3(elasticId, 'tcga_louvain')

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

@api.get('/api/getheatmap/filtered/:elasticId/:genes')
def get_heatmap_filtered(elasticId, genes):
    cluster_result = ElasticSearch.get_heatmap_filtered_by_id(elasticId, genes)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

@api.get('/api/getheatmapmatrix/filtered/:elasticId/:genes/:number_of_edges')
def get_heatmap_filtered_by_number_of_edges(elasticId, genes, number_of_edges):
    cluster_result = SearchViz.generate_filtered_matrix(elasticId, genes, int(number_of_edges))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

@api.get('/api/getheatmapmatrix/unfiltered/:elasticId')
def get_heatmap_unfiltered(elasticId):
    cluster_result = dumps(SearchViz.get_cluster_document_from_elastic_by_id2(elasticId))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, cluster_result)

    return cluster_result

@api.get('/nav/elasticsearch/star/search/neighborhood/map/:geneIdList')
def get_elasticsearch_star_search_neighborhood_mapping(geneIdList):
    return_value = dumps(app.NeighborhoodSearch.star_search_mapped_2_0(geneIdList)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/single/star/search/map/OR2J3
@api.get('/nav/elasticsearch/single/star/search/map/:term_name')
def get_elasticsearch_star_search_neighborhood_mapping(term_name):
    return_value = dumps(app.ElasticSearch.get_single_star_search(term_name)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/byid/OR2J3
@api.get('/nav/elasticsearch/byid/:geneId')
def get_elasticsearch_mapping(geneId):
    return_value = dumps(app.ElasticSearch.get_gene_network_by_nodeName(geneId)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/map/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/geneenrich/map/:geneIdList')
def get_geneenrich_mapping(geneIdList):
    return_value = dumps(app.go.get_gene_ontology_search_mapped(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/elasticsearch/cytoscape/star/OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1
@api.get('/nav/elasticsearch/cytoscape/star/:clusterName')
def get_elasticsearch_cytoscape_star_mapping(clusterName):
    return_value = dumps(app.ElasticSearch.star_prep_for_cytoscape_js(clusterName))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/mirbase/info/ENSG00000012048,ENSG00000233636,ENSG00000129673,ENSG00000163749,ENSG00000173261,ENSG00000013441,ENSG00000139433,ENSG00000090975
@api.get('/nav/mirbase/ext/:mirna')
def get_mirbase_info_ext(mirna):
    return_value = dumps(app.MirBase.get_mirbase_info(mirna))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/mirbase/info/ENSG00000012048,ENSG00000233636,ENSG00000129673,ENSG00000163749,ENSG00000173261,ENSG00000013441,ENSG00000139433,ENSG00000090975
@api.get('/nav/mirbase/info/:mirna')
def get_mirbase_info(mirna):
    return_value = dumps(app.MirBase.get_mir_data(mirna))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/go/enrich/ENSG00000012048,ENSG00000233636,ENSG00000129673,ENSG00000163749,ENSG00000173261,ENSG00000013441,ENSG00000139433,ENSG00000090975
@api.get('/nav/go/enrich/:genes')
def get_go_enrichment(genes):
    jsonp_return_raw = go.get_go_enrichment_with_overlap(genes)   #dumps(artifact['groups']['node'])

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return jsonp_return_raw

#http://localhost:8182/nav/elasticsearch/go/enrich/ENSG00000012048,ENSG00000233636,ENSG00000129673,ENSG00000163749,ENSG00000173261,ENSG00000013441,ENSG00000139433,ENSG00000090975
@api.get('/nav/elasticsearch/go/enrich/:elasticId')
def get_go_enrichment_from_elastic_search(elasticId):
    genes = ElasticSearch.get_genes_from_elastic_by_id(elasticId, 'node')
    jsonp_return_raw = go.get_go_enrichment_with_overlap(genes)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return jsonp_return_raw

@api.post('/nav/go/enrich/post')
def post_go_enrichment():
    mystr = "";
    request2 = request
    values2 = request.forms
    genes = request.forms.get('genesList')
    genes = 'BRCA1,BRCA2'

    genesarray = genes.split(',')

    genenodes = []
    for gene in genesarray:
        id = genemania.lookup_id(gene)
        if id is not None:
            genenodes.append({"id": id})

    client = pymongo.MongoClient()
    terms = list(client.go.genes.find({'gene': "ENSG00000249915"}).distinct('go'))
    artifact = {
        'project': "NO_PROJECT",
        'job': "NO_JOB_ID",
        'sources': {},
        'nodes': genenodes,
        'groups': {
            'node': [],
            'edge': []
        }
    }

    gene_list = [node['id'] for node in artifact['nodes']]
    enriched = go.gene_set_enrichment(gene_list)[:20]  # get the top 20 go terms

    enriched_dumps = dumps(enriched)

    for it in enriched:
        artifact['groups']['node'].append({
            'id': it['go'].replace('GO:', 'go'),
            'go_lookup': it['go'],
            'name': it['name'],
            'description': it['def'].replace('\"', ''),
            'items': it['overlap'],
            'count': it['n_genes'],
            'pvalue': it['pvalue'],
            'pvalue_log': round((-1 * math.log10(it['pvalue'])), 2),
            'qvalue': it['qvalue'],
            'qvalue_log': round((-1 * math.log10(it['qvalue'])), 2)
        })

    jsonp_return_raw = dumps(artifact['groups']['node'])

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return dumps(artifact['groups']['node'])





    client = pymongo.MongoClient(app.mongodb_uri)
    network = request.json
    network = deserialize(network)  # convert string id to ObjectId
    set_status(network, 'updated')
    client.nav.networks.save(network)
    return {'timestamp': network['timestamp']['updated']}

@api.get('/nav/go/enrich/full/:genes')
def get_go_enrichment_full(genes):
    # do gene set enrichment
    # create a network artifact
    # nodes, edges, and groups are added to this artifact as part of the job

    genesarray = genes.split(',')
    genenodes = []
    for gene in genesarray:
        id = genemania.lookup_id(gene)
        if id is not None:
            genenodes.append({"id": id})

    client = pymongo.MongoClient()
    terms = list(client.go.genes.find({'gene': "ENSG00000249915"}).distinct('go'))
    artifact = {
        'project': "NO_PROJECT",
        'job': "NO_JOB_ID",
        'sources': {},
        'nodes': genenodes,
        'groups': {
            'node': [],
            'edge': []
        }
    }

    gene_list = [node['id'] for node in artifact['nodes']]
    enriched = go.gene_set_enrichment(gene_list)[:20]  # get the top 20 go terms

    enriched_dumps = dumps(enriched)

    for it in enriched:
        go_genes = set(client.go.terms.find({'go': it['go']}).limit(10))
        #genes_found = {"genes": it['genes'] for it in client.go.terms.find({'go': it['go']}).limit(10)}
        artifact['groups']['node'].append({
            'id': it['go'].replace('GO:', 'go'),
            'go_lookup': it['go'],
            'name': it['name'],
            'description': it['def'],
            'items': it['overlap'],
            'count': it['n_genes'],
            'pvalue': it['pvalue'],
            'genes_members': go_genes,
            'pvalue_log': round((-1 * math.log10(it['pvalue'])), 2),
            'qvalue': it['qvalue'],
            'qvalue_log': round((-1 * math.log10(it['qvalue'])), 2)
        })

    jsonp_return_raw = dumps(artifact['groups']['node'])

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return dumps(artifact['groups']['node'])

@api.get('/nav/go/getmembers/:lookforthisname')
def get_go_members(lookforthisname):
    # do gene set enrichment
    # create a network artifact
    # nodes, edges, and groups are added to this artifact as part of the job

    client = pymongo.MongoClient()
    terms = list(client.go.terms.find({'go': 'GO:0005524'}).limit(10))
    return dumps(terms)

@api.get('/nav/terms/lookup/:terms')
def terms_lookup(terms):

    jsonp_return_raw = dumps(app.TermIdentifier.bulk_identify_terms(terms))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return jsonp_return_raw

@api.get('/nav/term/lookup/:term')
def terms_lookup(term):

    jsonp_return_raw = dumps(app.TermIdentifier.search_term_description(term))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return jsonp_return_raw

@api.get('/nav/terms/autocomplete/:term')
def terms_lookup(term):

    jsonp_return_raw = dumps(app.TermIdentifier.auto_complete_search(term))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return jsonp_return_raw

@api.get('/nav/tribe/lookup/:terms')
def terms_lookup(terms):

    jsonp_return_raw = dumps(app.RestBroker.getTribeTermResolution(terms))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

    return jsonp_return_raw

@api.get('/ontologies/distinguish/:lookupthisterm')
def term_distinguisher(lookupthisterm):
    geneId = genemania.lookup_id(lookupthisterm)

    #====================================
    # LOOK UP THE TERM IN MONGODB
    # START WITH GENES THEN TRY
    # PHENOTYPES, ETC...
    #====================================
    if geneId is None:
        #==================
        # DIDN'T FIND GENE
        #==================
        c = pymongo.MongoClient(app.mongodb_uri).ontologies.icd10

        query = ({"name": {"$regex": ".*" + lookupthisterm + ".*"}})

        cursor = c.find(query)

        print(cursor.count())

        if cursor.count() > 0:
            #=======================
            # FOUND PHENOTYPE
            #=======================
            if (request.query.callback):
                response.content_type = "application/javascript"
                return "%s(%s);" % (request.query.callback, "{'Found': 'phenotype'}")
        else:
            return None
    else:
        #==================
        # FOUND GENE
        #==================
        if (request.query.callback):
            response.content_type = "application/javascript"
            return "%s(%s);" % (request.query.callback, "{'status': 'found'}")
        else:
            return "{'status': 'found'}"

    return None

#http://localhost:8182/nav/restbroker/entrez/BRCA1
@api.get('/nav/restbroker/entrez/:geneid')
def get_mirbase_info_ext(geneid):
    return_value = dumps(RestBroker.getEntrezGeneInfoByID(geneid))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/restbroker/entrez/BRCA1
@api.get('/nav/getgeneinfo/:geneid')
def get_gene_info_all(geneid):
    entre_info = RestBroker.getEntrezGeneInfoByID(geneid)

    return_value = dumps(RestBroker.getEntrezGeneInfoByID(geneid))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/biomart/lookup/BRCA1
@api.get('/nav/biomart/lookup/:geneid')
def get_biomart_gene_info(geneid):
    return_value = dumps(TermIdentifier.get_biomart_info())

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/biomart/lookup/BRCA1 zB
@api.get('/nav/clinvar/:geneids')
def get_biomart_gene_info(geneids):
    #return_value = dumps(SearchConditionsTab.get_clinvar_search(geneids, None))
    #return_value = dumps(SearchConditionsTab.get_clinvar_search(geneids, None))
    return_value = dumps(SearchConditionsTab.get_condition_search(geneids, 1))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/biomart/lookup/BRCA1
@api.get('/nav/clinvar/:geneids/phenotypes/:phenotypes')
def get_biomart_gene_info(geneids, phenotypes):
    #return_value = dumps(ElasticSearch.get_clinvar_search(geneids, phenotypes))
    return_value = dumps(SearchConditionsTab.get_clinvar_search(geneids, phenotypes))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/biomart/lookup/BRCA1 zB
@api.get('/simple/conditions/search/:geneids/:pageNumber')
def get_paged_conditions_search(geneids, pageNumber):
    return_value = dumps(SearchConditionsTab.get_cosmic_grouped_by_tissues_then_diseases(geneids, int(pageNumber)))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#http://localhost:8182/nav/biomart/lookup/BRCA1 zB
@api.get('/nav/paged/conditions/:geneids/:pageNumber')
def get_conditions_search_paged(geneids, pageNumber):
    return_value = dumps(SearchConditionsTab.get_cosmic_grouped_by_disease_tissue(geneids, int(pageNumber)))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/save/search/:terms')
def save_search_get(terms):
    computed_hash = util.compute_query_list_hash(terms)
    #print computed_hash

    client = pymongo.MongoClient(app.mongodb_uri)
    cached_search_terms_collection = client.cache.searches
    cached_search_terms_found = cached_search_terms_collection.find_one({'searchId': computed_hash})

    write_result = {'searchId': computed_hash}
    if(cached_search_terms_found is None):
        client.cache.searches.insert({'searchId': computed_hash, 'terms': terms, 'termsSplit': terms.split(','), 'timeStamp': util.timestamp()})

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, write_result)

    return write_result

@api.get('/api/get/saved/search/:id')
def get_project(id):
    client = pymongo.MongoClient(app.mongodb_uri)
    #saved_search = client.cache.searches.find_one({'_id': ObjectId(id)})
    saved_search = client.cache.searches.find_one({'searchId': id})
    if saved_search:
        return_value = {'terms': dumps(saved_search['terms'])}
        if (request.query.callback):
            response.content_type = "application/javascript"
            return "%s(%s);" % (request.query.callback, return_value)

        return return_value
    else:
        return ''

@api.get('/api/get/search/stats')
def get_search_stats():
    results = dumps(util.agg_search_data())

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/api/get/people/genecenter/search/:terms')
def get_people_gene_center_star(terms):
    results = dumps(ElasticSearch.get_people_pubmed_search_mapped(terms, False))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/api/get/people/peoplecenter/search/:terms')
def get_people_people_center_star(terms):
    results = dumps(ElasticSearch.get_people_people_pubmed_search_mapped(terms))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/api/get/people/peoplecenter2/search/:terms')
def get_people_people_center_star(terms):
    #results = dumps(ElasticSearch.get_people_people_pubmed_search_mapped2(terms))
    results = dumps(SearchAuthorsTab.get_people_people_pubmed_search_mapped2(terms))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/api/get/people/gene/targeted/:author/:gene')
def get_people_gene_targeted(author, gene):
    results = dumps(ElasticSearch.get_people_gene_targeted_search(author, gene))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/api/get/people/genecenter/lazysearch/:terms')
def get_people_gene_center_lazy(terms):
    results = dumps(ElasticSearchLazy.get_people_gene_center_search(terms))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/api/get/people/genecenter/lazysearch/hydrate/:term')
def get_people_gene_center_lazy_hydrate(term):
    results = dumps(ElasticSearchLazy.get_people_gene_center_fill_in(term))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/nav/elasticsearch/getclinvar/:elasticId')
def get_clinvar_from_elastic_search(elasticId):
    return_value = dumps(ElasticSearch.get_information_page_data_phenotypes(elasticId))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/nav/elasticsearch/getgeneinfo/:geneId')
def get_clinvar_from_elastic_search(geneId):
    return_value = dumps(ElasticSearch.get_information_page_data_gene(geneId))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/elasticsearch/getauthorcenteredbyid/:elasticId/:genes')
def get_people_center_star_by_es_id(elasticId, genes):
    #return_value = dumps(ElasticSearch.get_information_page_data_people_centered(elasticId, genes))
    return_value = dumps(SearchAuthorsTab.get_information_page_data_people_centered(elasticId, genes))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/ds/getbpnet/:genes')
def get_people_author_bp_network(genes):
    return_value = dumps(author_gene_clustering_module.analyze_AG_bipartite_network(genes,[]))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/ds/getheatmapgraph/:cluster_id/:gene_list/:number_of_edges')
def get_heatmap_graph(cluster_id, gene_list, number_of_edges):

    #return_value = dumps(SearchViz.get_heat_prop_cluster_viz(gene_list, cluster_id))
    #return_value = dumps(SearchViz.get_heatmap_graph_from_es_by_id(cluster_id, gene_list, 'clusters_tcga_louvain', 0.5))
    #return_value = dumps(SearchViz.get_heatmap_graph_from_es_by_id_no_processing(cluster_id, gene_list))
    return_value = dumps(SearchViz.get_heatmap_graph_from_es_by_id_using_neighbors(cluster_id, gene_list, int(number_of_edges)))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/ds/getrawcluster/:cluster_id/:gene_list')
def get_raw_cluster(cluster_id, gene_list):
    return_value = dumps(SearchViz.get_heatmap_graph_from_es_by_id_no_processing(cluster_id, gene_list))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/elasticsearch/getclusterenrichmentbyid/:elasticId')
def get_cluster_enrichment_by_id(elasticId):
    return_value = dumps(SearchPathwaysTab.get_enrichment_from_es_by_id(elasticId))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/gettabcounts/:genes')
def get_tab_counts(genes):
    computed_hash = util.compute_query_list_hash(genes)
    #print computed_hash

    client = pymongo.MongoClient()
    db = client.cache

    tab_counts = db.tab_counts

    tab_counts_found = tab_counts.find_one({'countsId': computed_hash})

    if(tab_counts_found is not None):
        client.close()
        if (request.query.callback):
            response.content_type = "application/javascript"
            return "%s(%s);" % (request.query.callback, dumps(tab_counts_found['tab_counts']))

        return tab_counts_found['tab_counts']
    else:
        return_value = {
            'genes': 0,
            'clusters': 0,
            'conditions': 0,
            'authors': 0,
            'drugs': 0
        }

        return_value['genes'] = 0 #SearchCounts.get_counts_gene(genes)
        return_value['clusters'] = SearchCounts.get_counts_cluster(genes)
        return_value['conditions'] = SearchCounts.get_counts_condition(genes)
        return_value['authors'] = SearchCounts.get_counts_author(genes)
        return_value['drugs'] = 1 #SearchCounts.get_counts_drug(genes)

        #return_value = dumps(author_gene_clustering_module.analyze_AG_bipartite_network(genes,[]))

        tab_counts.save(
            {
                'countsId': computed_hash,
                'tab_counts': return_value
            }
        )

        client.close()

        if (request.query.callback):
            response.content_type = "application/javascript"
            return "%s(%s);" % (request.query.callback, return_value)

        return return_value


@api.get('/api/getImage')
def get_image():
    from PIL import Image
    import StringIO

    buffer = StringIO.StringIO()
    buffer.write(open('image.jpg', 'rb').read())
    buffer.seek(0)

    image = Image.open(buffer)
    #print image

    return_value = {'imagename': 'image.jpg'}

    myStr = 'iVBORw0KGgoAAAANSUhEUgAAB+kAAATcCAYAAABI9LdtAAAgAElEQVR4Xuzde5SWZb0//jcDMyCoCKKgBp4yD6mpYbXtoO3C8yE1Qc30m1qZu1a7tpadzbSV7cqt2/x+00q21t5keWCLWWpuLdNfwe6AluAJM0kQlPPBmWHmt+5nHAfwBATXPMO87rVmCTz3c3+u63V/lv+857quPu3t7e1xESBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAhtcoI+QfoMbK0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBGoCQnqNQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAA…gQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAgYj69oAAAE3SURBVEL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCTw/wGkKroztFBLmwAAAABJRU5ErkJggg=='

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/getAllClusterIds')
def get_all_cluster_ids():

    SearchPathwaysTab.get_all_cluster_ids()

    return_value = {'message': 'success'}

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/getTermNeighbors/:geneList/:elasticId')
def get_query_term_neighbors(geneList, elasticId):

    SearchPathwaysTab.get_document_overlaps(geneList, elasticId)

    return_value = {'message': 'success'}

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/getInferredDrugs/:elasticIds')
def get_inferred_drugs(elasticIds):

    return_value = dumps(SearchInferredDrugsTab.get_inferred_drug_search(elasticIds))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/heatProp/getInferredDrugs/:seedGenes/:clusterIds')
def get_heatprop_inferred_drugs(seedGenes,clusterIds):

    return_value = dumps(SearchViz.get_heat_prop_from_gene_list(seedGenes,clusterIds))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/experiment1/:seedGenes/:esIds')
def get_experiment_1(seedGenes, esIds):

    return_value = dumps(SearchViz.experiment_1(seedGenes, esIds))
    print return_value
    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/conditions/genevariants/:gene/:condition/:tissue')
def get_conditions_gene_variants(gene, condition, tissue):

    return_value = dumps(ElasticSearch.get_condition_variants(gene, condition, tissue))
    #print return_value
    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/api/gene/summary/:gene')
def get_gene_summary(gene):

    return_value = dumps(ESearch.get_gene_summary_from_entrez(gene))
    #print return_value
    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

# get genes in Ontology
@api.get('/api/go/genes/:goId')
def get_genes_from_go(goId):
    #go_result = dumps(go.get_genes_from_Ontology(goId))
    go_result = dumps(go.get_genes_from_Ontology_complete(goId))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, go_result)

    return go_result

#========================
# CLUSTER SEARCH
#========================
@api.get('/search/clusters/:geneIdList/')
def get_cluster_search_default(geneIdList):
    #return_value = dumps(app.ElasticSearch.get_cluster_search_mapped(geneIdList)) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchPathwaysTab.get_cluster_search_mapped(geneIdList, 99)) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/search/clusters/:geneIdList/:pageNumber')
def get_cluster_search_paged(geneIdList, pageNumber):
    #return_value = dumps(app.ElasticSearch.get_cluster_search_mapped(geneIdList)) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchPathwaysTab.get_cluster_search_mapped(geneIdList, int(pageNumber))) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/search/clusters/:geneIdList/:pageNumber/:disease')
def get_cluster_search_paged_with_disease(geneIdList, pageNumber, disease):
    #return_value = dumps(app.ElasticSearch.get_cluster_search_with_disease_mapped(geneIdList, [disease])) #get_all_searches(geneIdList))
    return_value = dumps(app.SearchPathwaysTab.get_cluster_search_with_disease_mapped(geneIdList, int(pageNumber), [disease])) #get_all_searches(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value


#========================
# CONDITIONS SEARCH
#========================
@api.get('/search/phenotypes/:geneids')
def get_search_conditions_default(geneids):
    return_value = dumps(SearchConditionsTab.get_condition_search(geneids, 99))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/search/phenotypes/:geneids/:pageNumber')
def get_search_conditions_paged(geneids, pageNumber):
    return_value = dumps(SearchConditionsTab.get_condition_search(geneids, int(pageNumber)))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#========================
# AUTHORS SEARCH
#========================
@api.get('/search/authors/:terms')
def get_people_search_default(terms):
    results = dumps(SearchAuthorsTab.get_people_people_pubmed_search_mapped2(terms, 99))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

@api.get('/search/authors/:terms/:pageNumber')
def get_people_search_paged(terms, pageNumber):
    #results = dumps(ElasticSearch.get_people_people_pubmed_search_mapped2(terms))
    if(pageNumber == 'undefined'):
        pageNumber = '99'

    results = dumps(SearchAuthorsTab.get_people_people_pubmed_search_mapped2(terms, int(pageNumber)))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, results)

    return results

#========================
# DRUG SEARCH
#========================
@api.get('/search/drugs/:geneIdList')
def get_search_drugs_default(geneIdList):
    #return_value = dumps(app.ElasticSearch.get_drug_network_search_mapped(geneIdList))
    return_value = dumps(app.SearchDrugsTab.get_drug_network_search_mapped(geneIdList))

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

@api.get('/search/drugs/and/inferred/:geneIdList/:clusterIds')
def get_search_drugs_paged(geneIdList, clusterIds):
    inferred_drugs =  []#app.SearchInferredDrugsTab.get_inferred_drug_search(clusterIds)
    #heat_inferred_drugs = app.SearchViz.get_heat_prop_from_gene_list_loop(geneIdList,clusterIds)
    heat_inferred_drugs = app.SearchViz.experiment_1(geneIdList,clusterIds)
    direct_drugs = app.SearchDrugsTab.get_drug_network_search_mapped(geneIdList)

    direct_drugs[0]['inferred_drugs'] = inferred_drugs
    direct_drugs[0]['heat_inferred_drugs'] = heat_inferred_drugs

    return_value = dumps(direct_drugs)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return return_value

#========================
# INFERRED DRUG SEARCH
#========================
@api.get('/search/inferred/drugs/:genes/:esIds')
def run_inferred_drugs_in_parallel(genes, esIds):

    return_results = SearchViz.experiment_1(genes, esIds)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, dumps(return_results))

    return dumps(return_results)

