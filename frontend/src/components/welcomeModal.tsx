import { useAtom } from "jotai"
import * as React from "react"
import { useSetting } from "../hooks/useSettings"
import Modal from "./modal"
import { isAnyModalOpenAtom } from "./pages/dashboard"
import { VideoBlock } from "./pages/help"
import { A } from "./styles"

export const WelcomeModal = () => {

  const [, setIsAnyModalOpen] = useAtom(isAnyModalOpenAtom)
  const [isModalOpen, setIsModalOpen] = React.useState(false)

  const [hasDismissedWelcomeModal, setHasDismissedWelcomeModal] = useSetting('hasDismissedWelcomeModal')

  const open = () => {
    setIsModalOpen(true)
    setIsAnyModalOpen(true)
  }

  const close = () => {
    setIsModalOpen(false)
    setIsAnyModalOpen(false)
    setHasDismissedWelcomeModal(true)
  }

  // React.useEffect(() => {
  //   if (hasDismissedWelcomeModal === false) {
  //     open()
  //   }
  // }, [hasDismissedWelcomeModal])

  return (
    <Modal
      showModal={isModalOpen}
      title={
        <>Welcome to <span className="font-bold">SESAME</span></>
      }
      onClose={close}
      wrapperClasses="!p-0 !w-5/6 !max-w-6xl !aspect-[20/8]"
    >
      <>
        <div className="px-4 py-6 text-center space-y-4">
          <div>
            SESAME is a tool for evaluating the impacts of the global energy system.
          </div>
          <div>
            <b>Watch the video tutorials below</b> or <A className="underline font-bold" href="#">get started with a demo case</A>.
          </div>
        </div>
        <VideoBlock />
      </>
    </Modal>
  )
}