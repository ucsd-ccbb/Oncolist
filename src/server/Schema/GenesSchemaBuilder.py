__author__ = 'guorongxu'

import sys

def build_schema(output_file, prefix):
    filewriter = open(output_file, "a")

    filewriter.write("curl -XDELETE \'http://localhost:9200/genes/" + prefix + "\'\n")
    filewriter.write("curl -XPUT \'http://localhost:9200/genes/" + prefix + "/_mapping\' -d \'\n")
    filewriter.write("{\n")
    filewriter.write("\t\"" + prefix + "\": {\n")
    filewriter.write("\t\t\"properties\": {\n")
    filewriter.write("\t\t\t\"source\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"species\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"network_name\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"network_full_name\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"node_name\": {\"type\": " + "\"string\", \"index\": \"not_analyzed\"},\n")
    filewriter.write("\t\t\t\"node_type\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"degree\": {\"type\": " + "\"integer\"},\n")
    filewriter.write("\t\t\t\"node_list\": {\n")
    filewriter.write("\t\t\t\t\"properties\": {\n")
    filewriter.write("\t\t\t\t\t\"name\": {\"type\": " + "\"string\", \"index\": \"not_analyzed\"},\n")
    filewriter.write("\t\t\t\t\t\"type\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\t\t\"correlation_value\": {\"type\": " + "\"double\"},\n")
    filewriter.write("\t\t\t\t\t\"p_value\": {\"type\": " + "\"double\"}\n")
    filewriter.write("\t\t\t\t}\n")
    filewriter.write("\t\t\t}\n")
    filewriter.write("\t\t}\n")
    filewriter.write("\t}\n")
    filewriter.write("}\n")
    filewriter.write("\'\n")

## Main entry
if __name__ == "__main__":
    #output_file = "/Users/guorongxu/Desktop/SearchEngine/TCGA/json_files/genes.map.sh"
    #prefix = "genes_tcga"
    output_file = sys.argv[1] + "/" + sys.argv[2] + "/json_files/map.sh"
    prefix = sys.argv[3]

    build_schema(output_file, prefix)