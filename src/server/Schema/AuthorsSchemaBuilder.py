__author__ = 'guorongxu'

import sys

def build_schema(output_file, prefix):
    filewriter = open(output_file, "a")

    filewriter.write("curl -XDELETE \'http://localhost:9200/authors/" + prefix + "\'\n")
    filewriter.write("curl -XPUT \'http://localhost:9200/authors/" + prefix + "/_mapping\' -d \'\n")
    filewriter.write("{\n")
    filewriter.write("\t\"" + prefix + "\": {\n")
    filewriter.write("\t\t\"properties\": {\n")
    filewriter.write("\t\t\t\"source\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"version\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"species\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"network_name\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"node_name\": {\"type\": " + "\"string\", \"index\": \"not_analyzed\"},\n")
    filewriter.write("\t\t\t\"node_type\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\"degree\": {\"type\": " + "\"integer\"},\n")
    filewriter.write("\t\t\t\"node_list\": {\n")
    filewriter.write("\t\t\t\t\"type\": " + "\"nested\",\n")
    filewriter.write("\t\t\t\t\"properties\": {\n")
    filewriter.write("\t\t\t\t\t\"name\": {\"type\": " + "\"string\", \"index\": \"not_analyzed\"},\n")
    filewriter.write("\t\t\t\t\t\"publications\": {\n")
    filewriter.write("\t\t\t\t\t\t\"properties\": {\n")
    filewriter.write("\t\t\t\t\t\t\t\"PMID\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\t\t\t\t\"title\": {\"type\": " + "\"string\", \"index\": \"not_analyzed\"},\n")
    filewriter.write("\t\t\t\t\t\t\t\"journal\": {\"type\": " + "\"string\"},\n")
    filewriter.write("\t\t\t\t\t\t\t\"impact_factor\": {\"type\": " + "\"float\"},\n")
    filewriter.write("\t\t\t\t\t\t\t\"date\": {\"type\": " + "\"date\", \"format\": \"basic_date\"},\n")
    filewriter.write("\t\t\t\t\t\t\t\"position\": {\"type\": " + "\"string\"}\n")
    filewriter.write("\t\t\t\t\t\t}\n")
    filewriter.write("\t\t\t\t\t},\n")
    filewriter.write("\t\t\t\t\t\"degree\": {\"type\": " + "\"integer\"},\n")
    filewriter.write("\t\t\t\t\t\"scores\": {\"type\": " + "\"float\"}\n")
    filewriter.write("\t\t\t\t}\n")
    filewriter.write("\t\t\t},\n")
    filewriter.write("\t\t\t\"total_scores\": {\"type\": " + "\"float\"},\n")
    filewriter.write("\t\t\t\"keywords\": {\"type\": " + "\"string\"}\n")
    filewriter.write("\t\t}\n")
    filewriter.write("\t}\n")
    filewriter.write("}\n")
    filewriter.write("\'\n")

## Main entry
if __name__ == "__main__":
    #output_file = "/Users/guorongxu/Desktop/SearchEngine/Pubmed/json_files/map.sh"
    output_file = sys.argv[1] + "/" + sys.argv[2] + "/json_files/map.sh"
    prefix = sys.argv[3]

    build_schema(output_file, prefix)
