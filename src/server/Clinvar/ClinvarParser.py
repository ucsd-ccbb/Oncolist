__author__ = 'guorongxu'

import csv
import re
import os
import sys

VALID_COLUMN_NO = 27

# split id lists into dictionary
def other_id(other_ids):
    p = other_ids.strip(";").replace(";", ",").split(",")
    other_id = {}
    for id in p:
        try:
            ind = id.index(":")
            key, value = id[:ind], id[ind+1:]
            if key in other_id:
                if not isinstance(other_id[key], list):
                    other_id[key] = [other_id[key]]
                other_id[key].append(value)
            else:
                other_id[key] = value
        except:
            continue
    return other_id


# convert one snp to json
def _map_line_to_json(fields):
    #assert len(fields) == VALID_COLUMN_NO

    chrom = fields[13]
    chromStart = fields[14]
    chromEnd = fields[15]

    HGVS = None
    cds = fields[18].split(":")
    cds = cds[1]

    seq = re.findall(r'[ATCGMNHYR]+|[0-9]+', cds)[-1]
    replace = re.findall(r'[ATCGMNYR=]+', cds)
    sub = re.search(r'[ATCGMNHYR]+>[ATCGMNHYR]+', cds)
    ins = re.search(r'ins[ATCGMNHYR]+|ins[0-9]+', cds)
    delete = fields[1] == 'deletion'
    indel = fields[1] == 'indel'
    dup = re.search(r'dup', cds)
    inv = re.search(r'inv|inv[0-9]+|inv[ATCGMNHYR]+', cds)
    if ins:
        delete = None
        indel = None
    elif delete:
        ins = None
        indel = None
    if sub:
        HGVS = "chr%s:g.%s%s" % (chrom, chromStart, sub.group())
    elif ins:
        HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, ins.group())
    elif delete:
        HGVS = "chr%s:g.%s_%sdel" % (chrom, chromStart, chromEnd)
    elif indel:
        try:
            HGVS = "chr%s:g.%s_%sdel%s" % (chrom, chromStart, chromEnd, ins.group())
        except AttributeError:
            print "ERROR:", fields[1], cds
    elif dup:
        HGVS = "chr%s:g.%s_%sdup%s" % (chrom, chromStart, chromEnd, seq)
    elif inv:
        HGVS = "chr%s:g.%s_%sinv%s" % (chrom, chromStart, chromEnd, inv.group())
    elif replace:
        HGVS = "chr%s:g.%s_%s%s" % (chrom, chromStart, chromEnd, replace)
    else:
        print 'ERROR:', fields[1], cds

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "clinvar":
            {
                "allele_id": fields[0],
                "hg19":
                    {
                        "chr": fields[13],
                        "start": fields[14],
                        "end": fields[15]
                    },
                "type": fields[1],
                "name": fields[2],
                "gene":
                    {
                        "id": fields[3],
                        "symbol": fields[4]
                    },
                "clinical_significance": fields[5].split(";"),
                "rsid": 'rs' + str(fields[6]),
                "nsv_dbvar": fields[7],
                "rcv_accession": fields[8].split(";"),
                "tested_in_gtr": fields[9],
                "phenotype_id": other_id(fields[10]),
                "origin": fields[11],
                "cytogenic": fields[16],
                "review_status": fields[17],
                "hgvs":
                    {
                        "coding": fields[18],
                        "protein": fields[19]
                    },
                "number_submitters": fields[20],
                "last_evaluated": fields[21],
                "guidelines": fields[22],
                "other_ids": other_id(fields[23]),
                "clinvar_id": fields[24]
            }
        }

    return HGVS + "\t" + fields[10] + "\t" + fields[3] + "\t" + fields[4] + " \t" + 'rs' + str(fields[6]) + "\t" + fields[0] + "\t" + fields[1] \
           + "\t"  + fields[2] + "\t" + fields[5] + "\t" + fields[7] + "\t" + fields[8] + "\t" + fields[16] + "\t" + fields[18] + "\t" + fields[19] \
           + "\t" + fields[23]

# open file, parse, pass to json mapper
def load_data(input_file, sorted_input_file, output_file):
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    os.system("sort -t$'\t' -k14 -k15 -k20 -n %s > %s" % (input_file, sorted_input_file))

    clinvar_list = []
    with open(sorted_input_file) as fp:
        clinvar = fp.readlines()
        for line in clinvar:
            row = re.split(r'\t', line)
            if row[18] != '-' and row[18].find('?') == -1 and row[13] != "" and row[12] == "GRCh37" and not re.search(r'p.', row[18]):
                clinvar_list.append(row)

        f = open(output_file, 'w')

        # print the header
        print >> f,"HGVS_id\tphenotype_id\tgene_id\tgene_symbol\trsid\tallele_id\ttype\tname\tclinical_significance\tnsv_dbvar" \
                   "\trcv_accession\tcytogenic\thgvs_coding\thgvs_protein\tother_ids"
        for field in clinvar_list:
            record = _map_line_to_json(field)
            print >> f, record

        f.close()

## Main entry
if __name__ == "__main__":
    workspace = sys.argv[1]
    #workspace = "/Users/guorongxu/Desktop/SearchEngine/Clinvar"
    input_file = workspace + "/raw_files/variant_summary.txt"
    sorted_input_file = workspace + "/converted_files/sorted_variant_summary.txt"
    output_file = workspace + "/converted_files/clinvar.out.txt"

    clinvar_data = load_data(input_file, sorted_input_file, output_file)
