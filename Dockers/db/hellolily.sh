#!/bin/bash

echo "Grant hellolily access from all IPs."
echo "host all hellolily 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf

echo "Create a user and database."
gosu postgres postgres --single <<- EOSQL
    CREATE USER hellolily;
    CREATE DATABASE hellolily;
    GRANT ALL PRIVILEGES ON DATABASE hellolily TO hellolily;
    ALTER USER hellolily CREATEDB;
EOSQL

echo "Done initializing."
