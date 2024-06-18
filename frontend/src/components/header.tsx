import React from "react";
import { useStaticQuery, graphql, Link } from "gatsby";
import { GatsbyImage } from "gatsby-plugin-image";

const Header = (): JSX.Element => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  const data = useStaticQuery(graphql`
    query LayoutQuery {
      MITEIFull: file(relativePath: { eq: "MITEIFull.png" }) {
        childImageSharp {
          gatsbyImageData(height: 60, placeholder: NONE, layout: FIXED)
        }
      }
    }
  `);

  return (
    <nav>
      <div className="relative max-w-screen-xl mx-auto flex items-center justify-between px-4 sm:gutter-x pt-6 pb-4">
        <div className="flex items-center flex-1">
          <div className="text-xl text-black font-semibold flex-shrink-0">
            <Link to="/" className="site-title">
              SESAME
            </Link>
          </div>
          <div className="hidden md:block md:ml-10">
            <Link
              to="/#about"
              className="header-link font-medium text-gray-500 hover:text-gray-900 focus:outline-none focus:text-gray-900 transition duration-150 ease-in-out"
            >
              About
            </Link>
            <Link
              to="/#team"
              className="header-link ml-10 font-medium text-gray-500 hover:text-gray-900 focus:outline-none focus:text-gray-900 transition duration-150 ease-in-out"
            >
              Team
            </Link>
            {/* <Link
              to="/covid"
              className="header-link ml-10 font-medium text-gray-500 hover:text-gray-900 focus:outline-none focus:text-gray-900 transition duration-150 ease-in-out"
            >
              COVID-19 Dashboard
            </Link> */}
          </div>
        </div>
        <div className="-ml-2 mr-2 flex items-center md:hidden">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:bg-gray-700 focus:text-white transition duration-150 ease-in-out"
            aria-label="Main menu"
            aria-expanded="false"
          >
            <svg
              className={`${isMobileMenuOpen ? "hidden" : "block"} h-6 w-6`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>

            <svg
              className={`${isMobileMenuOpen ? "block" : "hidden"} h-6 w-6`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="hidden md:block text-right">
          <a
            aria-label="Learn more about the MIT Energy Initiative"
            target="_blank"
            rel="noopener noreferrer"
            href="http://energy.mit.edu/"
            className="inline-flex header-logo"
            style={{ marginTop: "-0.75rem" }}
          >
            <GatsbyImage
              alt="MIT Energy Initiative Logo"
              image={data.MITEIFull.childImageSharp.gatsbyImageData}
            />
          </a>
        </div>
        <Link
          to="/app"
          className="hidden md:inline-flex items-center sm:py-3 sm:gutter-x px-4 py-2 ml-5 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Log in
        </Link>
      </div>

      <div
        className={`${
          !isMobileMenuOpen ? "hidden md:hidden" : "block md:block"
        }`}
      >
        <div className="px-2 pt-2 pb-3 sm:px-3">
          <Link
            onClick={() => setIsMobileMenuOpen(false)}
            to="/#about"
            className="mobile-header-link block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:text-white focus:bg-gray-700 transition duration-150 ease-in-out"
          >
            About
          </Link>
          <Link
            onClick={() => setIsMobileMenuOpen(false)}
            to="/#team"
            className="mobile-header-link mt-1 block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:text-white focus:bg-gray-700 transition duration-150 ease-in-out"
          >
            Team
          </Link>
          <Link
            onClick={() => setIsMobileMenuOpen(false)}
            to="/covid"
            className="mobile-header-link mt-1 block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:text-white focus:bg-gray-700 transition duration-150 ease-in-out"
          >
            COVID-19 Dashboard
          </Link>
          <Link
            onClick={() => setIsMobileMenuOpen(false)}
            to="/app"
            className="mobile-header-link mt-1 block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:text-white focus:bg-gray-700 transition duration-150 ease-in-out"
          >
            Log in
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Header;
