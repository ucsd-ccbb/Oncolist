__author__ = 'guorongxu'

import os
import re
import sys

#Parsing the expression files under the folder
def preprocess(root_raw_dir):
    for root, directories, filenames in os.walk(root_raw_dir):
        for filename in filenames:
            if filename.endswith(".txt"):
                inputfile = os.path.join(root,filename)

                gene_name_hash = {}
                print "Processing: " + inputfile
                if inputfile.endswith(".txt"):
                    outputFile = inputfile.replace(".txt", ".txt.new")
                    outputFile = outputFile.replace(" ", "_")
                    outputFile = outputFile.replace(";.", ".")
                    outputFile = outputFile.replace("_.", ".")
                    outputFile = outputFile.replace("__", "_")
                    filewriter = open(outputFile, "a")

                    with open(inputfile) as fp:
                        lines = fp.readlines()

                        for line in lines:
                            fields = re.split(r'\t+', line)
                            if "." not in fields:
                                if fields[0] == "id":
                                    filewriter.write(line)
                                else:
                                    ## For some gene names which have aliases
                                    if "///" in fields[0]:
                                            geneNames = re.split(r'///+', fields[0])
                                            for geneName in geneNames:
                                                geneNameStr = geneName.strip()
                                                if geneNameStr not in gene_name_hash:
                                                    gene_name_hash.update({geneNameStr:geneNameStr})
                                                    filewriter.write(line.replace(fields[0], geneNameStr))
                                    elif ";" in fields[0]:
                                            geneNames = re.split(r';+', fields[0])
                                            for geneName in geneNames:
                                                geneNameStr = geneName.strip()
                                                if geneNameStr not in gene_name_hash:
                                                    gene_name_hash.update({geneNameStr:geneNameStr})
                                                    filewriter.write(line.replace(fields[0], geneNameStr))
                                    else:
                                        if fields[0] not in gene_name_hash:
                                            gene_name_hash.update({geneNameStr:geneNameStr})
                                            filewriter.write(line)
                    filewriter.close()
                    fp.closed

if __name__ == "__main__":
    root_raw_dir = sys.argv[1]
    preprocess(root_raw_dir)