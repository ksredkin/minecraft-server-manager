import { apiUrl } from '../constants/api.js'


export const authLogin = async (login, password) => {
  const params = new URLSearchParams({ login, password })
  console.log(`${apiUrl}/auth/login?${params.toString()}`)
  const response = await fetch(`${apiUrl}/auth/login?${params.toString()}`, {method: 'POST'})
  return await response.json()
}