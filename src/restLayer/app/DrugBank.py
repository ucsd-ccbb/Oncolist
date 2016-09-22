__author__ = 'aarongary'

from xml.dom import minidom
from bson.json_util import dumps
import xml.etree.ElementTree as ET
import requests
import pymongo

def get_drugbank_synonym(drugbank_id):
    client = pymongo.MongoClient()
    db = client.identifiers

    drugbank_lookup = db.drugbank

    result = drugbank_lookup.find_one({'drugbank_id': drugbank_id})

    if(result is not None):
        return result['drug_name']
    else:

        pubchemUrl = 'https://pubchem.ncbi.nlm.nih.gov/compound/'
        r = requests.get(pubchemUrl + drugbank_id)
        lines = list(r.iter_lines())

        count=0
        for idx, line in enumerate(lines):
            if('data-pubchem-title=' in line):
                location_start = line.find('data-pubchem-title=')
                print location_start + 20
                line_parsed1 = line[(location_start + 20):]
                target_name = line_parsed1[:line_parsed1.find('"')]

                a = {
                    'drugbank_id': drugbank_id,
                    'drug_name': target_name
                }

                print dumps(a)
                drugbank_lookup.save(a)

                return a['drug_name']

def extract_ids_from_xml_file():
    file_names = ['drugbank1.xml','drugbank1b.xml','drugbank2.xml','drugbank3.xml','drugbank4.xml','drugbank5.xml','drugbank6.xml']
    for file_name in file_names:
        xmlfile = minidom.parse(file_name)
        drug_list = xmlfile.getElementsByTagName('drug')
        for drug in drug_list:
            drugbank_id = ''
            drug_product_name = ''
            if drug.parentNode.tagName == 'drugbank':
                drug_id_list = drug.getElementsByTagName('drugbank-id')
                for drug_id in drug_id_list:
                    if(drug_id.getAttribute('primary') == 'true'):
                        drugbank_id = drug_id.firstChild.nodeValue
                        drug_name_list = xmlfile.getElementsByTagName('name')
                        if(drug_name_list.length > 0):
                            drug_product_name = drug_name_list[0].firstChild.nodeValue

                            print drugbank_id + '\t' + drug_product_name



def extract_ids_from_xml_file_tree():
    tree = ET.parse('drugbank1.xml')
    root = tree.getroot()

    for drug_node in root.findall('drug'):
        rank = drug_node.find('drugbank-id').text
        print rank
