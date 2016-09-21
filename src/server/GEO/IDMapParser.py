__author__ = 'guorongxu'

import re
import os

## Parsing ID map table and return two dictionaries of name and ID.
def parse(id_map_folder):

#id_map_folder = "/Users/guorongxu/Desktop/SearchEngine/Louvain/ID_Map_Table/"

    id_vs_name_list = {}
    name_vs_id_list = {}

    for file in os.listdir(id_map_folder):
        if file.endswith(".txt"):
            myfile = id_map_folder + file

            with open(myfile) as fp:
                lines = fp.readlines()

                for line in lines:
                    fields = re.split(r'\t+', line)
                    if fields[1] not in id_vs_name_list:
                        id_vs_name_list.update({fields[1].rstrip(): fields[0].rstrip()})
                    if fields[0] not in name_vs_id_list:
                        name_vs_id_list.update({fields[0].rstrip(): fields[1].rstrip()})

            fp.closed

    return id_vs_name_list, name_vs_id_list