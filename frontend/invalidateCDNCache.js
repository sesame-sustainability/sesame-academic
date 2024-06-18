const execSync = require("child_process").execSync;
const activeEnv = process.env.NODE_ENV;

console.log(`Invalidating CDN for ${activeEnv} environment...`);

require("dotenv").config({
  path: `.env.${activeEnv}`,
});

execSync(
  `aws cloudfront create-invalidation --distribution-id ${process.env.DISTRIBUTION_ID} --paths "/*"`,
  { stdio: [0, 1, 2] }
);
