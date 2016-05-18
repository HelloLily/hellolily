#!/bin/bash

# Check for eslint.
which eslint &> /dev/null
if [[ "$?" == 1 ]]; then
  echo "Please install eslint & eslint-plugin-html."
  exit 1
fi

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep ".js")

if [[ "$STAGED_FILES" = "" ]]; then
  echo "Proceed: no staged javascript files."
  exit 0
fi

PASS=true

echo "Validating Javascript:"

for FILE in $STAGED_FILES
do
  eslint "$FILE"

  if [[ "$?" == 0 ]]; then
    echo "ESLint Passed: $FILE"
  else
    echo "ESLint Failed: $FILE"
    PASS=false
  fi
done

if ! $PASS; then
  echo "Abort: Your commit contains files that don't pass ESLint. Please fix the ESLint errors and try again."
  exit 1
else
  echo "Proceed: success validating javascript files."
  exit 0
fi

exit $?
