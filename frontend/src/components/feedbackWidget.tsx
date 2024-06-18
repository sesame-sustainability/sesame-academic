import * as React from "react"
import { AnnotationIcon, PencilIcon } from "@heroicons/react/solid"
import Modal from "./modal"
import { A, Button, Input, Label } from "./styles"
import { useAtom } from "jotai"
import { isAnyModalOpenAtom } from "./pages/dashboard"
import toast, { LoaderIcon } from "react-hot-toast"
import { customAlert } from "./customAlert";
import { InputBlock } from "./userInputs";
import { ExclamationCircleIcon } from "@heroicons/react/outline"

export const externalFeedbackFormUrl = "https://form.jotform.com/220834628448058"

export const FeedbackWidget = () => {

  const [isModalOpen, setIsModalOpen] = React.useState(false)
  const [, setisAnyModalOpen] = useAtom(isAnyModalOpenAtom)

  const closeModal = () => {
    setIsModalOpen(false)
    setisAnyModalOpen(false)
  }

  const openModal = () => {
    setIsModalOpen(true)
    setisAnyModalOpen(true)
  }

  return (
    <>
      <FeedbackButton onClick={openModal} />
      <FeedbackModal
        isModalOpen={isModalOpen}
        closeModal={closeModal}
      />
    </>
  )
}

export const FeedbackButton = ({
  onClick,
}: {
  onClick: () => void
}) => {
  return (
    <div
      className="group absolute bottom-4 right-4 shadow-lg z-50 rounded-full bg-gray-700 text-gray-200 hover:text-gray-100 cursor-pointer transition-colors flex"
      onClick={onClick}
    >
      <div className="w-0 group-hover:w-36 transition-width overflow-hidden flex items-center justify-center">
        <div className="pl-[3px] whitespace-nowrap text-white">Give feedback</div>
      </div>
      <PencilIcon className="absolute h-8 w-8 -right-2 -top-2 text-gray-500" />
      <AnnotationIcon className="h-12 w-12 p-2 shadow-lg border-gray-200 border-2 rounded-full bg-gray-700 group-hover:bg-gray-800" />
    </div>
  )
}

const FeedbackModal = ({
  isModalOpen,
  closeModal,
}: {
  isModalOpen: boolean
  closeModal: () => void
}) => {

  const textAreaRef = React.createRef<HTMLTextAreaElement>()
  const emailInputRef = React.createRef<HTMLInputElement>()

  const [isSubmitting, setIsSubmitting] = React.useState(false)

  React.useEffect(() => {
    if (isModalOpen && textAreaRef.current) {
      textAreaRef.current.focus()
    }
  }, [isModalOpen])

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    e.stopPropagation()
    const message = textAreaRef.current?.value
    const emailAddress = emailInputRef.current?.value
    if (message) {
      setIsSubmitting(true)
      let queryString = `?Feedback=${encodeURIComponent(message)}`;
      if (emailAddress) {
        queryString += `&Email=${emailAddress}`;
      }
      const env = process.env.NODE_ENV
      if (env) {
        queryString += `&Environment=${env}`
      }
      fetch(`https://script.google.com/macros/s/AKfycbxUdDkPhmSHFPkeeXcyCM00Bf3xYQNKKUo0Mae5-ETRt2umrv-0cAX9jnFDeBo4phBryQ/exec${queryString}`).then(response => {
        toast.success('Thanks for your feedback!')
        closeModal()
        setIsSubmitting(false)
      }).catch(error => {
        const mailtoUrl = `mailto:sesame@mit.edu?subject=SESAME%20Feedback&body=${encodeURIComponent(message)}`
        customAlert({
          type: 'error',
          message: <p>Sorry! Something went wrong, and we're not sure what. Please email your feedback to <A href={mailtoUrl}>sesame@mit.edu</A> instead. Thank you!</p>,
        })
        setIsSubmitting(false)
      })

      // Sentry.captureEvent({
      //   extra: {
      //     feedback: message,
      //   },
      //   message: 'User feedback',
      //   transaction: 'feedback',
      // })
    }

  }

  return (
    <Modal
      showModal={isModalOpen}
      headerColor="dark-gray"
      title="Give feedback"
      onClose={closeModal}
      wrapperClasses="!w-3/4 !max-w-2xl !p-0"
    >
      {/* <div className="bg-gray-700 !text-gray-200 rounded-t p-4">
        <div className="text-xl font-semibold text-center">Give feedback</div>
        <svg 
          onClick={() => {
            closeModal()
            textAreaRef.current ? textAreaRef.current.value = '' : null
          }}
          xmlns="http://www.w3.org/2000/svg"
          className="absolute top-3 right-3 cursor-pointer flex-shrink-0 hover:text-gray-100 h-8 w-8 rounded transition-colors text-gray-400"
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div> */}
      <div className="p-4">
        <div className="mb-3">Help us improve SESAME by reporting bugs, suggesting new features, or sharing your thoughts:</div>
        <div className="mb-3 flex items-center text-gray-600 bg-gray-100 text-gray-500 rounded py-1 px-2">
          <ExclamationCircleIcon className="h-5 w-5 mr-3"/>
          If you have more detailed feedback, consider taking our&nbsp;<A href={externalFeedbackFormUrl} target="_blank">user survey</A>.
        </div>
        <form onSubmit={onSubmit}>
          <div className="mb-4">
            <textarea disabled={isSubmitting} className="border-gray-300 mb-2 rounded w-full" rows={8} ref={textAreaRef} />
            <InputBlock layout="column">
              <Label className="mb-2">Email address (optional):</Label>
              <Input ref={emailInputRef} disabled={isSubmitting} type="email" className="!text-left" />
            </InputBlock>
          </div>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? <><LoaderIcon /></> : <>Submit</>}
          </Button>
        </form>
      </div>      
    </Modal>
  )

  
}