import { API_URL } from "../constants/api"


export const getServerProperties = async () => {
  const response = await fetch(`${API_URL}/properties/`)
  return await response.json()
}

export const updateServerProperty = async (key, new_value) => {
  await fetch(`${API_URL}/properties/${encodeURIComponent(key)}?value=${encodeURIComponent(new_value)}`, {method: "PUT"})
}
