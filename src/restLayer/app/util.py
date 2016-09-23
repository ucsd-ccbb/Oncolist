import os
import time
import pymongo
from bson import ObjectId
from bottle import request
import itertools
from fdr import fdr
from scipy.stats import hypergeom
from bson.json_util import dumps
from bson.code import Code
import hashlib

import app

log = app.get_logger('util')

def serialize(obj):
    if type(obj) in [list, set, tuple]:
        return [serialize(it) for it in obj]
    elif type(obj) == dict:
        for k, v in obj.iteritems():
            obj[k] = serialize(v)
        return obj
    elif type(obj) == ObjectId:
        return str(obj)
    else:
        return obj


def deserialize(obj):
    if type(obj) is list:
        return [deserialize(it) for it in obj]
    elif type(obj) == dict:
        for k, v in obj.iteritems():
            if k == '_id':
                obj[k] = ObjectId(obj[k])
            else:
                obj[k] = deserialize(obj[k])
        return obj
    else:
        return obj


def save_file_metadata(filepath, **kwargs):

    meta = pymongo.MongoClient(app.mongodb_uri).files.meta
    _id, filepath = split_id(filepath)

    record = meta.find_one({'_id': ObjectId(_id)})

    if not record:
        record = {
            'name': os.path.basename(filepath)
        }

    if 'status' in kwargs:
        set_status(record, kwargs['status'])
        del kwargs['status']

    for k, v in kwargs.iteritems():
        record[k] = v

    if _id is not None:
        record['_id'] = _id

    _id = meta.save(record)
    log.debug('saved metadata for file %s with id %s', filepath, _id)
    return _id


def split_id(filepath):
    pathname, filename = os.path.split(filepath)
    tokens = filename.split('.')
    try:
        _id = ObjectId(tokens[0])
        tokens = tokens[1:]
    except:
        _id = None
    return _id, os.path.join(pathname, '.'.join(tokens))


def add_id(new_id, filepath):
    new_id = str(new_id)
    old_id, filepath = split_id(filepath)
    old_id = str(old_id)
    pathname, filename = os.path.split(filepath)
    if old_id is not None and not old_id == new_id:
        log.warn('new id %s does not equal old id %s for file %s', new_id, old_id, filepath)
    return os.path.join(pathname, '.'.join([new_id, filename]))


def set_status(record, status):
    record['status'] = status
    record.setdefault('timestamp', {})[status] = timestamp()


def timestamp():
    return time.time() * 1000


def get_value(key, default, f=str):
    try:
        value = request.query[key]
        return f(value)
    except:
        return default


def post_value(key, default):
    try:
        return request.forms[key]
    except:
        return default

def to_numeric(s):
    if s == '':
        return 0.0
    return float(s)


def is_numeric(s):
    try:
        to_numeric(s)
        return True
    except ValueError:
        return False


def to_boolean(s):
    s = s.lower()
    if s in ['true', 't', 'yes', 'y', '1']:
        return True
    if s in ['false', 'f', 'no', 'n', '0', '']:
        return False
    raise ValueError


def is_boolean(s):
    try:
        to_boolean(s)
        return True
    except ValueError:
        return False


def create_edges_index():
    c = pymongo.MongoClient().networks.edges

    # find all edges from a source node
    # e.g., find({'source': id, 'meta': {'$in': meta_ids}})
    c.create_index([
        ('source', pymongo.ASCENDING),
        ('meta', pymongo.ASCENDING)
    ])

    # find all edges from a target node
    # e.g., find({'target': id, 'meta': {'$in': meta_ids}})
    c.create_index([
        ('target', pymongo.ASCENDING),
        ('meta', pymongo.ASCENDING)
    ])

    # find all edges within a set of nodes
    # e.g., find({'source': {'$in': query_ids}, 'target': {'$in': query_ids}, 'meta': {'$in': meta_ids}})
    c.create_index([
        ('source', pymongo.ASCENDING),
        ('target', pymongo.ASCENDING),
        ('meta', pymongo.ASCENDING)
    ])

    # find all edges from a source network
    # e.g., delete_many({'meta': meta_id})
    c.create_index('meta')


def cleanup_edges():
    log.info('dropping old edge data')
    db = pymongo.MongoClient().networks
    result = db.edges.delete_many({'meta': {'$nin': [it['_id'] for it in db.meta.find()]}})
    log.info('dropped %s edges', result.deleted_count)

    bad = [it['_id'] for it in db.meta.find() if db.edges.count({'meta': it['_id']}) == 0]
    if len(bad) > 0:
        log.info('dropping meta records with no edges')
        result = db.meta.delete_many({'_id': {'$in': bad}})
        log.info('dropped %s records', result.deleted_count)

