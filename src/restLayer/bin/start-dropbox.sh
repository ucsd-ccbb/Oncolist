#!/bin/bash

# starts the dropbox application as a standalone service
# dropbox is automatically started by the web server, so you shouldn't have to run this script unless you're debugging

source $( dirname "${BASH_SOURCE[0]}" )/setenv.sh
cd $TOP
python -m app.dropbox