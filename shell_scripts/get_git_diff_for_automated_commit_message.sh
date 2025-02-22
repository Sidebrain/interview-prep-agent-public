#!/usr/bin/env bash

echo "### DIFF ###" > commit_details.txt
git diff --cached >> commit_details.txt
echo "### FILE CONTENTS ###" >> commit_details.txt
for file in $(git diff --cached --name-only); do
  echo "### $file ###" >> commit_details.txt
  if [ -f "$file" ]; then
    cat "$file" >> commit_details.txt
  else
    echo "File deleted" >> commit_details.txt
  fi
  echo "\n" >> commit_details.txt
done
