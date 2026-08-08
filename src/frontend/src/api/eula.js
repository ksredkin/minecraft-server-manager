import { apiUrl } from '../constants/api.js'


export const getEulaStatus = async () => {
  const response = await fetch(`${apiUrl}/eula/`)
  return await response.json()
}

export const setEulaStatus = async (newEulaStatus) => {
  await fetch(`${apiUrl}/eula/?accept_eula=${String(newEulaStatus)}`, {method: "POST"})
}
