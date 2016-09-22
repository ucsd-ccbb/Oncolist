#!/usr/bin/python

__author__ = 'guorongxu'

import re
import logging
from Bio import Entrez
from Bio import Medline
import sys
import json
import pymongo
from models.TermResolver import TermAnalyzer

def query(geneName):

    Entrez.email = "A.N.Other@example.com"
    queryTerm = geneName + "[All Fields] AND (\"human\"[All Fields) AND (\"gene\"[All Fields) "
    handle = Entrez.esearch(db="pubmed", term=queryTerm, retmax=100000)
    #handle = Entrez.esearch(db="pubmed", term="Chang AN Institute for Genomic Medicine")
    record = Entrez.read(handle)

    idlist = record["IdList"]
    logging.info(geneName + ":\t" + record["Count"])

    handle = Entrez.efetch(db="pubmed", id=idlist, rettype="medline", retmode="text")
    records = Medline.parse(handle)
    records = list(records)

    authorList = {}
    geneList = {}

    for record in records:

        authors = record.get("FAU", "")
        abstract = record.get("AB", "")

        if re.search(geneName, abstract, re.IGNORECASE):
            for author in authors:
                authorPosition = ""
                #First author
                if authors.index(author) == 0:
                    authorPosition = "F"

                #Last author (Cooresponding author)
                if authors.index(author) == (len(authors) - 1):
                    authorPosition = "L"

                #Middle author
                if authors.index(author) > 0 and authors.index(author) < (len(authors) - 1):
                    authorPosition = "M"

                if authorList:
                    if author in authorList:
                        publications = authorList.get(author)
                        publications.append([record.get("PMID", ""), record.get("TI", ""), record.get("AB", ""),
                                             record.get("JT", ""), record.get("TA", ""), record.get("DA", ""), authorPosition])
                        authorList.update({author: publications})
                    else:
                        publications = []
                        publications.append([record.get("PMID", ""), record.get("TI", ""), record.get("AB", ""),
                                             record.get("JT", ""), record.get("TA", ""), record.get("DA", ""), authorPosition])
                        authorList.update({author: publications})

                else:
                    publications = []
                    publications.append([record.get("PMID", ""), record.get("TI", ""), record.get("AB", ""),
                                         record.get("JT", ""), record.get("TA", ""), record.get("DA", ""), authorPosition])
                    authorList.update({author: publications})

    geneList.update({geneName: authorList})

    handle.close()

    return geneList

def retrieve_annotation(id_list):

    """Annotates Entrez Gene IDs using Bio.Entrez, in particular epost (to
    submit the data to NCBI) and esummary to retrieve the information.
    Returns a list of dictionaries with the annotations."""

    Entrez.email = "A.N.Other@example.com"
    request = Entrez.epost("gene",id="ENSG00000206435")
    try:
        result = Entrez.read(request)
    except RuntimeError as e:
        #FIXME: How generate NAs instead of causing an error with invalid IDs?
        print "An error occurred while retrieving the annotations."
        print "The error returned was %s" % e
        sys.exit(-1)

    webEnv = result["WebEnv"]
    queryKey = result["QueryKey"]
    data = Entrez.esummary(db="gene", webenv=webEnv, query_key =
            queryKey)
    annotations = Entrez.read(data)

    print "Retrieved %d annotations for %d genes" % (len(annotations),
            len(id_list))

    return annotations


def get_gene_summary_from_entrez(gene_name):
    return_value = ""
    Entrez.email = "A.N.Other@example.com"

    # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?email=A.N.Other%40example.com&tool=biopython&db=gene&id=829&retmode=json
    most_likely_entry = Entrez.esearch(db="gene",term="{gene_name} [Preferred Symbol] AND 9606 [Taxonomy ID]".format(gene_name=gene_name),retmode="json")
    most_likely_entry_json = json.loads(most_likely_entry.read())
    my_ids = most_likely_entry_json['esearchresult']['idlist']

    client = pymongo.MongoClient()
    db = client.cache

    gene_summary = db.gene_summary

    found_summary_record = gene_summary.find_one({'geneId': gene_name})

    if(found_summary_record is not None):
        return found_summary_record['summary']
    else:
        if my_ids == []:
            return_value = "NO SUMMARY IN Entrez db"
        else:
            # We got the ID with the Preferred Symbol lookup
            for an_iden in my_ids:
                #print 'Entrez internal ID: ' + an_iden
                record_summary = Entrez.esummary(db="gene",id=an_iden,retmode="json")

                summary_json = json.load(record_summary)
                if(summary_json['result']):
                    for k, v in summary_json['result'].iteritems():
                        if(k == an_iden):
                            #print v
                            save_this_summary = v['summary']
                            if(len(save_this_summary) < 1):
                                save_this_summary = look_up_gene_short_desc(gene_name)
                                save_this_summary = save_this_summary.replace(gene_name + ' ', '')
                                mystr = ''
                            a = {
                                'geneId': gene_name,
                                'summary': save_this_summary
                            }

                            gene_summary.save(a)

                            client.close()

                            return save_this_summary

        #========================
        # Didn't find a summary
        #========================
        return look_up_gene_short_desc(gene_name)

        return 'Summary n/a'

def look_up_gene_short_desc(gene_name):
    tr = TermAnalyzer()
    termsClassified = tr.process_terms_bulk(gene_name)
    #entrez_summary = get_gene_summary_from_entrez(gene_name)

    term_summary = {
        'termClassification': termsClassified,
        'entrez_summary': ''
    }

    if(term_summary['termClassification'] is not None):
        if(len(term_summary['termClassification']) > 0):
            return term_summary['termClassification'][0]['desc']

    return 'Summary not available'

def get_pubmed_list(geneName):

    Entrez.email = "A.N.Other@example.com"
    queryTerm = geneName + "[All Fields] AND (\"human\"[All Fields) AND (\"gene\"[All Fields) "
    handle = Entrez.esearch(db="pubmed", term=queryTerm, retmax=1000)
    record = Entrez.read(handle)
    idlist = record["IdList"]
    logging.info(geneName + ":\t" + record["Count"])

    handle = Entrez.efetch(db="pubmed", id=idlist, rettype="medline", retmode="text")
    records = Medline.parse(handle)
    records = list(records)

    return_value = {
        'pubmed_ids': []
    }
    for record in records:
        return_value['pubmed_ids'].append(record.get("PMID", ""))
        #print record.get("PMID", "")

    handle.close()

    return return_value