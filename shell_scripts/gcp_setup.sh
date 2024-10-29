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

# Create a new project
# gcloud config projects create "$PROJECT_ID" --name="$PROJECT_NAME"

# Set the project
gcloud config set project "$PROJECT_ID"

# Enable necessary APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com \
  artifactregistry.googleapis.com

# Create an artifact registry
gcloud artifacts repositories create "$REPO_NAME" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Docker repository for audition"

# Configure Docker to use the artifact registry
gcloud auth configure-docker "$REGION-docker.pkg.dev"h
