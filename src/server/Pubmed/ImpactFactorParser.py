__author__ = 'guorongxu'

import re

#Parsing the impact factor file
def parse_impact_factor_file(impact_factor_file):
    #impact_factor_file = "/Users/guorongxu/Desktop/SearchEngine/pubmed/2014_SCI_IF.txt"

    journalList = {}

    with open(impact_factor_file) as fp:
        lines = fp.readlines()

        for line in lines:
            fields = re.split(r'\t+', line)
            if fields[3] == "Not Available":
                journalList.update({fields[1].lower(): "0"})
            else:
                journalList.update({fields[1].lower(): fields[3]})

    fp.closed

    return journalList
