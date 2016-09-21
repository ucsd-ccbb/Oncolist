__author__ = 'guorongxu'

import sys
import os
import json

import ImpactFactorParser

#To build the JSON file for author and gene.
def output_json(output_file, author_list, journal_list):
    prefix = "authors_pubmed"

    # Open a file
    filewriter = open(output_file, "a")

    for author in author_list:
        filewriter.write("curl -XPOST http://localhost:9200/authors/" + prefix + " -d \'\n")
        filewriter.write("{\n")
        filewriter.write("\t\"source\": \"pubmed\",\n")
        filewriter.write("\t\"version\": \"2016_07_28\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"authors_pubmed\",\n")
        filewriter.write("\t\"node_name\": \"" + author + "\",\n")
        filewriter.write("\t\"node_type\": \"a\",\n")
        filewriter.write("\t\"degree\": " + str(len(author_list.get(author))) + ",\n")
        filewriter.write("\t\"node_list\": [\n")
        nodes = ""

        gene_list = author_list.get(author)
        totalScore = 0
        keywords = ""
        for gene_name in gene_list:
            keywords = keywords + gene_name + ", "
            nodes = nodes + "\t\t{\n"
            nodes = nodes + "\t\t\t\"name\": " + "\"" + gene_name + "\", \n"
            nodes = nodes + "\t\t\t\"publications\": ["

            scores = 0;
            publications = gene_list.get(gene_name)
            for publication in publications:
                publicationStr = publication.get("Title")
                newpublicationStr = publicationStr
                if ("\"" in publicationStr):
                    newpublicationStr = publicationStr.replace("\"", "\\\"")
                if ("\\" in publicationStr):
                    newpublicationStr = publicationStr.replace("\\", "\\\\")

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
                totalScore = totalScore + factor * position_score
                nodes = nodes + "{\"PMID\": \"" + publication.get("PMID") + "\", \"title\": \"" + newpublicationStr \
                        + "\", \"journal\": \"" + publication.get("Journal_Short") + "\", \"impact_factor\": " \
                        + str(factor) + ", \"date\": \"" + publication.get("Date") \
                        + "\", \"position\": \"" + publication.get("Position") + "\"}, "

            nodes = nodes[:-2]
            nodes = nodes + "], \n"
            nodes = nodes + "\t\t\t\"degree\": " + str(len(publications)) + ",\n"
            nodes = nodes + "\t\t\t\"scores\": " + str(scores) + "\n"
            nodes = nodes + "\t\t}, \n"

        nodes = nodes[:-3]
        nodes = nodes + "\n\t],\n"

        filewriter.write(nodes)
        filewriter.write("\t\"total_scores\": " + str(totalScore) + ",\n")
        filewriter.write("\t\"keywords\": \"" + keywords[:-2] + "\"\n")
        filewriter.write("}\n")
        filewriter.write("\'\n")
    filewriter.close()

## To parse the raw pubmed json files and then output the author and gene JSON files.
def parse(workspace):
    pubmed_files = workspace + "/pubmed_files"
    impact_factor_file = workspace + "/2014_SCI_IF.txt"


    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    journal_list = ImpactFactorParser.parse_impact_factor_file(impact_factor_file)
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
                            geneList = author_list.get(author)
                            geneList.update({gene_name: publications})
                        else:
                            publications = node.get("publications")
                            geneList = {}
                            geneList.update({gene_name: publications})
                            author_list.update({author: geneList})
                except ValueError, e:
                    print myfile + "is empty!"

    return author_list, journal_list

if __name__ == "__main__":

    workspace = sys.argv[1]
    output_file = workspace + "/json_files/authors.json"

    print "Parsing pubmed files..."
    author_list, journal_list = parse(workspace)

    print "Printing JSON files..."
    output_json(output_file, author_list, journal_list)
