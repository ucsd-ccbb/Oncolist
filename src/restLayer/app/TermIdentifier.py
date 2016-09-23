__author__ = 'aarongary'
import sys
import pymongo
import requests
import MyGeneInfo

from itertools import islice
from app.util import set_status, create_edges_index
from app.status import Status
from bson.json_util import dumps
from models.TermResolver import TermAnalyzer
import ElasticSearch
import os
from sklearn.linear_model import LinearRegression
import numpy as np
import app
import ESearch

def bulk_identify_terms(terms):
    tr = TermAnalyzer()
    termsClassified = tr.process_terms_bulk(terms)
    return_value = {
        'termClassification': termsClassified
    }

    return return_value

def search_term_description(term):
    tr = TermAnalyzer()
    termsClassified = tr.process_terms_bulk(term)
    entrez_summary = ESearch.get_gene_summary_from_entrez(term)

    return_value = {
        'termClassification': termsClassified,
        'entrez_summary': entrez_summary
    }

    return return_value

def bulk_identify_terms2(terms):
    term_with_id = []

    #========================
    # Process GENOME terms
    #========================
    analyzed_terms = process_genome_terms(terms)


    for genome_term in analyzed_terms['special_terms']:
        a = {
            'probabilitiesMap': {
                'gene': '0.0',
                'icd10': '0.0',
                'drug': '0.0',
                'disease': '0.0',
                'genome': '1.0'
            },
            'status': 'success',
            'termId': genome_term['familiar_term'],
            'desc': 'Genome',
            'geneSymbol': genome_term['familiar_term'],
            'termTitle': genome_term['familiar_term'] + ' (' + genome_term['latin'] + ')'
        }
        term_with_id.append(a)

    terms = analyzed_terms['terms']

    #========================
    # Process DISEASE terms
    #========================
    analyzed_terms = process_disease_terms(terms)

    for disease_term in analyzed_terms['special_terms']:
        a = {
            'probabilitiesMap': {
                'gene': '0.0',
                'icd10': '0.0',
                'drug': '0.0',
                'disease': '1.0',
                'genome': '0.0'
            },
            'status': 'success',
            'termId': disease_term['familiar_term'],
            'desc': 'Disease',
            'geneSymbol': disease_term['familiar_term'],
            'termTitle': disease_term['familiar_term'] + ' (' + disease_term['latin'] + ')'
        }
        term_with_id.append(a)

    terms = analyzed_terms['terms']

    if(len(terms) > 0):
        queryTermArray = terms.split(',')

        types = ['gene','icd10','drug','disease','genome']

        for queryTerm in queryTermArray:
            termTitle = queryTerm
            print queryTerm
            a = {
                'probabilitiesMap': {},
                'status': 'success',
                'termId': queryTerm.upper(),
                'desc': '',
                'geneSymbol': '',
                'termTitle': queryTerm
            }

            term_result = identify_term(queryTerm)
            #tt = dumps(term_result)
            if(term_result is None or term_result.count() < 1):
                term_alt_result = identify_alt_term(queryTerm) #MyGeneInfo.get_gene_info_by_id(queryTerm)
                cc = dumps(term_alt_result)
                if(term_alt_result['term'] == 'UNKNOWN'):
                    a['probabilitiesMap'] = {
                        'gene': '0.0',
                        'icd10': '0.0',
                        'drug': '0.0',
                        'disease': '0.0',
                        'genome': '0.0'
                    }
                    a['status'] = 'unknown'

                    term_with_id.append(a)
                else:
                    termDesc = ''
                    termGeneSymbol = ''
                    term_result_types_array = []

                    if(term_alt_result['type'] == 'GENE'):
                        termDesc = term_alt_result['desc']
                        termGeneSymbol = term_alt_result['geneSymbol']

                        termTitle = queryTerm.upper() + ' (' + termGeneSymbol.upper() + ')'
                        a['termId'] = termGeneSymbol.upper()

                    if(term_alt_result['type'] not in term_result_types_array):
                        term_result_types_array.append(term_alt_result['type'])

                    total_found_terms = float(len(term_result_types_array))
                    for k in types:
                        if(k.upper() in term_result_types_array):
                            a['probabilitiesMap'][k] = str(1.0/total_found_terms)
                        else:
                            a['probabilitiesMap'][k] = str(0.0)

                    a['desc'] = termDesc
                    a['geneSymbol'] = termGeneSymbol
                    a['termTitle'] = termTitle
                    term_with_id.append(a)




            else:
                termDesc = ''
                termGeneSymbol = ''
                term_result_types_array = []
                #tr = dumps(term_result)
                for item_type in term_result:
                    if(item_type['type'] == 'GENE'):
                        termDesc = item_type['desc']
                        termGeneSymbol = item_type['geneSymbol']

                        if(len(queryTerm) > 12 and queryTerm[:3] == 'ENS'):
                            termTitle = termGeneSymbol.upper() + ' (' + queryTerm.upper() + ')'
                            a['termId'] = termGeneSymbol.upper()

                    if(item_type['type'] not in term_result_types_array):
                        term_result_types_array.append(item_type['type'])

                total_found_terms = float(len(term_result_types_array))
                for k in types:
                    if(k.upper() in term_result_types_array):
                        a['probabilitiesMap'][k] = str(1.0/total_found_terms)
                    else:
                        a['probabilitiesMap'][k] = str(0.0)

                a['desc'] = termDesc
                a['geneSymbol'] = termGeneSymbol
                a['termTitle'] = termTitle
                term_with_id.append(a)
                #print dumps(a)

                #term_with_id.append(term_result)

    return_value = {
        'termClassification': term_with_id
    }
    #print dumps(return_value)
    return dumps(return_value)

