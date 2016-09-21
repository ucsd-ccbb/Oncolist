#!/bin/bash

# redirecting all output to a file
exec 1>>"search_engine.log"
exec 2>>"search_engine.error"

export PATH=/shared/workspace/SearchEngineProject/software/miniconda/bin:$PATH
export PYTHONPATH="/shared/workspace/SearchEngineProject/codes/"

python_space="/shared/workspace/SearchEngineProject/codes/Clinvar"

operation=$1
workspace=$2

if [ $operation == "parse" ]; then
        python $python_space/ClinvarParser.py $workspace
fi

if [ $operation == "print_json" ]; then
        java -jar $python_space/clinvar.jar $workspace
fi

if [ $operation == "print_schema" ]; then
  python $python_space/SchemaBuilder.py $2 $3
fi

if [ $operation == "append_id" ]; then
  python $python_space/IDAppender.py $2 $3
fi