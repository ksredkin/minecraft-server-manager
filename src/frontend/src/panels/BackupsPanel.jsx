import { useState } from "react"
import { File} from "lucide-react"
import { deleteBackup, restoreBackup } from "../api/backups"


const BackupsPanel = ({search_backups, api_works, createBackup, backups, backup_creates, setBackupCreates, ask_confirmation, deleteBackup, restoreBackup, setSearchBackups}) => {
  const handle_create_backup = async () => {
    try {
      if (api_works == false) return undefined
      setBackupCreates(true)
      await createBackup()
    } finally {
      setBackupCreates(false)
    }
  }

  const reversed_backups = [...backups].reverse()
  const filtered_backups = reversed_backups.filter(backup => backup.toLowerCase().includes(search_backups.toLowerCase()))
  const backups_items = filtered_backups.map((backup, index) => {
    return <div key={index} className="backups-card-items-div-item">
      <File className="backups-card-items-div-item-image"/>
      <h5 className="backups-card-items-div-item-text">{backup}</h5>
      <button className={"backups-card-items-div-item-restore-button button-enabled-" + api_works} onClick={() => {ask_confirmation(() => {restoreBackup(backup)}, "Восстановить сервер?", "Текущее состояние сервера будет заменено выбранной резервной копией.", "Восстановить", "success")}}>Восстановить</button>
      <button className={"backups-card-items-div-item-delete-button button-enabled-" + api_works} onClick={() => {ask_confirmation(() => {deleteBackup(backup)}, "Удалить резервную копию?", "После удаления восстановить её будет невозможно.", "Удалить", "danger")}}>Удалить</button>
    </div>
  })

  return (<div className="panel">
    <div className="backups-card">
      <div className="backups-card-header">
        <h3 className="backups-card-header-text">Бэкапы</h3>
      </div>

      <div className="backups-card-subheader">
        <input value={search_backups} onChange={(e) => {setSearchBackups(e.target.value)}} type="text" className="backups-card-footer-input" placeholder="🔍︎ Введите имя бэкапа..."/>
        {(backup_creates && api_works) && <h4 className="backups-card-item-is-creating">Создается бэкап...</h4>}
        {!backup_creates && <button className={"backups-card-subheader-button button-enabled-" + api_works} onClick={handle_create_backup}>Создать бэкап</button>}
      </div>

      <div className="backups-card-items-div">
        {backups_items}
        {(backups_items.length == 0) && <h4 className="backups-card-items-div-no-items-text">Бэкапов нет</h4>}
      </div>
    </div>
  </div>)
}

export default BackupsPanel
