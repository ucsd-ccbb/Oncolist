import os
import sys
import time
import shutil
import pymongo
import tempfile
import itertools
import contextlib
import subprocess
from scipy.stats import hypergeom
from bson.json_util import dumps
from operator import itemgetter
import math
from collections import defaultdict
from app.GO_Parser import GOLocusParser
import pandas as pd

import app
import genemania
from fdr import fdr
from status import Status

log = app.get_logger('Gene Set Enrichment')

@contextlib.contextmanager
def mktemp(*args, **kwargs):
    d = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield d
    finally:
        shutil.rmtree(d)


def load_go_genes():
    info = {
        'database': 'go',
        'collection': 'genes',
        'url': 'http://geneontology.org/gene-associations/gene_association.goa_human.gz',
        'timestamp': time.time()
    }
    client = pymongo.MongoClient()
    collection = client[info['database']][info['collection']]
    collection.drop()
    with mktemp() as pathname:
        filename = os.path.join(pathname, 'gene_association.goa_human.gz')
        log.debug('downloading %s to %s', info['url'], filename)
        subprocess.call(['wget', info['url'], '-O', filename])
        log.debug('gunzip %s', filename)
        subprocess.call(['gunzip', filename])
        filename, _ = os.path.splitext(filename)

        with open(filename, 'rt') as fid:
            log.debug('creating a name to emsembl id lookup table from go genes...')
            go_genes = set([line.split('\t')[2] for line in fid if not line.startswith('!')])

        name_to_id = genemania.id_lookup_table(go_genes)

        with open(filename, 'rt') as fid:
            status = Status(filename, log).fid(fid).start()
            for line in fid:
                status.log()
                if not line.startswith('!'):
                    tokens = line.split('\t')
                    obj = {
                        'gene': name_to_id.get(tokens[2]),
                        'go': tokens[4]
                    }
                    collection.insert(obj)
            status.stop()

    update_info(info)
    collection.create_index('go')
    collection.create_index('gene')

def get_go_enrichment(genes):
    genesarray = genes.split(',')
    if(len(genesarray) > 1):
        genenodes = []
        for gene in genesarray:
            id = genemania.lookup_id(gene)
            if id is not None:
                genenodes.append({"id": id})

        client = pymongo.MongoClient()

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
        enriched = gene_set_enrichment(gene_list)[:20]  # get the top 20 go terms

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

        return artifact['groups']['node']
    else:
        return []

#    if (request.query.callback):
#        response.content_type = "application/javascript"
#        return "%s(%s);" % (request.query.callback, jsonp_return_raw)

#    return dumps(artifact['groups']['node'])

def get_genes_from_Ontology(goId):
    info = {
        'database': 'go',
        'collection': 'genes',
        'url': 'http://geneontology.org/gene-associations/gene_association.goa_human.gz',
        'timestamp': time.time()
    }
    client = pymongo.MongoClient()
    collection = client.go.genes

    go_collection = collection.find({'go': goId})
    genes = [gene['gene'] for gene in go_collection]

    return_list = []
    for gene in genes:
        add_this = get_gene_symbol_by_ensemble_id(gene)
        if(add_this != 'NOT FOUND'):
            return_list.append(add_this)
        else:
            return_list.append(gene)

    return return_list

def get_genes_from_Ontology_complete(goId):
    client = pymongo.MongoClient()
    go_gene_sets = client.identifiers.go_gene_sets

    go_collection = go_gene_sets.find_one({'go_id': goId})

    if go_collection is not None:
        return go_collection['genes']
    else:
        return ['NOT FOUND']

def get_gene_symbol_by_ensemble_id(ensemble_id):
    client = pymongo.MongoClient()
    collection = client.identifiers.genemania

    gene_id_record = collection.find_one({'source': 'Gene Name', 'preferred': ensemble_id})
    if gene_id_record is not None:
        return gene_id_record['name']
    else:
        return 'NOT FOUND'

