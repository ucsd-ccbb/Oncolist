#!/bin/bash

# start the mongo database as a background process (daemon) and use the specified log file

source $( dirname "${BASH_SOURCE[0]}" )/setenv.sh
mongod --fork --logpath $TOP/logs/mongodb.log --logappend --dbpath /home/ec2-user/data/mongo