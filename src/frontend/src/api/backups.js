import { API_URL } from '../constants/api.js'


export const getBackups = async () => {
  const response = await fetch(`${API_URL}/backups/`)
  return await response.json()
}

export const createBackup = async () => {
  await fetch(`${API_URL}/backups/`, {method: "POST"})
}

export const deleteBackup = async (backup) => {
  await fetch(`${API_URL}/backups/${backup}`, {method: "DELETE"})
}

export const restoreBackup = async (backup) => {
  await fetch(`${API_URL}/backups/restore/${backup}`, {method: "POST"})
}
