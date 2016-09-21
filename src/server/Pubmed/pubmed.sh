#!/bin/bash

# redirecting all output to a file
exec 1>>"search_engine.log"
exec 2>>"search_engine.error"

export PATH=/shared/workspace/SearchEngineProject/software/miniconda/bin:$PATH
export PYTHONPATH="/shared/workspace/SearchEngineProject/codes/"

python_space="/shared/workspace/SearchEngineProject/codes/Pubmed"

operation=$1
workspace=$2
begin=$3
end=$4

if [ $operation == "download" ]; then
        python $python_space/PubmedDownloader.py $workspace $begin $end
fi

if [ $operation == "print_json" ]; then
        python $python_space/JSONBuilder.py $workspace
fi

if [ $operation == "print_label" ]; then
        python $python_space/AuthorPrinter.py $workspace
fi

if [ $operation == "print_edge" ]; then
        python $python_space/EdgeBuilder.py $workspace
fi

if [ $operation == "print_schema" ]; then
  python $python_space/SchemaBuilder.py $2 $3
fi

if [ $operation == "append_id" ]; then
  python $python_space/IDAppender.py $2 $3
fi