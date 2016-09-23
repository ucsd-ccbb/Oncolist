import requests
import tarfile,sys
import urllib2
import json
import time
import app.genemania
import pymongo
from itertools import islice
from bson.json_util import dumps
from app import elastic_search_uri
from elasticsearch import Elasticsearch

es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300)

def get_genemania_identifiers():
    client = pymongo.MongoClient()
    db = client.identifiers
    genemania = db.genemania

    genemania_items = genemania.find({'source': 'Gene Name'})
    for item in genemania_items:
        print item['name']


def get_pubmed_counts():
    pubmed_counts_json = []

    try:
        all_gene_names = app.genemania.get_all_gene_names()

        of = open('pubmed_with_counts.json', 'w')
        i = 0
        for gene_name in all_gene_names:
            if(i > 19800):
                print '%s' % gene_name['name']
                pubmed_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s&retmode=json' % gene_name['name']
                pubmed_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + gene_name['name'] + '&retmode=json'

                r_json = requests.get(pubmed_url).json()

                if('esearchresult' in r_json):
                    print r_json['esearchresult']['count']

                    print_this_string = '\t'.join([gene_name['name'], r_json['esearchresult']['count']])
                    of.write(print_this_string + '\n')
            i += 1

        of.close()

        #print '%s' % dumps(all_gene_names)
    except Exception as e:
        print e.message
        return "ERROR"

def get_gene_pubmed_counts_normalized(gene_list, boost_factor):

    pubmed_counts = get_gene_pubmed_counts(gene_list)

    # if there is only one term set the normalized value to 1.0 and return
    if(len(gene_list) == 1):
        pubmed_counts[0]['normalizedValue'] = 1.0
        return pubmed_counts

    all_values = []

    for t in pubmed_counts['results']:
        all_values.append(float(t['count']))

    min_value = min(all_values)
    max_value = max(all_values)

    if(min_value == max_value):
        min_value = 0

    for s in pubmed_counts['results']:
        #s['normalizedValue'] = normValue(float(s['count']), max_value, min_value, boost_factor)
        s['normalizedValue'] = 1.0 #normValue(float(s['count']), max_value, min_value, boost_factor)

    #normalized_values = normList(all_values, boost_factor)

    return pubmed_counts

def get_pubmed_titles(operation_type):
    client = pymongo.MongoClient()
    db = client.identifiers
    pubmed = db.pubmed_id_trans
    pubmed_titles = db.pubmed_metadata

    count=0

    if(operation_type == 'LOAD_PUBMED_IDS'):
        url = 'http://geneli.st/static/file_list_small.txt'

        r = requests.get(url)
        #r.next()
        lines = list(r.iter_lines())

        for idx, line in enumerate(lines):
            if(count > 0 ):
                buff1, buff2, pmc, pmid  = line.split('\t')

                term_to_add = {
                    'pmc_id': pmc.upper(),
                    'pm_id': pmid.upper()
                }

                pubmed.save(term_to_add)

            count = count + 1

            if(count % 200 == 0):
                print count

        pubmed.ensure_index([("pm_id" , pymongo.ASCENDING)])
    else:
        search_body = {
            "size": 0,
            "aggs" : {
                "pubmed_agg" : {
                    "terms" : { "field" : "node_list.pubmed", "size": 11000 }
                }
            }
        }

        result = es.search(
            index = 'conditions',
            doc_type = 'conditions_cosmic_mutant',
            body = search_body
        )

        print("Got %d Hits:" % result['hits']['total'])

        if(result['aggregations']['pubmed_agg']['buckets'] > 0):
            print len(result['aggregations']['pubmed_agg']['buckets'])
            for hit in result['aggregations']['pubmed_agg']['buckets']:
                result = pubmed.find_one({'pm_id': 'PMID:' + hit['key']})
                if(result is not None):
                    #lookup_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id=' + result['pmc_id'].replace('PMC','') + '&retmode=json&tool=my_tool&email=my_email@example.com'
                    #response = urllib2.urlopen(lookup_url)
                    #data = json.load(response)
                    #print data['result'][result['pmc_id'].replace('PMC','')]['title']

                    #term_to_add = {
                    #    'title': data['result'][result['pmc_id'].replace('PMC','')]['title'],
                    #    'pm_id': result['pmc_id'].replace('PMC','')
                    #}

                    #pubmed_titles.save(term_to_add)
                    if(count % 200 == 0):
                        print 'found'
                else:
                    count = count + 1
                    print hit['key']

            pubmed.ensure_index([("pm_id" , pymongo.ASCENDING)])

    print 'Done'
    print str(count)

