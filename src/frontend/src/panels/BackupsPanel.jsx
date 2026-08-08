import { useState } from "react"
import { File} from "lucide-react"
import { deleteBackup, restoreBackup } from "../api/backups"


const BackupsPanel = ({searchBackups, apiWorks, createBackup, backups, backupCreates, setBackupCreates, showConfirm, deleteBackup, restoreBackup, setSearchBackups}) => {
  const handleCreateBackup = async () => {
    try {
      if (apiWorks == false) return undefined
      setBackupCreates(true)
      await createBackup()
    } finally {
      setBackupCreates(false)
    }
  }

  const reversedBackups = [...backups].reverse()
  const filteredBackups = reversedBackups.filter(backup => backup.toLowerCase().includes(searchBackups.toLowerCase()))
  const backupsItems = filteredBackups.map((backup, index) => {
    return <div key={index} className="backups-card-items-div-item">
      <File className="backups-card-items-div-item-image"/>
      <h5 className="backups-card-items-div-item-text">{backup}</h5>
      <button className={"backups-card-items-div-item-restore-button button-enabled-" + apiWorks} onClick={() => {showConfirm(() => {restoreBackup(backup)}, "Восстановить сервер?", "Текущее состояние сервера будет заменено выбранной резервной копией.", "Восстановить", "success")}}>Восстановить</button>
      <button className={"backups-card-items-div-item-delete-button button-enabled-" + apiWorks} onClick={() => {showConfirm(() => {deleteBackup(backup)}, "Удалить резервную копию?", "После удаления восстановить её будет невозможно.", "Удалить", "danger")}}>Удалить</button>
    </div>
  })

  return (<div className="panel">
    <div className="backups-card">
      <div className="backups-card-header">
        <h3 className="backups-card-header-text">Бэкапы</h3>
      </div>

      <div className="backups-card-subheader">
        <input value={searchBackups} onChange={(e) => {setSearchBackups(e.target.value)}} type="text" className="backups-card-footer-input" placeholder="🔍︎ Введите имя бэкапа..."/>
        {(backupCreates && apiWorks) && <h4 className="backups-card-item-is-creating">Создается бэкап...</h4>}
        {!backupCreates && <button className={"backups-card-subheader-button button-enabled-" + apiWorks} onClick={handleCreateBackup}>Создать бэкап</button>}
      </div>

      <div className="backups-card-items-div">
        {backupsItems}
        {(backupsItems.length == 0) && <h4 className="backups-card-items-div-no-items-text">Бэкапов нет</h4>}
      </div>
    </div>
  </div>)
}

export default BackupsPanel
