import React from "react";
import { useStaticQuery, graphql, Link } from "gatsby";
import { GatsbyImage } from "gatsby-plugin-image";
import { AnchorLink } from "gatsby-plugin-anchor-links";
import addToMailchimp from "gatsby-plugin-mailchimp";
import * as Styles from "./styles";

const Footer = (): JSX.Element => {
  const [email, setEmail] = React.useState<string>();
  const [mcResponse, setMcResponse] = React.useState<MailChimpResponse>();
  const handleSubmit = (
    e: React.FormEvent<HTMLFormElement>,
    userEmail?: string
  ) => {
    e.preventDefault();
    addToMailchimp(userEmail)
      .then((data: MailChimpResponse) => {
        setMcResponse(data);
      })
      .catch(() => {
        // unnecessary because MailChimp only ever returns a 200 status code
      });
  };

  const data = useStaticQuery(graphql`
    query FooterQuery {
      MITEIWhite: file(relativePath: { eq: "MITEIWhite.png" }) {
        childImageSharp {
          gatsbyImageData(height: 60, placeholder: NONE, layout: FIXED)
        }
      }
    }
  `);

  return (
    <footer className="bg-gray-900">
      <div className="max-w-screen-xl mx-auto py-12 px-4 sm:gutter-x lg:py-16 lg:px-8">
        <div className="xl:grid xl:grid-cols-3 xl:gap-8">
          <div className="grid grid-cols-2 gap-8 xl:col-span-2">
            <div className="md:grid md:grid-cols-2 md:gap-8">
              <a
                aria-label="Learn more about the MIT Energy Initiative"
                target="_blank"
                rel="noopener noreferrer"
                href="http://energy.mit.edu/"
              >
                <GatsbyImage
                  alt="MIT Energy Initiative Logo"
                  image={data.MITEIWhite.childImageSharp.gatsbyImageData}
                />
              </a>
              <div className="mt-12 md:mt-4">
                <ul>
                  <li>
                    <AnchorLink
                      to="/#about"
                      className="text-base leading-6 text-gray-300 hover:text-white"
                    >
                      About
                    </AnchorLink>
                  </li>
                  <li className="mt-4">
                    <AnchorLink
                      to="/#team"
                      className="text-base leading-6 text-gray-300 hover:text-white"
                    >
                      Team
                    </AnchorLink>
                  </li>
                  <li className="mt-4">
                    <Link
                      to="/covid"
                      className="text-base leading-6 text-gray-300 hover:text-white"
                    >
                      COVID-19 Dashboard
                    </Link>
                  </li>
                  <li className="mt-4">
                    {/* <a
                      href="#"
                      className="text-base leading-6 text-gray-300 hover:text-white"
                    >
                      Log in
                    </a> */}
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div className="mt-8 xl:mt-0">
            <h4 className="text-sm leading-5 font-semibold tracking-wider text-gray-400 uppercase">
              Sign up
            </h4>
            <p className="mt-4 text-gray-300 text-base leading-6">
              Sign up to become a beta user:
            </p>
            <form
              className="mt-4 sm:flex sm:max-w-md"
              onSubmit={(e) => handleSubmit(e, email)}
            >
              <input
                aria-label="Email address"
                type="email"
                required
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none w-full px-5 py-3 border border-transparent text-base leading-6 rounded-md text-gray-900 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 transition duration-150 ease-in-out"
                placeholder="Enter your email"
              />
              <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3 sm:flex-shrink-0">
                <Styles.Button className="!py-6">Sign up</Styles.Button>
              </div>
            </form>
            {mcResponse && mcResponse.result === "error" && (
              <div
                className="text-red-300 mt-4"
                dangerouslySetInnerHTML={{ __html: mcResponse.msg }}
              />
            )}
            {mcResponse && mcResponse.result === "success" && (
              <div
                className="text-white mt-4"
                dangerouslySetInnerHTML={{ __html: mcResponse.msg }}
              />
            )}
          </div>
        </div>
        <div className="mt-8 border-t border-gray-700 pt-8 md:flex md:items-center md:justify-between">
          <div className="flex md:order-2">
            <a
              href="mailto:sesame@mit.edu"
              className="text-gray-400 hover:text-gray-300"
            >
              <svg
                className="h-5 w-5 text-gray-400 inline-block"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884zM18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"
                  clipRule="evenodd"
                />
              </svg>{" "}
              <span>sesame@mit.edu</span>
            </a>
          </div>
          <p className="mt-8 text-base leading-6 text-gray-400 md:mt-0 md:order-1">
            A project from the{" "}
            <a
              aria-label="Learn more about the MIT Energy Initiative"
              className="underline hover:text-gray-300"
              href="http://energy.mit.edu/"
              target="_blank"
              rel="noopener noreferrer"
            >
              MIT Energy Initiative
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
