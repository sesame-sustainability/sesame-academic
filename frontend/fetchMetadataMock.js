// fetch metadata and save to a mock
// in order to automatically generate types

const fs = require("fs");
const fetch = require("node-fetch");

(async () => {
  const response = await fetch("http://127.0.0.1:5000/pathway/metadata");
  const lcaResponse = await fetch("http://127.0.0.1:5000/lca/metadata");
  const teaResponse = await fetch("http://127.0.0.1:5000/tea/metadata");

  const { stages, links } = await response.json();
  const { indicators } = await lcaResponse.json();
  const { analyses } = await teaResponse.json();

  // manually write the fetched metadata to a file
  const file = fs.createWriteStream("__tests__/config/metadataMock.ts");

  // links
  file.write("export const links: Link[] = [");
  for (const [start, end] of links) {
    const item = { node: { start, end, id: `${start}-${end}` } };
    file.write(JSON.stringify(item));
    file.write(",");
  }
  file.write("];");

  // stages
  file.write("export const stages: Stage[] = [");
  for (const { activities, categories, name, id } of stages) {
    // options must be cast as strings since
    // the GraphQL spec does not support union scalar types:
    // https://github.com/graphql/graphql-spec/issues/215
    const newActivities = activities.map((a) => ({
      ...a,
      sources: a.sources.map((s) => ({
        ...s,
        user_inputs: s.user_inputs.map((u) => ({
          ...u,
          options: u.options ? u.options.map((o) => ({ ...o, value: o.value.toString() })) : undefined,
          // if the second arg in a conditional is not an array, return it in an array
          conditionals:
            u.conditionals.length > 0
              ? u.conditionals.map(({ args, ...rest }) => ({
                  ...rest,
                  args: [
                    [args[0]],
                    Array.isArray(args[1]) ? args[1] : [args[1]],
                  ],
                }))
              : [],
        })),
      })),
    }));

    const item = { node: { id, name, activities: newActivities, categories } };
    file.write(JSON.stringify(item));
    file.write(",");
  }
  file.write("];");

  // lca metadata
  file.write("export const indicators: LCAIndicator[] = [");
  for (const { label, value } of indicators) {
    file.write(JSON.stringify({ label, value, id: `${value}-${label}` }));
    file.write(",");
  }
  file.write("];");

  // tea metadata
  file.write("export const analyses: TEAAnalysis[] = [");
  for (const { name, pathway_id, user_inputs } of analyses) {
    file.write(
      JSON.stringify({
        analysis: {
          name,
          pathway_id,
          user_inputs,
        },
        id: `${pathway_id.join("-")}`,
      })
    );
    file.write(",");
  }
  file.write("];");

  // close the stream
  file.end();
})();
