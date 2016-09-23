#!/usr/local/bin/python

import sys
import pymongo
import argparse
from bson import ObjectId
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import bottle
from bottle import Bottle, redirect, request, response, static_file, request
from bson.json_util import dumps
import author_gene_clustering_module

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

import app

api = Bottle()

log = app.get_logger('api_alt')

# generic API for returning the record count for a specific mongo database/collection
@api.get('/ds/getmessage')
def ds_getmessage():
    return {
        'message' : 'success'
    }

# generic API for returning the record count for a specific mongo database/collection
@api.get('/ds/getbpnet/:genes')
def ds_get_bp_net(genes):
    genes_list = genes.split(',')
    graph_json = author_gene_clustering_module.analyze_AG_bipartite_network(genes_list)

    if (request.query.callback):
        response.content_type = "application/javascript"
        return "%s(%s);" % (request.query.callback, graph_json)

    return graph_json



    return {
        'message' : graph_json
    }

# run the web server
def main():
    status = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, help='HTTP port', default=80)
    args = parser.parse_args()

    print 'starting web server on port %s' % args.port
    print 'press control-c to quit'
    try:
        server = WSGIServer(('0.0.0.0', args.port), api, handler_class=WebSocketHandler)
        log.info('entering main loop')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('exiting main loop')
    except Exception as e:
        str = 'could not start web server: %s' % e
        log.error(str)
        print str
        status = 1

    log.info('exiting with status %d', status)
    return status


if __name__ == '__main__':
    sys.exit(main())