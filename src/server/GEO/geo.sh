#!/bin/bash

# redirecting all output to a file
exec 1>>"search_engine.log"
exec 2>>"search_engine.error"

export PATH=/shared/workspace/SearchEngineProject/software/miniconda/bin:$PATH
export PYTHONPATH="/shared/workspace/SearchEngineProject/codes/"

python_space="/shared/workspace/SearchEngineProject/codes/GEO"

operation=$1

if [ $operation == "download" ]; then
  aws s3 cp $2 $3/$4 --recursive
fi

if [ $operation == "preprocess" ]; then
  python $python_space/Preprocess.py $2
fi

if [ $operation == "calculate" ]; then
  python $python_space/CorrelationCalculator.py $2 $3 $4 $5
fi

if [ $operation == "louvain_cluster" ]; then
  python $python_space/ClusterBuilder.py $2 $3 $4 $operation
fi

if [ $operation == "dedup_louvain_cluster" ]; then
  python $python_space/ClusterFilter.py $2 $3 $4
fi

if [ $operation == "oslom_cluster" ]; then
  python $python_space/ClusterBuilder.py $2 $3 $4 $operation
fi

if [ $operation == "print_star_json" ]; then
  python $python_space/StarJSONBuilder.py $2 $3 $4 $5
fi

if [ $operation == "print_louvain_cluster_json" ]; then
  python $python_space/ClusterJSONBuilder.py $2 $3 $4 $5 $operation
fi

if [ $operation == "print_oslom_cluster_json" ]; then
  python $python_space/ClusterJSONBuilder.py $2 $3 $4 $5 $operation
fi

if [ $operation == "print_schema" ]; then
  python $python_space/SchemaBuilder.py $2 $3
fi

if [ $operation == "append_id" ]; then
  python $python_space/IDAppender.py $2 $3
fi

if [ $operation == "upload" ]; then
  aws s3 cp $3 $2 --recursive
fi
