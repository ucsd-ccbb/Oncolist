__author__ = 'guorongxu'

import sys
import os
import json

import ImpactFactorParser

## To build the edge file between author and gene.
def output(output_file, author_list, journal_list):
    # Open a file
    filewriter = open(output_file, "a")

    for author in author_list:
        gene_list = author_list.get(author)
        for gene_name in gene_list:
            scores = 0
            publications = gene_list.get(gene_name)
            for publication in publications:
                journal_name = publication.get("Journal")

                factor = 0;
                if str(journal_name).lower() in journal_list:
                    factor = float(journal_list.get(str(journal_name).lower()))

                ## position_score = 0.1 if M
                ## otherwise position_score = 1 if F or position_score =5 if L
                position_score = 1
                if ("M" == publication.get("Position")):
                    position_score = 0.1
                if ("F" == publication.get("Position")):
                    position_score = 1
                if ("L" == publication.get("Position")):
                    position_score = 5
                scores = scores + factor * position_score

            filewriter.write(author + "\t" + gene_name + "\t" + str(scores) + "\t" + str(len(publications)) + "\n")

    filewriter.close()

def process(workspace):
    pubmed_files = workspace + "/pubmed_files"
    output_file = workspace + "/edge_files/author_vs_gene.edges.txt"
    impact_factor_file = workspace + "/2014_SCI_IF.txt"
    journal_list = ImpactFactorParser.parse_impact_factor_file(impact_factor_file)

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    author_list = {}

    for file in os.listdir(pubmed_files):
        if file.endswith(".json"):
            myfile = pubmed_files + "/" + file

            #Extract the gene list and publications for each author
            with open(myfile) as json_file:
                try:
                    json_data = json.load(json_file)
                    gene_name = json_data.get("node_name")
                    node_list = json_data.get("node_list")
                    nodes = node_list.get("node")

                    for node in nodes:
                        author = node.get("name")
                        if author in author_list:
                            publications = node.get("publications")
                            gene_list = author_list.get(author)
                            gene_list.update({gene_name: publications})
                        else:
                            publications = node.get("publications")
                            gene_list = {}
                            gene_list.update({gene_name: publications})
                            author_list.update({author: gene_list})
                except ValueError, e:
                    print myfile + "is empty!"

    output(output_file, author_list, journal_list)

if __name__ == "__main__":

    workspace = sys.argv[1]

    print "Printing pubmed edge files..."
    process(workspace)