import { API_URL } from "../constants/api.js"

const createLogsWebSocket = async ({onMessage, onClose, socketRef, reconnectInterval = 3000}) => {
  if (socketRef.current && socketRef.current.readyState !== 3) return

  socketRef.current = new WebSocket(`ws://${API_URL.slice(5)}/ws/logs`)

  socketRef.current.onmessage = (event) => {onMessage(event.data)}
  socketRef.current.onclose = (event) => {setTimeout(createLogsWebSocket, reconnectInterval)}
  socketRef.current.onerror = (error) => {onClose(error)}
}

export default createLogsWebSocket