def identify_term(name):
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms2

    results = allterms.find({'term': name.upper(),'genomeType': 'human'})

    return None if results is None else results

def identify_alt_term(name):
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms2

    gene_alt_id = MyGeneInfo.get_gene_info_by_id(name)
    results = allterms.find_one({'term': gene_alt_id.upper(),'genomeType': 'human'})

    if(results is None):
        results = {
          'term': 'UNKNOWN',
          'desc': 'UNKNOWN'
        }

    return results

#def identify_term(name):
#    client = pymongo.MongoClient()
#    db = client.identifiers

#    allterms = db.allterms

#    result = allterms.find_one({'term': name.upper()})

#    return None if result is None else result

def add_terms_from_file():
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms2

    #url = 'http://geneli.st:8181/add-terms1.tsv'
    #url = 'http://geneli.st:8181/mirna-terms.txt'
    url = 'http://geneli.st:8181/mirna_label.txt'


    r = requests.get(url)
    lines = list(r.iter_lines())

    count=0
    for idx, line in enumerate(lines):
        term, term_type  = line.split('\t')

        term_to_add = {
            'term': term.upper(),
            'type': term_type
        }

        allterms.save(term_to_add)

        count = count + 1

    print 'Done'
    print str(count)

def load_variant_to_gene_from_file():
    client = pymongo.MongoClient()
    db = client.identifiers

    variants = db.variants
    variants.drop()

    f_path = os.path.abspath('./variant_vs_gene.txt')
    f = open(f_path, 'r')
    count = 0
    for line in f:
        count += 1

        if(count % 5000 == 0):
            print str(count) + ' (' + "{0:.2f}%".format(float(count)/89000000 * 100) + ')'
            #print str(count) + ' (' + str(count/89000000) + ')c'

        #if(count > 10000):
        #    break

        variant, gene = line.split('\t')
        #print variant + ' - ' + gene
        insertThisRecord = {
            'geneSymbol': gene.rstrip().upper(),
            'genomeType': 'human',
            'term': variant.upper(),
            'type': 'GENE'
        }
        variants.save(insertThisRecord)


    variants.create_index([
        ("term", pymongo.ASCENDING)
    ])

