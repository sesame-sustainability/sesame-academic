<div align="center">
  <h1>SESAME Web Front-End</h1>
</div>

<h2>Build Statuses</h2>
<table>
  <th>
    <td>
      <b>Build + Test (<code>main</code>)</b>
    </td>
    <td>
      <b>Auto-Deploy (<code>main</code>)</b>
    </td>
    <td>
      <b>Daily Dashboard Update Cron</b>
    </td>
  </th>
  <tr>
    <td><b>Status</b></td>
    <td style="text-align: center;">
      <a href="https://console.aws.amazon.com/codesuite/codebuild/408114791087/projects/sesame-web/history?region=us-east-1&builds-meta=%7B%22f%22%3A%7B%22text%22%3A%22%22%7D%2C%22s%22%3A%7B%7D%2C%22n%22%3A20%2C%22i%22%3A0%7D" title="AWS Build Status: sesame-web"><img src="https://sesame-web-build-badges-badges-images-prod.s3.amazonaws.com/sesame-web.svg"/></a>
    </td>
    <td style="text-align: center;">
      <a href="https://console.aws.amazon.com/codesuite/codebuild/408114791087/projects/sesame-web-deploybot/history?region=us-east-1&builds-meta=%7B%22f%22%3A%7B%22text%22%3A%22%22%7D%2C%22s%22%3A%7B%7D%2C%22n%22%3A20%2C%22i%22%3A0%7D" title="AWS Build Status: sesame-web-deploybot"><img src="https://sesame-web-build-badges-badges-images-prod.s3.amazonaws.com/sesame-web-deploybot.svg"/></a>
    </td>
    <td style="text-align: center;">
      <a href="https://console.aws.amazon.com/codesuite/codebuild/408114791087/projects/sesame-web-cron/history?region=us-east-1&builds-meta=%7B%22f%22%3A%7B%22text%22%3A%22%22%7D%2C%22s%22%3A%7B%7D%2C%22n%22%3A20%2C%22i%22%3A0%7D" title="AWS Build Status: sesame-web-cron"><img src="https://sesame-web-build-badges-badges-images-prod.s3.amazonaws.com/sesame-web-cron.svg"/></a>
    </td>
  </tr>
</table>
<br />

The front-end web interface for the SESAME project. Built with:

