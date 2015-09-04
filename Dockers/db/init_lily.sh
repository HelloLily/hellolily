#!/bin/bash

echo "Grant hellolily access from all IPs."
echo "host all hellolily 0.0.0.0/0 trust" >> /var/lib/postgresql/data/pg_hba.conf

echo "Done initializing."