def get_mirna_from_cluster_file():
    f = open('/Users/aarongary/Development/DataSets/Terms/BRCA.json', 'r')
    count = 0
    for line in f:
        if('hsa-' in line):
            print count
            count += 1
            hsa_items = line.split('hsa-')
            for hsa_item in hsa_items:
                print hsa_item


def add_biomart_terms_from_file():
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms2
    allterms.drop()

    #filesToParse = [{'genomeType': 'human', 'url': 'http://geneli.st:8181/biomart/human Homo sapiens protein coding genes.txt','termType': 'GENE'},
    #                {'genomeType': 'human', 'url': 'http://geneli.st:8181/biomart/add-terms-non-GENE.tsv','termType': 'NONGENE'}]
    terms_host = 'http://ec2-52-40-169-254.us-west-2.compute.amazonaws.com:3000/Biomart'

    filesToParse = [
                    #{'genomeType': 'dog', 'url': terms_host + '/dog Canis familiaris protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'fruitfly', 'url': terms_host + '/fruitfly Drosophila melanogaster protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'monkey', 'url': terms_host + '/monkey Macaca mulatta protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'mouse', 'url': terms_host + '/mouse Mus musculus protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'rat', 'url': terms_host + '/rat Rattus norvegicus protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'worm', 'url': terms_host + '/worm Caenorhabditis elegans protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'zebrafish', 'url': terms_host + '/zebrafish Danio rerio protein coding genes.txt','termType': 'GENE'},
                    #{'genomeType': 'dog', 'url': terms_host + '/dog Canis familiaris mirna genes.txt','termType': 'GENE'},
                    #{'genomeType': 'fruitfly', 'url': terms_host + '/fruitfly Drosophila melanogaster pre-mirna genes.txt','termType': 'GENE'},
                    #{'genomeType': 'monkey', 'url': terms_host + '/monkey Macaca mulatta mirna genes.txt','termType': 'GENE'},
                    #{'genomeType': 'mouse', 'url': terms_host + '/mouse Mus musculus mirna genes.txt','termType': 'GENE'},
                    #{'genomeType': 'rat', 'url': terms_host + '/rat Rattus norvegicus mirna genes.txt','termType': 'GENE'},
                    #{'genomeType': 'worm', 'url': terms_host + '/worm Caenorhabditis elegans mirna genes.txt','termType': 'GENE'},
                    #{'genomeType': 'zebrafish', 'url': terms_host + '/zebrafish Danio rerio mirna genes.txt','termType': 'GENE'},
                    {'genomeType': 'human', 'url': terms_host + '/add-terms-DISEASE.tsv','termType': 'NONGENE'},
                    {'genomeType': 'human', 'url': terms_host + '/human Homo sapiens protein coding genes.txt','termType': 'GENE'},
                    {'genomeType': 'human', 'url': terms_host + '/human Homo sapiens miRNA genes.txt','termType': 'GENE'}
                    ]

    for f in filesToParse:
        r = requests.get(f['url'], stream=True)
        lines = r.iter_lines()
        lines.next()  # ignore header
        count = 0
        for line in lines:
            count += 1
            if(count % 1000 == 0):
                print count
            try:
                if(f['termType'] == 'GENE'):
                    ensGID,	desc, geneType, geneStatus, geneSymbol = line.split('\t')
                    insertThisRecord = {
                        'ensGID': ensGID,
                        'desc': desc,
                        'geneType': geneType,
                        'geneStatus': geneStatus,
                        'geneSymbol': geneSymbol,
                        'genomeType': f['genomeType'],
                        'term': ensGID.upper(),
                        'type': 'GENE'
                    }
                    allterms.save(insertThisRecord)

                    insertThisInvertedRecord = {
                        'ensGID': ensGID,
                        'desc': desc,
                        'geneType': geneType,
                        'geneStatus': geneStatus,
                        'geneSymbol': geneSymbol,
                        'genomeType': f['genomeType'],
                        'term': geneSymbol.upper(),
                        'type': 'GENE'
                    }
                    allterms.save(insertThisInvertedRecord)

                else:
                    fTerm, fType = line.split('\t')

                    allterms.save({'genomeType': 'human','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'dog','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'fruitfly','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'monkey','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'mouse','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'rat','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'worm','term': fTerm.upper(),'type': fType})
                    #allterms.save({'genomeType': 'zebrafish','term': fTerm.upper(),'type': fType})

            except Exception as e:
                print 'Didnt work' + e.message

        print 'Done with file'

    allterms.ensure_index([("ensGID" , pymongo.ASCENDING)])
    allterms.ensure_index([("term" , pymongo.ASCENDING)])
    allterms.ensure_index([("type" , pymongo.ASCENDING)])
    allterms.ensure_index([("geneType" , pymongo.ASCENDING)])

