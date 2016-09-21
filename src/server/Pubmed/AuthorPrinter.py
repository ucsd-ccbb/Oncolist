__author__ = 'guorongxu'

import sys
import os
import json

#To build the JSON file for author and gene.
def output(output_file, author_list):
    # Open a file
    filewriter = open(output_file, "a")

    for author in author_list:
        filewriter.write(author + "\tAuthor\n")

    filewriter.close()

## To
def print_author_list(workspace):
    pubmed_files = workspace + "/pubmed_files"
    output_file = workspace + "/json_files/authorNameTable.txt"

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
                    geneName = json_data.get("node_name")
                    node_list = json_data.get("node_list")
                    nodes = node_list.get("node")

                    for node in nodes:
                        author = node.get("name")
                        if author in author_list:
                            publications = node.get("publications")
                            geneList = author_list.get(author)
                            geneList.update({geneName: publications})
                        else:
                            publications = node.get("publications")
                            geneList = {}
                            geneList.update({geneName: publications})
                            author_list.update({author: geneList})
                except ValueError, e:
                    print myfile + "is empty!"

    output(output_file, author_list)

if __name__ == "__main__":

    workspace = sys.argv[1]

    print "Printing pubmed author json files..."
    print_author_list(workspace)