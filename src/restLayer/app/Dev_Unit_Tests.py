import unittest
import app.PubMed
import app.MirBase
import app.InterPro
import app.ElasticSearch
import app.util
import app.NihNcbi
import app.NeighborhoodSearch
import app.AllPurposeDownloader
import app.TermIdentifier
import app.SearchPathwaysTab as spwt
from app import util
#from app import author_gene_clustering_module
from models import SearchResult
from models.SearchResult import SearchResultModel
from models.ConditionResults import ConditionResultModel
from models.PathwaySearchModel import PathwaySearchResult
from models.ConditionSearchModel import ConditionSearchResults
from app import SearchPathwaysTab
from app import SearchViz
from app import SearchInferredDrugsTab
from app import ESearch
from app import PubMed

class Dev_Uint_Tests(unittest.TestCase):
    def test_groupedConditions(self):
        #myPathwaysSearchResult = PathwaySearchResult()
        #myPathwaysSearchResult.name = 'my name'

        #result = myPathwaysSearchResult.to_JSON()

        #print result


        self.assertTrue(1 == 1)

    def test_searchTypes(self):
        #myConditionSearchResults = ConditionSearchResults()
        #myConditionSearchResults.name = 'my name'
        #myConditionSearchResults.addGroupedClinvarConditions('BRCA1', {'phenotype_name': 'breast|NS'})
        ##myConditionSearchResults.addGroupedClinvarConditions('BRCA1', {'phenotype_name': 'central_nervous_system|NS'})
        #myConditionSearchResults.addGroupedCosmicConditions('BRCA2', {'phenotype_name': 'cosmic phenotype'})
        #myConditionSearchResults.addGroupedClinvarConditions('BRCA2', {'phenotype_name': 'clinvar phenotype'})

        #result = myConditionSearchResults.to_JSON()

        #print result

#        myConditionResultModel = ConditionResultModel()

#        myConditionResultModel.loadTestData()
#        myConditionResultModel.addGroupedClinvarConditions('BRCA1', {'phenotype_name': 'breast|NS'})
#        myConditionResultModel.addGroupedClinvarConditions('BRCA1', {'phenotype_name': 'central_nervous_system|NS'})
#        myConditionResultModel.addGroupedCosmicConditions('BRCA2', {'phenotype_name': 'cosmic phenotype'})
#        myConditionResultModel.addGroupedClinvarConditions('BRCA2', {'phenotype_name': 'cosmic phenotype'})
            #addGroupedConditions({'id': 'add this grouped item'})

#        result = myConditionResultModel.toJson()

