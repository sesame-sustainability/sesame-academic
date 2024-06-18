import * as React from "react"
import Layout from "../layout";
import { db, demoTag } from "../../hooks/useDB";
import { useLiveQuery } from "dexie-react-hooks";
import { format } from "date-fns";
import { A, Button, H2, Loader, } from "../styles";
import { atom, useAtom } from "jotai";
import { VideoBlock } from "./help";
import SEO from "../seo";
import { Link, navigate } from "gatsby";
import { comparableResultsModules } from "../../pages/app";
import { WelcomeModal } from "../welcomeModal";
import { demoBatches } from "../../data/demoBatches";
import { externalFeedbackFormUrl } from "../feedbackWidget";
import { XIcon } from "@heroicons/react/solid";
import { ExclamationCircleIcon } from "@heroicons/react/outline";

export const isAnyModalOpenAtom = atom(false)

type ModuleBlock = {
  title: string;
  colorClasses: string;
  icon: JSX.Element;
  items: Array<{title: string; description: string; path: string}>
}

const hasDisclaimerBeenClosedAtom = atom<Boolean>(false)

export const Dashboard = ({
  // location,
  pathname
}: {
  // location: RouteComponentProps["location"],
  pathname: string;
}): JSX.Element => {

  const recentCases = useLiveQuery(() => db.savedCases.reverse().limit(5).sortBy('createdAt'));

  const demoBatches = useLiveQuery(() => db.savedBatches.filter(batch => batch.isDemo).toArray() )

  const [hasDisclaimerBeenClosed, setHasDisclaimerBeenClosed] = useAtom(hasDisclaimerBeenClosedAtom)

  const getModulesByGroup = (group: ModuleGroup) => {
    return comparableResultsModules.filter(m => m.group === group).map(({ title, description, path }) => ({ title, description, path }))
  }

  const moduleBlocks: ModuleBlock[] = [
    {
      title: 'Systems',
      colorClasses: 'text-gray-100 bg-gradient-to-r from-blue-700 to-purple-700',
      icon: <svg className="mr-3 h-8 w-8 text-gray-300 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"></path></svg>,
      items: getModulesByGroup('systems'),
    },
    {
      title: 'Paths',
      colorClasses: 'text-white bg-gradient-to-r from-orange-500 to-red-500',
      icon: <svg className="mr-3 h-8 w-8 text-gray-200 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.871 4A17.926 17.926 0 003 12c0 2.874.673 5.59 1.871 8m14.13 0a17.926 17.926 0 001.87-8c0-2.874-.673-5.59-1.87-8M9 9h1.246a1 1 0 01.961.725l1.586 5.55a1 1 0 00.961.725H15m1-7h-.08a2 2 0 00-1.519.698L9.6 15.302A2 2 0 018.08 16H8"></path></svg>,
      items: getModulesByGroup('paths'),
    },
    {
      title: 'Saved',
      colorClasses: 'text-gray-100 bg-gradient-to-r from-lime-600 to-emerald-600',
      icon: <svg className="mr-3 h-8 w-8 text-gray-200 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>,
      items: [
        {
          title: 'Your Saved',
          description: 'View all your saved cases and batches',
          path: '/app/saved',
        },
        {
          title: 'Demo Saved',
          description: 'See examples of cases and batches you could build',
          path: '/app/saved/'
        }
      ]
    }
  ]

  const iconClasses = 'h-12 w-12';

  const breezyBlocks = [
    {
      title: 'Cars',
      moduleType: 'fleet',
      batchName: 'Car Decarbonization Options',
      icon: (
        <svg width="62" height="25" viewBox="0 0 62 25" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g clipPath="url(#clip0_64_192)">
        <path d="M14.3658 14.3882C12.2812 14.3882 10.5854 16.0889 10.5854 18.1796C10.5854 20.2703 12.2812 21.971 14.3658 21.971C16.4505 21.971 18.1463 20.2703 18.1463 18.1796C18.1463 16.0889 16.4505 14.3882 14.3658 14.3882ZM14.3658 20.4544C13.1156 20.4544 12.0976 19.4335 12.0976 18.1796C12.0976 16.9257 13.1156 15.9048 14.3658 15.9048C15.6161 15.9048 16.6341 16.9257 16.6341 18.1796C16.6341 19.4335 15.6161 20.4544 14.3658 20.4544Z" fill="currentColor"/>
        <path d="M48.3902 14.3882C46.3056 14.3882 44.6097 16.0889 44.6097 18.1796C44.6097 20.2703 46.3056 21.971 48.3902 21.971C50.4749 21.971 52.1707 20.2703 52.1707 18.1796C52.1707 16.0889 50.4749 14.3882 48.3902 14.3882ZM48.3902 20.4544C47.14 20.4544 46.1219 19.4335 46.1219 18.1796C46.1219 16.9257 47.14 15.9048 48.3902 15.9048C49.6405 15.9048 50.6585 16.9257 50.6585 18.1796C50.6585 19.4335 49.6405 20.4544 48.3902 20.4544Z" fill="currentColor"/>
        <path d="M45.9734 9.83724C47.0657 9.83724 47.5221 8.4385 46.6472 7.78178C39.922 2.74874 29.9563 2.08254 21.8296 4.05676C21.0384 4.24903 20.8859 5.31197 21.5906 5.72496C23.2338 6.68634 24.6515 7.94833 25.8086 9.48112L45.9734 9.83724ZM26.8239 8.31934C25.8909 7.12912 24.8081 6.09191 23.5916 5.21854C30.4653 3.84959 38.7919 4.40475 44.7758 8.31934H26.8239Z" fill="currentColor"/>
        <path d="M57.7375 9.88996L50.317 6.91374C40.3 -2.51458 21.2585 -1.71433 10.3342 5.77633C8.41969 7.08841 6.5551 7.56368 4.52038 7.56368C2.02931 7.56368 0 9.59748 0 12.0971V17.4212C0 19.5119 1.69582 21.2126 3.78049 21.2126H8.27252C10.7622 26.2592 17.9668 26.266 20.4605 21.2126H42.2969C44.7866 26.2592 51.9912 26.266 54.4849 21.2126H59.7331C60.9833 21.2126 62.0014 20.1916 62.0014 18.9378V16.2039C62.0014 13.4065 60.3272 10.9285 57.7389 9.88996H57.7375ZM60.4878 18.9378C60.4878 19.3562 60.1489 19.6961 59.7317 19.6961H53.9948C53.687 19.6961 53.4102 19.8829 53.2941 20.17C51.5105 24.5856 45.2714 24.5883 43.4851 20.17C43.3703 19.8829 43.0935 19.6961 42.7857 19.6961H19.9704C19.6626 19.6961 19.3858 19.8829 19.2697 20.17C17.4861 24.5856 11.247 24.5883 9.46067 20.17C9.34456 19.8829 9.06777 19.6961 8.76128 19.6961H3.78049C2.53023 19.6961 1.5122 18.6751 1.5122 17.4212V12.0971C1.5122 10.4329 2.86237 9.08023 4.52173 9.08023C6.81838 9.08023 8.98811 8.5359 11.1889 7.02883C21.3679 0.0473007 39.8639 -0.970952 49.3813 8.11208C49.5528 8.27592 56.9558 11.2102 57.1758 11.2982C59.1876 12.1052 60.4878 14.0307 60.4878 16.2039V18.9378Z" fill="currentColor"/>
        </g>
        <defs>
        <clipPath id="clip0_64_192">
        <rect width="62" height="25" fill="white"/>
        </clipPath>
        </defs>
        </svg>
      )
    },
    {
      title: 'Hydrogen',
      moduleType: 'lca-tea',
      batchName: 'Clean H2',
      icon: (
        <svg width="45" height="45" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="25" cy="25" r="10.25" stroke="currentColor" strokeWidth="1.5"/>
        <circle cx="25" cy="25" r="24.25" stroke="currentColor" strokeWidth="1.5"/>
        <circle cx="7.5" cy="8.5" r="4.75" fill="white" stroke="currentColor" strokeWidth="1.5"/>
        <path d="M21.6422 29.9999C21.8218 29.9999 21.9767 29.938 22.1057 29.8161C22.2337 29.6951 22.2983 29.5427 22.2983 29.3638V25.6066H27.7027V29.3638C27.7027 29.5427 27.7643 29.6951 27.8883 29.8161C28.0124 29.937 28.1643 29.9999 28.3449 29.9999C28.5256 29.9999 28.6794 29.938 28.8074 29.8161C28.9365 29.6951 29.001 29.5427 29.001 29.3638V20.6479C29.001 20.469 28.9375 20.3166 28.8074 20.1897C28.6794 20.0629 28.5246 19.999 28.3449 19.999C28.1653 19.999 28.0124 20.0619 27.8883 20.1897C27.7643 20.3166 27.7027 20.468 27.7027 20.6479V24.406H22.2983V20.6479C22.2983 20.469 22.2347 20.3166 22.1057 20.1897C21.9767 20.0629 21.8218 19.999 21.6422 19.999C21.4625 19.999 21.3097 20.0629 21.1856 20.1907C21.0615 20.3175 21 20.469 21 20.6479V29.3638C21 29.5427 21.0615 29.6951 21.1856 29.8161C21.3097 29.937 21.4615 29.9999 21.6432 29.9999H21.6422Z" fill="currentColor"/>
        </svg>  
      )
    },
    {
      title: 'Power',
      moduleType: 'lca-tea',
      batchName: 'Power Paths',
      icon: (
        <svg width="26" height="44" viewBox="0 0 26 44" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M23.9333 1H12.7333L1 22.5122H10.0667L1.53333 43L25 15.3415H15.4L23.9333 1Z" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
        </svg>  
      )
    },
    {
      title: 'California Power',
      moduleType: 'pps',
      batchName: 'California Power',
      icon: (
        <svg width="37" height="45" viewBox="0 0 37 45" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path strokeWidth="2" d="M26.6711 45C25.9906 45 25.3482 44.5266 25.1433 43.8736L24.6205 42.2017C24.5352 41.9285 24.2368 41.5122 24.0075 41.3459L20.8252 39.035C20.5861 38.8612 20.082 38.6841 19.7885 38.6709L19.121 38.6402C18.5193 38.6129 17.7916 38.2248 17.4282 37.7356L16.7534 36.8301C16.5964 36.6191 16.1923 36.365 15.937 36.3162L14.1475 35.9752C13.5719 35.8659 12.8946 35.4066 12.5726 34.9075L7.89912 27.6522C7.58203 27.1597 7.42348 26.3528 7.52999 25.7751L7.63975 25.1775C7.66577 25.0343 7.59422 24.8953 7.55926 24.8704C7.12265 24.6817 6.57952 24.1677 6.30308 23.6794L6.21446 23.523C5.93801 23.033 5.78516 22.2418 5.85996 21.6814L5.98842 20.718C6.01119 20.5451 5.88273 20.2628 5.73719 20.1701L5.09812 19.758C4.68834 19.4939 4.12977 18.9849 3.82731 18.5984L1.41251 15.5178C1.07997 15.0932 0.777511 14.3674 0.710027 13.8286L0.0994174 8.99669C0.0351855 8.4885 0.0847823 7.73202 0.214059 7.23625L0.786455 5.04874C0.862882 4.75575 0.853126 4.20618 0.766941 3.9165L0.0587643 1.55269C-0.0575036 1.16369 0.000223818 0.768898 0.218937 0.469285C0.436025 0.171326 0.787268 0 1.18242 0H1.21575L15.102 0.33272C15.8525 0.350929 16.4785 0.986573 16.4972 1.75051L16.8152 14.5503C16.8208 14.8003 17.007 15.2108 17.1892 15.378L34.9123 31.6473C35.2936 31.9966 35.731 32.6231 35.9302 33.1048L36.8474 35.3213C37.0823 35.8891 37.0433 36.725 36.7571 37.268L35.5741 39.5085C35.4343 39.7741 35.3204 40.3113 35.34 40.6126L35.4896 42.8928C35.54 43.6683 34.9627 44.3478 34.2017 44.4082L26.7833 44.995C26.7459 44.9983 26.7085 45 26.6719 45H26.6711ZM1.30356 1.29033L1.97678 3.54074C2.13288 4.06217 2.14671 4.85258 2.0093 5.3798L1.4369 7.56732C1.34991 7.90004 1.31088 8.49099 1.35397 8.83198L1.96458 13.6647C2.00279 13.9668 2.215 14.4775 2.40201 14.715L4.8168 17.7964C5.03308 18.0728 5.48107 18.4817 5.7754 18.6712L6.41447 19.0834C6.97548 19.4451 7.3316 20.2223 7.24298 20.8919L7.11451 21.8552C7.07711 22.1367 7.17306 22.6366 7.31209 22.8832L7.40071 23.0396C7.55194 23.307 7.88692 23.6157 8.06417 23.6918C8.66421 23.9525 9.01627 24.6941 8.88374 25.4167L8.77397 26.0143C8.72682 26.2692 8.81788 26.731 8.95691 26.9479L13.6304 34.2031C13.7662 34.4134 14.1369 34.665 14.3792 34.7113L16.1688 35.0523C16.7306 35.1591 17.4152 35.5903 17.7607 36.0538L18.4356 36.9593C18.5738 37.1455 18.9478 37.3449 19.1763 37.3557L19.8438 37.3863C20.3829 37.4103 21.1203 37.6694 21.5594 37.9889L24.7417 40.2997C25.1921 40.6266 25.6572 41.2772 25.8255 41.8127L26.3483 43.4846C26.3841 43.5988 26.5467 43.7146 26.6703 43.7146H26.6833L34.1017 43.127C34.1724 43.1212 34.2301 43.0533 34.2252 42.9813L34.0756 40.7011C34.0399 40.1565 34.2041 39.3835 34.4578 38.9026L35.6408 36.6621C35.7473 36.4594 35.7668 36.0364 35.6798 35.8245L34.7627 33.6081C34.6367 33.3051 34.3041 32.8276 34.0643 32.6066L16.3411 16.3356C15.9045 15.935 15.5647 15.1818 15.55 14.5842L15.2321 1.78444C15.2297 1.7025 15.1524 1.62305 15.0711 1.62139L1.30356 1.29033Z" fill="currentColor"/>
        </svg>  
      )
    },
    {
      title: 'Texas Power',
      moduleType: 'pps',
      batchName: 'Texas Power',
      icon: (
        <svg width="47" height="45" viewBox="0 0 47 45" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path strokeWidth="2" d="M32.8291 45C32.6515 44.998 32.4748 44.9638 32.3091 44.8985C31.5525 44.6725 30.778 44.5148 29.9945 44.4264C29.6312 44.3812 29.1501 44.0779 28.1499 43.3918C27.7697 43.1165 27.3714 42.8664 26.9592 42.6434C26.1317 42.3682 25.9531 41.7213 25.461 39.9885L25.4111 39.8147C24.936 38.1271 24.6785 37.9413 24.1645 37.5254C23.36 36.8785 22.0963 34.5551 21.8279 34.0097C21.7101 33.7736 21.5763 33.4923 21.4366 33.188C21.1082 32.4065 20.7159 31.6541 20.2628 30.9379C19.4304 29.8128 18.6638 29.3005 18.4522 29.3739C17.9991 29.4743 17.5339 29.5125 17.0718 29.4864C16.2005 29.4864 14.3949 29.4864 14.2771 30.0881C14.0535 31.1398 13.5894 31.8771 12.9745 32.1754C12.6032 32.3613 12.167 32.3613 11.7947 32.1754C11.7558 32.1754 7.88212 30.1503 7.41799 29.1438C7.34812 28.9861 7.26927 28.8314 7.18343 28.6828C6.87701 28.1684 6.68637 27.5919 6.62449 26.9952C6.34501 26.0298 5.74015 25.1921 4.91371 24.6276L4.72906 24.5542C4.01939 24.279 2.83462 23.8169 2.49327 22.715C2.40543 22.3965 2.23375 22.1082 1.9952 21.8812C1.75665 21.6542 1.46121 21.4975 1.14081 21.4272C0.779493 21.3669 0.458099 21.163 0.247495 20.8616C0.036892 20.5603 -0.0439557 20.1866 0.0229183 19.824C0.0438789 19.5287 0.28742 19.3006 0.581866 19.3006L12.5044 19.2384L12.5383 0.562525C12.5383 0.252132 12.7889 0 13.0973 0H23.7173C23.865 0 24.0077 0.059266 24.1125 0.164739C24.2174 0.270213 24.2762 0.412853 24.2762 0.562525V8.43587C24.6406 8.63476 24.938 8.93812 25.1316 9.30778L25.4331 9.21838L25.8074 9.10588C26.1387 8.95419 26.523 8.97529 26.8364 9.16112C27.1498 9.34696 27.3544 9.67443 27.3834 10.0401L27.6629 10.1355C27.9962 10.2701 28.3426 10.3665 28.6969 10.4228C28.6969 10.4228 30.1562 9.94464 30.5754 10.7151C30.6433 10.8577 30.6812 11.0124 30.6872 11.1711C30.6922 11.2585 30.7051 11.3449 30.7261 11.4303C30.8618 11.4193 30.9946 11.3831 31.1174 11.3228C32.5596 10.7322 33.2084 11.3901 33.5208 11.7106L33.5598 11.812C33.6825 11.812 33.8951 11.7618 34.0568 11.7327C34.7944 11.6031 35.7337 11.4404 36.3315 11.8904C36.5611 12.0852 36.8536 12.1897 37.153 12.1827C37.2348 12.1706 37.3087 12.1234 37.3546 12.0531C37.7349 11.4906 38.8528 11.0858 39.7072 10.9893C40.2681 10.8778 40.85 11.0124 41.3062 11.361L41.6306 11.6644C42.0388 12.0521 42.1226 12.1365 42.5588 12.1937C42.975 12.248 43.3753 12.3856 43.7386 12.5986C43.8244 12.6558 43.9183 12.699 44.0181 12.7281C44.065 12.7342 44.1119 12.7342 44.1578 12.7281C44.6439 12.7281 45.2757 12.914 45.2757 14.0892V15.4052C45.2757 16.6538 45.2088 19.2414 45.2757 19.602C45.3555 19.7406 45.4474 19.8732 45.5502 19.9958C45.8945 20.3544 46.1101 20.8174 46.165 21.3127C46.165 22.286 46.3776 22.4879 46.3996 22.511C46.7829 22.9611 46.9875 23.5387 46.9755 24.1303C47.0523 24.5482 46.9465 24.9791 46.685 25.3116C46.5493 25.5939 46.4585 25.8952 46.4165 26.2056C46.3826 26.3915 46.3497 26.5663 46.3157 26.7119C46.2748 26.9249 46.2558 27.1418 46.2598 27.3588C46.2768 27.7405 46.2219 28.1222 46.0981 28.4839C46.0932 28.523 46.0932 28.5632 46.0981 28.6024C46.182 29.2493 45.8576 29.6149 45.12 29.8118C44.8575 29.8872 44.6 29.9766 44.3484 30.082C43.5709 30.3854 42.6716 30.7289 42.1127 30.082C42.0588 30.0198 41.9949 29.9685 41.922 29.9304C41.922 29.9695 41.9559 30.0037 41.9669 30.0368C42.1127 30.3131 42.1745 30.6255 42.1456 30.9369C42.1067 31.1729 42.0338 31.6119 39.6523 33.1357C38.8248 33.6651 37.4504 34.5471 36.5721 33.861C36.4603 33.7726 36.3405 33.6932 36.2138 33.6249C36.4753 33.9373 36.5182 34.3803 36.3206 34.7379C36.1229 35.0955 35.7267 35.2924 35.3244 35.2342C34.7655 35.2342 34.1506 35.414 34.0997 35.9765C34.0558 36.4084 33.8851 36.8183 33.6077 37.1518C33.4899 37.3014 33.3921 37.4662 33.3172 37.642C33.0567 38.2085 32.879 38.8112 32.7922 39.43C32.7034 39.9443 32.7752 40.4727 32.9988 40.9438C33.2034 41.3175 33.2823 41.7474 33.2224 42.1703C33.1745 42.4917 33.2184 42.8192 33.3512 43.1155C33.7584 43.5013 33.8502 44.117 33.5747 44.6062C33.4011 44.8493 33.1236 44.996 32.8261 45H32.8291ZM18.4702 28.2428C19.4873 28.2428 20.5612 29.4693 21.1471 30.2628C21.6512 31.0293 22.0854 31.8409 22.4437 32.6867L22.824 33.4853C23.333 34.5089 24.378 36.2357 24.8581 36.6244C25.6067 37.2261 25.976 37.654 26.4791 39.4822L26.529 39.656C26.9542 41.1467 27.0879 41.4732 27.3065 41.5515C27.8256 41.7936 28.3166 42.0919 28.7708 42.4405C29.208 42.769 29.6721 43.0603 30.1572 43.3124C30.9267 43.4069 31.6883 43.5555 32.4379 43.7574C32.1674 43.2743 32.0576 42.7157 32.1245 42.1653C32.1414 41.9774 32.1324 41.7876 32.0965 41.6027C31.7222 40.9177 31.5805 40.1271 31.6943 39.3526C31.7861 38.6264 31.9877 37.9192 32.2921 37.2542C32.4009 36.9911 32.5437 36.7429 32.7163 36.5169C32.875 36.3472 32.9749 36.1302 33.0018 35.8981C33.0966 34.8796 33.9241 34.2106 35.2376 34.1372C35.2356 34.1202 35.2356 34.1031 35.2376 34.087C35.1058 33.8429 35.017 33.5787 34.9751 33.3045C34.9272 32.967 35.0859 32.6345 35.3773 32.4607C36.093 32.0669 37.1879 32.8997 37.3117 32.9951C37.4355 33.0905 37.675 33.1247 39.1003 32.2126C39.813 31.7937 40.4777 31.2975 41.0846 30.733L40.9838 30.4909C40.7732 30.1353 40.7482 29.6983 40.9169 29.3206C41.0986 29.0213 41.414 28.8304 41.7613 28.8083C42.2404 28.7832 42.7025 28.9931 43.002 29.3708C43.3403 29.3156 43.6687 29.2161 43.9801 29.0725C44.2726 28.952 44.57 28.8485 44.8745 28.7631L45.0421 28.7069C45.0172 28.4929 45.0461 28.2759 45.126 28.077C45.1849 27.844 45.2088 27.6029 45.1988 27.3628C45.1829 27.0524 45.1988 26.742 45.2438 26.4347C45.2777 26.3111 45.3056 26.1594 45.3326 26.0017C45.3835 25.4633 45.5761 24.949 45.8915 24.511C45.9494 24.1142 45.8825 23.7094 45.7019 23.3518C45.2717 22.9972 45.0701 22.3393 45.0701 21.2986C44.9892 21.0656 44.8595 20.8526 44.6898 20.6748C44.4712 20.4478 44.2985 20.1806 44.1808 19.8873C44.0919 19.5719 44.0799 18.5653 44.1358 15.3871V14.0872C44.1408 14.0089 44.1408 13.9295 44.1358 13.8512H43.8065C43.5849 13.803 43.3733 13.7166 43.1806 13.598C42.9381 13.4544 42.6706 13.358 42.3931 13.3168C41.7803 13.2485 41.2183 12.9421 40.8281 12.4619L40.5266 12.1747C40.32 12.0672 40.0845 12.033 39.8559 12.0792C39.271 12.1274 38.7111 12.3354 38.235 12.6809C38.0204 12.9983 37.684 13.2123 37.3067 13.2716C36.7038 13.3419 36.099 13.1641 35.6299 12.7764C35.4003 12.6076 34.6238 12.7764 34.2105 12.8216C33.6516 12.923 33.2883 12.9843 32.9918 12.8216C32.879 12.7492 32.7752 12.6618 32.6844 12.5634C32.4439 12.3213 32.2422 12.1134 31.4937 12.4228C31.0605 12.6659 30.5365 12.6809 30.0913 12.4619C29.7569 12.2369 29.5493 11.8643 29.5323 11.4604C29.3427 11.4675 29.1541 11.4996 28.9734 11.5559C28.5652 11.6965 28.0062 11.5217 27.2576 11.2575C27.0959 11.2013 26.9562 11.1511 26.8773 11.134C26.4242 11.0446 26.3184 10.5715 26.2625 10.3806C26.2625 10.3354 26.2625 10.2621 26.2176 10.2118C26.1717 10.2189 26.1268 10.2299 26.0838 10.246L25.7205 10.3525C25.1007 10.5433 24.7653 10.6448 24.429 10.4318C24.2174 10.2832 24.0836 10.0451 24.0656 9.78492C23.881 9.59708 23.6654 9.44239 23.4288 9.32888C23.2392 9.23244 23.1194 9.03656 23.1214 8.8226V1.12304H13.6193L13.5634 19.7768C13.5634 19.9264 13.5045 20.0691 13.3997 20.1746C13.2949 20.28 13.1522 20.3393 13.0045 20.3393L1.70275 20.4187C2.55515 20.7481 3.21391 21.4463 3.49638 22.3202C3.698 22.9219 4.54141 23.2544 5.10036 23.4452L5.29599 23.5246C6.09548 23.845 7.53178 25.5105 7.70545 26.8043C7.75037 27.2744 7.90507 27.7285 8.1586 28.1263C8.24244 28.284 8.33726 28.4527 8.42709 28.6607C8.68361 29.1057 11.121 30.5622 12.2898 31.1528C12.3487 31.187 12.4216 31.187 12.4795 31.1528C12.703 31.0464 13.0055 30.6405 13.1781 29.842C13.4916 28.3794 15.5537 28.3623 17.0628 28.3513C17.4102 28.3593 17.7575 28.3402 18.1019 28.295C18.2216 28.2589 18.3464 28.2428 18.4712 28.2448L18.4702 28.2428Z" fill="currentColor"/>
        </svg>
  
      )
    },
  ]

  return (
    <Layout
      type="page"
      pathname={pathname ?? ""}
      title="Dashboard"
      contentWrapperClasses="bg-gray-100"
    >

      <WelcomeModal />

      <SEO title="Dashboard" />

        {/* <div className="text-3xl mb-2 text-gray-600">Welcome to <b>SESAME</b></div>
        <div className="text-gray-400 mb-4">Sustainable Energy System Analysis Modeling Environment</div> */}
        {/* <Button className="mb-4">Open Sesame</Button> */}

        {!hasDisclaimerBeenClosed &&
          <div className="rounded bg-blue-100 border border-blue-200 border-opacity-20 px-6 pt-5 pb-6 mb-6 space-y-3">
            <div className="text-lg font-bold opacity-60 flex items-center"><ExclamationCircleIcon className="w-6 h-6 mr-3 text-blue-900" />Beta Note<XIcon className="w-6 h-6 ml-auto cursor-pointer" onClick={(e) => setHasDisclaimerBeenClosed(true)} /></div>
            <div>Thank you for being part of a small select group of beta users. We hope SESAME brings you some value. As a beta, this early prototype will contain some bugs. Please help us by reporting any bugs you encounter, and general improvements you recommend, using the feedback button on the bottom right of the screen.</div>
            <div>After significant use, please consider answering the feedback questions <A href={externalFeedbackFormUrl} target="_blank">here</A>, and also listed in the navigation panel on the left. Thank you!</div>
          </div>
        }
        
        <div className="flex items-stretch space-x-6 mb-6">

          <Block className="w-1/2">
            <H2>Quick start</H2>
            <div className="mb-4">Explore the emissions and costs of different energy pathways:</div>
            <div className="flex flex-wrap">
              {breezyBlocks.map(block => {
                const moduleInfo = comparableResultsModules.find(m => m.type === block.moduleType)
                const matchingDemoBatch = demoBatches?.find(batch => batch.name === `${block.batchName}${demoTag}`)
                const url = `${moduleInfo?.path}?loadBatchId=${matchingDemoBatch?.id}`
                return (
                  <>
                    {matchingDemoBatch &&
                      <Link to={url} >
                        <div className="rounded border transition-colors cursor-pointer w-[7.5rem] h-[7.5rem] mr-4 flex flex-col items-center justify-center text-gray-600 hover:bg-gray-100 mb-4">
                          <div className="h-20 p-4 flex items-center">{block.icon}</div>
                          <div className="h-8 pb-2 leading-tight font-semibold text-gray-500 text-center items-center flex px-3">{block.title}</div>
                        </div>
                      </Link>
                    }
                  </>
                )
              })}
            </div>
            {/* Or <A className="underline font-bold" href="#">get started with a demo case</A> */}
          </Block>

          <Block className="w-1/2">
            <H2>Recent cases</H2>
            <div className="divide-y div">
              {!recentCases &&
                <Loader />
              }
              {recentCases && recentCases.length === 0 &&
                <span className="text-gray-400">You have no recent cases.</span>
              }
              {recentCases?.map(savedCase => {
                const { name, type, createdAt, id } = savedCase;
                const colorClass = getColorClassForModuleType(type);
                const modulePath = comparableResultsModules.find(c => c.type === type)?.path;
                return (
                  <div className="py-1 flex items-center">
                    <Tag colorClass={colorClass} className="whitespace-nowrap">{formatModuleTypeForDisplay(type)}</Tag>
                    <Link to={`${modulePath}?loadCaseIds=${id}`} className="leading-tight">
                      <span>{name}</span>
                      {createdAt &&
                        <>
                          {/* <span className="text-gray-300 px-3">•</span> */}
                          <div className="text-gray-400">{format(createdAt, 'MMMM d, yyyy')}</div>
                        </>
                      }
                    </Link>
                  </div>
                )
              })}
            </div>
            <Button className="mt-6" onClick={(e) => navigate("/app/saved")}>See all</Button>
          </Block>

        </div>

        <Block>
          <H2>Advanced modules</H2>
          <div className="grid grid-cols-3 gap-6 mt-2 mb-2 items-stretch">
            {moduleBlocks.map(block => {
              return (
                <div className={`rounded bg-gray-50 shadow-lg flex flex-col`}>
                  <div className={`flex items-center ${block.colorClasses} rounded-t py-4 px-6`}>
                    {block.icon}
                    <div className="text-xl font-semibold">{block.title}</div>
                  </div>
                  <div className="py-2 grid grid-cols-1 divide-y border-l border-r rounded-b flex-grow">
                    <div>
                    {block.items?.map(item => {
                      return (
                        <Link to={item.path}>
                          <div className="relative group rounded-r py-3 px-6 hover:bg-white">
                            {/* <div className="absolute left-0 top-5 border-t-2 border-white w-2"></div> */}
                            <span className="block font-semibold text-lg">{item.title}</span>
                            <span className="block font-light opacity-90 group-hover:opacity-100 transition-colors">{item.description}</span>
                          </div>
                        </Link> 
                      )
                    })}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Block>

    </Layout>
  )
}

const Block: React.FC<{className?: string}> = ({children, className = ''}) => (
  <div className={`border rounded p-6 bg-white ${className ?? ''}`}>
    {children}
  </div>
)

const Tag: React.FC<{colorClass: string; className?: string;}> = ({children, className, colorClass}) => {

  return (
    <div className={`inline-flex mr-3 ${colorClass} text-white py-1 px-2 rounded ${className}`}><span className="opacity-80">{children}</span></div>
  )
}

const formatModuleTypeForDisplay = (type: string): string => {
  return comparableResultsModules.find(c => c.type === type)?.title ?? '';
}

const getColorClassForModuleType = (type: string): string => {
  const moduleGroup = comparableResultsModules.find(c => c.type === type)?.group;
  let colorClass = '';
  if (moduleGroup === 'systems') {
    colorClass = 'bg-gradient-to-r from-blue-700 to-purple-700';
  } else if (moduleGroup === 'paths') {
    colorClass = 'bg-gradient-to-r from-orange-500 to-red-500';
  } else {
    colorClass = 'bg-red-500';
  }
  return colorClass;
}