import React from "react";
import { graphql } from "gatsby";
import addToMailchimp from "gatsby-plugin-mailchimp";
import { Global } from "@emotion/react";
import tw, { styled, css } from "twin.macro";
import { GatsbyImage, IGatsbyImageData } from "gatsby-plugin-image";
import { LiteYouTubeEmbed } from "react-lite-youtube-embed";

import SEO from "../components/seo";

const CoreTeamMember = styled.a`
  filter: grayscale(100%);
  ${tw`transition ease-in-out duration-300 col-span-1 md:col-span-4 flex justify-center py-8 px-12 bg-gray-50 text-center hover:bg-blue-100`}
  transition : -webkit-filter 300ms linear;
  -webkit-transition: -webkit-filter 300ms linear;
  :hover {
    filter: none;
  }

  // center two items in bottom row
  @media (min-width: 768px) {
    :last-child:nth-of-type(3n - 1) {
      grid-column-end: -3;
    }

    :nth-last-of-type(2):nth-of-type(3n + 1) {
      grid-column-end: 7;
    }
  }
`;

type HeadshotImages =
  | "Amanda"
  | "Emre"
  | "Ian"
  | "Jenn"
  | "Jim"
  | "Maryam"
  | "Ragini"
  | "Sydney"
  | "Lingyan"
  | "Paul"
  | "Devin"
  | "Scott"
  | "screenshot";

type IndexImageData = {
  [key in HeadshotImages]: {
    childImageSharp: {
      gatsbyImageData: IGatsbyImageData;
    };
  };
};

