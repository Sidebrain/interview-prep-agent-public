#!/bin/bash

# Check if a commit hash is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <commit-hash>"
  exit 1
fi

# Get the commit hash from the first argument
start_hash=$1

# Fetch all commits starting from the specified hash (inclusive)
commit_messages=$(git log --pretty=format:"%B" "$start_hash^..HEAD")

# Initialize variables
concatenated_messages=""
commit_index=1

# Loop through each commit message (split by NULL delimiter %x00)
IFS=$'\0'
for commit_message in $commit_messages; do
  # Append the commit message with a dynamic delimiter
  echo "-----------------------"
  echo "$commit_message"
  concatenated_messages+="---- commit $commit_index ----"$'\n'
  concatenated_messages+="$commit_message"$'\n\n'
  ((commit_index++))
done

# Output the concatenated commit messages
echo "$concatenated_messages"
