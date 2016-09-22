#!/usr/local/bin/python

#from gevent import monkey
#monkey.patch_all()

import sys
import pymongo
import argparse
from bson import ObjectId
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import bottle
from bottle import Bottle, redirect, static_file, request

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

import app
from app.util import serialize, get_value
from app.dropbox import dropbox

api = Bottle()

import nav.api
api.merge(nav.api.api)

import nav.SearchRESTLayer
api.merge(nav.SearchRESTLayer.api)

log = app.get_logger('api')

# default to the network analysis app index page
@api.get('/')
def index():
    redirect('/static/workflow/html/index.html')


# generic API to serve any resource in the static directory
@api.get('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root=app.static_path)


# generic API for querying a specific mongo database/collection
@api.get('/api/mongo/:database/:collection')
def api_mongo_get(database, collection):
    limit = get_value('limit', 0, int)
    skip = get_value('skip', 0, int)
    client = pymongo.MongoClient(app.mongodb_uri)
    query = {k:v for k, v in request.query.iteritems() if not k == 'limit' and not k == 'skip'}
    cursor = client[database][collection].find(query)
    return {
        'skip': skip,
        'count': cursor.count(),
        'records': [serialize(record) for record in cursor.limit(limit).skip(skip)]
    }

# generic API for returning the record count for a specific mongo database/collection
@api.get('/api/mongo/:database/:collection/count')
def api_mongo_count(database, collection):
    client = pymongo.MongoClient(app.mongodb_uri)
    return {
        'count' : client[database][collection].count()
    }


# generic API for returning a single record by id from a specific mongo database/collection
@api.get('/api/mongo/:database/:collection/:id')
def api_mongo_get_id(database, collection, id):
    client = pymongo.MongoClient(app.mongodb_uri)
    return serialize(client[database][collection].find_one({'_id': ObjectId(id)}))


# run the web server
def main():
    status = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, help='HTTP port', default=80)
    args = parser.parse_args()

    # start the dropbox service for handling file uploads
    #dropbox.start()

    print 'starting web server on port %s' % args.port
    print 'press control-c to quit'
    try:
        server = WSGIServer(('0.0.0.0', args.port), api, handler_class=WebSocketHandler)
        log.info('entering main loop')
        server.serve_forever()
    except KeyboardInterrupt:
        dropbox.stop()
        log.info('exiting main loop')
    except Exception as e:
        str = 'could not start web server: %s' % e
        log.error(str)
        print str
        status = 1

    dropbox.stop()
    dropbox.join(60)

    log.info('exiting with status %d', status)
    return status


if __name__ == '__main__':
    sys.exit(main())