const Homepage = ({
  data: imageData,
}: {
  data: IndexImageData;
}): JSX.Element => {
  const [email, setEmail] = React.useState<string>();
  const [mcResponse, setMcResponse] = React.useState<MailChimpResponse>();
  const handleSubmit = (
    e: React.FormEvent<HTMLFormElement>,
    userEmail?: string
  ) => {
    e.preventDefault();
    addToMailchimp(userEmail, { "group[13581][8]": "8" })
      .then((data: MailChimpResponse) => {
        setMcResponse(data);
      })
      .catch(() => {
        // unnecessary because MailChimp only ever returns a 200 status code
      });
  };

  return (
    <>
      <Global
        styles={css`
          .br-circle {
            border-radius: 50% !important;
          }

          form + div {
            a {
              ${tw`underline`}
            }
          }
        `}
      />
      <SEO />
      <div className="bg-white pb-8 2xl:py-12">
        <>
          <div className="pb-2 lg:pb-24 xl:pb-32 mt-10 mx-auto max-w-screen-xl px-4 sm:mt-12 sm:px-6 md:mt-22 xl:mt-24">
            <div className="lg:grid lg:grid-cols-12 lg:gap-8">
              <div className="sm:text-center md:max-w-3xl md:mx-auto lg:col-span-6 lg:text-left">
                <h1 className="mt-1 text-4xl tracking-tight leading-10 font-extrabold text-gray-900 sm:leading-none sm:text-6xl lg:text-5xl">
                  The global energy system is undergoing a{" "}
                  <br className="hidden md:inline" />
                  <span className="text-blue-600">major transformation.</span>
                </h1>
                <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                  In response, researchers at MIT have developed <b>SESAME</b>,
                  an online tool for evaluating the impacts of the global energy
                  system.
                </p>
                <div className="mt-5 sm:max-w-lg sm:mx-auto sm:text-center lg:text-left lg:mx-0">
                  <p className="text-base font-medium text-gray-900 lg:max-w-sm">
                    Sign up to become a beta user:
                  </p>
                  <form
                    onSubmit={(e) => handleSubmit(e, email)}
                    className="mt-3 sm:flex"
                  >
                    <input
                      type="email"
                      required
                      onChange={(e) => setEmail(e.target.value)}
                      aria-label="Email"
                      className="appearance-none block w-full px-3 py-3 border border-gray-400 text-base leading-6 rounded-md placeholder-gray-500 shadow-sm focus:outline-none focus:placeholder-gray-400 focus:shadow-outline focus:border-blue-300 transition duration-150 ease-in-out sm:flex-1"
                      placeholder="Enter your email"
                    />
                    <button
                      type="submit"
                      className="mt-3 w-full px-6 py-3 border border-transparent text-base leading-6 font-medium rounded-md text-white bg-gray-800 shadow-sm hover:bg-gray-700 focus:outline-none focus:shadow-outline active:bg-gray-900 transition duration-150 ease-in-out sm:mt-0 sm:ml-3 sm:flex-shrink-0 sm:inline-flex sm:items-center sm:w-auto"
                    >
                      Sign up
                    </button>
                  </form>
                  {mcResponse && mcResponse.result === "error" && (
                    <div
                      className="mt-4 text-red-800"
                      dangerouslySetInnerHTML={{ __html: mcResponse.msg }}
                    />
                  )}
                  {mcResponse && mcResponse.result === "success" && (
                    <div
                      className="mt-4 text-blue-800"
                      dangerouslySetInnerHTML={{ __html: mcResponse.msg }}
                    />
                  )}
                </div>
              </div>
              <div className="sm:mx-auto sm:max-w-3xl sm:px-6">
                <div className="py-12 sm:relative sm:mt-16 sm:py-16 lg:mt-24 lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
                  <div className="hidden sm:block">
                    <svg
                      className="absolute top-8 right-1/2 -mr-3 lg:m-0 lg:left-0"
                      width="404"
                      height="392"
                      fill="none"
                      viewBox="0 0 404 392"
                    >
                      <defs>
                        <pattern
                          id="837c3e70-6c3a-44e6-8854-cc48c737b659"
                          x="0"
                          y="0"
                          width="20"
                          height="20"
                          patternUnits="userSpaceOnUse"
                        >
                          <rect
                            x="0"
                            y="0"
                            width="4"
                            height="4"
                            className="text-gray-200"
                            fill="currentColor"
                          />
                        </pattern>
                      </defs>
                      <rect
                        width="404"
                        height="392"
                        fill="url(#837c3e70-6c3a-44e6-8854-cc48c737b659)"
                      />
                    </svg>
                  </div>
                  <div className="relative pl-4 sm:mx-auto sm:max-w-3xl sm:px-0 lg:max-w-none lg:h-full lg:pl-12">
                    <GatsbyImage
                      image={
                        imageData.screenshot.childImageSharp.gatsbyImageData
                      }
                      className="w-full rounded-md shadow-xl ring-1 ring-black ring-opacity-5 xl:w-auto lg:max-w-none 2xl:w-3/4"
                      alt="A screenshot of the SESAME web application"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      </div>
      <div className="py-12 2xl:py-16 bg-white" id="about">
        <div className="max-w-xl mx-auto px-4 sm:px-6 lg:max-w-screen-xl lg:px-8">
          <div className="lg:grid lg:grid-cols-3 lg:gap-8">
            <div>
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white">
                <svg
                  className="h-6 w-6"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                  />
                </svg>
              </div>
              <div className="mt-5">
                <h2 className="font-bold text-lg leading-6 text-gray-900">
                  The energy sector is transforming
                </h2>
                <p className="mt-2 text-base leading-6 text-gray-500">
                  One of the global community’s most significant contemporary
                  challenges is the need to satisfy growing energy demand while
                  simultaneously achieving very significant reductions in the
                  greenhouse gas emissions associated with the production,
                  delivery, and consumption of this energy.
                </p>
                <p className="mt-2 text-base leading-6 text-gray-500">
                  The energy sector is transforming via the convergence of
                  power, transportation, and industrial sectors and
                  inter-sectoral integration. To assess the level of
                  decarbonization achieved through this change, one needs to
                  study the carbon footprint of the energy system as a whole.
                </p>
              </div>
            </div>
            <div className="mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white">
                <svg
                  className="h-6 w-6"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
                  />
                </svg>
              </div>
              <div className="mt-5">
                <h2 className=" font-bold text-lg leading-6 text-gray-900">
                  A new tool for analysis
                </h2>
                <p className="mt-2 text-base leading-6 text-gray-500">
                  Sustainable Energy System Analysis Modelling Environment
                  (SESAME) is a novel, system-scale energy analysis tool to
                  assess the system-level greenhouse gas (GHG) emissions of
                  today’s changing energy system.
                </p>
                <p className="mt-2 text-base leading-6 text-gray-500">
                  The underlying analytic tool constitutes more than a thousand
                  individual energy pathways. SESAME, developed as a MATLAB
                  application, provides a consistent platform to estimate life
                  cycle GHG emissions of all stages of the energy sector.
                  Furthermore, the system representation is embedded into the
                  tool for power and transportation sectors.
                </p>
              </div>
            </div>
            <div className="mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white">
                <svg
                  className="h-6 w-6"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <div className="mt-5">
                <h2 className="font-bold text-lg leading-6 text-gray-900">
                  A rapidly evolving system
                </h2>
                <p className="mt-2 text-base leading-6 text-gray-500">
                  In the midst of the rapidly evolving energy system, making
                  informed decisions to properly shape this change requires
                  understanding the system and associated trade-offs. All of the
                  presented examples underline that GHG emissions are very
                  sensitive to energy choices and a comprehensive systems-level
                  analysis is essential for making informed decisions.
                </p>
                <p className="mt-2 text-base leading-6 text-gray-500">
                  The SESAME platform is developed to address this pressing need
                  and will continue to evolve to capture the emerging
                  complexities.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-gray-50">
        <div className="bg-gray-50 overflow-hidden">
          <div className="relative max-w-screen-xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
            <div className="relative lg:grid lg:grid-cols-3 lg:gap-x-8">
              <div className="lg:col-span-1">
                <h3 className="text-3xl leading-9 font-extrabold tracking-tight text-gray-900 sm:text-4xl sm:leading-10">
                  Videos
                </h3>
              </div>
              <div className="mt-10 sm:grid sm:grid-cols-2 sm:gap-x-8 sm:gap-y-10 lg:col-span-2 lg:mt-0">
                <div>
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <a
                        target="_blank"
                        rel="noopener noreferrer"
                        href="https://youtu.be/gZwrdoIpvuQ"
                      >
                        <b>
                          Forecasting emissions impacts of the evolving energy
                          system
                        </b>
                        <br />
                        Oil and Gas Climate Initiative (OGCI) webinar
                      </a>
                      <div
                        className="hidden md:block mt-4"
                        style={{ width: 560, height: 315 }}
                      >
                        <LiteYouTubeEmbed
                          id="gZwrdoIpvuQ"
                          title="Forecasting emissions impacts of the evolving energy
                          system - Oil and Gas Climate Initiative webinar"
                        />
                      </div>
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative lg:grid lg:grid-cols-3 lg:gap-x-8">
              <div className="lg:col-span-1"></div>
              <div className="mt-10 sm:grid sm:grid-cols-2 sm:gap-x-8 sm:gap-y-10 lg:col-span-2 lg:mt-0">
                <div>
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <a
                        target="_blank"
                        rel="noopener noreferrer"
                        href="https://youtu.be/7b463EJDGy8"
                      >
                        <b>
                          Understanding emissions impacts of the evolving energy
                          system
                        </b>
                        <br />
                        MITEI Low-Carbon Energy Center webinar
                      </a>
                      <div
                        className="hidden md:block mt-4"
                        style={{ width: 560, height: 315 }}
                      >
                        <LiteYouTubeEmbed
                          id="7b463EJDGy8"
                          title="Understanding emissions impacts of the evolving energy
                          system - MITEI Low-Carbon Energy Center webinar"
                        />
                      </div>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-gray-50 overflow-hidden">
          <div className="relative max-w-screen-xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
            <div className="relative lg:grid lg:grid-cols-3 lg:gap-x-8">
              <div className="lg:col-span-1">
                <h3 className="text-3xl leading-9 font-extrabold tracking-tight text-gray-900 sm:text-4xl sm:leading-10">
                  Papers
                </h3>
              </div>
              <div className="mt-10 sm:grid sm:grid-cols-2 sm:gap-x-8 sm:gap-y-10 lg:col-span-2 lg:mt-0">
                <div>
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <a
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline"
                        href="https://pubs.acs.org/doi/10.1021/acs.est.0c02312"
                      >
                        &quot;Hourly Power Grid Variations, Electric Vehicle
                        Charging Patterns, and Operating Emissions.&quot;
                      </a>{" "}
                      <em>Environmental Science & Technology</em>, 2020.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <a
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline"
                        href="https://doi.org/10.1016/j.apenergy.2020.115550"
                      >
                        &quot;Sustainable Energy System Analysis Modeling
                        Environment: Analyzing Life Cycle Emissions of the
                        Energy Transition.&quot;
                      </a>{" "}
                      <em>Applied Energy</em>, 2020.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <em>
                        Insights Into Future Mobility – A report from the
                        Mobility of the Future study
                      </em>
                      . MIT Energy Initiative, 2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      &quot;A Framework for Multi-level Life Cycle Analysis of
                      the Energy System.&quot;{" "}
                      <em>Computer Aided Process Engineering</em>, 2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      &quot;Modeling Impacts of Tracking on Greenhouse Gas
                      Emissions from Photovoltaic Power.&quot;{" "}
                      <em>Computer Aided Process Engineering</em>, 2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      &quot;Parametric modeling of life cycle greenhouse gas
                      emissions from photovoltaic power.&quot;{" "}
                      <em>Applied Energy</em>, 2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      &quot;A general model for estimating emissions from
                      integrated power generation and energy storage. Case
                      study: Integration of solar photovoltaic power and wind
                      power with batteries.&quot; <em>Processes</em>, 2018.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-gray-50 overflow-hidden">
          <div className="relative max-w-screen-xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
            <div className="relative lg:grid lg:grid-cols-3 lg:gap-x-8">
              <div className="lg:col-span-1">
                <h3 className="text-3xl leading-9 font-extrabold tracking-tight text-gray-900 sm:text-4xl sm:leading-10">
                  Conference talks
                </h3>
              </div>
              <div className="mt-10 sm:grid sm:grid-cols-2 sm:gap-x-8 sm:gap-y-10 lg:col-span-2 lg:mt-0">
                <div>
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      Multi-Level Life Cycle Analysis Tool for Sustainable
                      Energy Systems Modeling, AIChE Annual Meeting, Orlando,
                      FL, 2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      Modeling the Impact of Solar Tracking on Life Cycle
                      Greenhouse Gas Emissions from Photovoltaic Power, AIChE
                      Annual Meeting, Orlando, FL, 2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      SESAME: A Modular Technology Assessment Tool, Workshop on
                      Analytical Frameworks for Assessment of National Energy
                      Options, International Energy Agency Gas & Oil Technology
                      Collaboration Program, Paris, France, 10/30/2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      A Framework for Multi-level Life Cycle Analysis of the
                      Energy System, ESCAPE 29, Eindhoven, Netherlands,
                      06/17/2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      Modeling Impacts of Tracking on Greenhouse Gas Emissions
                      from Photovoltaic Power, ESCAPE 29, Eindhoven,
                      Netherlands, 06/18/2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <b>(Selected for spotlight presentations)</b> Integrated
                      Life Cycle Analysis and Multi-level Energy Systems
                      Modeling, SETAC Europe 29th Annual Meeting, Helsinki,
                      Finland, 05/29/2019.
                    </p>
                  </div>
                </div>
                <div className="mt-10 sm:mt-0">
                  <div className="mt-5">
                    <p className="mt-2 text-base leading-6 text-gray-500">
                      <a
                        className="underline"
                        href="https://ui.adsabs.harvard.edu/abs/2018AGUFM.A31M3101G/abstract"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        The Hidden Emissions Impact of Operational Variability
                        of Fossil Fuel Fired Power Plants
                      </a>
                      , American Geophysical Union Fall Meeting 2018,
                      Washington, DC, 12/11/2018.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white">
          <div className="max-w-screen-xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8">
            <h2
              id="team"
              className="text-center text-3xl leading-9 font-extrabold text-gray-900 sm:text-4xl sm:leading-10"
            >
              Core team
            </h2>

            <div className="mt-6 grid grid-cols-1 gap-0.5 md:grid-cols-12 lg:mt-8">
              {[
                {
                  name: 'Amanda Farnsworth',
                  title: 'Research Assistant',
                  url: "https://web.mit.edu/bin/cgicso?options=general&query=Amanda+Farnsworth",
                  image: imageData.Amanda.childImageSharp.gatsbyImageData,
                },
                {
                  name: 'Emre Gençer',
                  title: 'Principal Investigator & Research Scientist',
                  url: "http://energy.mit.edu/profile/emre-gencer/",
                  image: imageData.Emre.childImageSharp.gatsbyImageData,
                },
                {
                  name: 'Sydney Johnson',
                  title: 'Research Assistant',
                  url: "https://web.mit.edu/bin/cgicso?options=general&query=Sydney+Rose+Johnson",
                  image: imageData.Sydney.childImageSharp.gatsbyImageData,
                },
                {
                  name: 'Ian Miller',
                  title: 'Project Manager & Research Specialist',
                  url: "http://energy.mit.edu/profile/ian-miller/",
                  image: imageData.Ian.childImageSharp.gatsbyImageData,
                },
                {
                  name: 'Devin Mooers',
                  title: 'Lead Frontend Developer',
                  url: "https://www.devinmooers.com/",
                  image: imageData.Devin.childImageSharp.gatsbyImageData
                },
                {
                  name: 'Scott Nelson',
                  title: 'Lead Backend Developer',
                  url: 'https://www.linkedin.com/in/scttnlsn/',
                  image: imageData.Scott.childImageSharp.gatsbyImageData
                },
                {
                  name: 'Jim Owens',
                  title: 'Research Assistant',
                  url: "https://web.mit.edu/bin/cgicso?options=general&query=James+Thomas+Owens",
                  image: imageData.Jim.childImageSharp.gatsbyImageData,
                },
                {
                  name: 'Jenn Schlick',
                  title: 'Frontend Designer',
                  url: "https://www.linkedin.com/in/jennschlick/",
                  image: imageData.Jenn.childImageSharp.gatsbyImageData,
                },
                {
                  name: 'Paul Sizaire',
                  title: 'Research Assistant',
                  url: '',
                  image: imageData.Paul.childImageSharp.gatsbyImageData,
                },
              ].map(({name, title, url, image}) => (
                <CoreTeamMember
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  key={name}
                >
                  <div>
                    <GatsbyImage
                      image={image}
                      className="br-circle"
                      alt={`${name}, ${title}`}
                      style={{
                        marginLeft: "auto",
                        marginRight: "auto",
                        marginBottom: 10,
                      }}
                    />
                    <h3 className="text-lg font-semibold">{name}</h3>
                    <h4 style={{ maxWidth: "12rem" }}>{title}</h4>
                  </div>
                </CoreTeamMember>
              ))}
            </div>
          </div>
        </div>
        <div className="max-w-screen-xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8">
          <h2 className="text-center text-3xl leading-9 font-extrabold text-gray-900 sm:text-4xl sm:leading-10">
            Contributors
          </h2>
          <div className="mt-6 grid grid-cols-1 gap-0.5 md:grid-cols-3 lg:mt-8">
            <div className="mt-6 lg:mt-8 text-center">
              <h3 className="font-bold">Undergraduates</h3>
              <p>Tevita Akau</p>
              <p>Eva Anderson</p>
              <p>Patrick Callahan</p>
              <p>Patricia Chan</p>
              <p>Philip Desmond</p>
              <p>Allison Shepard</p>
              <p>Hilary Vogelbaum</p>
              <p>Brendan Wagner</p>
              <p>Kelly Wu</p>
            </div>
            <div className="mt-6 lg:mt-8 text-center">
              <h3 className="font-bold">Graduates and Postdocs</h3>
              <p>Lingyan Deng</p>
              <p>Seiji Engelkeimer</p>
              <p>Maria Etcheverry</p>
              <p>Drake Hernandez</p>
              <p>Mohammad Ostadi</p>
              <p>Devaki Sakhamuru</p>
              <p>Haoshui Yu</p>
            </div>
            <div className="mt-6 lg:mt-8 text-center">
              <div>
                <h3 className="font-bold">Alumni</h3>
                <p>Maryam Arbabzadeh</p>
                <p>Ragini Sreenath</p>
                <p>Alessia Bellisario</p>
                <p>Bentley Clinton</p>
                <p>Tapajyoti Ghosh</p>
                <p>Srujana Goteti</p>
                <p>Monica Hernato</p>
                <p>Emmanuel Kasseris</p>
                <p>Sapna Kumari</p>
                <p>Patricia Luna</p>
                <p>Justin Montgomery</p>
                <p>Omar Sabir</p>
                <p>Michael Schulthoff</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export const query = graphql`
  query Images {
    screenshot: file(relativePath: { eq: "sesame-screenshot-2022-03-12.png" }) {
      childImageSharp {
        gatsbyImageData(layout: FULL_WIDTH)
      }
    }
    Amanda: file(relativePath: { eq: "amanda-farnsworth.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Emre: file(relativePath: { eq: "emre-gencer.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Maryam: file(relativePath: { eq: "maryam-arbabzadeh.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Ian: file(relativePath: { eq: "ian-miller.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Jenn: file(relativePath: { eq: "jenn-schlick.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Jim: file(relativePath: { eq: "jim-owens.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Ragini: file(relativePath: { eq: "ragini-sreenath.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Sydney: file(relativePath: { eq: "sydney-johnson.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Lingyan: file(relativePath: { eq: "lingyan-deng.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Paul: file(relativePath: { eq: "paul-sizaire.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Devin: file(relativePath: { eq: "devin-mooers.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }
    Scott: file(relativePath: { eq: "scott-nelson.jpg" }) {
      childImageSharp {
        gatsbyImageData(width: 125, height: 125, layout: FIXED)
      }
    }

  }
`;

export default Homepage;
