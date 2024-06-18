#!/bin/bash

set -e
set -o pipefail

BASE=https://github.mit.edu
AUTH_HEADER="Authorization: token ${GITHUB_TOKEN}"
HEADER="Accept: application/vnd.github.v3+json"
HEADER="${HEADER}; application/vnd.github.antiope-preview+json; application/vnd.github.shadow-cat-preview+json"

# URLs
REPO_URL="${BASE}/api/v3/repos/${GITHUB_REPOSITORY}"
PULLS_URL="${REPO_URL}/pulls"

main() {
  currentDate=`date +%b-%d-%Y`

  # configure git
  git config --global push.default current
  git config --global user.email "github@bellisar.io"
  git config --global user.name "Alessia Bellisario"


  # checkout new branch
  BRANCH="main"
  git checkout "${BRANCH}"

  # run update:csvs
  npm run update:csvs

  # if the branch is dirty
  # 1. update the dashboardLastBuilt date in the repository
  # 2. commit changes
  # 3. push to main branch
  # 4. deploy to production and invalidate CDN

  if ! [ -z "$(git status --porcelain)" ]; then
    # Uncommitted changes
    # update the "last updated" date
    rm dashboardLastBuilt.js
    touch dashboardLastBuilt.js
    echo "module.exports.dashboardLastBuilt = \"${currentDate}\";" >> dashboardLastBuilt.js

    # commit the changes
    git add .
    git commit -m "Updates dashboard for ${currentDate}"

    git push "https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.mit.edu/${GITHUB_REPOSITORY}.git" "${BRANCH}"

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
  fi
}

main;
