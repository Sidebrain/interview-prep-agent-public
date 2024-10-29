#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Consider a pipeline failed if any of the commands fail.
set -o pipefail
# Optionally, print each command before executing it for easier debugging.
set -x

# Define top-level variables
PROJECT_ID="audition-prod"
PROJECT_NAME="Audition's prod environment"
REGION="asia-south2"
REPO_NAME="docker-repo"

# Create firebase admin key certificate key
gcloud secrets create firebase-admin-credentials \
  --data-file=./../backend/secrets/firebase-admin-key.json

# Create backend secrets
echo -n "sk-svcacct-N01rxd0mhEUkLqDAjeP9_99WpG2UpvvRjJ4fKc_c913hZTCXyazW-NCy7lYhSjBXVaKefc4VrZ1_JJr4jT3BlbkFJLLLZmYkRj_UcW39LKnmpBoDprz79ao-VS3rhcjG7er0NX3c38xpGi41TrHTehi3hbu-zlX4CAsRhmXymwA" | \
  gcloud secrets create openai-api-key --date-file=-

echo -n "sk_test_51GnG2zAMWKJyocPO049kHadWpGhlnZlo7M8gO2fnVaPUc8dCc47OgWBg1mhXwgJ0OvCHoAAW69dqdo5SJNkycnzW0010qRbOtM" | \
  gcloud secrets create stripe-api-key --data-file=-

# there is an additional secret for client url, but I will instantiate that during run time 
# CLIENT_URL='will be set during runtime'


# Create frontend secrets
#
# BACKEND_URL=http://localhost:8000
# SERVER_LOG_LEVEL=debug
# NEXT_PUBLIC_CLIENT_LOG_LEVEL=debug
# NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/websocket/ws
# NEXT_PUBLIC_WS_URL_V2=ws://localhost:8000/api/v2/websocket/ws

