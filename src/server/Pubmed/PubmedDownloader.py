#!/usr/bin/python

__author__ = 'guorongxu'

import os
import sys

from ESearch import query

# To output the pubmed raw json files
def output_json(workspace, gene_name, gene_list):

    output_file = workspace + "/pubmed_files/" + gene_name + ".json"

    # Open a file
    filewriter = open(output_file, "wb")

    for gene in gene_list:
        author_list = gene_list.get(gene)
        if len(author_list) == 0:
            continue

        filewriter.write("{\n")
        filewriter.write("\t\"source\": \"pubmed\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"gene_network\",\n")
        filewriter.write("\t\"node_name\": \"" + gene + "\",\n")
        filewriter.write("\t\"degree\": " + str(len(author_list)) + ",\n")
        filewriter.write("\t\"node_list\": {\n")
        filewriter.write("\t\t\"node\": [\n")
        nodes = ""

        for author in author_list:
            nodes = nodes + "\t\t\t{\n"
            nodes = nodes + "\t\t\t\t\"name\": " + "\"" + author + "\", \n"
            nodes = nodes + "\t\t\t\t\"publications\": ["

            publications = author_list.get(author)
            for publication in publications:
                publicationStr = publication[1]
                newpublicationStr = publicationStr
                if ("\"" in publicationStr):
                    newpublicationStr = publication[1].replace("\"", "\\\"")
                if ("\\" in publicationStr):
                    newpublicationStr = publication[1].replace("\\", "\\\\")
                nodes = nodes + "{\"PMID\": \"" + publication[0] + "\", \"Title\": \"" + newpublicationStr \
                        + "\", \"Journal\": \"" + publication[3] + "\", \"Journal_Short\": \"" + publication[4] \
                        + "\", \"Date\": \"" + publication[5] + "\", \"Position\": \"" + publication[6] + "\"}, "

            nodes = nodes[:-2]

            nodes = nodes + "]\n"
            nodes = nodes + "\t\t\t}, \n"

        nodes = nodes[:-3]
        nodes = nodes + "\n\t\t]\n"

        filewriter.write(nodes)
        filewriter.write("\t}\n")
        filewriter.write("}\n")
    filewriter.close()

## To download pubmed files from PUBMED by the provided gene list.
def download_pubmed(workspace, begin, end):

    try:
        if not os.path.exists(workspace + "/pubmed_files"):
            os.makedirs(workspace + "/pubmed_files")

        if not os.path.exists(workspace + "/json_files"):
            os.makedirs(workspace + "/json_files")
    except OSError:
        print "File exists!"

    with open(workspace + "/gene_list.txt") as f:
        content = f.readlines()

        line_index = 1
        for line in content:

            if line_index >= begin and line_index <= end:
                gene_name = line[:-1]
                gene_list = query(gene_name)
                output_json(workspace, gene_name, gene_list)

            line_index = line_index + 1

if __name__ == "__main__":

    workspace = sys.argv[1]
    begin = int(sys.argv[2])
    end = int(sys.argv[3])

    print "processing pubmed downloading..."
    download_pubmed(workspace, begin, end)

