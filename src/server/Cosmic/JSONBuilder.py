__author__ = 'guorongxu'

#To build the JSON file for author and gene.
def outputJSON(outputFile, record):
    prefix = "conditions_cosmic_mutant"

    # Open a file
    filewriter = open(outputFile, "a")

    if "COSM" not in record["_id"]:
        filewriter.write("curl -XPOST http://localhost:9200/conditions/" + prefix + " -d \'\n")
        filewriter.write("{\n")
        filewriter.write("\t\"source\": \"Cosmic\",\n")
        filewriter.write("\t\"version\": \"GRCh37.v77\",\n")
        filewriter.write("\t\"species\": \"human\",\n")
        filewriter.write("\t\"network_name\": \"" + prefix + "\",\n")
        filewriter.write("\t\"node_name\": \"" + record["_id"] + "\",\n")
        filewriter.write("\t\"degree\": 1,\n")
        filewriter.write("\t\"phenotype_id_list\": [],\n")
        filewriter.write("\t\"node_list\": [\n")
        filewriter.write("\t\t{\n")
        filewriter.write("\t\t\t\"name\": " + "\"" + record["cosmic"]["gene"]["symbol"] + "\", \n")
        filewriter.write("\t\t\t\"id\": " + "\"" + record["cosmic"]["transcript"] + "\", \n")
        filewriter.write("\t\t\t\"type\": " + "\"g\", \n")
        filewriter.write("\t\t\t\"cosmic_id\": " + "\"" + record["cosmic"]["mutation"]["id"] + "\", \n")
        filewriter.write("\t\t\t\"tissue\": " + "\"" + record["cosmic"]["tumour"]["primary_site"].replace("_", " ") + "\", \n")
        filewriter.write("\t\t\t\"description\": " + "\"" + record["cosmic"]["tumour"]["histology_subtype"].replace("_", " ") + "\", \n")
        filewriter.write("\t\t\t\"pubmed\": " + "\"" + record["cosmic"]["pubmed"] + "\"\n")
        filewriter.write("\t\t}\n")
        filewriter.write("\t]\n")
        filewriter.write("}\n")
        filewriter.write("\'\n")

    filewriter.close()