def get_gene_ontology_search_mapped(queryTerms):
    gene_ontology_data = {
        'searchGroupTitle': 'Gene Ontologies',
        'searchTab': 'PATHWAYS',
        'items': [],
        'geneSuperList': [],
        'geneScoreRangeMax': '20',
        'geneScoreRangeMin': '5',
        'geneScoreRangeStep': '0.1'
    }

    gene_super_list = []

    queryTermArray = queryTerms.split(',')


    results = get_go_enrichment(queryTerms)

    #==================================
    #
    #==================================
    hitCount = 0
    hitMax = 0
    hitMin = 9999.9

    resultsSorted = sorted(results, key=lambda k: k['qvalue_log'], reverse=True)
    for hit in resultsSorted:
        if(hitCount == 0):
            hitMax = hit['qvalue_log']
        else:
            if(hitMin > float(hit['qvalue_log'])):
                hitMin = hit['qvalue_log']

        hit_score = float(hit["qvalue_log"])
        scoreRankCutoff = 3.52

        gene_network_data_items = {
            'searchResultTitle': hit["name"],
            'searchResultSummary': hit["description"],
            'searchResultScoreRank': hit["qvalue_log"],
            'searchResultScoreRankTitle': 'Q Rank ',
            'filterValue': '0.0000000029',
            'emphasizeInfoArray': [],
            'top5': hitCount < 5,
            'hitOrder': hitCount
        }
        gene_ontology_data['items'].append(gene_network_data_items)
        hitCount += 1

    print('%s ' % dumps(gene_ontology_data))

    return gene_ontology_data

def get_go_enrichment_with_overlap(genes):
    # do gene set enrichment
    # create a network artifact
    # nodes, edges, and groups are added to this artifact as part of the job

    genesarray = genes
    genenodes = []
    count = 0
    for gene in genesarray:
        id = genemania.lookup_id(gene)
        if id is not None:
            genenodes.append({"id": id})
            if(count % 200 == 0):
                print 'gene: %s' % gene
                print 'Ens: %s' % id

        count += 1

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
    enriched = gene_set_enrichment(gene_list)[:20]  # get the top 20 go terms

    enriched_dumps = dumps(enriched)
    geneCounts = defaultdict(int)
    for it in enriched:
        for overlap in it['overlap']:
            geneCounts[overlap] = geneCounts[overlap] + 1
        print 'Overlap: %s' % it['overlap']
        if(it['pvalue'] > 0):
            pvalue_log = round((-1 * math.log10(it['pvalue'])), 2)
            qvalue_log = round((-1 * math.log10(it['qvalue'])), 2)
        else:
            pvalue_log = 0.0
            qvalue_log = 0.0

        artifact['groups']['node'].append({
            'id': it['go'].replace('GO:', 'go'),
            'go_lookup': it['go'],
            'name': it['name'],
            'description': it['def'].replace('\"', ''),
            'items': it['overlap'],
            'count': it['n_genes'],
            'pvalue': it['pvalue'],
            'pvalue_log': pvalue_log, #round((-1 * math.log10(it['pvalue'])), 2),
            'qvalue': it['qvalue'],
            'qvalue_log': qvalue_log, #round((-1 * math.log10(it['qvalue'])), 2)
        })
    print 'Gene Counts: %s' % dumps(geneCounts)
    jsonp_return_raw = dumps(artifact['groups']['node'])

    return jsonp_return_raw


def load_go_terms():
    info = {
        'database': 'go',
        'collection': 'terms',
        'url': 'http://geneontology.org/ontology/go.obo',
        'timestamp': time.time()
    }
    client = pymongo.MongoClient()
    collection = client[info['database']][info['collection']]
    collection.drop()
    with mktemp() as pathname:
        filename = os.path.join(pathname, 'go.obo')
        log.debug('downloading %s to %s', info['url'], filename)
        subprocess.call(['wget', info['url'], '-O', filename])
        with open(filename, 'rt') as fid:
            status = Status(filename, log).fid(fid).start()
            obj = None
            state = None
            for line in fid:
                status.log()
                line = line.strip()
                if line and not line.startswith('!'):
                    if line[0] == '[' and line[-1] == ']':
                        if state == 'Term' and obj:
                            collection.insert(obj)
                        state = line[1:-1]
                        obj = {}
                    elif state == 'Term':
                        key, _, value = line.partition(': ')
                        if value:
                            if key == 'id':
                                obj['go'] = value
                            else:
                                try:
                                    obj[key].append(value)
                                except KeyError:
                                    obj[key] = value
                                except AttributeError:
                                    obj[key] = [obj[key], value]
            status.stop()

    if state == 'Term' and obj:
        collection.insert(obj)

    collection.create_index('go')

    update_info(info)


def join_go_terms_with_genes():
    client = pymongo.MongoClient()
    terms = client.go.terms.find()
    status = Status('joining terms with genes').n(terms.count())
    for k, term in enumerate(terms):
        status.log(k)
        genes = client.go.genes.find({'go': term['go']})
        term['genes'] = list(set(g['gene'] for g in genes))
        term['n_genes'] = len(term['genes'])
        client.go.terms.save(term)
    status.stop()


