from bson import ObjectId
import pymongo
from app import genemania
import threading
import multiprocessing
from collections import defaultdict
from operator import itemgetter
import math

from app.diffusion.kernel_scipy import SciPYKernel

from app import go
from app.util import set_status, to_boolean, to_numeric

import app
log = app.get_logger('network analysis job queue')


def run_job(job, event):
    ''' network analysis job, run as a separate process

    :param job: job object that contains a snapshot of the project
    :param event: used to inform parent thread of completion
    :return: all artifacts are saved to the database

    The job creates a network artifact, with values defined as follows:

    sources:
    {
       source1_id: source1, # file meta-data object
       source2_id: source2
    }

    nodes:
    [
       {
          'id': id,
          source_id: {key: value, ...} # data objects contain key/value pairs of node attributes from the different sources
       },
       ...
    ]

    edges:
    [
       {
          'source': source_id,
          'target': target_id,
          'source node': source_name,
          'target node': target_name,
          'type': type
       },
       ...
    ]
    '''

    job_query = {'_id': job['_id']}

    client = pymongo.MongoClient(app.mongodb_uri)
    project = job['project']

    # create a network artifact
    # nodes, edges, and groups are added to this artifact as part of the job
    artifact = {
        'project': job['project']['_id'],
        'job': job['_id'],
        'sources': {},
        'groups': {
            'node': [],
            'edge': []
        }
    }

    query_genes = [gene['Ensembl Gene ID'] for gene in project['gene_list'] if 'Ensembl Gene ID' in gene]

    meta = {it['_id']: it for it in client.networks.meta.find()}

    meta_ids = [ObjectId(id) for id, value in project['networks'].iteritems() if value]

    if project.get('include_neighbors', False):

        query_genes = set(query_genes)

        client.nav.jobs.update(job_query, {'$set': {'status_message': 'finding genes in one-step neighborhood'}})

        # find one-step neighborhood around query genes (ignoring duplicate edges)
        # originally, we found all edges using a single query {'$or': [{'source': {'$in': query_genes}, 'target': {'$in': query_genes}], 'meta': {'$in': meta_ids}}
        # however, the approach below seems to be faster, perhaps due to the distinct operation
        degrees = defaultdict(int)
        for gene in query_genes:
            for target in client.networks.edges.find({'source': gene, 'meta': {'$in': meta_ids}}).distinct('target'):
                degrees[target] += 1
            for source in client.networks.edges.find({'target': gene, 'meta': {'$in': meta_ids}}).distinct('source'):
                degrees[source] += 1

        n = project['n_connected_neighbors']

        client.nav.jobs.update(job_query, {'$set': {'status_message': 'finding top {} neighbors'.format(n)}})

        # remove query genes from the degrees dictionary
        degrees = {key: value for key, value in degrees.iteritems() if key not in query_genes}

        # sort by descending value
        neighbors = [gene for gene, _ in sorted(degrees.items(), key=itemgetter(1), reverse=True)]

        # take top n neighbors
        neighbors = neighbors[:n]

        # final gene set contains the query genes and top n neighbors
        nodes = list(query_genes | set(neighbors))

        if project.get('do_heat_diffusion', False):
            # use heat diffusion algorithm to further refine the list of neighbors

            # find all edges within the one-step neighborhood
            client.nav.jobs.update(job_query, {'$set': {'status_message': 'finding edges for {} node one-step neighborhood'.format(len(nodes))}})
            edges = set()
            for edge in client.networks.edges.find({'source': {'$in': nodes}, 'target': {'$in': nodes}, 'meta': {'$in': meta_ids}}):
                edges.add(tuple(sorted((edge['source'], edge['target']))))

            client.nav.jobs.update(job_query, {'$set': {'status_message': 'calculating heat diffusion kernel for {} nodes and {} edges (this may take a while)'.format(len(nodes), len(edges))}})

            # calculate heat diffusion kernel (influence matrix)
            # THIS TAKES A LONG TIME
            kernel = SciPYKernel(edges)

            client.nav.jobs.update(job_query, {'$set': {'status_message': 'calculating heat diffusion result'}})

            weighted = 'heat_diffusion_weights' in project

            if weighted:
                try:
                    # w = {'file': <file meta object>, 'header': {'key': <column key>, ...}}
                    w = project['heat_diffusion_weights']
                    file = w['file']
                    id = str(file['_id'])
                    key = w['header']['key']

                    # vector = {name: |value|, ...}, where name is untranslated
                    # NOTE: we take the absolute value of the data because we can't have negative weights
                    #       this works well for values like fold change, where we're interested in either large positive or negative changes
                    #       any more sophisticated transforms should be provided in the input file
                    vector = {it[file['headers'][0]['key']]: math.fabs(float(it[key])) for it in client.files[id].find()}

                    # translate gene name to id
                    name_to_id = genemania.id_lookup_table(vector.keys())
                    vector = {name_to_id[key]: value for key, value in vector.iteritems()}

                    # reduce the vector to only the query genes
                    vector = {key: value for key, value in vector.iteritems() if key in query_genes}

                    # normalize weights
                    total = sum(vector.values())
                    vector = {key: value / total for key, value in vector.iteritems()}

                    # flag success if we made it this far
                    weighted = True

                except KeyError:
                    log.warning('weighted heat diffusion failed, reverting to uniform weights')

            if not weighted:
                # create uniform weighted heat vector (treats all query genes as equal point sources)
                vector = {gene: 1.0 / len(query_genes) for gene in query_genes}

            # calculate diffused heat
            metric = kernel.kernelMultiplyOne(vector)

            n = project.get('n_hottest_neighbors', 20)

            client.nav.jobs.update(job_query, {'$set': {'status_message': 'finding top {} neighbors'.format(n)}})

            # remove query genes from the metric
            metric = {key: value for key, value in metric.iteritems() if key not in query_genes}

            # sort by descending value
            neighbors = [gene for gene, _ in sorted(metric.items(), key=itemgetter(1), reverse=True)]

            # take top n neighbors
            neighbors = neighbors[:n]

            # final gene set contains the query genes and top n neighbors
            nodes = list(query_genes | set(neighbors))

    else:
        nodes = query_genes

    client.nav.jobs.update(job_query, {'$set': {'status_message': 'finding final edge list for {} genes'.format(len(nodes))}})

    # final edge list
    query = {
        'source': {'$in': nodes},
        'target': {'$in': nodes},
        'meta': {'$in': meta_ids}
    }

    # final edge list contains all edges in the final gene set
    edges = list(client.networks.edges.find(query, ['source', 'target', 'meta']))

    client.nav.jobs.update(job_query, {'$set': {'status_message': 'calculating degree for {} genes from {} edges'.format(len(nodes), len(edges))}})

    # calculate degrees based on final edge list (do not count duplicates)
    degrees = defaultdict(int)
    for source, target in set(tuple(sorted((edge['source'], edge['target']))) for edge in edges):
        degrees[source] += 1
        degrees[target] += 1

    id_to_name = genemania.name_lookup_table(nodes)

    # create node objects
    def make_node(node):
        return {
            'id': node,
            'name': id_to_name[node],
            'query': node in query_genes,
            'degree': degrees[node]
        }

    # for convenience in merging data, nodes are initially stored as a dict keyed by id
    # it will be converted to a list of values later
    artifact['nodes'] = {node: make_node(node) for node in nodes}

    # create edge objects
    def make_edge(idx, edge):
        m = meta[edge['meta']]
        return {
            'id': 'e{}'.format(idx),
            'source': edge['source'],
            'target': edge['target'],
            'source name': id_to_name[edge['source']],
            'target name': id_to_name[edge['target']],
            'network collection': m.get('collection'),
            'network type': m.get('type'),
            'network source': m.get('source'),
            'network name': m.get('name')
        }

    artifact['edges'] = [make_edge(idx, e) for idx, e in enumerate(edges)]

    # add data from uploaded files
    for file in project['files']:
        client.nav.jobs.update(job_query, {'$set': {'status_message': 'adding node data from {}'.format(file['name'])}})

        source_id = str(file['_id'])
        artifact['sources'][source_id] = file

        # merge node data from file and add source info
        key = file['headers'][0]['key']
        for data in client.files[str(file['_id'])].find():
            id = genemania.lookup_id(data.pop(key))
            if id in artifact['nodes']:
                data.pop('_id')
                for header in file['headers']:
                    try:
                        value = data[header['key']]
                    except Exception:
                        continue

                    if header['datatype'] == 'numeric':
                        value = to_numeric(value)
                    elif header['datatype'] == 'boolean':
                        value = to_boolean(value)

                    data[header['key']] = value

                artifact['nodes'][id][source_id] = data

        set_status(file, 'success')
        client.nav.jobs.save(job)

    # convert nodes dictionaries to list of values
    artifact['nodes'] = artifact['nodes'].values()

    client.nav.jobs.update(job_query, {'$set': {'status_message': 'calculating gene set enrichment'}})

    # add query genes to node_groups
    artifact['groups']['node'].append({
        'id': 'query',
        'name': 'Query Genes',
        'description': 'Set of {} gene{} in the user query.'.format(len(query_genes), '' if len(query_genes) == 1 else 's'),
        'items': list(query_genes)
    })

    # do gene set enrichment
    gene_list = [node['id'] for node in artifact['nodes']]
    enriched = go.gene_set_enrichment(gene_list)[:20]  # get the top 20 go terms

    for it in enriched:
        artifact['groups']['node'].append({
            'id': it['go'].replace('GO:', 'go'),
            'name': it['name'],
            'description': it['def'],
            'items': it['overlap'],
            'count': it['n_genes'],
            'pvalue': it['pvalue'],
            'qvalue': it['qvalue']
        })

    # group edges by field
    def make_edge_groups(field):
        items = set(edge[field] for edge in artifact['edges'] if edge[field] is not None)
        for it in items:
            artifact['groups']['edge'].append({
                'name': it,
                'items': [e['id'] for e in artifact['edges'] if e[field] == it]
            })

    make_edge_groups('network collection')
    make_edge_groups('network type')

    set_status(artifact, 'created')
    print('made it to create networks')
    id = client.nav.networks.insert(artifact)

    job['network'] = {
        '_id': id,
        'nodes': len(artifact['nodes']),
        'edges': len(artifact['edges'])
    }

    set_status(job, 'success')
    client.nav.jobs.save(job)

    # inform parent thread of job completion
    event.set()


