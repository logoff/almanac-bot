#!/usr/bin/env bash
echo "Compiling..."
python -m compileall -f almanacbot -q
if [ $? -eq 0 ]
then
  echo "Compilation OK."
else
  exit -1
fi

echo "Checking style..."
pycodestyle almanacbot
if [ $? -eq 0 ]
then
  echo "Style  OK."
  exit 0
else
  exit -1
fi

