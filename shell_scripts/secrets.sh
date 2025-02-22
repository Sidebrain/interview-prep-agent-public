#!/usr/bin/env bash

echo -e "sk-svcacct-N01rxd0mhEUkLqDAjeP9_99WpG2UpvvRjJ4fKc_c913hZTCXyazW-NCy7lYhSjBXVaKefc4VrZ1_JJr4jT3BlbkFJLLLZmYkRj_UcW39LKnmpBoDprz79ao-VS3rhcjG7er0NX3c38xpGi41TrHTehi3hbu-zlX4CAsRhmXymwA" | tr -d '\n' | gcloud secrets versions add openai_api_key --data-file=- --project=audition-prod

echo "sk_test_51GnG2zAMWKJyocPO049kHadWpGhlnZlo7M8gO2fnVaPUc8dCc47OgWBg1mhXwgJ0OvCHoAAW69dqdo5SJNkycnzW0010qRbOtM"\
  | gcloud secrets versions add stripe_api_key --data-file=- --project=661221507813

# gcloud secrets create firebase-admin-credentials \
#   --data-file=./backend/secrets/firebase-admin-key.json