#    allterms.create_indexes([
#        pymongo.IndexModel([('ensGID', pymongo.ASCENDING)]),
#        pymongo.IndexModel([('term', pymongo.ASCENDING)]),
#        pymongo.IndexModel([('type', pymongo.ASCENDING)]),
#        pymongo.IndexModel([('geneType', pymongo.ASCENDING)])
#    ])


    print 'Done'

    return ""

def add_terms_from_file_autocomplete():
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms

    #url = 'http://geneli.st:8181/add-terms3a.tsv'
    url = 'http://geneli.st:8181/add-terms3.tsv'

    r = requests.get(url)
    lines = list(r.iter_lines())

    count=0
    for idx, line in enumerate(lines):
        term, term_type  = line.split('\t')
        #print term

        term_to_add = {
            'term': term.upper(),
            'type': term_type
        }

        allterms.save(term_to_add)

        count = count + 1

        if(count % 200 == 0):
            print count #dumps(term_to_add)

    #allterms.create_indexes([pymongo.IndexModel([('term', pymongo.ASCENDING)])])

    print 'Done'

def add_terms_from_elasticsearch_autocomplete():
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms3

    count=0
    phenotypes = ElasticSearch.get_clinvar_phenotypes()
    for term in phenotypes:
        term_to_add = {
            'term': term.upper(),
            'type': 'ICD10'
        }

        allterms.save(term_to_add)

        count = count + 1

        if(count % 200 == 0):
            print count #dumps(term_to_add)

    #allterms.create_indexes([pymongo.IndexModel([('term', pymongo.ASCENDING)])])

    print 'Done'

def load_terms_from_file():
    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms

    allterms.drop()

    url = 'http://ec2-52-26-19-122.us-west-2.compute.amazonaws.com:8080/all-terms3.tsv'

    r = requests.get(url)
    lines = list(r.iter_lines())

    count=0
    for idx, line in enumerate(lines):
        term, term_type  = line.split('\t')
        #print term

        term_to_add = {
            'term': term.upper(),
            'type': term_type
        }

        allterms.save(term_to_add)

        count = count + 1

        if(count % 200 == 0):
            print count #dumps(term_to_add)

    allterms.create_indexes([pymongo.IndexModel([('term', pymongo.ASCENDING)])])

    print 'Done'

