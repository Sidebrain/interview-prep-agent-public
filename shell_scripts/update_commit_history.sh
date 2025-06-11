#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

{
  echo "# Project README"
  echo ""
  echo "## Detailed Git Log"
  echo "*Last updated: $(date +"%Y-%m-%d %H:%M:%S")*"
  echo ""

  # Use a custom format for each commit
  git log --pretty=format:"### Commit: %h%n**Author:** %an <%ae>%n**Date:** %ad%n%n> %s%n%n%b%n%n---%n"
} > COMMIT_HISTORY.md

# Stage the updated README.md so it’s included in your commit
git add COMMIT_HISTORY.md

exit 0
