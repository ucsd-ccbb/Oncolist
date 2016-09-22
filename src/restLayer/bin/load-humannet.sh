#!/bin/bash

# loads the humannet database

source $( dirname "${BASH_SOURCE[0]}" )/setenv.sh
cd $TOP
python -m app.humannet "$@"

