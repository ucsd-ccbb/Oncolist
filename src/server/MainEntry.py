__author__ = 'guorongxu'

import sys
from datetime import datetime
from GEO import GEOCaller
from TCGA import TCGACaller
from Pubmed import PubmedCaller
from Cosmic import CosmicCaller
from Clinvar import ClinvarCaller
from Drugbank import DrugbankCaller
from ClusterDrug import ClusterDrugCaller
from Utils import PBSTracker

## Main entry
if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "usage: python MainEntry.py [data_set] [operation]"
        print "- GEO: run GEO dataset;"
        print "\t- preprocess: preprocess correlation;"
        print "\t- calculate: calculate correlation;"
        print "\t- oslom_cluster: clustering GEO dataset;"
        print "\t- print_oslom_cluster_json: print json files;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        print "\t- all: run all operations;"
        print ""
        print "- TCGA: run TCGA dataset;"
        print "\t- download: download TCGA dataset;"
        print "\t- parse: parse TCGA dataset;"
        print "\t- calculate: calculate correlation;"
        print "\t- filter: filter the correlation less than a cut off;"
        print "\t- louvain_cluster: clustering TCGA dataset using louvain;"
        print "\t- dedup_louvain_cluster: deduplicate the TCGA dataset louvain clusters;"
        print "\t- oslom_undirected_cluster: clustering TCGA dataset using oslom undirected;"
        print "\t- ivanovska_cluster: clustering TCGA dataset using ivanovska;"
        print "\t- print_louvain_json: print the clusters to louvain json files;"
        print "\t- print_ivanovska_json: print the clusters to ivanovska json files;"
        print "\t- print_cluster_oslom_json: print the clusters to oslom json files;"
        print "\t- print_label: print the labels file;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        print "\t- all: run all operations;"
        print ""
        print "- Pubmed: run Pubmed dataset;"
        print "\t- download: download Pubmed dataset;"
        print "\t- print_json: print author vs publications json files;"
        print "\t- print_label: print author labels file;"
        print "\t- print_edge: print author and gene interaction edges;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        print "\t- all: run all operations;"
        print ""
        print "- Cosmic: run Cosmic dataset;"
        print "\t- download: download Cosmic dataset;"
        print "\t- print_json: print variant vs phenotype json files;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        print ""
        print "- Clinvar: run Clinvar dataset;"
        print "\t- parse: download Clinvar dataset;"
        print "\t- print_json: print phenotype, gene and variant json files;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        print ""
        print "- Drugbank: run Drugbank dataset;"
        print "\t- print_json: print drug and gene json files;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        print ""
        print "- ClusterDrug: run ClusterDrug dataset;"
        print "\t- print_json: print cluster and drug json files;"
        print "\t- print_schema: print the schema files;"
        print "\t- append_id: append id into json files;"
        exit()

    data_set = sys.argv[1]
    disease_name = sys.argv[2]
    operation = sys.argv[3]
    s3_input_files_address = sys.argv[4]
    s3_output_files_address = sys.argv[5]

    print disease_name
    print operation
    print s3_input_files_address
    print s3_output_files_address

    workspace = "/shared/workspace/SearchEngineProject"

    if data_set == "GEO":
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing GEO tumor data."
        if operation == "download" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is downloading GEO raw files."
            GEOCaller.download(workspace, data_set, s3_input_files_address, disease_name)
            PBSTracker.trackPBSQueue(1, "geo")
        if operation == "calculate" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is calculating GEO correlations."
            GEOCaller.calculate(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "geo")
        if operation == "oslom_cluster" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is oslom clustering GEO dataset."
            GEOCaller.oslom_undirected_cluster(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "geo")
        if operation == "print_oslom_cluster_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing GEO oslom cluster json files."
            GEOCaller.print_oslom_cluster_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "geo")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing GEO schema files."
            GEOCaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "geo")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into GEO json files."
            GEOCaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "geo")
        if operation == "upload" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is uploading GEO resulting files."
            GEOCaller.upload(workspace, data_set, s3_output_files_address, disease_name)
            PBSTracker.trackPBSQueue(1, "geo")

    if data_set == "TCGA":
        release_year = "2016"
        release_month = "01"
        release_day = "28"
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing TCGA data."
        if operation == "download" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is downloading TCGA dataset."
            TCGACaller.download(workspace, data_set, release_year, release_month, release_day)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "parse" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is parsing TCGA dataset."
            TCGACaller.parse(workspace, data_set, release_year, release_month, release_day)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "calculate" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is calculating TCGA correlations."
            TCGACaller.calculate(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "filter":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is filtering TCGA correlations."
            TCGACaller.filter(workspace, data_set, cut_off=0.5)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "louvain_cluster" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is doing louvain clustering TCGA dataset."
            TCGACaller.louvain_cluster(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "dedup_louvain_cluster" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is deduplicating TCGA dataset louvain clusters."
            TCGACaller.dedup_louvain_cluster(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "oslom_undirected_cluster" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is doing oslom undirected clustering TCGA dataset."
            TCGACaller.oslom_undirected_cluster(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "ivanovska_cluster" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is doing ivanovska cluster TCGA dataset."
            TCGACaller.ivanovska_cluster(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "replace_cluster" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is replacing TCGA oslom cluster files."
            TCGACaller.replace_cluster(workspace, data_set)
        if operation == "print_louvain_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing TCGA louvain json files."
            TCGACaller.print_louvain_json(workspace, data_set)
        if operation == "print_ivanovska_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing TCGA ivanovska json files."
            TCGACaller.print_ivanovska_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "print_oslom_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing TCGA oslom json files."
            TCGACaller.print_oslom_undirected_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "print_label" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing TCGA label files."
            TCGACaller.print_label(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing TCGA schema files."
            TCGACaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into TCGA json files."
            TCGACaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "tcga")

    if data_set == "Pubmed":
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing Pubmed data."
        if operation == "download" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is downloading Pubmed dataset."
            PubmedCaller.download(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "pubmed")
        if operation == "print_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Pubmed json files."
            PubmedCaller.print_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "pubmed")
        if operation == "print_label" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Pubmed labels file."
            PubmedCaller.print_label(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "pubmed")
        if operation == "print_edge" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Pubmed edge files."
            PubmedCaller.print_edge(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "pubmed")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Pubmed schema files."
            PubmedCaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "pubmed")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into Pubmed json files."
            PubmedCaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "pubmed")

    if data_set == "Cosmic":
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing Cosmic data."
        if operation == "download" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is downloading Cosmic dataset."
            CosmicCaller.download(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "cosmic")
        if operation == "print_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Cosmic json files."
            CosmicCaller.print_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "cosmic")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Cosmic schema files."
            CosmicCaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "cosmic")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into Cosmic json files."
            CosmicCaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "cosmic")

    if data_set == "Clinvar":
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing Clinvar data."
        if operation == "parse" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is parsing Clinvar dataset."
            ClinvarCaller.parse(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clinvar")
        if operation == "print_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Clinvar json files."
            ClinvarCaller.print_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clinvar")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Clinvar schema files."
            ClinvarCaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clinvar")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into Clinvar json files."
            ClinvarCaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clinvar")

    if data_set == "Drugbank":
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing Drugbank data."
        if operation == "print_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Drugbank json files."
            DrugbankCaller.print_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "drugbank")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing Drugbank schema files."
            DrugbankCaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "drugbank")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into Drugbank json files."
            DrugbankCaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "drugbank")
        if operation == "extract_gene" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is extracting gene name from Drugbank json files."
            DrugbankCaller.extract_gene(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "drugbank")

    if data_set == "ClusterDrug":
        print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is processing ClusterDrug data."
        if operation == "print_json" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing ClusterDrug json files."
            ClusterDrugCaller.print_json(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clusterd")
        if operation == "print_schema" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is printing ClusterDrug schema files."
            ClusterDrugCaller.print_schema(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clusterd")
        if operation == "append_id" or operation == "all":
            print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is appending id into ClusterDrug json files."
            ClusterDrugCaller.append_id(workspace, data_set)
            PBSTracker.trackPBSQueue(1, "clusterd")

    print datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": System is done."

