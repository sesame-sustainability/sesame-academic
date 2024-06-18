#!/bin/bash

set -e
set -o pipefail

main() {
  if [ -d .git ]; then
    git checkout main
  fi

  S3_BUCKET_NAME=sesame-web
  API_URL=https://d234aluy00nb20.cloudfront.net
  WEBSITE_URL=https://sesame.mit.edu

  touch .env.production

  echo "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" >> .env.production
  echo "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" >> .env.production
  echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env.production
  echo "SENTRY_INGEST_URL=${SENTRY_INGEST_URL}" >> .env.production
  echo "SENTRY_AUTH_TOKEN=${SENTRY_AUTH_TOKEN}" >> .env.production
  echo "SENTRY_ORG=${SENTRY_ORG}" >> .env.production
  echo "API_URL=${API_URL}" >> .env.production
  echo "WEBSITE_URL=${WEBSITE_URL}" >> .env.production
  echo "DISTRIBUTION_ID=${DISTRIBUTION_ID}" >> .env.production

  npm run clean
  npm run deploy:prod-and-invalidate
}

main;
