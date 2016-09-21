#!/bin/bash

export PATH=/shared/workspace/SearchEngineProject/software/miniconda/bin:$PATH
export PYTHONPATH="/shared/workspace/SearchEngineProject/codes/"

# redirecting all output to a file
exec 1>>"search_engine.log"
exec 2>>"search_engine.error"

python_space="/shared/workspace/SearchEngineProject/codes/TCGA"

operation=$1
rootRawDir=$2
tumorType=$3
releaseYear=$4
releaseMonth=$5
releaseDay=$6

if [ $operation == "download" ]; then

  if [ ! -d $rootRawDir"/"$tumorType ]; then
    mkdir -p $rootRawDir"/"$tumorType
  fi

  ## Download clinical data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/"$tumorType

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"

  else
    wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" -P $rootRawDir"/"$tumorType
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Clinical_Pick_Tier1.Level_4."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz"

  fi

  ## Download SNP data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_snp__genome_wide_snp_6__broad_mit_edu__Level_3__segmented_scna_minus_germline_cnv_hg19__seg.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/"$tumorType

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_$tumorType.Merge_snp__genome_wide_snp_6__broad_mit_edu__Level_3__segmented_scna_minus_germline_cnv_hg19__seg.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_$tumorType.Merge_snp__genome_wide_snp_6__broad_mit_edu__Level_3__segmented_scna_minus_germline_cnv_hg19__seg.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_$tumorType.Merge_snp__genome_wide_snp_6__broad_mit_edu__Level_3__segmented_scna_minus_germline_cnv_hg19__seg.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download rnaSeq data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/"$tumorType

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  else
    ## Download rnaSeq data if when the first link does not work.
    wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" -P $rootRawDir"/"$tumorType

    if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" ]; then
      tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" -C $rootRawDir"/"$tumorType
      rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz"
    fi
  fi
  ## Download Mutation Calls data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download Mutation Oncotated Calls data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Oncotated_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Oncotated_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Oncotated_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Mutation_Packager_Oncotated_Calls.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download miRNASeq data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_mirnaseq__illuminahiseq_mirnaseq__bcgsc_ca__Level_3__miR_gene_expression__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download methylation27 data
  #wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation27__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation27__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation27__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation27__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download methylation450 data
  #wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation450__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation450__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation450__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm  $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_methylation__humanmethylation450__jhu_usc_edu__Level_3__within_bioassay_data_set_function__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download methylation data at gene level
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Methylation_Preprocess.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Methylation_Preprocess.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Methylation_Preprocess.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm  $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Methylation_Preprocess.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  fi

  ## Download rppa data
  wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -P $rootRawDir"/""$tumorType"

  if [ -f $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" ]; then
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.0.0.tar.gz"
  else
    wget http://gdac.broadinstitute.org/runs/stddata__"$releaseYear"_"$releaseMonth"_"$releaseDay"/data/"$tumorType"/"$releaseYear""$releaseMonth""$releaseDay"/gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" -P $rootRawDir"/""$tumorType"
    tar -zxvf $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz" -C $rootRawDir"/"$tumorType
    rm $rootRawDir"/"$tumorType"/"gdac.broadinstitute.org_"$tumorType".Merge_protein_exp__mda_rppa_core__mdanderson_org__Level_3__protein_normalization__data.Level_3."$releaseYear""$releaseMonth""$releaseDay""00.1.0.tar.gz"
  fi

fi

if [ $operation == "parse_mirna" ]; then
  python $python_space/MicroRNAParser.py $2 $3 $4 $5 $6 $7
fi

if [ $operation == "parse_rnaseq" ]; then
  python $python_space/RNASeqParser.py $2 $3 $4 $5 $6 $7
fi

if [ $operation == "parse_mutation" ]; then
  python $python_space/MutationParser.py $2 $3 $4 $5 $6 $7
fi

if [ $operation == "calculate" ]; then
  python $python_space/CorrelationCalculator.py $2 $3 $4 $5
fi

if [ $operation == "filter" ]; then
  python $python_space/CorrelationFilter.py $2 $3 $4
fi

if [ $operation == "louvain_cluster" ]; then
  python $python_space/ClusterBuilder.py $2 $3 $4 $operation
fi

if [ $operation == "dedup_louvain_cluster" ]; then
  python $python_space/ClusterFilter.py $2 $3 $4
fi

if [ $operation == "oslom_undirected_cluster" ]; then
  python $python_space/ClusterBuilder.py $2 $3 $4 $operation
fi

if [ $operation == "print_ivanovska_json" ]; then
  python $python_space/ClusterBuilder.py $2 $3 $4 $operation
fi

if [ $operation == "replace_cluster" ]; then
  python $python_space/ClusterReplacer.py $2 $3
fi

if [ $operation == "print_louvain_json" ]; then
  python $python_space/ClusterJSONBuilder.py $2 $3 $4 $5 $6 $7
fi

if [ $operation == "print_oslom_json" ]; then
  python $python_space/ClusterJSONBuilder.py $2 $3 $4 $5 $6 $7
fi

if [ $operation == "print_star_louvain_json" ]; then
  python $python_space/StarJSONBuilder.py $2 $3 $4
fi

if [ $operation == "print_cluster_ivanovska_json" ]; then
  python $python_space/IvanovskaJSONBuilder.py $2 $3 $4 $5 $6 $7
fi

if [ $operation == "print_label" ]; then
  python $python_space/LabelPrinter.py $2 $3 $4 $5
fi

if [ $operation == "print_schema" ]; then
  python $python_space/SchemaBuilder.py $2 $3
fi

if [ $operation == "append_id" ]; then
  python $python_space/IDAppender.py $2 $3
fi
