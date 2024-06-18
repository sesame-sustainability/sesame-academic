const activeEnv =
  process.env.GATSBY_ACTIVE_ENV || process.env.NODE_ENV || "development";

// set source version via build script to get short commit hash
const sourceVersion = process.env.RESOLVED_SOURCE_VERSION || "main";

const { dashboardLastBuilt } = require("./dashboardLastBuilt");

console.log(`Using environment config: '${activeEnv}'`);

require("dotenv").config({
  path: `.env.${activeEnv}`,
});

// for local development, we fall back to sesame.mit.edu
const siteUrl = new URL(process.env.WEBSITE_URL || "https://sesame.mit.edu");

const config = {
  flags: {
    FAST_DEV: true,
    DEV_SSR: true,
  },
  siteMetadata: {
    title: `SESAME`,
    siteUrl: siteUrl.href.slice(0, -1),
    lastUpdated: dashboardLastBuilt,
  },
  plugins: [
    `gatsby-source-sesame-metadata`,
    `gatsby-plugin-emotion`,
    `gatsby-plugin-react-helmet`,
    `gatsby-plugin-anchor-links`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
    },
    {
      resolve: `gatsby-plugin-posthog`,
      options: {
        apiKey: "phc_4vZhb7KXnyZMcUGQXu2gNc18rzvWQN4nEwSEzHK0ksE",
      },
    },
    `gatsby-plugin-image`,
    `gatsby-plugin-sharp`,
    `gatsby-transformer-sharp`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `data`,
        path: `${__dirname}/src/data`,
      },
    },
    `gatsby-transformer-csv`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-typescript`,
    `gatsby-plugin-postcss`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-plugin-mailchimp`,
      options: {
        endpoint: `https://mit.us4.list-manage.com/subscribe/post?u=1a57a715520513505ca5cda89&id=eb3c6d9c51`,
      },
    },
    {
      resolve: `gatsby-plugin-create-client-paths`,
      options: { prefixes: [`/app/*`] },
    },
    {
      resolve: `gatsby-plugin-sitemap`,
    },
    `gatsby-plugin-remove-serviceworker`,
  ],
};

if (activeEnv !== "development") {
  const s3Config = {
    resolve: `gatsby-plugin-s3`,
    options: {
      bucketName: process.env.S3_BUCKET_NAME || "no-bucket",
      protocol: siteUrl.protocol.slice(0, -1),
      hostname: siteUrl.hostname,
      generateRoutingRules: false,
      generateRedirectObjectsForPermanentRedirects: false,
    },
  };
  const canonicalConfig = {
    resolve: `gatsby-plugin-react-helmet-canonical-urls`,
    options: {
      siteUrl: siteUrl.href.slice(0, -1),
    },
  };
  const sentryConfig = {
    resolve: `@sentry/gatsby`,
    options: {
      dsn: process.env.SENTRY_INGEST_URL,
      tracesSampleRate: 0.7,
      environment: activeEnv,
      release: sourceVersion,
    },
  };

  console.log(`Deploying source version: '${sourceVersion}'`);
  config.plugins.push(s3Config);
  config.plugins.push(canonicalConfig);
  config.plugins.push(sentryConfig);
}

module.exports = config;
