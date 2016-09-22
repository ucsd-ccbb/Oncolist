__author__ = 'aarongary'
import pymongo
from bottle import Bottle, request, HTTPError, response

import app
from app import genemania

from bson.json_util import dumps
api = Bottle()



@api.put('/api/nav/project/:id/state/:state')
def put_state(id, state):
    client = pymongo.MongoClient(app.mongodb_uri)

    genelist = {
        'id': 1,
        'mygenelist': ['BRCA1','BRCA2']
    }


    client.nav.projects.save(genelist)

@api.get('/gene/lookup/list/:id')
def get_gene(id):
    client = pymongo.MongoClient(app.mongodb_uri)
    c = client.identifiers.genemania

    id = genemania.lookup_id(id)
    if id is None:
        return HTTPError(404)




    returnValue = c.find({'id': id})

    pre_return_value = {result['source']: result['name'] for result in c.find({'id': id})}

    return_value = dumps(pre_return_value)
    print return_value

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, return_value)

    return pre_return_value
    #return {result['source']: result['name'] for result in c.find({'preferred': id, 'source': {'$ne': 'Synonym'}})}