#        print result

        #result = app.SearchPathwaysTab.get_heatmap_graph_from_es_by_id('AVHqDnuVQyqp5jv2wXxp', 'louvain_cluster')
        #print result

        #app.TermIdentifier.load_variant_to_gene_from_file()

        #app.SearchPathwaysTab.get_all_cluster_ids()
        #app.SearchViz.plot_cluster()
        #earchInferredDrugsTab.get_inferred_drug_search('CLK1', '1234')

        #seed_genes = 'GPAM,LYVE1,LHX6,GPR182,ACSM5,AQPEP' #'CDH11,DLL4,FOSB,GPIHBP1' # set seed genes (must be in cluster)

        #SearchViz.get_heat_prop_cluster_viz(seed_genes,'2020014671')
        #SearchViz.get_heat_prop_from_gene_list(seed_genes,'2020004787')

        #result = app.ElasticSearch.get_disease_types_from_ES()

        #print result

        #print app.ElasticSearch.get_cluster_disease_by_es_id('2020000100')

        #app.PubMed.get_genemania_identifiers()

        app.ElasticSearch.convert_name_to_index('abc',[{'name': 'xyz'},{'name': 'xyz2'},{'name': 'xyz3'},{'name': 'abc'},{'name': 'xyz4'}])
        self.assertTrue(1 == 1)

    def test_pubMed(self):
        #app.PubMed.download_tar_gz('ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/fd/6e/Crit_Care_1998_Mar_12_2(1)_19-23.tar.gz', 'Downloaded_Crit_Care_1998_Mar_12_2(1)_19-23.tar.gz')
        #app.PubMed.untar("Crit_Care_1998_Mar_12_2(1)_19-23.tar.gz")
        #app.PubMed.load_pubmed_list()
        #term_id = app.MirBase.get_mir_name_converter("hsa-mir-27b")
        #app.InterPro.run_interpro_download()
        #app.ElasticSearch.get_gene_network_search('OR2J3,AANAT,lymphatic,MACC1,CCDC158,PLAC8L1,Caffeine,CLK1,Cholera,GLTP,Aspirin,PITPNM2,TRAPPC8,EIF2S2,adverse,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3')
        #app.ElasticSearch.get_star_search_mapped('OR2J3,AANAT,lymphatic,MACC1,CCDC158,PLAC8L1,Caffeine,CLK1,Cholera,GLTP,Aspirin,PITPNM2,TRAPPC8,EIF2S2,adverse,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3')
        #app.ElasticSearch.get_star_search_neighborhood_mapped('OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3')
        #app.NeighborhoodSearch.star_search_mapped_2_0('OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3')
        #app.ElasticSearch.get_star_pvalue('OR2J3,AANAT,lymphatic,MACC1,CCDC158,PLAC8L1,Caffeine,CLK1,Cholera,GLTP,Aspirin,PITPNM2,TRAPPC8,EIF2S2,adverse,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3')
        #app.util.printGoList()
        #app.PubMed.get_pubmed_counts()
        #app.PubMed.load_pubmed_counts_list()
        #app.NihNcbi.load_gene_info()
        #app.NihNcbi.lookup_id('BRCA1')
        #app.PubMed.get_gene_pubmed_counts_normalized('OR2J3,AANAT,MACC1,CCDC158,PLAC8L1,CLK1,PITPNM2,TRAPPC8,EIF2S2')
        #app.PubMed.normValue(70.0, 254.0, 1.0)
        #app.AllPurposeDownloader.download_tar_gz()
        #app.TermIdentifier.load_terms_from_file()
        #app.TermIdentifier.add_terms_from_file()
        #result = app.TermIdentifier.identify_term('lip')
        #result = app.TermIdentifier.bulk_identify_terms('BRCA1,BRCA2,FOSB,ldfsdf,caffeine')
        #result = app.TermIdentifier.bulk_identify_terms('lip,BRCA1,jjsdkfg')
        #result = app.TermIdentifier.add_biomart_terms_from_file()
        #result = app.TermIdentifier.load_disease_groups()

        #spwt.transform_matrix_to_graph()
        #print result

        #app.util.agg_search_data()

        #author_gene_clustering_module.save_gene_gene_json('example_input.tsv', 'testexample', 30.0)
        #author_gene_clustering_module.create_author_gene_groupby('author_vs_gene.edges.txt')

        #mySearchResult = SearchResultModel()

        #mySearchResult.loadTestData()

        #result = mySearchResult.toJson()

        #result = app.SearchPathwaysTab.get_heatmap_graph_from_es_by_id('AVHqDnuVQyqp5jv2wXxp', 'louvain_cluster')
        #print result

        #app.SearchPathwaysTab.get_document_overlaps('OR2J3','AVMFmdsjRXVvO0gLmFIp')

        #app.TermIdentifier.load_variant_to_gene_from_file()

        #result = app.ESearch.query('GATA1')
        #result = app.ESearch.retrieve_annotation(['GATA1'])
        #result = app.ESearch.get_gene_summary_from_entrez('GATA1')
        #app.PubMed.get_pubmed_titles('ES_LOOKUP')
        #print result

        self.assertTrue(1 == 1)


if __name__ == '__main__':
    unittest.main()