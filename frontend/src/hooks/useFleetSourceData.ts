import { useStaticQuery, graphql } from "gatsby";

type AllFleetDataSources = {
  nodes: {
    Region: string;
    Source_1: string;
    Source_2: string;
    Source_3: string;
    Source_Description___click_for_URL_: string;
    Source__Abbreviation: string;
    Variable_Description: string;
    source_1_URL: string;
    source_2_URL: string;
    source_3_URL: string;
    source_description_URL: string;
  }[];
};

const useFleetSourceData = (): AllFleetDataSources["nodes"] => {
  const {
    allFleetSourceData: { nodes },
  }: {
    allFleetSourceData: AllFleetDataSources;
  } = useStaticQuery(graphql`
    query AllFleetDataSourcesCsv {
      allFleetSourceData: allFleetDataSourcesCsv {
        nodes {
          Region
          Source_1
          Source_2
          Source_3
          Source_Description___click_for_URL_
          Source__Abbreviation
          Variable_Description
          source_1_URL
          source_2_URL
          source_3_URL
          source_description_URL
        }
      }
    }
  `);
  return nodes;
};

export default useFleetSourceData;
