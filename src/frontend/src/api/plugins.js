import { apiUrl } from "../constants/api"


export const getPlugins = async () => {
  const response = await fetch(`${apiUrl}/plugins/`)
  return await response.json()
}

export const deletePlugin = async (plugin) => {
  await fetch(`${apiUrl}/plugins/delete/${plugin}`, {method: "DELETE"})
}

export const searchPlugins = async (query) => {
  const response = await fetch(`${apiUrl}/plugins/search?query=${query}`)
  return await response.json()
}

export const installPlugin = async (projectIdOrSlug) => {
  await fetch(`${apiUrl}/plugins/install/${projectIdOrSlug}`, {method: "POST"})
}
