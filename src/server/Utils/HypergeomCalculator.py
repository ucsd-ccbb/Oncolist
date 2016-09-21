__author__ = 'James & Guorong'

import logging
import itertools
import math
from fdr import fdr
from GO import GOLocusParser
from scipy.stats import hypergeom

def calc_pvalue(gene_list, gene_set, M):
    gene_list = set(gene_list)
    gene_set = set(gene_set)

    N = len(gene_list)
    n = len(gene_set)
    overlap = gene_list & gene_set
    k = len(overlap)

    return hypergeom(M, n, N).sf(k), list(overlap)

def calc_enrichment(gene_list, GO_ID_list, total_unique_gene, GO_Term_list):
    M = total_unique_gene

    enriched_list = []
    for term in GO_ID_list:
        if len(GO_ID_list.get(term)) >= 20 and len(GO_ID_list.get(term)) <= 2000:
            pvalue, overlap = calc_pvalue(gene_list, GO_ID_list.get(term), M)
            if len(overlap) > 1:
                enriched_item = {"go_id": term, "name":GO_Term_list.get(term)[0] ,"description":GO_Term_list.get(term)[1],
                                 "pvalue": pvalue, "overlap": overlap, "genes_from_list": len(gene_list), "genes_from_go": len(GO_ID_list.get(term))}
                enriched_list.append(enriched_item)

    enriched_list.sort(key=lambda it: it['pvalue'])

    for qvalue, it in itertools.izip(fdr([it['pvalue'] for it in enriched_list], presorted=True), enriched_list):
        if math.fabs(qvalue) == 0:
            it['qvalue'] = 1000
        else:
            it['qvalue'] = -math.log(qvalue, 10)

    enriched_list.sort(key=lambda it: it['qvalue'], reverse=True)

    return enriched_list

## Main entry
if __name__ == "__main__":
    go_gene_file = "/Users/guorongxu/Desktop/SearchEngine/GO/GO2all_locus.txt"
    gene_info_file = "/Users/guorongxu/Desktop/SearchEngine/GO/Homo_sapiens.gene_info"
    go_term_file = "/Users/guorongxu/Desktop/SearchEngine/GO/go.obo"

    gene_list = ['HIF3A', 'ZFPM2', 'GAB1', 'OLFM2', 'OLFM1', 'SRCIN1', 'TTC9B', 'NPAS1', 'CDC42SE1', 'TMEM55A', 'HTR2B',
                 'C7', 'C10orf35', 'LNX1', 'PAQR6', 'HOXC10', 'F12', 'C21orf34', 'FAM82B', 'CAB39L', 'MEF2C', 'EMP2',
                 'ANGPTL1', 'RRP12', 'C17orf55']

    logging.info("parsing GO gene and term files...")

    GO_ID_list, total_unique_gene, GO_Term_list = GOLocusParser.parse(go_gene_file, gene_info_file, go_term_file)
    #GO_ID_list, total_unique_gene, GO_Term_list = GOParser.parse(go_gene_file, go_term_file)
    enriched_list = calc_enrichment(gene_list, GO_ID_list, total_unique_gene, GO_Term_list)

    print enriched_list