- [Gatsby](https://www.gatsbyjs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [TailwindCSS](https://tailwindcss.com/) + [TailwindUI](https://tailwindui.com) + [Emotion](https://emotion.sh/docs/introduction) + [twin.macro](https://github.com/ben-rogerson/twin.macro)
- [Cypress](https://www.cypress.io/) + [Testing Library](https://testing-library.com/)

## 1. Running the Site Locally

### 1.1 Local Development

In order to get the web front-end running locally:

1. **Clone this repository and run `npm i && cd plugins/gatsby-source-sesame-metadata && npm i && cd -` to install the project's dependencies.** You will then need to manually create three files containing environment variables—`.env.development`, `.env.staging` and `.env.production`—in the project root. (These files store secrets and are intentionally kept out of the repo's git history.)

2. **`.env.development` needs just one environment variable, `API_URL`** You can copy + paste the following, replacing the URL with the path to your local API server:

```
API_URL=http://127.0.0.1:5000
```

> **NB:** The secrets in `.env.development` are used any time the command `gatsby develop` is run, and the secrets in `.env.production` are used any time the command `gatsby build` is run.

3. **Run `npm start`.** This will trigger the command `gatsby develop` which is optimized for local development with hot reloading (the browser displays changes without the need to manually refresh the page). If the port is available, the site will run at at `http://localhost:8000/` by default, or the user will be asked to select a new port. Read the docs for `gatsby develop` [here](https://www.gatsbyjs.org/docs/gatsby-cli/#develop).

### 1.2 Production Bundles

`gatsby develop` uses `webpack-dev-server` under the hood which dynamically serves JavaScript optimized for development, but production Gatsby builds generate static assets, including server-rendered HTML. In order to test the production build, run `npm run build && npm run serve`. These commands will build the assets and serve them at `http://localhost:9000` by default. Read the docs for `gatsby build` [here](https://www.gatsbyjs.org/docs/gatsby-cli/#build) and `gatsby serve` [here](https://www.gatsbyjs.org/docs/gatsby-cli/#serve).

In order to build the production bundles, you will also need to have the file `.env.production` in the project root containing an `API_URL` as described in the previous step. This URL should point to the production API server.

## 2. Deploying

### 2.1 To Production

In order to deploy:

1. **Set seven environment variables in `.env.production` (a file you will need to create in the project root)**:
   1. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` represent the access key and secret for the Amazon user `sesame-web` which has appropriate permissions to upload to both `sesame-web` and `sesame-web-staging` buckets
   1. `S3_BUCKET_NAME=sesame-web` in order to deploy to the **production** bucket
   1. `API_URL=https://d234aluy00nb20.cloudfront.net` in order to point to the production API
   1. `WEBSITE_URL=https://sesame.mit.edu` in order to ensure [CloudFront redirects are configured properly](https://gatsby-plugin-s3.jari.io/recipes/with-cloudfront/)
   1. `SENTRY_ORG=sesame-s7` as well as `SENTRY_INGEST_URL` and `SENTRY_AUTH_TOKEN` (ask [Alessia](https://github.mit.edu/alessia-1) for these tokens) in order to log errors in Sentry
1. **Run `npm run deploy:prod`.** This command will run `npm run build` followed by the S3 deploy script using the variables in `.env.production`. The files in `/public` will be uploaded and can immediately be accessed at [https://sesame.mit.edu](https://sesame.mit.edu) which is pointing to the CloudFront CDN URL [https://du3n7r87naj55.cloudfront.net/](https://du3n7r87naj55.cloudfront.net/).

### 2.2 To Staging

1. **Set seven environment variables in `.env.staging` (a file you will need to create in the project root)**:
   - see the list of environment variables in 2.1
1. **Run `npm run deploy:staging`.** This command will run `npm run build` followed by the S3 deploy script using the variables in `.env.staging`. The files in `/public` will be uploaded and can immediately be accessed at [http://sesame-web-staging.s3-website.us-east-2.amazonaws.com/](http://sesame-web-staging.s3-website.us-east-2.amazonaws.com/) or at the CloudFront CDN URL [https://dlisf9whidv7c.cloudfront.net/](https://dlisf9whidv7c.cloudfront.net/).

## 3. Updating the COVID-19 Dashboard

There are a series of scripts in `/data-scripts` which both:

1. Asynchronously fetch the latest daily data of both **hourly EIA data** and **daily COVID-19 cases** via `downloadCovidData.js` and `downloadEIAData.js`.
2. Use these fetched CSVs which are stored in `/data-scripts/bulk-data` to generate smaller CSVs which are then saved in `/src/data`. At build time, Gatsby statically analyzes the files in `/src/data` which are detected using the [`gatsby-source-filesystem` plugin](https://github.mit.edu/sesame/sesame-web/blob/9fa1ee3f7cd3ccad1672ebe34d29d689041931b3/gatsby-config.js#L36) and consumed with `gatsby-transformer-csv` so they can then be accessed in pages or components via the GraphQL layer.

```
.
├── data-scripts
│   └── bulk-data <- where all bulk EIA930_BALANCE CSVs are stored + us-counties_historical
└── src
    └── data <- where the aggregated output of the data scripts are saved which are used to build the site
```

The script to perform both steps 1 & 2 can be manually run with `npm run update:csvs`, however, it automatically runs daily at 1AM EST. It is run via CloudBuild cron (bash script in `cron-job/update-dash.sh`) which fetches new data, updates the dashboard, deploys to staging and opens a PR which is automatically deployed to production upon being merged to `main` (bash script in `cron-job/deploy-on-merge.sh`).

### Updating the scripts annually

Every year, there are a few manual updates that need to be made to keep the scripts running smoothly:

- update `exports.datesToIgnore` and `exports.firstDates` in `data-scripts/constants.js`
- update the file names in `data-scripts/index.js`
- if it's a new year, update graph labels in `src/hooks/useDashboardData.ts`
- also for a new year, update the color map in `src/components/graphs/usDailyDemand.tsx`
- update `analysisYears` in `src/utils/constants.ts` and `AnalysisYearsTuple` in `types.d.ts`

## 4. Tests

### Cypress

End-to-end tests are written using Cypress, `@testing-library/cypress` and Axe.

### Local Development

Tests can be run while developing with `npm run test:e2e:local`: this runs the development server with HMR and uses `start-server-and-test` to start the dev server, wait and then run Cypress once the app has started up. Tests and test suites can be re-run against the newest changes as the developer is working.

### CI

On the CI, Cypress tests will run against a production build of the app, which hits the production API. It can be run with `npm run test:e2e:ci`.

## 5. Linting and Code Formatting

ESLint handles linting and formatting using Prettier and TypeScript plugins. Husky also runs the TypeScript compiler and ESLint via pre-commit hook. All files in `/src` can be formatted with the command `npm run format`.

## 6. Rendering User Inputs

There is a [custom hook](https://reactjs.org/docs/hooks-custom.html) in `/src/hooks/useUserInputs.ts` which accepts an array of `user_inputs` and returns a tuple of an `inputs` dictionary with values, error messages and an `isVisible` boolean for each field, and a `setInput` function for setting individual values.