def get_gene_pubmed_counts(gene_list):
    client = pymongo.MongoClient()

    pubmed_data = {
        'results': []
    }

    pubmed_gene_array = gene_list.split(',')
    for pubmed_gene_item in pubmed_gene_array :
        mystr = "";

        terms = list(client.dataset.pubmed_counts.find({'gene_name': pubmed_gene_item}))
        if(len(terms) > 0):
            pubmed_data['results'].append({
                'id': pubmed_gene_item,
                'count': int(terms[0]['abstract_count']),
                'normalizedValue': 0.0
            })
        else:
            pubmed_data['results'].append({
                'id': pubmed_gene_item,
                'count': 0,
                'normalizedValue': 0.0
            })

    sorted_by_count = sorted(pubmed_data['results'], key=lambda k: k['count'], reverse=True)

    pubmed_data['results'] = sorted_by_count

    pubmed_json = dumps(pubmed_data)

    return pubmed_data

def normList(L, normalizeTo=1):
    '''normalize values of a list to make its max = normalizeTo'''

    vMax = max(L)
    return [ x/(vMax*1.0)*normalizeTo for x in L]

def normValue(value, vMax, vMin, boost_factor):
    if(vMax != vMin):
        z = ((value * 1.0) - (vMin * 1.0)) / ((vMax * 1.0) - (vMin * 1.0)) * boost_factor
    else:
        z = 0

    return z

def lookup_id(name):
    '''
    :param name: gene id, symbol, or synonym to find in the name column (case insensitive)
    :return: ensembl ID (or None)
    '''

    return "not yet implemented!"

def id_lookup_table(names):
    '''
    :param names: gene id, symbol, or synonym (case insensitive)
    :return: dictionary mapping names to ensembl IDs
    '''

    return "not yet implemented!"

def name_lookup_table(ids, source='Gene Name'):
    '''
    :param ids: ensembl IDs
    :param source: source (e.g., 'Gene Name')
    :return: dictionary mapping ensembl IDs to
    '''

    return "not yet implemented!"

def load_network(url, _id, batch):
    return "not yet implemented!"

def run_pubmed_download():
    for i in range(33, 108):
        load_pubmed_list(i)

    return 0

def load_pubmed_counts_list():
    url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/pubmed_with_counts_complete.txt'

    r = requests.get(url)
    lines = r.iter_lines()

    def parse(lines):
        for line in lines:
            try:
                gene, gene_count = line.split('\t')
                yield {
                    'gene': gene.upper(),
                    'abstract_count': gene_count
                }
            except Exception as e:
                warningLabel = e.message

    db = pymongo.MongoClient().dataset
    collection = db.pubmed_counts
    collection.drop()

    count = 0
    iterator = parse(lines)


    for line in iterator:
        insert_this_gene_record = {
            'gene_name': line.get('gene'),
            'abstract_count': line.get('abstract_count')
        }
        collection.insert_one(insert_this_gene_record)
        count += 1
        print('%s' % count)

    collection.create_indexes([
        pymongo.IndexModel([('gene', pymongo.ASCENDING)])
    ])

    db.close()


def load_pubmed_list(file_batch_number):

    #ftpServerHost = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/"
    url = 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200/_plugin/head/file_list_dir/file_list_' + str(file_batch_number) + '.csv'
    #url = 'http://localhost:9200/_plugin/carrot2/file_list_dir/file_list_' + str(file_batch_number) + '.csv'
    #url = 'http://localhost:9200/_plugin/carrot2/file_list_small.csv'

    #status = Status('loading pubmed identifiers from ' + url, logger=log).start()

    r = requests.get(url)
    lines = r.iter_lines()

    def parse(lines):
        for line in lines:
            try:
                fileName, articleCitation, accessionId, four, pmid  = line.split(',')
                yield {
                    'File': fileName,
                    'ArticleCitation': articleCitation,
                    'AccessionId': accessionId,
                    'pmid': pmid
                }
            except Exception as e:
                warningLabel = "";
                #log.warn(e.message)

    count = 0
    iterator = parse(lines)
    iterator.next() # skip the header line


    of = open('pubmed_json_files/ElasticSearchAbstractLoad_' + str(file_batch_number) + '.json', 'w')

    for line in iterator:
        getAbstractStatus = "ERROR"
        while getAbstractStatus == "ERROR" :
            #print getAbstractStatus
            getAbstractStatus = getAbstractByID(line.get("pmid"), of)
            if(getAbstractStatus == "ERROR"):
                print "sleeping... " + getAbstractStatus
                time.sleep(10)

        #download_tar_gz(ftpServerHost, line.get("File"))

    of.close()

    print "Done"

    #status.stop()

