__author__ = 'aarongary'
import unittest
import warnings
from app import SearchPathwaysTab
from app import SearchConditionsTab
from app import SearchAuthorsTab
from app import SearchDrugsTab
#from app import SearchViz
from bson.json_util import dumps
#from app.nav import job_queue
import json

class ClusterSearchTests(unittest.TestCase):
    #==============================
    # CLUSTER SEARCH TEST
    #==============================
    def test_get_cluster_search_mapped(self):
        search_results = SearchPathwaysTab.get_cluster_search_mapped('GATA1,GATA2',99)

        for search_result in search_results:
            if(len(search_result['disease_filter_all']) <= 1):
                self.fail('No diseases found')

            #THIS IS EQUIVALENT TO THE ABOVE ASSERTION
            self.assertGreaterEqual(len(search_result['disease_filter_all']), 1)

            if(len(search_result['matrix_filter_all']) <= 1):
                self.fail('No matrix types found')

            if(len(search_result['annotation_filter_all']) <= 1):
                self.fail('No annotations found')

            for grouped_item in search_result['grouped_items']:
                if(grouped_item['groupTopQValue'] < 3.5):
                    warnings.warn("Result has Q value lower than 3.5: " + dumps(grouped_item), Warning)
                for group_member in grouped_item['group_members']:
                    if(len(group_member['emphasizeInfoArray']) < 1):
                        warnings.warn("Group result has no overlap: " + dumps(group_member), Warning)

        with self.assertRaises(Exception):
            SearchPathwaysTab.get_cluster_search_mapped('INVALIDGENE1,INVALIDGENE2',99)

        try:
            search_results = SearchPathwaysTab.get_cluster_search_mapped('INVALIDGENE1,INVALIDGENE2',99)
            self.fail('Unrecognized query terms should raise an exception')
        except Exception:
            self.assertTrue(1 == 1)

        self.assertTrue(1 == 1)

    #==============================
    # PHENOTYPE SEARCH TEST
    #==============================
    def test_get_conditions_search(self):
        search_results = json.loads(SearchConditionsTab.get_condition_search('DLL4,PLAC8L1,GLTP', 99))

        for search_result in search_results:
            self.assertEqual(search_result['searchTab'], 'PHENOTYPES')
            for tissue_group in search_result['simple_disease_tissue_group']:
                self.assertGreater(tissue_group['grouped_by_conditions_count'],0)

    #==============================
    # AUTHOR SEARCH TEST
    #==============================
    def test_get_authors_search(self):
        search_results = SearchAuthorsTab.get_people_people_pubmed_search_mapped2('DLL4,PLAC8L1,GLTP', 1)

        for search_result in search_results:
            self.assertEqual(search_result['searchTab'], 'PEOPLE_GENE')

    #==============================
    # DRUG SEARCH TEST
    #==============================
    def test_get_drugs_search(self):
        search_results = SearchDrugsTab.get_drug_network_search_mapped('DLL4,PLAC8L1,GLTP')

        for search_result in search_results:
            self.assertEqual(search_result['searchTab'], 'DRUG') # drug

    def test_get_cosmic_grouped_by_disease(self):
        condition_search_results = SearchConditionsTab.get_cosmic_grouped_by_disease_tissue('OR2J3,AANAT,KRT80,MACC1,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3', 1)

        print dumps(condition_search_results)