def process_genome_terms(terms):
    terms_uppercase = terms.upper()
    return_value = []

    genome_id_kv = [
        {'k': 'CANIS,FAMILIARIS', 'v': 'DOG'},
        {'k': 'DROSOPHILA,MELANOGASTER', 'v': 'FRUITFLY'},
        {'k': 'HOMO,SAPIEN', 'v': 'HUMAN'},
        {'k': 'MACACA,MULATTA', 'v': 'MONKEY'},
        {'k': 'MUS,MUSCULUS', 'v': 'MOUSE'},
        {'k': 'RATTUS,NORVEGICUS', 'v': 'RAT'},
        {'k': 'CAENORHABDITIS,ELEGANS', 'v': 'WORM'},
        {'k': 'DANIO,RERIO', 'v': 'ZEBRAFISH'}
    ]

    for kv in genome_id_kv:
        if(kv['k'] in terms_uppercase):
            terms_uppercase = terms_uppercase.replace(kv['k'], '').replace(',,',',')
            return_value.append({'latin': kv['k'].replace(',',' '), 'familiar_term': kv['v']})

    if(terms_uppercase[0:1] == ','):
        terms_uppercase = terms_uppercase[1:-1]

    if(terms_uppercase == ','):
        terms_uppercase = ''

    print terms_uppercase

    return {'terms': terms_uppercase, 'special_terms': return_value}

