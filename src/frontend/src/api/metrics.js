import { apiUrl } from "../constants/api.js"


export const getRamUsage = async () => {
  const response = await fetch(`${apiUrl}/metrics/ram`)
  return response.json()
}

export const getCpuPercent = async () => {
  const response = await fetch(`${apiUrl}/metrics/cpu`)
  return response.json()
}
