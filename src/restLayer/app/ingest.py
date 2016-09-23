import re
import csv
import pymongo
import itertools
from bioservices import WikiPathways


import app
from util import save_file_metadata, split_id, is_numeric, is_boolean

log = app.get_logger('ingest')


def ingest(filepath):
    _id, _ = split_id(filepath)

    client = pymongo.MongoClient()

    meta = client.files.meta.find_one({'_id': _id})

    if meta:
        parser = meta['parser']

        if parser == 'tsv':
            data = ingest_tsv(filepath)
        else:
            raise NotImplementedError('unknown parser %s'.format(parser))

        client.files[str(_id)].insert(data)

        return save_file_metadata(filepath, status='success', count=len(data))

    else:
        save_file_metadata(filepath, status='error')
        raise LookupError('no metadata found for {}'.format(filepath))


def ingest_tsv(filepath):
    log.info('ingesting %s as tsv file', filepath)
    save_file_metadata(filepath, status='parsing', filetype='tsv')
    with open(filepath, 'rU') as fid:
        reader = csv.reader(fid, delimiter='\t')
        header = reader.next()
        log.debug("%d columns: %s", len(header), ", ".join(header))
        if len(header) == 0:
            raise ValueError('header row must contain at least one column')

        keys = [normalize_column_name(h) for h in header]

        def parse(row):
            if len(keys) == len(row):
                return dict(zip(keys, row))

        parsed = [parse(row) for row in reader]
        parsed = [v for v in parsed if v is not None]

        header = [{'raw': h, 'key': k} for h, k in itertools.izip(header, keys)]

        for h in header:
            data = [p[h['key']] for p in parsed]
            if all(is_boolean(d) for d in data):
                h['datatype'] = 'boolean'
            elif all(is_numeric(d) for d in data):
                h['datatype'] = 'numeric'
            else:
                h['datatype'] = 'string'

        save_file_metadata(filepath, headers=header)

        return parsed


# replace all " " with "_"
def normalize_column_name(name):
    return re.sub(r'\W+', '_', name.lower())