def split_file_list():
    url = 'http://localhost:9200/_plugin/carrot2/file_list.csv'

    i = 0
    j = 0
    of = open('file_list_' + str(j) + '.csv', 'w')

    for line in urllib2.urlopen(url):
        if(i % 10000 == 0):
            j = j + 1
            of.close()
            of = open('file_list_dir/file_list_' + str(j) + '.csv', 'w')

        of.write(line)

        i = i + 1

    of.close()

def process_PMID_file():
    p_file = None
    try:
        p_file = open('/Users/aarongary/Development/DataSets/PubMed/file_list_small.json', 'r')
        count = 0
        for line in p_file:
            count += 1
            if(count % 200 == 0):
                print count
            file,citation,accID,l_updated,pmid = line.split(',')
            if(len(pmid) > 0):
                if(pmid != '\n'):
                    download_tar_gz('ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/', file)
                    print pmid

    except Exception as e:
        print e.message
    finally:
        if(p_file is not None):
            p_file.close()


def getAbstractByID(pmid, of):
    if(len(pmid) > 0):

        try:
            abstract_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + str(pmid) + "&retmode=text&rettype=abstract"
            meta_data_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=" + str(pmid) + "&version=2.0&retmode=json"

            fullAbstract = "";
            pubmed_data = {}

            print 'processing: ' + str(pmid)

            for line in urllib2.urlopen(abstract_url):
                fullAbstract += line.rstrip() + " "

            r_json = requests.get(meta_data_url).json()

            if('result' in r_json):
                pubmed_data['articleMetaData'] = r_json['result'][str(pmid)]
            else :
                pubmed_data['articleMetaData'] = 'NO_DATA'

            pubmed_data['abstract'] = fullAbstract
            pubmed_data['pmid'] = pmid

            json_data = json.dumps(pubmed_data, indent=4, sort_keys=True)

            #of = open('pubmed_json_files/' + str(pmid) + '.json', 'w')

            of.write("curl -XPOST http://localhost:9200/datasets/pubmed -d '\n" + json_data + "\n'\n")
        except Exception as e:
            print e.message
            return "ERROR"

        #of.close()

        return "SUCCESS"
    else :
        return "SUCCESS"

def download_tar_gz(ftpPath, fileName):
    #============================================================================================
    # Pubmed gives the file name in the following format:
    # hex_folder_name/hex_folder_name/filename.tar.gz
    # For example: be/ab/Genome_Biol_2000_Dec_4_1(6)_research0014_1-14_17.tar.gz
    # therefore we need to parse it out
    #============================================================================================
    ftpPathParts = fileName.split("/")

    #print fileName

    fullPath = ftpPath + ftpPathParts[0] + "/" + ftpPathParts[1] + "/" + ftpPathParts[2]
    print "wget -c " + '\"' + fullPath + '\"'

    # THIS WAS TOO SLOW
    #testfile = urllib.URLopener()
    #testfile.retrieve(fullPath, ftpPathParts[2])

    # THIS SHOULD BE FASTER
    #subprocess.call(["wget -c", fileName])

    #print "Done"

def unzip_gz(fileName):
    #print "gunzip", fileName, " > ", destinationName

    #subprocess.call(["gunzip", fileName])
    #time.sleep(3) # delays for 5 seconds

    #print "tar -xf", destinationName
    #subprocess.call(["tar -xf", destinationName])

    #untar(fileName)

    #with gzip.open(fileName, 'rb') as infile:
    #    with open(fileName + "_unzipped", 'w') as outfile:
    #        for line in infile:
    #            outfile.write(line)

    print "done"

def untar(fname):
    if (fname.endswith("tar.gz")):
        tar = tarfile.open(fname)
        tar.extractall()
        tar.close()
        print "Extracted in Current Directory"
    else:
        print "Not a tar.gz file: '%s '" % sys.argv[0]


def main():
    return 0

if __name__ == '__main__':
    sys.exit(main())