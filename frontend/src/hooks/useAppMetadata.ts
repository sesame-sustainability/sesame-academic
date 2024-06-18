import { useStaticQuery, graphql } from "gatsby";

const useAppMetadata = (): {
  allStage: {
    edges: Stage[];
  };
  allLink: {
    edges: Link[];
  };
  allAnalysis: {
    nodes: TEAAnalysis[];
  };
  allIndicator: {
    nodes: LCAIndicator[];
  };
  allSystem: {
    nodes: PowerSystemAnalysis[];
  };
  fleet: {
    fleet: BasicModuleMetadata;
  };
  grid: {
    grid: GridMetadata;
  };
  pps: {
    pps: BasicModuleMetadata;
  };
  industryCement: {
    industryCement: BasicModuleMetadata;
  };
  industrySteel: {
    industrySteel: BasicModuleMetadata;
  };
  industryAluminum: {
    industryAluminum: BasicModuleMetadata;
  };
  industrialFleet: {
    industrialFleet: BasicModuleMetadata;
  };
} => {
  const {
    allStage,
    allLink,
    allAnalysis,
    allIndicator,
    allSystem,
    fleet,
    grid,
    pps,
    industryCement,
    industrySteel,
    industryAluminum,
    industrialFleet,
  }: {
    allStage: { edges: Stage[] };
    allLink: { edges: Link[] };
    allAnalysis: { nodes: TEAAnalysis[] };
    allIndicator: { nodes: LCAIndicator[] };
    allSystem: { nodes: PowerSystemAnalysis[] };
    fleet: { fleet: BasicModuleMetadata };
    grid: { grid: GridMetadata };
    pps: { pps: BasicModuleMetadata };
    industryCement: { industryCement: BasicModuleMetadata };
    industrySteel: { industrySteel: BasicModuleMetadata };
    industryAluminum: { industryAluminum: BasicModuleMetadata };
    industrialFleet: { industrialFleet: BasicModuleMetadata };
  } = useStaticQuery(graphql`
    query Metadata {
      allStage {
        edges {
          node {
            id
            name
            categories
            activities {
              category
              id
              name
              sources {
                id
                name
                user_inputs
                hash
                version
              }
              resources
              products
              product_types
            }
          }
        }
      }
      allLink {
        edges {
          node {
            start
            end
            id
          }
        }
      }
      allAnalysis {
        nodes {
          id
          analysis {
            name
            unit
            user_inputs
            hash
            version
            pathway_id
          }
        }
      }
      allIndicator {
        nodes {
          label
          value
          id
        }
      }
      allSystem {
        nodes {
          id
          system {
            name
            user_inputs
            hash
            axes {
              x
              y {
                name
                type
                label
                unit
              }
            }
          }
        }
      }
      fleet {
        fleet {
          user_inputs
          hash
          version
        }
      }
      grid {
        grid {
          user_inputs
          hash
          version
        }
      }
      pps {
        pps {
          user_inputs
          hash
          version
        }
      }
      industryCement {
        industryCement {
          user_inputs
          hash
          version
        }
      }
      industrySteel {
        industrySteel {
          user_inputs
          hash
          version
        }
      }
      industryAluminum {
        industryAluminum {
          user_inputs
          hash
          version
        }
      }
      industrialFleet {
        industrialFleet {
          user_inputs
          hash
          version
        }
      }
    }
  `);

  return {
    allStage,
    allLink,
    allAnalysis,
    allIndicator,
    allSystem,
    fleet,
    grid,
    pps,
    industryCement,
    industrySteel,
    industryAluminum,
    industrialFleet,
  };
};

export default useAppMetadata;
