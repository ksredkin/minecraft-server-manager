import { API_URL  } from "../constants/api"


export const getPlugins = async () => {
  const response = await fetch(`${API_URL}/plugins/`)
  return await response.json()
}

export const deletePlugin = async (plugin) => {
  await fetch(`${API_URL}/plugins/delete/${plugin}`, {method: "DELETE"})
}

export const searchPlugins = async (query) => {
  const response = await fetch(`${API_URL}/plugins/search?query=${query}`)
  return await response.json()
}

export const installPlugin = async (project_id_or_slug) => {
  await fetch(`${API_URL}/plugins/install/${project_id_or_slug}`, {method: "POST"})
}
