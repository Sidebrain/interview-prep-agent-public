#!/bin/bash

# Check if a directory is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

DIRECTORY="$1"

# Initialize an empty variable to store formatted content
OUTPUT=""

# Iterate over all .py files in the specified directory
for FILE in "$DIRECTORY"/*.py; do
  if [ -f "$FILE" ]; then
    FILENAME=$(basename "$FILE")
    CONTENT=$(cat "$FILE")
    OUTPUT+="\`\`\`python\n$FILENAME\n$CONTENT\n\`\`\`\n\n"
  fi
done

# Copy the result to the clipboard using pbcopy
echo -e "$OUTPUT" | pbcopy

echo "Python files copied to clipboard!"
