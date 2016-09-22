import pymongo
import math
import glob
import os
import argparse
import sys
from itertools import islice
from util import set_status, create_edges_index, cleanup_edges
import genemania

from status import Status

import app
log = app.get_logger('tcga')

#create dictionary of mappings of genes to Ensembl IDs
def build_mapping(file):
    id_to_symbol = dict()
    with open(file) as fid:
        for line in fid:
            target, src = line.split()
            id_to_symbol[src] = target

    symbol_to_id = genemania.id_lookup_table(id_to_symbol.values())
    id_to_ensembl = {k: symbol_to_id[v] for k, v in id_to_symbol.iteritems() if v in symbol_to_id}

    return id_to_symbol, id_to_ensembl


def parse_edges(dir, meta_id, id_to_symbol, id_to_ensembl, threshold):
    for filename in glob.glob(os.path.join(dir, '*.cor')):
        with open(filename) as fid:
            status = Status('processing ' + filename, logger=log).fid(fid).start()
            for line in fid:
                status.log()
                try:
                    source, target, correlation, pvalue = line.split()
                    correlation = float(correlation)
                except Exception as e:
                    log.error(e.message)
                    continue

                if math.fabs(correlation) > threshold:
                    try:
                        yield {'source': id_to_ensembl[source], 'target': id_to_ensembl[target], 'correlation': correlation, 'pvalue': float(pvalue), 'meta': meta_id}
                    except KeyError as e:
                        log.error('could not map identifier %s (%s)', e.message, id_to_symbol.get(e.message))

            status.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', help='mapping file')
    parser.add_argument('--path', help='folder(s) containing correlation files (e.g., ./*_rnaSeqV2_vs_rnaSeqV2)')
    parser.add_argument('--threshold', nargs='?', type=float, help='correlation threshold', default=0.5)
    args = parser.parse_args()

    id_to_symbol, id_to_ensembl = build_mapping(args.map)

    client = pymongo.MongoClient()
    db = client.networks

    # collection stores metadata about source networks
    meta = db.meta

    # collection stores edge data
    edges = db.edges

    create_edges_index()

    dirs = [dir for dir in glob.glob(args.path) if os.path.isdir(dir)]

    for dir in dirs:
        log.info('processing %s', dir)

        metadata = {
            'name': os.path.basename(dir).split('_')[0].upper(),
            'collection': 'TCGA',
            'type': 'co-expression'
        }

        # old metadata records and their associated edges will be dropped after the new network is finished processing
        _ids = [result['_id'] for result in meta.find(metadata)]
        log.info('found %d matching network(s) that will be replaced: %s', len(_ids), ', '.join([str(_id) for _id in _ids]))

        set_status(metadata, 'parsing')
        meta_id = meta.insert_one(metadata).inserted_id

        count = 0
        iterator = parse_edges(dir, meta_id, id_to_symbol, id_to_ensembl, args.threshold)
        while True:
            records = [record for record in islice(iterator, 10000)]
            if len(records) > 0:
                count += len(edges.insert_many(records).inserted_ids)
                log.debug('inserted %d edges (%d total)', len(records), count)
            else:
                break

        # add record count to the metadata
        metadata['count'] = count
        log.info('%s network has %d edges', metadata['name'], metadata['count'])

        set_status(metadata, 'success')
        meta.save(metadata)

        if len(_ids) > 0:
            log.info('dropping old network metadata')
            meta.delete_many({'_id': {'$in': _ids}})

    cleanup_edges()

    log.info('finished')

    return 0


if __name__ == '__main__':
    sys.exit(main())