def gene_set_enrichment(gene_list, M=None):
    '''
    :param gene_list: list of gene symbols --> ENSG00000233636, ENSG00000129673, etc...
    :param M: total number of genes (derived from database, if None)
    :return: filtered list of set terms with p-value, q-value, and size of overlap
    '''
    client = pymongo.MongoClient()
    if not M:
        M = len(client.go.genes.distinct('gene'))
    terms = list(client.go.genes.find({'gene': {'$in': list(gene_list)}}).distinct('go')) #GO:0004059, GO:0006474, etc...
    terms = list(client.go.terms.find({'go': {'$in': terms}, 'n_genes': {'$gt': 2}}))
    enriched = [dict(term.items() + zip(('pvalue', 'overlap'), calc_pvalue(gene_list, term['genes'], M))) for term in terms]
    enriched.sort(key=lambda it: it['pvalue'])
    for qvalue, it in itertools.izip(fdr([it['pvalue'] for it in enriched], presorted=True), enriched):
        it['qvalue'] = qvalue

    return enriched

def calc_pvalue(gene_list, gene_set, M):
    gene_list = set(gene_list)
    gene_set = set(gene_set)
    N = len(gene_list)
    n = len(gene_set)
    overlap = gene_list & gene_set
    k = len(overlap)
    return hypergeom(M, n, N).sf(k), list(overlap)

def printGoList():
    client = pymongo.MongoClient()
    genesarray = ['OR2J3', 'AANAT', 'CCDC158', 'PLAC8L1']


    if(len(genesarray) > 1):
        genenodes = []
        for gene in genesarray:
            id = ''
            if id is not None:
                genenodes.append({"id": id})

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

        gene_set_enrichment(gene_list)

        for term in gene_list:
            print('%s' % term)

    terms = list(client.go.genes.find({'gene': {'$in': list(gene_list)}}).distinct('go'))
    terms = list(client.go.terms.find({'go': {'$in': terms}, 'n_genes': {'$gt': 2}})) #{"synonym": "\"response to insulin stimulus\" EXACT [GOC:dos]", "name": "response to insulin", "genes": ["ENSG00000121769", "ENSG00000065675", "ENSG00000006071", "ENSG00000158571", "ENSG00000123612", "ENSG00000054356", "ENSG00000165458", "ENSG00000106128", "ENSG00000149212", "ENSG00000176387", "ENSG00000178567", "ENSG00000137563", "ENSG00000186951", "ENSG00000125629", "ENSG00000136634", "ENSG00000067225", "ENSG00000130766", "ENSG00000082556", "ENSG00000121691", "ENSG00000125931", "ENSG00000254087", "ENSG00000149485", "ENSG00000166603", "ENSG00000100311", "ENSG00000106070", "ENSG00000130304", "ENSG00000124253", "ENSG00000136244", "ENSG00000197487", "ENSG00000115457", "ENSG00000116266", "ENSG00000174697", "ENSG00000159723", "ENSG00000175564", "ENSG00000187210", "ENSG00000175206", "ENSG00000084754", "ENSG00000129673", "ENSG00000121671", "ENSG00000096717", "ENSG00000122877", "ENSG00000069482", "ENSG00000008405", "ENSG00000128564", "ENSG00000138796", "ENSG00000148926", "ENSG00000138030", "ENSG00000071677", "ENSG00000134243", "ENSG00000184557", "ENSG00000165699", "ENSG00000147162", "ENSG00000094841", "ENSG00000173039", "ENSG00000114650", "ENSG00000036473", "ENSG00000271503", "ENSG00000169047", "ENSG00000198523"], "namespace": "biological_process", "n_genes": 59, "is_a": "GO:0043434 ! response to peptide hormone", "go": "GO:0032868", "_id": {"$oid": "55c3c49df6f4070f2afbe857"}, "def": "\"Any process that results in a change in state or activity of a cell or an organism (in terms of movement, secretion, enzyme production, gene expression, etc.) as a result of an insulin stimulus. Insulin is a polypeptide hormone produced by the islets of Langerhans of the pancreas in mammals, and by the homologous organs of other organisms.\" [GOC:mah, ISBN:0198506732]"}


    for term in terms:
        print('%s' % dumps(term))

def agg_search_data():
    client = pymongo.MongoClient(app.mongodb_uri)
    #write_result = dumps(client.cache.searches.insert({'terms': terms, 'termsSplit': terms.split(','), 'timeStamp': util.timestamp()}))

    group_this = [{'$unwind': '$termsSplit'},
        {'$group': {'_id': '$termsSplit', 'count': {'$sum': 1}}}]

    result = list(client.cache.searches.aggregate(group_this))

    return result

def mapreduce_stats():

    map = Code("function () {"
        "  this.tags.forEach(function(z) {"
        "    emit(z, 1);"
        "  });"
        "}")

    reduce = Code("function (key, values) {"
           "  var total = 0;"
           "  for (var i = 0; i < values.length; i++) {"
           "    total += values[i];"
           "  }"
           "  return total;"
           "}")

    #result = db.things.map_reduce(map, reduce, "myresults")
    #for doc in result.find():
    #    print doc

def compute_query_list_hash(search_terms):
    query_terms_sorted = sorted(search_terms.split(','))
    query_terms_sorted_string = ''.join(query_terms_sorted)
    #print query_terms_sorted_string
    h = hashlib.new('ripemd160')
    h.update(query_terms_sorted_string)  #network_info['queryTerms'])
    computed_hash = h.hexdigest()
    return computed_hash

