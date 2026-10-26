import { apiUrl } from '../constants/api.js'


export const getServers = async () => {
  const response = await fetch(`${apiUrl}/servers/`, {"credentials": "include"})
  return await response.json()
}

export const getServer = async (uuid) => {
  const response = await fetch(`${apiUrl}/servers/${uuid}`, {"credentials": "include"})
  return await response.json()
}

export const updateServer = async (uuid, new_display_name) => {
  const params = new URLSearchParams({ new_display_name })
  const response = await fetch(`${apiUrl}/servers/${uuid}?${params.toString()}`, {"method": "PUT", "credentials": "include"})
  return await response.json()
}

export const deleteServer = async (uuid) => {
  const response = await fetch(`${apiUrl}/servers/${uuid}`, {"method": "DELETE", "credentials": "include"})
  return await response.json()
}

export const leaveServer = async (uuid) => {
  const response = await fetch(`${apiUrl}/servers/${uuid}/members/me`, {"method": "DELETE", "credentials": "include"})
  return await response.json()
}

export const connectServerWebsocket = async (uuid) => {
  const websocket = new WebSocket(`${apiUrl}/servers/${uuid}/ws`)
  return websocket
}

export const startServer = async (uuid) => {
  await fetch(`${apiUrl}/servers/${uuid}/start`, {method: "POST", "credentials": "include"})
}

export const stopServer = async (uuid) => {
  await fetch(`${apiUrl}/servers/${uuid}/stop`, {method: "POST", "credentials": "include"})
}

export const restartServer = async (uuid) => {
  await fetch(`${apiUrl}/servers/${uuid}/restart`, {method: "POST", "credentials": "include"})
}


export const executeCommand = async (command) => {
  await fetch(`${apiUrl}/command?command=${encodeURIComponent(command)}`, {method: "POST"})
}

export const createLogsWebSocket = () => {
  const wsUrl = apiUrl.replace("http", "ws") + "ws/logs"
  return new WebSocket(wsUrl)
}

export const getServerInfo = async () => {
  const response = await fetch(`${apiUrl}/info`)
  return await response.json()
}
