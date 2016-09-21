__author__ = 'guorongxu'

import sys
import logging

from Schema import ClustersSchemaBuilder
from Schema import GenesSchemaBuilder

if __name__ == "__main__":

    output_file = sys.argv[1] + "/" + sys.argv[2] + "/oslom_undirected_json_files/map.sh"

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Output file: " + output_file)

    prefix = "clusters_tcga_oslom"
    logging.info("printing schema of : " + prefix)
    ClustersSchemaBuilder.build_schema(output_file, prefix)

