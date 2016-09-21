__author__ = 'guorongxu'

import sys
import logging

from Schema import ClustersSchemaBuilder
from Schema import GenesSchemaBuilder

if __name__ == "__main__":

    output_file = sys.argv[1] + "/" + sys.argv[2] + "/json_files/map.sh"

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Output file: " + output_file)

    prefix = "clusters_geo_louvain"
    logging.info("printing schema of : " + prefix)
    ClustersSchemaBuilder.build_schema(output_file, prefix)

    prefix = "genes_geo"
    logging.info("printing schema of : " + prefix)
    GenesSchemaBuilder.build_schema(output_file, prefix)