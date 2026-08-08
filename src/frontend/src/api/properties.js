import { apiUrl } from "../constants/api"


export const getServerProperties = async () => {
  const response = await fetch(`${apiUrl}/properties/`)
  return await response.json()
}

export const updateServerProperty = async (key, newValue) => {
  await fetch(`${apiUrl}/properties/${encodeURIComponent(key)}?value=${encodeURIComponent(newValue)}`, {method: "PUT"})
}
