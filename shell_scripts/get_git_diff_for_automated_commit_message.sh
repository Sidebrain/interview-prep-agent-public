#!/usr/bin/env bash

echo "### DIFF ###" > commit_details.txt
git diff --cached >> commit_details.txt
echo "### FILE CONTENTS ###" >> commit_details.txt
for file in $(git diff --cached --name-only); do
  echo "### $file ###" >> commit_details.txt
  cat "$file" >> commit_details.txt
  echo "\n" >> commit_details.txt
done
