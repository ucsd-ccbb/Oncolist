#!/bin/bash

# loads TCGA networks (see app.tcga.py for usage)

source $( dirname "${BASH_SOURCE[0]}" )/setenv.sh
cd $TOP
python -m app.tcga "$@"

