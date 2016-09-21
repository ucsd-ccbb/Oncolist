#!/bin/bash

export PATH=/shared/workspace/SearchEngineProject/software/miniconda/bin:$PATH

disease_name=$1
operation=$2
s3_input_files_address=$3 
s3_output_files_address=$4
python_space="/shared/workspace/SearchEngineProject/codes"

nohup python -u $python_space/MainEntry.py \
GEO $disease_name $operation $s3_input_files_address $s3_output_files_address > \
$python_space/nohup.out &
