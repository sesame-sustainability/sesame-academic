import { navigate } from "gatsby"
import * as React from "react"
import * as Sentry from "@sentry/browser"
import { useQueryClient } from "react-query"
import useClient from "../../hooks/useClient"
import { useUserProfile } from "../../hooks/useUserProfile"
import { capitalize } from "../../utils"
import { customAlert } from "../customAlert"
import { Button, Input, Label, Loader } from "../styles"
import { InputBlock } from "../userInputs"

export const UserProfile = ({

}: {

}) => {

  const { client } = useClient()

  const [isLoading, setIsLoading] = React.useState(false)

  const [profileInputData, setProfileInputData] = React.useState<UserProfile>({name: '', institution: ''})

  // const [profile, setProfile] = useLocalStorage("profile", "")
  // const [name, setName] = useLocalStorage("name", '')
  // const [institution, setInstitution] = useLocalStorage("")

  const [ userProfile, isUserProfileLoading ] = useUserProfile()

  React.useEffect(() => {
    if (userProfile) {
      if (userProfile.name && userProfile.institution) {
        navigate('/app/dashboard')
      }
    }
  }, [userProfile])

  const queryClient = useQueryClient()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    if (profileInputData.name && profileInputData.institution) {
      client('/users/current', {
        body: profileInputData,
        method: 'PUT',
      }).then((res: { name: string; institution: string; }) => {
        console.log(res)
        setIsLoading(false)
        const { name, institution } = res;
        if (name && institution) {
          customAlert({type: 'success', message: 'Profile updated!'})
          // if we receive a success from the server in setting our profile,
          // invalidate the react-query query so it can refetch the profile data and cache it
          queryClient.invalidateQueries('userProfile')
        } else {
          customAlert({type: 'error', message: 'Something went wrong on our end, and we don\'t know what.'})
          Sentry.captureEvent({
            message: 'Error submitting user profile data to database',
            extra: {
              profileData: { name, institution }
            }
          })
        }
      }).catch(e => {
        alert(e)
        setIsLoading(false)
      })
    }
  }

  return (
    <div className="flex items-center justify-center bg-gray-100 min-h-screen min-w-screen">
      {isUserProfileLoading
        ?
        <Loader />
        :
        <div className="p-12 rounded-lg bg-white max-w-lg m-6">
          <div className="font-bold text-gray-600 text-3xl mb-6 text-center">Welcome to SESAME!</div>
          <div className="font-medium text-gray-500 text-xl mb-4">Please set up your profile before diving in:</div>
          <form
            className="mt-4 space-y-4"
            onSubmit={handleSubmit}
          >
            {['name', 'institution'].map(field => (
              <InputBlock layout="column">
                <Label>
                  {capitalize(field)}
                  <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  className="!text-left"
                  type="text"
                  required
                  name={field}
                  onChange={(e) => {
                    setProfileInputData(profile => ({
                      ...profile,
                      [field]: e.target.value,
                    }))
                  }}
                />
              </InputBlock>
            ))}
            <Button type="submit" disabled={isLoading} size="large" className="w-full !mt-6 !h-10 flex justify-center">{isLoading ? <Loader size="small" color="light" /> : 'Submit'}</Button>
          </form>
        </div>
      }
    </div>
  )
}