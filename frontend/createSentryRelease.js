const execSync = require("child_process").execSync;
const activeEnv = process.env.NODE_ENV;

console.log(
  `Creating Sentry release for ${process.env.RESOLVED_SOURCE_VERSION}...`
);

require("dotenv").config({
  path: `.env.${activeEnv}`,
});

if (activeEnv === "production") {
  // Create a release in Sentry
  execSync(
    `sentry-cli releases new -p gatsby ${process.env.RESOLVED_SOURCE_VERSION}`,
    { stdio: [0, 1, 2] }
  );

  // Associate commits with the release
  execSync(
    `sentry-cli releases set-commits --auto ${process.env.RESOLVED_SOURCE_VERSION}`,
    {
      stdio: [0, 1, 2],
    }
  );
}
