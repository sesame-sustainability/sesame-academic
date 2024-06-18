const axios = require(`axios`);

exports.createSchemaCustomization = ({ actions }) => {
  const { createTypes } = actions
  const typeDefs = `

    type Tooltip {
      content: String
      source: String
      source_link: String
    }

    type stageActivitiesSources {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type analysisAnalysis {
      user_inputs: JSON
      pathway_id: JSON
      hash: String
      version: Int
    }

    type systemSystem {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type fleetFleet  {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type gridGrid {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type ppsPps {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type industryCementIndustryCement {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type industrySteelIndustrySteel {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type industryAluminumIndustryAluminum {
      user_inputs: JSON
      hash: String
      version: Int
    }

    type industrialFleetIndustrialFleet {
      user_inputs: JSON
      hash: String
      version: Int
    }
  `
  createTypes(typeDefs)
}

exports.sourceNodes = async ({
  actions,
  createNodeId,
  createContentDigest,
  reporter,
}) => {
  const { createNode } = actions;
  const { API_URL } = process.env;

  const activity = reporter.activityTimer(`fetching SESAME metadata`);
  activity.start();

  const { data, status } = await axios({ url: `${API_URL}/pathway/metadata` });

  const { data: lcaData, status: lcaStatus } = await axios({
    url: `${API_URL}/lca/metadata`,
  });
  const { data: teaData, status: teaStatus } = await axios({
    url: `${API_URL}/tea/metadata`,
  });
  const { data: powerSystemData, status: powerSystemStatus } = await axios({
    url: `${API_URL}/power_historic/metadata`,
  });
  // new DRYer way of getting metadata (see bottom for createNode)
  const fleetResponse = await axios({
    url: `${API_URL}/fleet/metadata`
  });
  const gridResponse = await axios({
    url: `${API_URL}/grid/metadata`
  });
  const ppsResponse = await axios({
    url: `${API_URL}/pps/metadata`
  });
  const industryCementResponse = await axios({
    url: `${API_URL}/industry/cement/metadata`
  });
  const industrySteelResponse = await axios({
    url: `${API_URL}/industry/steel/metadata`
  });
  const industryAluminumResponse = await axios({
    url: `${API_URL}/industry/aluminum/metadata`
  })
  const industrialFleetResponse = await axios({
    url: `${API_URL}/industry/fleet/metadata`
  });
  // const { data: fleetData, status: fleetStatus } = await axios({
  //   url: `${API_URL}/fleet/metadata`,
  // });

  console.log(fleetResponse)

  const mapConditionals = (conditionals) => {
    // if the second arg in a conditional is not an array, return it in an array
    return conditionals.length > 0
      ? conditionals.map(({ args, ...rest }) => ({
          ...rest,
          args: [[args[0]], Array.isArray(args[1]) ? args[1] : [args[1]]],
        }))
      : [];
  };

  const mapUserInputs = (u) => ({
    ...u,
    options: u.options
      ? u.options.map(({ value, conditionals }) => ({
          // toString() all options (string | number)...
          // since the GraphQL spec does not support union scalar types:
          // https://github.com/graphql/graphql-spec/issues/215
          value: value.toString(),
          conditionals: mapConditionals(conditionals),
        }))
      : undefined,
    conditionals: mapConditionals(u.conditionals),
  });

  // Create pathway metadata nodes
  if (status !== 200) {
    reporter.panic(
      `gatsby-source-sesame-metadata: pathway metadata API call failed`
    );
  } else {
    for (const tuple of data.links) {
      const [start, end] = tuple;
      const name = `${start}_${end}`;
      createNode({
        start,
        end,
        id: createNodeId(`link-${name}`),
        internal: {
          type: `link`,
          contentDigest: createContentDigest({ start, end }),
        },
      });
    }
    for (const stage of data.stages) {
      const activities = stage.activities.map((a) => {
        return {
          ...a,
          sources: a.sources.map((s) => ({
            ...s,
            user_inputs: s.user_inputs.map(mapUserInputs),
          })),
        };
      });

      createNode({
        name: stage.name,
        activities,
        categories: stage.categories,
        id: createNodeId(`stage-${stage.id}`),
        parent: null,
        children: [],
        internal: {
          type: `stage`,
          contentDigest: createContentDigest({ ...stage, activities }),
        },
      });
    }
  }

  // Create LCA metadata nodes
  if (lcaStatus !== 200) {
    reporter.panic(
      `gatsby-source-sesame-metadata: LCA metadata API call failed`
    );
  } else {
    for (const { label, value } of lcaData.indicators) {
      createNode({
        label,
        value,
        id: createNodeId(`indicator-${value}`),
        internal: {
          type: `indicator`,
          contentDigest: createContentDigest({ label, value }),
        },
      });
    }
  }

  // Create TEA metadata nodes
  if (teaStatus !== 200) {
    reporter.panic(
      `gatsby-source-sesame-metadata: TEA metadata API call failed`
    );
  } else {
    for (const analysis of teaData.analyses) {
      createNode({
        analysis: {
          ...analysis,
          user_inputs: analysis.user_inputs.map(mapUserInputs),
        },
        id: createNodeId(`analysis-${analysis.name}`),
        internal: {
          type: `analysis`,
          contentDigest: createContentDigest(analysis),
        },
      });
    }
  }

  // Create power system metadata nodes
  if (powerSystemStatus !== 200) {
    reporter.panic(
      `gatsby-source-sesame-metadata: Power system metadata API call failed`
    );
  } else {
    for (const system of powerSystemData.analyses) {
      createNode({
        system: {
          ...system,
          user_inputs: system.user_inputs.map(mapUserInputs),
        },
        id: createNodeId(`system-${system.name}`),
        internal: {
          type: `system`,
          contentDigest: createContentDigest(system),
        },
      });
    }
  }

  // Create Fleet metadata nodes
  // if (fleetStatus !== 200) {
  //   reporter.panic(
  //     `gatsby-source-sesame-metadata: Fleet metadata API call failed`
  //   );
  // } else {
  //   createNode({
  //     fleet: {
  //       ...fleetData,
  //       user_inputs: fleetData.user_inputs.map(mapUserInputs),
  //     },
  //     id: createNodeId("fleetMetadata"),
  //     internal: {
  //       type: `fleet`,
  //       contentDigest: createContentDigest(fleetData),
  //     },
  //   });
  // }

  const moduleMetadataNodesToCreate = [
    {
      moduleName: 'fleet',
      response: fleetResponse,
    },
    {
      moduleName: 'grid',
      response: gridResponse,
    },
    {
      moduleName: 'pps',
      response: ppsResponse,
    },
    {
      moduleName: 'industryCement',
      response: industryCementResponse,
    },
    {
      moduleName: 'industrySteel',
      response: industrySteelResponse,
    },
    {
      moduleName: 'industryAluminum',
      response: industryAluminumResponse,
    },
    {
      moduleName: 'industrialFleet',
      response: industrialFleetResponse,
    }
  ];

  moduleMetadataNodesToCreate.forEach(({moduleName, response}) => {
    const { data, status } = response;
    // const { data, status } = await axios({
    //   url: `${API_URL}${apiEndpoint}`
    // });
    console.log(moduleName, status)
    // Create grid metadata nodes
    if (status !== 200) {
      reporter.panic(
        `gatsby-source-sesame-metadata: ${moduleName} metadata API call failed`
      );
    } else {
      createNode({
        [moduleName]: {
          ...data,
          user_inputs: data.user_inputs?.map(mapUserInputs),
        },
        id: createNodeId(`${moduleName}Metadata`),
        internal: {
          type: moduleName,
          contentDigest: createContentDigest(data),
        },
      });
    }
  })

  activity.end();
  return;
};
