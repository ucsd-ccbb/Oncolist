__author__ = 'guorongxu'

import os
import sys
import logging

from Schema import ConditionsSchemaBuilder

if __name__ == "__main__":

    output_file = sys.argv[1] + "/" + sys.argv[2] + "/json_files/map.sh"

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    logging.basicConfig(filename='search_engine.log',level=logging.DEBUG)
    logging.info("Output file: " + output_file)

    prefix = "conditions_cosmic_mutant"
    logging.info("printing schema of : " + prefix)
    ConditionsSchemaBuilder.build_schema(output_file, prefix)
