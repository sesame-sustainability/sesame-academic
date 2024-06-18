#!/bin/bash

set -e
set -o pipefail

main() {
  if [ -d .git ]; then
    git checkout develop
  fi

  S3_BUCKET_NAME=sesame-web-staging
  API_URL=https://d23txx36opf6dg.cloudfront.net
  WEBSITE_URL=https://dlisf9whidv7c.cloudfront.net

  touch .env.staging

  echo "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" >> .env.staging
  echo "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" >> .env.staging
  echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}" >> .env.staging
  echo "SENTRY_INGEST_URL=${SENTRY_INGEST_URL}" >> .env.staging
  echo "SENTRY_AUTH_TOKEN=${SENTRY_AUTH_TOKEN}" >> .env.staging
  echo "SENTRY_ORG=${SENTRY_ORG}" >> .env.staging
  echo "API_URL=${API_URL}" >> .env.staging
  echo "WEBSITE_URL=${WEBSITE_URL}" >> .env.staging
  echo "DISTRIBUTION_ID=${DISTRIBUTION_ID}" >> .env.staging

  npm run clean
  npm run deploy:staging
}

main;
