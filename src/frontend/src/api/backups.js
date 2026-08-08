import { apiUrl } from '../constants/api.js'


export const getBackups = async () => {
  const response = await fetch(`${apiUrl}/backups/`)
  return await response.json()
}

export const createBackup = async () => {
  await fetch(`${apiUrl}/backups/`, {method: "POST"})
}

export const deleteBackup = async (backup) => {
  await fetch(`${apiUrl}/backups/${backup}`, {method: "DELETE"})
}

export const restoreBackup = async (backup) => {
  await fetch(`${apiUrl}/backups/restore/${backup}`, {method: "POST"})
}