def process_disease_terms(terms):
    terms_uppercase = terms.upper()
    return_value = []

    genome_id_kv = [
        {'k': 'BLADDER,CANCER', 'v': 'BLCA'},
        {'k': 'BRAIN,CANCER', 'v': 'LGG'},
        {'k': 'BREAST,CANCER', 'v': 'BRCA'},
        {'k': 'CERVICAL,CANCER', 'v': 'CESC'},
        {'k': 'ENDOCERVICAL,CANCER', 'v': 'CESC'},
        {'k': 'CERVICAL,CANCER', 'v': 'CESC'},
        {'k': 'CHOLANGIOCARCINOMA', 'v': 'CHOL'},
        {'k': 'BILE,DUCT,CANCER', 'v': 'CHOL'},
        {'k': 'COLON,CANCER', 'v': 'COAD'},
        {'k': 'ESOPHAGEAL,CANCER', 'v': 'ESCA'},
        {'k': 'GLIOBLASTOMA,CANCER', 'v': 'GBM'}, #Wikify
        {'k': 'HEAD,AND,NECK,CANCER', 'v': 'HNSC'},
        {'k': 'NECK,CANCER', 'v': 'HNSC'},
        {'k': 'HEAD,CANCER', 'v': 'HNSC'},
        {'k': 'KIDNEY,CHROMOPHOBE', 'v': 'KICH'},
        {'k': 'KIDNEY,RENAL,CLEAR,CELL,CARCINOMA', 'v': 'KIRC'}, #Wikify
        {'k': 'KIDNEY,RENAL,PAPILLARY,CELL,CARCINOMA', 'v': 'KIRP'},
        {'k': 'LIVER,CANCER', 'v': 'LIHC'},
        {'k': 'LUNG,CANCER', 'v': 'LUAD'},
        {'k': 'LUNG,SQUAMOUS,CELL,CARCINOMA', 'v': 'LUSC'}, #Wikify
        {'k': 'LYMPHOID,CANCER', 'v': 'DLBC'},
        {'k': 'LYMPHOMA,CANCER', 'v': 'DLBC'},
        {'k': 'MESOTHELIOMA,CANCER', 'v': 'MESO'},
        {'k': 'OVARIAN,CANCER', 'v': 'OV'},
        {'k': 'PANCREATIC,CANCER', 'v': 'PAAD'},
        {'k': 'PHEOCHROMOCYTOMA,CANCER', 'v': 'PCPG'},
        {'k': 'PARAGANGLIOMA,CANCER', 'v': 'PCPG'},
        {'k': 'PROSTATE,CANCER', 'v': 'PRAD'},
        {'k': 'RECTUM,CANCER', 'v': 'READ'},
        {'k': 'SARCOMA,CANCER', 'v': 'SARC'},
        {'k': 'SKIN,CANCER', 'v': 'SKCM'},
        {'k': 'STOMACH,CANCER', 'v': 'STAD'},
        {'k': 'TESTICULAR,CANCER', 'v': 'TGCT'},
        {'k': 'THYMOMA,CANCER', 'v': 'THYM'}, #Wikify
        {'k': 'THYROID,CANCER', 'v': 'THCA'},
        {'k': 'UTERINE,CANCER', 'v': 'UCS'},
        {'k': 'UTERINE,CORPUS,ENDOMETRIAL,CANCER', 'v': 'UCEC'}, #Wikify
        {'k': 'UVEAL,MELANOMA,CANCER', 'v': 'UVM'},
        {'k': 'UVEAL,CANCER', 'v': 'UVM'},
        {'k': 'LEUKEMIA', 'v': 'LAML'},
        {'k': 'MYELOID,LEUKEMIA', 'v': 'LAML'},
        {'k': 'ADRENOCORTICAL,CARCINOMA', 'v': 'ACC'},
        {'k': 'BLADDER,UROTHELIAL,CARCINOMA', 'v': 'BLCA'},
        {'k': 'BRAIN,LOWER,GRADE,GLIOMA', 'v': 'LGG'},
        {'k': 'BREAST,INVASIVE,CARCINOMA', 'v': 'BRCA'},
        {'k': 'CERVICAL,SQUAMOUS,CELL,CARCINOMA', 'v': 'CESC'},
        {'k': 'ENDOCERVICAL,ADENOCARCINOMA', 'v': 'CESC'},
        {'k': 'CHOLANGIOCARCINOMA', 'v': 'CHOL'},
        {'k': 'COLON,ADENOCARCINOMA', 'v': 'COAD'},
        {'k': 'ESOPHAGEAL,CARCINOMA', 'v': 'ESCA'},
        {'k': 'GLIOBLASTOMA,MULTIFORME', 'v': 'GBM'},
        {'k': 'HEAD,AND,NECK,SQUAMOUS,CELL,CARCINOMA', 'v': 'HNSC'},
        {'k': 'KIDNEY,CHROMOPHOBE', 'v': 'KICH'},
        {'k': 'KIDNEY,RENAL,CLEAR,CELL,CARCINOMA', 'v': 'KIRC'},
        {'k': 'KIDNEY,RENAL,PAPILLARY,CELL,CARCINOMA', 'v': 'KIRP'},
        {'k': 'LIVER,HEPATOCELLULAR,CARCINOMA', 'v': 'LIHC'},
        {'k': 'LUNG,ADENOCARCINOMA', 'v': 'LUAD'},
        {'k': 'LUNG,SQUAMOUS,CELL,CARCINOMA', 'v': 'LUSC'},
        {'k': 'LYMPHOID,NEOPLASM,DIFFUSE,LARGE,B-CELL,LYMPHOMA', 'v': 'DLBC'},
        {'k': 'MESOTHELIOMA', 'v': 'MESO'},
        {'k': 'OVARIAN,SEROUS,CYSTADENOCARCINOMA', 'v': 'OV'},
        {'k': 'PANCREATIC,ADENOCARCINOMA', 'v': 'PAAD'},
        {'k': 'PHEOCHROMOCYTOMA', 'v': 'PCPG'},
        {'k': 'PARAGANGLIOMA', 'v': 'PCPG'},
        {'k': 'PROSTATE,ADENOCARCINOMA', 'v': 'PRAD'},
        {'k': 'RECTUM,ADENOCARCINOMA', 'v': 'READ'},
        {'k': 'SARCOMA', 'v': 'SARC'},
        {'k': 'SKIN,CUTANEOUS,MELANOMA', 'v': 'SKCM'},
        {'k': 'STOMACH,ADENOCARCINOMA', 'v': 'STAD'},
        {'k': 'TESTICULAR,GERM,CELL,TUMORS', 'v': 'TGCT'},
        {'k': 'THYMOMA', 'v': 'THYM'},
        {'k': 'THYROID,CARCINOMA', 'v': 'THCA'},
        {'k': 'UTERINE,CARCINOSARCOMA', 'v': 'UCS'},
        {'k': 'UTERINE,CORPUS,ENDOMETRIAL,CARCINOMA', 'v': 'UCEC'},
        {'k': 'UVEAL,MELANOMA', 'v': 'UVM'}
    ]

    for kv in genome_id_kv:
        if(kv['k'] in terms_uppercase):
            terms_uppercase = terms_uppercase.replace(kv['k'], '').replace(',,',',')
            return_value.append({'latin': kv['k'].replace(',',' '), 'familiar_term': kv['v']})

    if(terms_uppercase[0:1] == ','):
        terms_uppercase = terms_uppercase[1:-1]

    if(terms_uppercase == ','):
        terms_uppercase = ''

    print terms_uppercase

    return {'terms': terms_uppercase, 'special_terms': return_value}

