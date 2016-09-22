import sys
import pymongo
import requests
import itertools
import genemania
from itertools import islice

from app.util import set_status, create_edges_index, cleanup_edges
from app.status import Status
import app

log = app.get_logger('humannet')

def parse(columns, metadata, lines):
    status = Status('networks', logger=log).n(len(lines)).start()
    for idx, line in enumerate(lines):
        status.log(idx)
        tokens = line.split('\t')

        if not len(tokens) == len(columns) + 3:
            continue

        source = tokens[0]
        target = tokens[1]

        # humannet composite score
        #score = float(tokens[-1])

        for column, token in itertools.izip(columns, tokens[2:-1]):
            try:
                # individual edge score
                score = float(token)
                metadata[column]['count'] += 1
                yield {
                    'source': source,
                    'target': target,
                    'score': score,
                    'meta': metadata[column]['_id']
                }
            except ValueError:
                pass

    status.stop()


def main():
    client = pymongo.MongoClient()
    db = client.networks

    # collection stores metadata about source networks
    meta = db.meta

    # collection stores edge data
    edges = db.edges

    # create index, if necessary
    create_edges_index()

    # get list of previously loaded networks to delete, if any
    _ids = [result['_id'] for result in meta.find({'collection': 'humannet'})]

    # From http://www.functionalnet.org/humannet/HumanNet.v1.evidence_code.txt:
    # File format: [gene1] [gene2] [CE-CC] [CE-CX] [CE-GT] [CE-LC] [CE-YH] [DM-PI] [HS-CC] [HS-CX] [HS-DC] [HS-GN] [HS-LC] [HS-MS] [HS-PG] [HS-YH] [SC-CC] [SC-CX] [SC-GT] [SC-LC] [SC-MS] [SC-TS] [SC-YH] [IntNet]
    # CE-CC = Co-citation of worm gene
    # CE-CX = Co-expression among worm genes
    # CE-GT = Worm genetic interactions
    # CE-LC = Literature curated worm protein physical interactions
    # CE-YH = High-throughput yeast 2-hybrid assays among worm genes
    # DM-PI = Fly protein physical interactions
    # HS-CC = Co-citation of human genes
    # HS-CX = Co-expression among human genes
    # HS-DC = Co-occurrence of domains among human proteins
    # HS-GN = Gene neighbourhoods of bacterial and archaeal orthologs of human genes
    # HS-LC = Literature curated human protein physical interactions
    # HS-MS = human protein complexes from affinity purification/mass spectrometry
    # HS-PG = Co-inheritance of bacterial and archaeal orthologs of human genes
    # HS-YH = High-throughput yeast 2-hybrid assays among human genes
    # SC-CC = Co-citation of yeast genes
    # SC-CX = Co-expression among yeast genes
    # SC-GT = Yeast genetic interactions
    # SC-LC = Literature curated yeast protein physical interactions
    # SC-MS = Yeast protein complexes from affinity purification/mass spectrometry
    # SC-TS = Yeast protein interactions inferred from tertiary structures of complexes
    # SC-YH = High-throughput yeast 2-hybrid assays among yeast genes
    # IntNet = Integrated network (HumanNet)

    columns = [
        'co-citation of worm gene',
        'co-expression among worm genes',
        'worm genetic interactions',
        'literature curated worm protein physical interactions',
        'high-throughput yeast 2-hybrid assays among worm genes',
        'fly protein physical interactions',
        'co-citation of human genes',
        'co-expression among human genes',
        'co-occurrence of domains among human proteins',
        'gene neighbourhoods of bacterial and archaeal orthologs of human genes',
        'literature curated human protein physical interactions',
        'human protein complexes from affinity purification/mass spectrometry',
        'co-inheritance of bacterial and archaeal orthologs of human genes',
        'high-throughput yeast 2-hybrid assays among human genes',
        'co-citation of yeast genes',
        'co-expression among yeast genes',
        'yeast genetic interactions',
        'literature curated yeast protein physical interactions',
        'yeast protein complexes from affinity purification/mass spectrometry',
        'yeast protein interactions inferred from tertiary structures of complexes',
        'high-throughput yeast 2-hybrid assays among yeast genes'
    ]

    metadata = {}

    for column in columns:
        m = {
            'collection': 'humannet',
            'name': column,
            'count': 0
        }
        set_status(m, 'parsing')
        m['_id'] = meta.insert_one(m).inserted_id
        metadata[column] = m

    url = 'http://www.functionalnet.org/humannet/HumanNet.v1.join.txt'
    log.info('reading network list from %s', url)
    r = requests.get(url)
    lines = list(r.iter_lines())

    count = 0

    iterator = parse(columns, metadata, lines)
    while True:
        records = [record for record in islice(iterator, 1000)]
        if len(records) > 0:
            name_to_id = genemania.id_lookup_table(set(it['source'] for it in records) | set(it['target'] for it in records))
            for record in records:
                source = name_to_id[record['source']]
                if source is None:
                    log.warning('unknown source %s', record['source'])
                record['source'] = source

                target = name_to_id[record['target']]
                if target is None:
                    log.warning('unknown target %s', record['target'])
                record['target'] = target

            records = [record for record in records if record['source'] is not None and record['target'] is not None]
            count += len(records)
            edges.insert_many(records)
            log.debug('inserted %d edges (%d total)', len(records), count)
        else:
            break

    for m in metadata.itervalues():
        set_status(m, 'success')
        meta.replace_one({'_id': m['_id']}, m)

    if len(_ids) > 0:
        log.info('dropping old network metadata')
        meta.delete_many({'_id': {'$in': _ids}})

    cleanup_edges()

    return 0


if __name__ == '__main__':
    sys.exit(main())