def calc_pvalue(gene_list, gene_set, M):
    gene_list = set(gene_list)
    gene_set = set(gene_set)
    N = len(gene_list)
    n = len(gene_set)
    overlap = gene_list & gene_set
    k = len(overlap)
    return hypergeom(M, n, N).sf(k), list(overlap)


def gene_set_enrichment(gene_list, M=None):
    '''
    :param gene_list: list of gene symbols
    :param M: total number of genes (derived from database, if None)
    :return: filtered list of GO terms with p-value, q-value, and size of overlap
    '''
    client = pymongo.MongoClient()
    if not M:
        M = len(client.go.genes.distinct('gene'))
    terms = list(client.go.genes.find({'gene': {'$in': list(gene_list)}}).distinct('go'))
    terms = list(client.go.terms.find({'go': {'$in': terms}, 'n_genes': {'$gt': 2}}))
    enriched = [dict(term.items() + zip(('pvalue', 'overlap'), calc_pvalue(gene_list, term['genes'], M))) for term in terms]
    enriched.sort(key=lambda it: it['pvalue'])
    for qvalue, it in itertools.izip(fdr([it['pvalue'] for it in enriched], presorted=True), enriched):
        it['qvalue'] = qvalue

    return enriched

def get_genes_by_go_id(gene_list):
    info = {
        'database': 'go',
        'collection': 'genes',
        'url': 'http://geneontology.org/gene-associations/gene_association.goa_human.gz',
        'timestamp': time.time()
    }
    client = pymongo.MongoClient()
    collection = client[info['database']][info['collection']]

    collection.find({'gene': "ENSG00000249915"})

def get_GO_gene_identifiers_Roman_dataset():
    client = pymongo.MongoClient()
    go_genes = client.identifiers.go_genes
    go_genes.drop()

    with open('/Users/aarongary/Development/DataSets/GO/GX/GO/Homo_sapiens.gene_info.txt') as f:
        for line in f:
            #if not line.startswith('#'):
            split_line = line.split('\t')
            if(len(split_line) > 3):
                go_genes.save(
                    {
                        'GeneID': split_line[1],
                        'Symbol': split_line[2]
                     }
                )

    go_genes.ensure_index([("GeneID" , pymongo.ASCENDING)])

def load_GO_sets_from_parser():
    client = pymongo.MongoClient()
    go_gene_sets = client.identifiers.go_gene_sets
    go_gene_sets.drop()

    go_gene_file = '/Users/aarongary/Development/DataSets/GO/GX/GO/GO2all_locus.txt'
    gene_info_file = '/Users/aarongary/Development/DataSets/GO/GX/GO/Homo_sapiens.gene_info'
    go_term_file = '/Users/aarongary/Development/DataSets/GO/GX/GO/go.obo'
    GO_ID_list, total_unique_gene, GO_Term_list = GOLocusParser.parse(go_gene_file, gene_info_file, go_term_file)
    count = 0
    v = 1
    for go_id in GO_ID_list:
        if(count % 100 == 0):
            print count
        go_gene_sets.save(
            {
                'go_id': go_id,
                'genes': GO_ID_list[go_id]
            }
        )
        count += 1

    go_gene_sets.ensure_index([("go_id" , pymongo.ASCENDING)])

def get_GO_genes_Roman_dataset():
    client = pymongo.MongoClient()
    go_genes = client.identifiers.go_index

    with open('/Users/aarongary/Development/DataSets/GO/GX/GO/GO2all_locus.txt') as f:
        header_line = f.readline()
        header_index = header_line.split('\t')[:]

        for line in f:
            if not line.startswith('GOterm'):
                split_line = line.split('\t')
                add_this_GO = {'go_id': split_line[0],
                               'go_genes': []}
                print split_line[0]
                go_set = [i for i, j in enumerate(split_line) if j == '1']

                for go_item in go_set:
                    add_this_GO['go_genes'].append(header_index[go_item])
                    #print header_index[go_item]

                print dumps(add_this_GO)
                myStr = ''

def update_info(info):
    client = pymongo.MongoClient()
    collection = client.db.info
    old = collection.find_one({'database': info['database'], 'collection': info['collection']})
    if old:
        info['_id'] = old['_id']
    collection.save(info)


def load():
    load_go_genes()
    load_go_terms()
    join_go_terms_with_genes()

def main():
    load()
    return 0


if __name__ == '__main__':
    sys.exit(main())
