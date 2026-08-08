import { apiUrl } from '../constants/api.js'


export const startServer = async () => {
  await fetch(`${apiUrl}/start`, {method: "POST"})
}

export const stopServer = async () => {
  await fetch(`${apiUrl}/stop`, {method: "POST"})
}

export const restartServer = async () => {
  await fetch(`${apiUrl}/restart`, {method: "POST"})
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
