__author__ = 'aarongary'
import pymongo
import app.MyGeneInfo
from elasticsearch import Elasticsearch
from app import elastic_search_uri

class TermAnalyzer():

    def get_resolved_terms(self):
        return self.terms

    def process_terms_bulk(self, terms):
        terms_with_id = []

        #========================
        # Process GENOME terms
        #========================
        analyzed_terms = self.process_genome_terms(terms)

        #print analyzed_terms

        #========================
        # Process DISEASE terms
        #========================
        analyzed_terms = self.process_disease_terms(terms)

        #print analyzed_terms
        #print self.terms

        #========================
        # Process VARIANT terms
        #========================
        analyzed_terms = self.process_variant_terms(analyzed_terms)

        #========================
        # Process OTHER terms
        #========================
        analyzed_terms = self.process_other_terms(analyzed_terms)

        #print analyzed_terms
        #print self.terms

        #========================
        # Process UNKNOWN terms
        #========================
        analyzed_terms = self.process_unknown_terms(analyzed_terms)

        #print analyzed_terms
        #print self.terms

        for term in self.terms:
            a = {
            'probabilitiesMap': term.probabilitiesMap,
            'status': term.status,
            'termId': term.termId,
            'desc': term.desc,
            'geneSymbol': term.geneSymbol,
            'termTitle': term.termTitle
            }
            terms_with_id.append(a)

        print len(terms_with_id)
        return terms_with_id


    #========================
    # IDENTIFY UNKNOWN TERMS
    #========================
    def process_unknown_terms(self, terms):
        if(len(terms) > 0):

            queryTerms = terms.upper()
            queryTermArray = queryTerms.split(',')

            types = ['gene','icd10','drug','disease','genome']

            for queryTerm in queryTermArray:
                term_alt_result = self.identify_alt_term(queryTerm)

                a = TermModel()
                if(term_alt_result['term'] == 'UNKNOWN'):
                    a.termId
                    a.status = 'unknown'
                    a.termId = queryTerm

                    self.terms.append(a)
                else:
                    termDesc = ''
                    termGeneSymbol = ''
                    term_result_types_array = []

                    if(term_alt_result['type'] == 'GENE'):
                        termDesc = term_alt_result['desc']
                        termGeneSymbol = term_alt_result['geneSymbol']

                        termTitle = queryTerm.upper() + ' (' + termGeneSymbol.upper() + ')'
                        a.termId = termGeneSymbol.upper()

                    if(term_alt_result['type'] not in term_result_types_array):
                        term_result_types_array.append(term_alt_result['type'])

                    total_found_terms = float(len(term_result_types_array))
                    for k in types:
                        if(k.upper() in term_result_types_array):
                            a.probabilitiesMap[k] = str(1.0/total_found_terms)
                        else:
                            a.probabilitiesMap[k] = str(0.0)

                    a.desc = termDesc
                    a.geneSymbol = termGeneSymbol
                    a.termTitle = termTitle
                    self.terms.append(a)


    #========================
    # IDENTIFY OTHER TERMS
    #========================
    def process_other_terms(self, terms):
        queryTerms = terms.upper()
        queryTermArray = queryTerms.split(',')

        if(len(terms) > 0):

            types = ['gene','icd10','drug','disease','genome']

            for queryTerm in queryTermArray:
                termTitle = queryTerm

                a = TermModel()

                a.status = 'success'
                a.termId = queryTerm
                a.termTitle = queryTerm

                term_result = self.identify_term(queryTerm)

                if(term_result is None or term_result.count() < 1):
                    warning_msg = 'Not found: ' + queryTerm
                else:
                    termDesc = ''
                    termGeneSymbol = ''
                    term_result_types_array = []

                    for item_type in term_result:
                        if(item_type['type'] == 'GENE'):
                            if('desc' in item_type):
                                termDesc = item_type['desc']
                            if('geneSymbol' in item_type):
                                termGeneSymbol = item_type['geneSymbol']

                            if(len(queryTerm) > 12 and queryTerm[:3] == 'ENS'):
                                termTitle = termGeneSymbol.upper() + ' (' + queryTerm.upper() + ')'
                                a.termId = termGeneSymbol.upper()

                        if(item_type['type'] not in term_result_types_array):
                            term_result_types_array.append(item_type['type'])



                    total_found_terms = float(len(term_result_types_array))
                    for k in types:
                        if(k.upper() in term_result_types_array):
                            a.probabilitiesMap[k] = str(1.0/total_found_terms)
                        else:
                            a.probabilitiesMap[k] = str(0.0)

                    a.desc = termDesc
                    a.geneSymbol = termGeneSymbol
                    a.termTitle = termTitle

                    self.terms.append(a)

                    if(',' not in queryTerms):
                        if(queryTerm == queryTerms):
                            queryTerms = ''
                    else:
                        queryTerms = queryTerms.replace(queryTerm + ',', '').replace(',,',',')


            if(len(queryTerms) > 0 and queryTerms[0:1] == ','):
                queryTerms = queryTerms[1:]

            if(len(queryTerms) > 0 and queryTerms[-1] == ','):
                queryTerms = queryTerms[:-1]

        return queryTerms


    #========================
    # IDENTIFY GENOME TERMS
    #========================
    def process_genome_terms(self, terms):
        terms_uppercase = terms.upper()

        for kv in self.genome_id_kv:
            if(kv['k'] in terms_uppercase):
                terms_uppercase = terms_uppercase.replace(kv['k'], '').replace(',,',',')
                a = TermModel()
                a.probabilitiesMap['genome'] = '1.0'
                a.status = 'success'
                a.termId = kv['v']
                a.desc = 'Genome'
                a.geneSymbol = kv['v']
                a.termTitle = kv['v'] + ' (' + kv['k'].replace(',',' ') + ')'
                self.terms.append(a)

        if(len(terms_uppercase) > 0 and terms_uppercase[0:1] == ','):
            terms_uppercase = terms_uppercase[1:]

        if(len(terms_uppercase) > 0 and terms_uppercase[-1] == ','):
            terms_uppercase = terms_uppercase[:-1]

        return terms_uppercase

    #=========================
    # IDENTIFY DISEASE TERMS
    #=========================
    def process_disease_terms(self, terms):
        terms_uppercase = terms.upper()


        for kv in self.cancer_id_kv:
            if(kv['k'] in terms_uppercase):
                terms_uppercase = terms_uppercase.replace(kv['k'], '').replace(',,',',')
                a = TermModel()
                a.probabilitiesMap['disease'] = '1.0'
                a.status = 'success'
                a.termId = kv['v']
                a.desc = 'Disease'
                a.geneSymbol = kv['v']
                a.termTitle = kv['v'] + ' (' + kv['k'].replace(',',' ') + ')'
                self.terms.append(a)


        if(len(terms_uppercase) > 0 and terms_uppercase[0:1] == ','):
            terms_uppercase = terms_uppercase[1:]

        if(len(terms_uppercase) > 0 and terms_uppercase[-1] == ','):
            terms_uppercase = terms_uppercase[:-1]

        return terms_uppercase

    #=========================
    # IDENTIFY VARIANT TERMS
    #=========================
    def process_variant_terms(self, terms):
        return_list = ''
        terms_uppercase = terms.upper()

        terms_array = terms_uppercase.split(',')

        for term_to_check in terms_array:
            variant_identified = self.identify_variant_term(term_to_check)
            if(variant_identified['term'] == 'UNKNOWN'):
                return_list += term_to_check + ','
            else:
                a = TermModel()
                a.probabilitiesMap['gene'] = '1.0'
                a.status = 'success'
                a.termId = variant_identified['geneSymbol']
                a.desc = 'Variant'
                a.geneSymbol = variant_identified['geneSymbol']
                a.termTitle = variant_identified['geneSymbol'] + ' (' + term_to_check + ')'
                self.terms.append(a)

                b = TermModel()
                b.probabilitiesMap['gene'] = '1.0'
                b.status = 'success'
                b.termId = term_to_check
                b.desc = 'Variant'
                b.geneSymbol = term_to_check
                b.termTitle = term_to_check + ' (' + variant_identified['geneSymbol']  + ')'
                self.terms.append(b)


        if(len(return_list) > 0 and return_list[0:1] == ','):
            return_list = return_list[1:]

        if(len(return_list) > 0 and return_list[-1] == ','):
            return_list = return_list[:-1]

        return return_list

    def identify_term(self, name):
        client = pymongo.MongoClient()
        db = client.identifiers

        allterms = db.allterms2

        results = allterms.find({'term': name.upper()})#,'genomeType': 'human'})

        return None if results is None else results

    def identify_term_partial(self, name):
        client = pymongo.MongoClient()
        db = client.identifiers
        if(len(name) >= 5):
            if(name.upper()[:5] == 'CHR1:'):
                allterms = db.variants
            else:
                allterms = db.allterms2
                #allterms = db.allterms
        else:
            allterms = db.allterms2
            #allterms = db.allterms

        results = allterms.find({'term': {'$regex': '^' + name.upper()} })

        return None if results is None else results[:25] # limit the auto complete results to 25

    def identify_variant_term(self, variant_term):
        client = pymongo.MongoClient()
        db = client.identifiers

        variants_db = db.variants

        results = variants_db.find_one({'term': variant_term.upper()})
        if(results is not None and len(results) > 0):
            return results

        if(results is None or len(results) < 1):
            results = {
              'term': 'UNKNOWN',
              'desc': 'UNKNOWN'
            }

        return results

    def identify_alt_term(self, name):
        client = pymongo.MongoClient()
        db = client.identifiers

        allterms = db.allterms2

        gene_alt_id_array = app.MyGeneInfo.get_gene_info_by_id(name)
        for gene_alt_id in gene_alt_id_array:
            results = allterms.find_one({'term': gene_alt_id.upper(),'genomeType': 'human'})
            if(results is not None and len(results) > 0):
                return results

        if(results is None or len(results) < 1):
            results = {
              'term': 'UNKNOWN',
              'desc': 'UNKNOWN'
            }

        return results

    def get_cancer_description_by_id(self, cancer_id):
        for kv in self.cancer_id_kv_lookup:
            if(kv['v'] == cancer_id):
                return kv['k']

        return 'Unknown type'

    def get_disease_types_from_ES(self):
        client = pymongo.MongoClient()
        db = client.identifiers
        disease_collection = db.disease_lookup

        disease_types = []

        search_body = {
            'size': 0,
            'aggs' : {
                'diseases_agg' : {
                    'terms' : { 'field' : 'network_name', 'size': 100 }
                }
            }
        }

        result = self.es.search(
            index = 'clusters',
            body = search_body
        )
        count = 0
        disease_keys = []
        if(result['aggregations']['diseases_agg']['buckets'] < 1):
            print 'no results'
        else:
            for hit in result['aggregations']['diseases_agg']['buckets']:
                disease_keys.append(hit['key'])
                print hit['key']


        for disease_key in disease_keys:
            search_body = {
                'size': 1,
                'query' : {
                    'bool': {
                        'must': [{ 'match': {'network_name': disease_key} }]
                    }
                }
            }

            result = es.search(
                index = 'clusters',
                body = search_body
            )

            if(len(result) > 0):
                result = result['hits']['hits'][0]['_source']
                #disease_collection.save(
                #    {
                #        'id': disease_key,
                #        'desc': result['network_full_name'],
                #        'synonym': disease_key
                #    }
                #)

                print result['network_full_name'] + '\t' + disease_key

        return 'success'

    def __init__(self):
        self.es = Elasticsearch([elastic_search_uri],send_get_body_as='POST',timeout=300) # Prod Clustered Server

        self.terms = []

        self.genome_id_kv = [
            {'k': 'CANIS,FAMILIARIS', 'v': 'DOG'},
            {'k': 'DROSOPHILA,MELANOGASTER', 'v': 'FRUITFLY'},
            {'k': 'HOMO,SAPIENS', 'v': 'HUMANS'},
            {'k': 'MACACA,MULATTA', 'v': 'MONKEY'},
            {'k': 'MUS,MUSCULUS', 'v': 'MOUSE'},
            {'k': 'RATTUS,NORVEGICUS', 'v': 'RAT'},
            {'k': 'CAENORHABDITIS,ELEGANS', 'v': 'WORM'},
            {'k': 'DANIO,RERIO', 'v': 'ZEBRAFISH'}
        ]

        self.cancer_id_kv_lookup = [

            {'k': 'Acute Myeloid Leukemia', 'v': 'LAML'},
            {'k': 'Adrenocortical carcinoma', 'v': 'ACC'},
            {'k': 'Bladder Urothelial Carcinoma', 'v': 'BLCA'},
            {'k': 'Brain Lower Grade Glioma', 'v': 'LGG'},
            {'k': 'Breast invasive carcinoma', 'v': 'BRCA'},
            {'k': 'Cervical squamous cell carcinoma and endocervical adenocarcinoma', 'v': 'CESC'},
            {'k': 'Cholangiocarcinoma', 'v': 'CHOL'},
            {'k': 'Colon adenocarcinoma', 'v': 'COAD'},
            {'k': 'Esophageal carcinoma', 'v': 'ESCA'},
            {'k': 'FFPE Pilot Phase II', 'v': 'FPPP'},
            {'k': 'Glioblastoma multiforme', 'v': 'GBM'},
            {'k': 'Head and Neck squamous cell carcinoma', 'v': 'HNSC'},
            {'k': 'Kidney Chromophobe', 'v': 'KICH'},
            {'k': 'Kidney renal clear cell carcinoma', 'v': 'KIRC'},
            {'k': 'Kidney renal papillary cell carcinoma', 'v': 'KIRP'},
            {'k': 'Liver hepatocellular carcinoma', 'v': 'LIHC'},
            {'k': 'Lung adenocarcinoma', 'v': 'LUAD'},
            {'k': 'Lung squamous cell carcinoma', 'v': 'LUSC'},
            {'k': 'Lymphoid Neoplasm Diffuse Large B-cell Lymphoma', 'v': 'DLBC'},
            {'k': 'Mesothelioma', 'v': 'MESO'},
            {'k': 'Ovarian serous cystadenocarcinoma', 'v': 'OV'},
            {'k': 'Pancreatic adenocarcinoma', 'v': 'PAAD'},
            {'k': 'Pheochromocytoma and Paraganglioma', 'v': 'PCPG'},
            {'k': 'Prostate adenocarcinoma', 'v': 'PRAD'},
            {'k': 'Rectum adenocarcinoma', 'v': 'READ'},
            {'k': 'Sarcoma', 'v': 'SARC'},
            {'k': 'Skin Cutaneous Melanoma', 'v': 'SKCM'},
            {'k': 'Stomach adenocarcinoma', 'v': 'STAD'},
            {'k': 'Testicular Germ Cell Tumors', 'v': 'TGCT'},
            {'k': 'Thymoma', 'v': 'THYM'},
            {'k': 'Thyroid carcinoma', 'v': 'THCA'},
            {'k': 'Uterine Carcinosarcoma', 'v': 'UCS'},
            {'k': 'Uterine Corpus Endometrial Carcinoma', 'v': 'UCEC'},
            {'k': 'KIPAN', 'v': 'KIPAN'},
            {'k': 'COADREAD', 'v': 'COADREAD'},
            {'k': 'Glioma and Glioblastoma', 'v': 'GBMLGG'},
            {'k': 'Uveal Melanoma', 'v': 'UVM'}
        ]


        self.cancer_id_kv = [
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
            {'k': 'GLIOBLASTOMA,CANCER', 'v': 'GBM'},
            {'k': 'HEAD,AND,NECK,CANCER', 'v': 'HNSC'},
            {'k': 'NECK,CANCER', 'v': 'HNSC'},
            {'k': 'HEAD,CANCER', 'v': 'HNSC'},
            {'k': 'KIDNEY,CHROMOPHOBE', 'v': 'KICH'},
            {'k': 'KIDNEY,RENAL,CLEAR,CELL,CARCINOMA', 'v': 'KIRC'},
            {'k': 'KIDNEY,RENAL,PAPILLARY,CELL,CARCINOMA', 'v': 'KIRP'},
            {'k': 'LIVER,CANCER', 'v': 'LIHC'},
            {'k': 'LUNG,CANCER', 'v': 'LUAD'},
            {'k': 'LUNG,SQUAMOUS,CELL,CARCINOMA', 'v': 'LUSC'},
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
            {'k': 'THYMOMA,CANCER', 'v': 'THYM'},
            {'k': 'THYROID,CANCER', 'v': 'THCA'},
            {'k': 'UTERINE,CANCER', 'v': 'UCS'},
            {'k': 'GLIOMA,GLIOBLASTOMA', 'v': 'GBMLGG'},
            {'k': 'UTERINE,CORPUS,ENDOMETRIAL,CANCER', 'v': 'UCEC'},
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





class TermModel():
    def __init__(self):
        self.probabilitiesMap = {
            'gene': '0.0',
            'icd10': '0.0',
            'drug': '0.0',
            'disease': '0.0',
            'genome': '0.0'
        }
        self.status = 'pending'
        self.termId = 'none'
        self.desc = 'none'
        self.geneSymbol = 'none'
        self.termTitle = 'none'
