import { API_URL } from '../constants/api.js'


export const startServer = async () => {
  await fetch(`${API_URL}/start`, {method: "POST"})
}

export const stopServer = async () => {
  await fetch(`${API_URL}/stop`, {method: "POST"})
}

export const restartServer = async () => {
  await fetch(`${API_URL}/restart`, {method: "POST"})
}

export const executeCommand = async (command) => {
  await fetch(`${API_URL}/command?command=${encodeURIComponent(command)}`, {method: "POST"})
}

export const createLogsWebSocket = () => {
  const ws_url = API_URL.replace("http", "ws") + "ws/logs"
  return new WebSocket(wsUrl)
}

export const getServerInfo = async () => {
  const response = await fetch(`${API_URL}/info`)
  return await response.json()
}
