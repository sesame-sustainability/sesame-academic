import { useQuery } from "react-query"
import useClient from "./useClient"

export const useUserProfile = (): [
  UserProfile | undefined,
  boolean,
 ] => {

  const { client } = useClient()

  const userProfileQuery = useQuery('userProfile', () => {
    return client(`/users/current`)
  })
  
  const userProfileFull = userProfileQuery?.data as UserProfile & {
    email: string,
    id: number,
  }

  const { isLoading, isFetching } = userProfileQuery

  const { name, institution } = userProfileFull ?? {}

  const isProfileValid = name && institution

  return [
    isProfileValid ? { name, institution } : undefined,
    isLoading || isFetching,
  ]
}