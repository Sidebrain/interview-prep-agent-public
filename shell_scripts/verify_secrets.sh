#!/usr/bin/env bash
set -e
set -o pipefail

PROJECT_ID="661221507813"

# Function to check if a secret exists and list its versions
check_secret() {
    local secret_name=$1
    echo "Checking secret: $secret_name"
    
    if gcloud secrets describe $secret_name --project=$PROJECT_ID 2>/dev/null; then
        echo "✅ Secret '$secret_name' exists"
        echo "Versions available:"
        gcloud secrets versions list $secret_name --project=$PROJECT_ID
    else
        echo "❌ Secret '$secret_name' not found"
    fi
    echo "----------------------------------------"
}

# List all available secrets
echo "Listing all secrets in project:"
gcloud secrets list --project=$PROJECT_ID

echo "\nChecking specific secrets:"
# Check each required secret
check_secret "openai_api_key"
check_secret "stripe_api_key"
check_secret "firebase-admin-credentials"

# Show secrets that need to be created
echo "\nMissing secrets that need to be created:"
for secret in "openai_api_key" "stripe_api_key" "firebase-admin-credentials"; do
    if ! gcloud secrets describe $secret --project=$PROJECT_ID &>/dev/null; then
        echo "- $secret"
    fi
done
