import { API_URL } from '../constants/api.js'


export const getEulaStatus = async () => {
  const response = await fetch(`${API_URL}/eula/`)
  return await response.json()
}

export const setEulaStatus = async (new_eula_status) => {
  await fetch(`${API_URL}/eula/?accept_eula=${String(new_eula_status)}`, {method: "POST"})
}
