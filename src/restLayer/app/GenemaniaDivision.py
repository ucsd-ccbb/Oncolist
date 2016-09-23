import sys
import pymongo
import requests
import argparse
from itertools import islice

from app.util import set_status, create_edges_index
from app.status import Status
import app

log = app.get_logger('genemania')

def lookup_name(id, source='Gene Name'):
    '''
    :param id: ensembl ID
    :param source: source (e.g., 'Gene Name')
    :return: name
    '''
    c = pymongo.MongoClient().identifiers.genemania
    result = c.find_one({'preferred': id, 'source': source})
    return None if result is None else result['name']


def lookup_id(name):
    '''
    :param name: gene id, symbol, or synonym to find in the name column (case insensitive)
    :return: ensembl ID (or None)
    '''
    c = pymongo.MongoClient().identifiers.genemania
    result = c.find_one({'NAME': name.upper()})
    return None if result is None else result['preferred']


def id_lookup_table(names):
    '''
    :param names: gene id, symbol, or synonym (case insensitive)
    :return: dictionary mapping names to ensembl IDs
    '''
    c = pymongo.MongoClient().identifiers.genemania
    map = {it['NAME']: it['preferred'] for it in c.find({'NAME': {'$in': [name.upper() for name in names]}})}
    return {name: map.get(name.upper()) for name in names}


def name_lookup_table(ids, source='Gene Name'):
    '''
    :param ids: ensembl IDs
    :param source: source (e.g., 'Gene Name')
    :return: dictionary mapping ensembl IDs to
    '''
    c = pymongo.MongoClient().identifiers.genemania
    return {it['preferred']: it['name'] for it in c.find({'preferred': {'$in': ids}, 'source': source})}


def load_network(url, _id):
    log.info('loading %s', url)
    r = requests.get(url, stream=True)
    lines = r.iter_lines()
    lines.next()  # ignore header

    def parse(lines):
        for line in lines:
            try:
                source, target, weight = line.split()
                yield {
                    'source': source,
                    'target': target,
                    'weight': float(weight),
                    'meta': _id
                }
            except Exception as e:
                log.warn(e.message)

    edges = pymongo.MongoClient().networks.edges

    count = 0
    iterator = parse(lines)
    while True:
        records = [record for record in islice(iterator, 1000)]
        if len(records) > 0:
            count += len(edges.insert_many(records).inserted_ids)
            log.debug('inserted %d edges (%d total)', len(records), count)
        else:
            break
    return count


def load_identifiers():
    db = pymongo.MongoClient().human
    db.identifiers.drop()
    collection = db.identifiers
    humanUrl = 'http://genemania.org/data/current/Homo_sapiens/identifier_mappings.txt'

    status = Status('loading genemania identifiers from ' + humanUrl, logger=log).start()

    r = requests.get(humanUrl)
    lines = r.iter_lines()
    lines.next() # ignore header row

    def parse(lines):
        for line in lines:
            try:
                preferred, name, source = line.split('\t')
                yield {
                    'preferred': preferred,
                    'name': name,
                    'NAME': name.upper(), # indexed to support case-insensitive queries
                    'source': source
                }
            except Exception as e:
                log.warn(e.message)

    count = 0
    iterator = parse(lines)
    while True:
        records = [record for record in islice(iterator, 1000)]
        if len(records) > 0:
            count += len(collection.insert_many(records).inserted_ids)
            log.debug('inserted %d identifiers (%d total)', len(records), count)
        else:
            break

    log.info('creating NAME and preferred indexes')
    collection.create_indexes([
        pymongo.IndexModel([('NAME', pymongo.ASCENDING)]),
        pymongo.IndexModel([('preferred', pymongo.ASCENDING)])
    ])

    status.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--warmstart', action='store_true', help='warmstart')
    args = parser.parse_args()

    if not args.warmstart:
        load_identifiers()

    client = pymongo.MongoClient()
    db = client.networks

    # collection stores metadata about source networks
    meta = db.meta

    # collection stores edge data
    edges = db.edges

    create_edges_index()

    url = 'http://genemania.org/data/current/Homo_sapiens/networks.txt'
    log.info('reading network list from %s', url)
    r = requests.get(url)
    lines = list(r.iter_lines())[1:] # ignore header line

    status = Status('networks', logger=log).n(len(lines)).start()
    for idx, line in enumerate(lines):
        status.log(idx)
        file_name, network_group_name, network_name, source, pubmed_id = line.split('\t')

        metadata = {
            'collection': 'identifiers',
            'type': network_group_name.lower(),
            'source': source,
            'name': network_name,
            'pubmed': int(pubmed_id) if not pubmed_id == '' else 0
        }

        if not args.warmstart or meta.find_one(dict(metadata.items() + [('status', 'success')])) is None:

            # old metadata records and their associated edges will be dropped after the new network is finished processing
            _ids = [result['_id'] for result in meta.find(metadata)]
            log.info('found %d matching network(s) that will be replaced: %s', len(_ids), ', '.join([str(_id) for _id in _ids]))

            set_status(metadata, 'parsing')
            _id = meta.insert_one(metadata).inserted_id

            metadata['count'] = load_network('http://genemania.org/data/current/Homo_sapiens/' + file_name, _id)
            log.info('%s %s %s network has %d edges', metadata['source'], metadata['name'], metadata['type'], metadata['count'])

            set_status(metadata, 'success')
            meta.save(metadata)

            if len(_ids) > 0:
                log.info('dropping old network metadata')
                meta.delete_many({'_id': {'$in': _ids}})

    log.info('dropping old edge data')
    edges.delete_many({'meta': {'$nin': [it['_id'] for it in meta.find()]}})

    status.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())