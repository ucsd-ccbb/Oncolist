# -*- coding: utf-8 -*-
import os
import sys
import csv
import re
from itertools import imap, groupby, ifilter
import operator
import collections
import JSONBuilder

VALID_COLUMN_NO = 28

# convert one snp to json
def parse(fields):
    chr_info = re.findall(r"[\w']+", fields[23])
    chrom = chr_info[0]  # Mutation GRCh37 genome position
    chromStart = chr_info[1]
    chromEnd = chr_info[2]

    HGVS = None
    cds = fields[17]
    sub = re.search(r'[ATCGMNHKRY]+>[ATCGMNHKRY]+', cds)
    ins = re.search(r'ins[ATCGMN]+|ins[0-9]+', cds)
    delete = cds.find('del') != -1
    del_ins = re.search(r'[0-9]+>[ATCGMN]+', cds)
    comp = re.search(r'[ATCGMN]+', cds)

    if sub:
        HGVS = "chr%s:g.%s%s" % (chrom, chromStart, sub.group())
    elif ins:
        HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, ins.group())
    elif delete:
        HGVS = "chr%s:g.%s_%sdel" % (chrom, chromStart, chromEnd)
    elif del_ins:
        HGVS = "chr%s:g.%s_%sdelins%s" % (chrom, chromStart, chromEnd, comp.group())
    #elif comp:
    #    HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, comp.group())
    else:
        HGVS = fields[16]
        print "Error2:", fields[19], cds, fields[23]

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {
        "sorter" : fields[23] + fields[17],
        "_id": HGVS,
        "cosmic":
            {
                "gene":
                    {
                        "symbol": fields[0],  # Gene name
                        "id": fields[3],  # HGNC ID
                        "cds_length": fields[2]
                    },
                "transcript": fields[1],  # Accession Number
                "sample":
                    {
                        "name": fields[4],  # Sample name
                        "id": fields[5]  # ID_sample
                    },
                "tumour":
                    {
                        "id": fields[6],  # ID_tumour
                        "primary_site": fields[7],  # Primary site
                        "site_subtype": fields[8],  # Site subtype
                        "primary_histology": fields[11],  # Primary histology
                        "histology_subtype": fields[12],  # Histology subtype
                        "origin": fields[1]
                    },
                "mutation":
                    {
                        "id": fields[16],  # Mutation ID
                        "cds": cds,  # Mutation CDS
                        "aa": fields[18],  # Mutation AA
                        "description": fields[19],  # Mutation Description
                        "zygosity": fields[20],  # Mutation zygosity
                        "somatic_status": fields[28]  # Mutation somatic status
                    },
                "chrom": chrom,
                "hg19":
                   {
                        "start": chromStart,
                        "end": chromEnd
                    },
                "pubmed": fields[30]  # Pubmed_PMID
            }
        }

    return one_snp_json

def process(workspace):
    input_file = workspace + "/raw_data/CosmicMutantExport.tsv"
    output_file = workspace + "/json_files/Cosmic.mutant.json"
    label_file = workspace + "/label_files/Cosmic_label.txt"

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    if not os.path.exists(os.path.dirname(label_file)):
        os.makedirs(os.path.dirname(label_file))

    f = open(output_file, 'a')

    open_file = open(input_file)
    open_file = csv.reader(open_file, delimiter="\t")
    cosmic = []
    for row in open_file:
        try:
            c = row[17].split(".")[1]
        except:
            c = ""

        item = row[23]
        if item and item.find("-") > -1:
            row.append(row[23].split("-")[0] + "." + c)
            cosmic.append(row)

    cosmic = sorted(cosmic, key=operator.itemgetter(23), reverse=True)
    cosmic = ifilter(lambda row:
                row[23] != "" and
                row[23] != "", cosmic)

    filewriter = open(label_file, "a")

    for item in cosmic:
        record = parse(item)
        JSONBuilder.outputJSON(output_file, record)

        filewriter.write(record["_id"] + "\t" + "variant\n")

    f.close()
    filewriter.close()
if __name__ == "__main__":
    workspace = sys.argv[1]
    process(workspace)

