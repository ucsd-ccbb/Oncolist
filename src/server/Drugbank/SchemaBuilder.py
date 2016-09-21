__author__ = 'guorongxu'

import sys
import logging

from Schema import DrugsSchemaBuilder

if __name__ == "__main__":

    output_file = sys.argv[1] + "/" + sys.argv[2] + "/json_files/map.sh"

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Output file: " + output_file)

    prefix = "drugs_drugbank"
    logging.info("printing schema of : " + prefix)
    DrugsSchemaBuilder.build_schema(output_file, prefix)
