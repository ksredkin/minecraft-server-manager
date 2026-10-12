import { apiUrl } from '../constants/api.js'


export const authLogin = async (login, password) => {
  const params = new URLSearchParams({ login, password })
  console.log(`${apiUrl}/auth/login?${params.toString()}`)
  const response = await fetch(`${apiUrl}/auth/login?${params.toString()}`, {method: 'POST', credentials: "include"})
  return await response.json()
}


export const authRegister = async (login, password, email) => {
  const params = new URLSearchParams({ login, password, email })
  console.log(`${apiUrl}/auth/register?${params.toString()}`)
  const response = await fetch(`${apiUrl}/auth/register?${params.toString()}`, {method: 'POST', credentials: "include"})
  return await response.json()
}


export const authMe = async () => {
  const response = await fetch(`${apiUrl}/auth/me`, {credentials: "include"})
  return await response.json()
}

