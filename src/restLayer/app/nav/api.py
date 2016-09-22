import pymongo
from bson import ObjectId
from bottle import Bottle, request, HTTPError, response

import app
from app.util import serialize, deserialize, set_status
from app import genemania

from bson.json_util import dumps

log = app.get_logger('nav api')
api = Bottle()

@api.put('/api/nav/project')
def create_project():
    client = pymongo.MongoClient(app.mongodb_uri)
    project = {
        'gene_list': [],
        'include_neighbors': True,
        'n_connected_neighbors': 20,
        'n_hottest_neighbors': 20,
        'do_heat_diffusion': False
    }
    set_status(project, 'created')
    project['_id'] = str(client.nav.projects.insert(project))
    return serialize(project)


@api.get('/api/nav/networks')
def get_networks():
    client = pymongo.MongoClient(app.mongodb_uri)
    pre_return_value = {'networks': serialize(list(client.networks.meta.find({'status': 'success'})))}
    return_value = dumps(pre_return_value)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return pre_return_value
    #return {'networks': serialize(list(client.networks.meta.find({'status': 'success'})))}


@api.put('/api/nav/project/:id/state/:state')
def put_state(id, state):
    client = pymongo.MongoClient(app.mongodb_uri)
    project = client.nav.projects.find_one({'_id': ObjectId(id)})
    project['state'] = state
    set_status(project, 'updated')
    client.nav.projects.save(project)


@api.post('/api/nav/project')
def update_project():
    client = pymongo.MongoClient(app.mongodb_uri)
    project = request.json
    try:
        project = deserialize(project)  # convert string id to ObjectId
        set_status(project, 'updated')
        client.nav.projects.save(project)
        return {'timestamp': project['timestamp']['updated']}
    except:
        return HTTPError(400)


@api.post('/api/nav/network')
def save_network():
    client = pymongo.MongoClient(app.mongodb_uri)
    network = request.json
    network = deserialize(network)  # convert string id to ObjectId
    set_status(network, 'updated')
    client.nav.networks.save(network)
    return {'timestamp': network['timestamp']['updated']}


@api.delete('/api/nav/project/:id')
def delete_project(id):
    client = pymongo.MongoClient(app.mongodb_uri)
    return client.nav.projects.remove({'_id': ObjectId(id)})


@api.get('/api/nav/project/:id')
def get_project(id):
    client = pymongo.MongoClient(app.mongodb_uri)
    project = client.nav.projects.find_one({'_id': ObjectId(id)})
    if project:
        meta = {str(meta['_id']): meta for meta in client.networks.meta.find({'status': 'success'})}
        try:
            networks = project['networks']
            networks = {id: True for id in meta.iterkeys() if networks.get(id)}
        except KeyError:
            # include all genemania networks except co-expression for new projects
            networks = {id: True for id, it in meta.iteritems() if it['collection'] == 'genemania' and not it['type'] == 'co-expression'}
        project['networks'] = networks
        client.nav.projects.save(project)

        pre_return_value = serialize(project)
        return_value = dumps(pre_return_value)

        if (request.query.callback):
            response.content_type = "application/javascript"
            return "%s(%s);" % (request.query.callback, return_value)

        return pre_return_value
        #return serialize(project)
    else:
        return HTTPError(404)


@api.get('/api/nav/project/:id/files')
def get_files(id):
    client = pymongo.MongoClient(app.mongodb_uri)
    project = client.nav.projects.find_one({'_id': ObjectId(id)})
    try:
        files = list(client.files.meta.find({'_id': {'$in': [f['_id'] for f in project.get('files', [])]}}))



        pre_return_value = {'records': serialize(files)}
        return_value = dumps(pre_return_value)

        if (request.query.callback):
            response.content_type = "application/javascript"
            return "%s(%s);" % (request.query.callback, return_value)

        return pre_return_value
        #return {'records': serialize(files)}
    except:
        return HTTPError(404)


@api.get('/api/nav/project/:id/jobs')
def get_jobs(id):
    client = pymongo.MongoClient(app.mongodb_uri)
    jobs = list(client.nav.jobs.find({'project._id': ObjectId(id)}))

    pre_return_value = {'records': serialize(jobs)}
    return_value = dumps(pre_return_value)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return pre_return_value
    #return {'records': serialize(jobs)}

@api.post('/api/nav/job/:id/name')
def update_job_name(id):
    try:
        client = pymongo.MongoClient(app.mongodb_uri)
        job = client.nav.jobs.find_one({'_id': ObjectId(id)})
        job['name'] = request.json['name']
        log.debug('updated job %s with name %s', id, job['name'])
        client.nav.jobs.save(job)
    except Exception as e:
        raise HTTPError(500, e)


@api.delete('/api/nav/job/:id')
def delete_job(id):
    try:
        client = pymongo.MongoClient(app.mongodb_uri)
        client.nav.jobs.remove({'_id': ObjectId(id)})
    except:
        return HTTPError(404)


@api.get('/api/nav/gene/:name')
def get_gene(name):
    client = pymongo.MongoClient(app.mongodb_uri)
    c = client.identifiers.genemania

    id = genemania.lookup_id(name)
    if id is None:
        return HTTPError(404)

    pre_return_value = {result['source']: result['name'] for result in c.find({'preferred': id, 'source': {'$ne': 'Synonym'}})}
    return_value = dumps(pre_return_value)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return pre_return_value
    #return {result['source']: result['name'] for result in c.find({'preferred': id, 'source': {'$ne': 'Synonym'}})}

@api.get('/api/nav/gene/batch/:names')
def get_gene_batch(names):
    returnResults = []
    client = pymongo.MongoClient(app.mongodb_uri)
    c = client.identifiers.genemania

    queryTermArray = names.split(',')

    for queryTerm in queryTermArray:

        id = genemania.lookup_id(queryTerm)
        if id is not None:
            returnResults.append({result['source']: result['name'] for result in c.find({'preferred': id, 'source': {'$ne': 'Synonym'}})})

    return dumps(returnResults)
