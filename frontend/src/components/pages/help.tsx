import { Link, navigate } from "gatsby"
import { useAtom } from "jotai"
import * as React from "react"
import Layout from "../layout"
import SEO from "../seo"
import { A, Button, H2, Loader } from "../styles"
import { isAnyModalOpenAtom } from "./dashboard"

type Video = {
  title: string;
  id: string;
}

const videos: Video[] = [
  {
    title: 'Intro',
    id: '7b463EJDGy8',
  },
  {
    title: 'Running an analysis',
    id: 'gZwrdoIpvuQ',
  },
  {
    title: 'Saving a case',
    id: '',
  },
  {
    title: 'Saving a batch',
    id: '',
  }
]

export const VideoBlock = () => {

  const [currentVideo, setCurrentVideo] = React.useState<Video>(videos[0])
  const currentVideoIndex = videos.indexOf(currentVideo)
  const isLastVideo = currentVideoIndex >= (videos.length - 1)

  const [isModalOpen, setIsModalOpen] = useAtom(isAnyModalOpenAtom)

  return (
    <>
      <div className="flex w-full items-stretch border bg-gray-50">
        <div className="w-52">
          <VideoList currentVideo={currentVideo} setCurrentVideo={setCurrentVideo} />
        </div>
        <div className="flex-grow">
          <VideoPane currentVideo={currentVideo} />
          <div className="bg-gray-200 h-16 px-10 flex items-center">
            <Button color="dark-gray" disabled={currentVideoIndex <= 0} onClick={(e) => {
              setCurrentVideo(videos[currentVideoIndex - 1])
            }}>Previous</Button>
            {isLastVideo ?
              <Button color="blue" className="ml-auto" onClick={(e) => {
                navigate('/app/dashboard')
              }}>Go to Dashboard</Button>
              :
              <Button color="dark-gray" className="ml-auto" disabled={currentVideoIndex >= (videos.length - 1)} onClick={(e) => {
                setCurrentVideo(videos[currentVideoIndex + 1])
              }}>Next</Button>
            }
            
          </div>
        </div>
      </div>
    </>
    
  )
}

const VideoPane = ({ currentVideo }: { currentVideo: Video }) => (
  <div className="px-10 pt-8 pb-4 relative">
    {/* <div className="absolute top-1/2 left-1/2 z-10 mt-3 ml-3 text-gray-300">
      <Loader />
    </div> */}
    <YouTubeEmbed id={currentVideo.id} />
  </div>
)


const VideoList = ({ currentVideo, setCurrentVideo }: { currentVideo: Video, setCurrentVideo: React.Dispatch<React.SetStateAction<Video>> }) => (
  <div className="h-full flex flex-col">
    <div className="pt-5">
      {videos.map((video, index) => {
        const isActive = video.title === currentVideo?.title
        return (
          <div
            className={`select-none transition-colors pl-6 pr-8 py-2 cursor-pointer ${isActive ? 'text-gray-800 font-medium' : 'text-gray-400 hover:text-gray-600'} ${index === 0 ? 'mt-[-1px]' : ''}`}
            onClick={(e) => setCurrentVideo(video)}
          >
            {video.title}
          </div>
        )
      })}
    </div>

    <div className="bg-gray-200 h-16 w-full mt-auto" />
  </div>
)

const YouTubeEmbed = ({ id }: { id: string }) => (
  <>
    <div className="embed-container w-full shadow bg-black">
      <iframe src={`https://www.youtube.com/embed/${id}`} frameBorder='0' allowFullScreen />
    </div>
  </>
);

export const HelpPage = () => {

  return (
    <Layout title="Help" type="page">
      <SEO title="Help" />
      {/* <H2>Video Tutorials</H2> */}
      <div className="text-xl mt-2 font-bold text-gray-600 leading-6 mb-4 gutter-x">
        
      </div>
      <H2>Tutorial Videos</H2>
      <div className="mb-6">Tutorial videos are forthcoming.</div>
      {/* <div className="border-gray-200 shadow-lg mb-6">
        <VideoBlock />
      </div>  */}
      <H2>Email Support</H2>
      <div className="mb-3">Get help or give feedback by emailing us at <A className="underline text-gray-500 font-medium" href="mailto:sesame@mit.edu">sesame@mit.edu</A>.</div>
      <div className="mb-5">Alternatively, you can click the feedback button at the bottom right of the screen.</div>
      <div>Thanks for trying SESAME!</div>
      <div className="">-- The SESAME Team</div>
    </Layout>
  )
}