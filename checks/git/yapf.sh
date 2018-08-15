#!/bin/bash

# Check for yapf.
which yapf &> /dev/null
if [[ "$?" == 1 ]]; then
  echo "Please install yapf using pip install yapf"
  exit 1
fi

yapf --recursive --diff --parallel --exclude '**/migrations/*.py' ./lily/
