import { apiUrl } from "../constants/api.js"

const createLogsWebSocket = async (onMessage, onError, socketRef, reconnectInterval = 3000) => {
  if (socketRef.current && socketRef.current.readyState !== 3) return

  socketRef.current = new WebSocket(`ws://${apiUrl.slice(5)}/ws/logs`)

  socketRef.current.onmessage = (event) => {onMessage(event.data)}
  socketRef.current.onclose = () => {setTimeout(() => createLogsWebSocket(onMessage, onError, socketRef, reconnectInterval), reconnectInterval)}
  socketRef.current.onerror = (error) => {onError(error)}
}

export default createLogsWebSocket
