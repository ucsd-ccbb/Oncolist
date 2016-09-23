#!/bin/bash

# loads the genemania identifier lookup and network databases

source $( dirname "${BASH_SOURCE[0]}" )/setenv.sh
cd $TOP
python -m app.genemania --id