class JobQueue(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = multiprocessing.Event()
        self.daemon = True

    @staticmethod
    def process_name(id):
        return 'job-{}'.format(id)

    def submit(self, project_id):
        client = pymongo.MongoClient(app.mongodb_uri)
        project = client.nav.projects.find_one({'_id': project_id})

        if project:

            def plural(n, singular, plural=None):
                str = '{} '.format(n)
                if n == 1:
                    return str + singular
                else:
                    return str + (plural if plural is not None else singular + 's')

            name = plural(len(project['gene_list']), 'Gene')


            n = len(project.get('files', []))
            if n > 0:
                name += ' + ' + plural(n, 'File')

            if project.get('include_neighbors'):
                name += ' + ' + (plural(project['n_hottest_neighbors'], 'Hottest Neighbor') if project.get('do_heat_diffusion') else plural(project['n_connected_neighbors'], 'Most Connected Neighbor'))

            # create new job
            job = {
                'project': project,
                'name': name
            }
            set_status(job, 'pending')

            # add snapshot of successful file meta-data to job and reset status
            project['files'] = [it for it in client.files.meta.find({'_id': {'$in': [it['_id'] for it in project.get('files', [])]}}) if it['status'] == 'success']
            for file in project['files']:
                del file['status']
                del file['timestamp']

            job_id = client.nav.jobs.insert(job)

            log.info('submit project %s succeeded as job %s', project_id, job_id)

            # FIXME comment out the following line to run jobs in a separate thread (uncomment it to enable debug breakpoints in the job)
            #run_job(job, self.event)

            # inform the job queue thread
            self.event.set()
        else:
            log.error('submit project failed because project %s was not found', project_id)
            raise LookupError()

    def cancel(self, id):
        client = pymongo.MongoClient(app.mongodb_uri)
        job = client.nav.jobs.find_one({'_id': id})

        if job:
            log.info('cancelling job %s with status %s', id, job['status'])

            # look for job among active processes
            for process in multiprocessing.active_children():
                if process.name == self.process_name(id):
                    # send terminate signal to process and wait for it to finish
                    log.info('terminating job %s', id)
                    process.terminate()

                    log.info('waiting for job %s to terminate', id)
                    process.join()

                    log.info('job %s terminated', id)

                    # inform the job queue thread
                    self.event.set()

            set_status(job, 'cancelled')
            client.nav.jobs.save(job)

        else:
            log.error('cancel job failed because job %s was not found', id)
            raise LookupError

    def run(self):
        while True:
            if len(multiprocessing.active_children()) < multiprocessing.cpu_count():
                # look for the next pending job
                client = pymongo.MongoClient(app.mongodb_uri)
                job = client.nav.jobs.find_one({'status': 'pending'})
                if job:
                    # start the job as a new process
                    set_status(job, 'processing')
                    client.nav.jobs.save(job)
                    try:
                        process = multiprocessing.Process(name=self.process_name(job['_id']), target=run_job, args=(job, self.event))
                        process.start()
                        log.info('processing job %s', job['_id'])
                    except Exception as e:
                        set_status(job, 'error')
                        client.nav.jobs.save(job)
                        log.error('could not start job %s (%s)', job['_id'], e.message)

            # wait for events like new, cancelled, or finished jobs
            self.event.wait()
            self.event.clear()


