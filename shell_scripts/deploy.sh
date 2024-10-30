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

# Deploy frontend inside a subshell
(
  echo "deplying frontend"
  cd ./frontend 
  gcloud builds submit --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend" 
  gcloud run deploy frontend \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated
)

# Deploy backend
(
  echo "deplying backend"
  cd ./backend 
  gcloud builds submit --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend" 
  gcloud run deploy backend \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated
)

# backend and frontend urls
FRONTEND_URL=$(gcloud run services describe frontend --format='value(status.url)')
BACKEND_URL=$(gcloud run services describe backend --format='value(status.url)')
echo "frontend url: $FRONTEND_URL, backend url: $BACKEND_URL"

# Setting env variables 
echo "setting env variables"
# gcloud run services update frontend \
#   --set-env-vars "NEXT_PUBLIC_CLIENT_LOG_LEVEL=debug" \
#   --set-env-vars "NEXT_PUBLIC_WS_URL=ws:" \
#   --set-env-vars "NEXT_PUBLIC_WS_URL_V2=debug" \

# BACKEND_URL=http://localhost:8000
# SERVER_LOG_LEVEL=debug
# NEXT_PUBLIC_CLIENT_LOG_LEVEL=debug
# NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/websocket/ws
# NEXT_PUBLIC_WS_URL_V2=ws://localhost:8000/api/v2/websocket/ws

