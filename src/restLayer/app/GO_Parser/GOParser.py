__author__ = 'guorongxu'

import re
import sys
import logging

## Parsing the go gene file and return GO ID list with all gene lists.
def parse_go_gene_file(go_gene_file):
    GO_ID_list = {}
    GO_unique_gene_list = {}

    with open(go_gene_file) as fp:
        lines = fp.readlines()

        for line in lines:
            if line.startswith("!"):
                continue
            fields = re.split(r'\t', line)

            if fields[8] == 'P' and fields[4] not in GO_unique_gene_list:
                GO_unique_gene_list.update({fields[4]:fields[4]})

            if fields[8] == 'P' and fields[4] in GO_ID_list:
                gene_list = GO_ID_list.get(fields[4])
                gene_list.append(fields[2])
                GO_ID_list.update({fields[4]: gene_list})
            elif fields[8] == 'P':
                gene_list = []
                gene_list.append(fields[2])
                GO_ID_list.update({fields[4]: gene_list})

    fp.closed

    return GO_ID_list, len(GO_ID_list)

## Parsing the go term file and return GO ID list with descriptions.
def parse_go_term_file(go_term_file):
    GO_Term_list = {}

    with open(go_term_file) as fp:
        lines = fp.readlines()

        accepted = False
        go_term_id = ""
        go_term_def = ""
        for line in lines:
            if line.startswith("[Term]"):
                accepted = True
                continue

            if accepted and line.startswith("id: GO:"):
                go_term_id = line[len("id: "):].rstrip()
            if accepted and line.startswith("name: "):
                go_term_name = line[len("name: "):].rstrip()
            if accepted and line.startswith("def: "):
                go_term_def = line[len("def: \""):line.index("[") - 2].rstrip()
            if accepted and line.startswith("\n"):
                GO_Term_list.update({go_term_id: [go_term_name, go_term_def]})
                accepted = False
                go_term_id = ""
                go_term_def = ""

    fp.closed

    return GO_Term_list, len(GO_Term_list)

## Parsing go gene file and go term file.
def parse(go_gene_file, go_term_file):

    logging.info("parsing GO gene file...")
    GO_ID_list, total_unique_gene = parse_go_gene_file(go_gene_file)

    logging.info("parsing GO term file...")
    GO_Term_list, total_unique_term = parse_go_term_file(go_term_file)

    print total_unique_gene, total_unique_term

    return GO_ID_list, total_unique_gene, GO_Term_list

## Main entry
if __name__ == "__main__":

    #go_gene_file = sys.argv[1]
    #go_term_file = sys.argv[2]
    go_gene_file = "/Users/guorongxu/Desktop/SearchEngine/GO/gene_association.goa_human"
    go_term_file = "/Users/guorongxu/Desktop/SearchEngine/GO/go.obo"

    logging.info("parsing GO gene and term files...")
    GO_ID_list, total_unique_gene, GO_Term_list = parse(go_gene_file, go_term_file)