def auto_complete_search(term):
    tr = TermAnalyzer()
    termsClassified = tr.identify_term_partial(term)
    return_value = {
        'termClassification': termsClassified
    }

    return return_value

def test_linear_classifier():
    est = LinearRegression(fit_intercept=False)
    # random training data
    X = np.random.rand(10, 2)
    y = np.random.randint(2, size=10)
    est.fit(X, y)
    est.coef_   # access coefficients

def load_disease_groups():
    disease_groups_array = [{
       'genomeType': 'human',
       'term': 'Adrenocortical Cancer  ',
       'group': 'Adrenal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Adrenocortical Carcinoma  ',
       'group': 'Adrenal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Pheochromocytoma and Paraganglioma ',
       'group': 'Adrenal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Cholangiocarcinoma  ',
       'group': 'Bile',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Cholangiocarcinoma  ',
       'group': 'Bile',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Bladder Cancer',
       'group': 'Bladder',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Bladder Urothelial Carcinoma ',
       'group': 'Bladder',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Brain Lower Grade Glioma  ',
       'group': 'Brain',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Glioblastoma  ',
       'group': 'Brain',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Glioblastoma Multiforme',
       'group': 'Brain',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Glioblastoma Multiforme and Brain Lower Grade Glioma ',
       'group': 'Brain',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Glioma High Grade',
       'group': 'Brain',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Breast Invasive Carcinoma ',
       'group': 'Breast',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Breast Tumors RNA',
       'group': 'Breast',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Cervical Cancer ChemoradioResistant',
       'group': 'Cervical',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Cervical Squamous Cell Carcinoma and Endocervical Adenocarcinoma ',
       'group': 'Cervical',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Colon Adenocarcinoma',
       'group': 'Colon',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Colon Adenocarcinoma and Rectum adenocarcinoma ',
       'group': 'colon',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Colon Cancer  ',
       'group': 'colon',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Ulcerative Colitis Colon Inflammation ',
       'group': 'colon',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Endometrial Cancer Stage I',
       'group': 'Endometrial',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Esophageal Cancer',
       'group': 'Esophagus',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Esophageal Carcinoma',
       'group': 'Esophagus',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Head and Neck ',
       'group': 'HeadAndNeck',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Head and Neck Squamous Cell Carcinoma ',
       'group': 'HeadAndNeck',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Kidney Chromophobe  ',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Kidney Chromophobe and Kidney Renal Clear Cell Carcinoma and Kidney Renal Papillary Cell Carcinoma',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Kidney Renal Clear Cell Carcinoma  ',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Kidney Renal Clear Cell Carcinoma  ',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Kidney Renal Papillary Cell Carcinoma ',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Renal Cell Carcinoma',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Acute Myeloid Leukemia ',
       'group': 'Leukemia',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Acute Myeloid Leukemia ',
       'group': 'Leukemia',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Hepatocellular Carcinoma  ',
       'group': 'Liver',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Liver Hepatocellular Carcinoma  ',
       'group': 'Liver',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Liver Hepatocellular Carcinoma Early Stage Cirrhosis ',
       'group': 'Liver',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Blood Lung Cancer',
       'group': 'Lung',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Blood Lung Cancer Stage I ',
       'group': 'Lung',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Lung Adenocarcinoma ',
       'group': 'Lung',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Lung Squamous Cell Carcinoma ',
       'group': 'Lung',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Diffuse Large B-Cell Lymphoma',
       'group': 'Lymphoma',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Lymphoid Neoplasm Diffuse Large B-cell Lymphoma',
       'group': 'Lymphoma',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Mesothelioma  ',
       'group': 'Ovarian',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Ovarian Cancer',
       'group': 'Ovarian',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Ovarian Serous Cystadenocarcinoma  ',
       'group': 'Ovarian',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Pancreatic ',
       'group': 'Pancreatic',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Pancreatic Adenocarcinoma ',
       'group': 'Pancreatic',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Pancreatic Ductal Adenocarcinoma',
       'group': 'Pancreatic',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Prostate Adenocarcinoma',
       'group': 'Prostate',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Prostate Carcinoma  ',
       'group': 'Prostate',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Rectal Cancer ',
       'group': 'Rectal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Rectum Adenocarcinoma  ',
       'group': 'Rectal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Sarcoma ',
       'group': 'Sarcoma',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Sarcoma ',
       'group': 'Sarcoma',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Melanoma Malignant  ',
       'group': 'Skin',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Skin Cutaneous Melanoma',
       'group': 'Skin',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Stomach Adenocarcinoma ',
       'group': 'Stomach',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Stomach and Esophageal Carcinoma',
       'group': 'Stomach',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Stomach Cancer 126  ',
       'group': 'Stomach',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Testicular Germ Cell Tumors  ',
       'group': 'Testicular',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Thymoma ',
       'group': 'Thymus',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Thyroid Cancer',
       'group': 'Thyroid',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Thyroid Carcinoma',
       'group': 'Thyroid',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Uterine Carcinosarcoma ',
       'group': 'Uterine',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Uterine Corpus Endometrial Carcinoma  ',
       'group': 'Uterine',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Uveal Melanoma',
       'group': 'Uveal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Uveal Melanoma',
       'group': 'Uveal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Adrenal ',
       'group': 'Adrenal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Bile ',
       'group': 'Bile',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Bladder ',
       'group': 'Bladder',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Brain',
       'group': 'Brain',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Breast  ',
       'group': 'Breast',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Cervical',
       'group': 'Cervical',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'colon',
       'group': 'colon',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Endometrial',
       'group': 'Endometrial',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Esophagus  ',
       'group': 'Esophagus',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'HeadAndNeck',
       'group': 'HeadAndNeck',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Kidney  ',
       'group': 'Kidney',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Leukemia',
       'group': 'Leukemia',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Liver',
       'group': 'Liver',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Lung ',
       'group': 'Lung',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Lymphoma',
       'group': 'Lymphoma',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Ovarian ',
       'group': 'Ovarian',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Pancreatic ',
       'group': 'Pancreatic',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Prostate',
       'group': 'Prostate',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Rectal  ',
       'group': 'Rectal',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Sarcoma ',
       'group': 'Sarcoma',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Skin ',
       'group': 'Skin',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Stomach ',
       'group': 'Stomach',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Testicular ',
       'group': 'Testicular',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Thymus  ',
       'group': 'Thymus',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Thyroid ',
       'group': 'Thyroid',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Uterine ',
       'group': 'Uterine',
       'type': 'DISEASE'
       },
    {
       'genomeType': 'human',
       'term': 'Uveal',
       'group': 'Uveal',
       'type': 'DISEASE'
       }]

    client = pymongo.MongoClient()
    db = client.identifiers

    allterms = db.allterms2
    #allterms.drop()

    for disease in disease_groups_array:
        allterms.save({'genomeType': disease['genomeType'],'term':  disease['term'].upper(),'type':  disease['type'], 'group':  disease['group']})























