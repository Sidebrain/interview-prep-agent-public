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
DEPLOY_REGION="us-east1"

# Create backend cloudbuild.yaml if it doesn't exist
cat > ./backend/cloudbuild.yaml << EOF
steps:
  # Pull the previous image for caching
  - name: 'gcr.io/cloud-builders/docker'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        docker pull $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest || exit 0
  
  # Build with cache
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest',
      '--cache-from', '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest',
      '.'
    ]
  
  # Push the image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest']

images:
  - '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest'

options:
  machineType: 'E2_HIGHCPU_8'
EOF

# Deploy backend
(
  echo "deploying backend"
  cd ./backend 
  gcloud builds submit --config=cloudbuild.yaml
  gcloud run deploy backend \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:latest" \
    --platform managed \
    --region "$DEPLOY_REGION" \
    --allow-unauthenticated \
    --set-secrets "OPENAI_API_KEY=openai_api_key:latest,STRIPE_API_KEY=stripe_api_key:latest" \
    --set-secrets "/app/secrets/firebase-admin-key.json=firebase-admin-credentials:latest" \
    --set-env-vars "FIREBASE_ADMIN_CREDENTIALS=/app/secrets/firebase-admin-key.json"
)

# Get backend URL and transform it for websockets
BACKEND_URL=$(gcloud run services describe backend --format='value(status.url)' --region "$DEPLOY_REGION")
# Transform http:// to ws:// for websocket URLs
WS_URL="${BACKEND_URL/https:/wss:}/api/v1/websocket/ws"
WS_URL_V2="${BACKEND_URL/https:/wss:}/api/v2/websocket/ws"

# Create frontend cloudbuild.yaml if it doesn't exist
cat > ./frontend/cloudbuild.yaml << EOF
steps:
  # Pull the previous image for caching
  - name: 'gcr.io/cloud-builders/docker'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        docker pull $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest || exit 0
  
  # Build with cache
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest',
      '--cache-from', '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest',
      '--build-arg', 'NEXT_PUBLIC_WS_URL=$WS_URL',
      '--build-arg', 'NEXT_PUBLIC_WS_URL_V2=$WS_URL_V2',
      '--build-arg', 'NEXT_PUBLIC_CLIENT_LOG_LEVEL=debug',
      '--build-arg', 'BACKEND_URL=$BACKEND_URL',
      '.'
    ]
  
  # Push the image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest']

images:
  - '$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest'

options:
  machineType: 'E2_HIGHCPU_8'
EOF

# Deploy frontend inside a subshell
(
  echo "deploying frontend"
  cd ./frontend 
  gcloud builds submit --config=cloudbuild.yaml
  gcloud run deploy frontend \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:latest" \
    --platform managed \
    --region "$DEPLOY_REGION" \
    --allow-unauthenticated \
    --set-env-vars "BACKEND_URL=$BACKEND_URL,\
SERVER_LOG_LEVEL=debug,\
NEXT_PUBLIC_CLIENT_LOG_LEVEL=debug,\
NEXT_PUBLIC_WS_URL=$WS_URL,\
NEXT_PUBLIC_WS_URL_V2=$WS_URL_V2"
)

# frontend url
FRONTEND_URL=$(gcloud run services describe frontend --format='value(status.url)' --region "$DEPLOY_REGION")

# updating the backend with the client url
gcloud run services update backend \
  --region "$DEPLOY_REGION" \
  --set-env-vars "CLIENT_URL=$FRONTEND_URL"

# Print all URLs for verification
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo "Websocket URL v1: $WS_URL"
echo "Websocket URL v2: $WS_URL_V2"
