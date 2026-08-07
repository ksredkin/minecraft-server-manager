import { API_URL } from "../constants/api.js"


export const getRamUsage = async () => {
  const response = await fetch(`${API_URL}/metrics/ram`)
  return response.json()
}

export const getCpuPercent = async () => {
  const response = await fetch(`${API_URL}/metrics/cpu`)
  return response.json()
}
