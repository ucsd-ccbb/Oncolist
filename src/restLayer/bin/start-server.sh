#!/bin/bash

# start the web server
# you may specify the port as a command-line argument
# you will need to run this script as an administrator (sudo) to use the default port (80)

# FIXME: running this script as an administrator causes log files to be owned by an administrator, which will cause permission errors when running other scripts as a standard user

source $( dirname "${BASH_SOURCE[0]}" )/setenv.sh
cd $TOP
python -m app.api "$@"


