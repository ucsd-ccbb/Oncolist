#!/usr/bin/python

__author__ = 'guorongxu'

import re
import logging
from Bio import Entrez
from Bio import Medline

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