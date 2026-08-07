import { useState, useEffect, useRef } from "react"
import "./App.css"
import { Home, Terminal, Clock, User, Save, Package, Settings, File, MemoryStick, Cpu, Trash, ChevronDown, FileText } from "lucide-react"
import HomePanel from "./panels/HomePanel.jsx"
import TerminalPanel from "./panels/TerminalPanel.jsx"
import PlayersPanel from "./panels/PlayersPanel.jsx"
import PluginsPanel from "./panels/PluginsPanel.jsx"
import BackupsPanel from "./panels/BackupsPanel.jsx"
import PropertiesPanel from "./panels/PropertiesPanel.jsx"
import { getBackups, createBackup, deleteBackup, restoreBackup } from "./api/backups.js"
import { getServerInfo, startServer, stopServer, restartServer, executeCommand } from "./api/server.js"
import { getEulaStatus, setEulaStatus as setEulaStatusApi } from "./api/eula.js"
import { getCpuPercent, getRamUsage } from "./api/metrics.js"
import { getPlugins, deletePlugin, searchPlugins, installPlugin } from "./api/plugins.js"
import { getServerProperties, updateServerProperty } from "./api/properties.js"


function App() {
  const API_URL = "http://127.0.0.1:8000/"

  const [server_software, setServerSoftware] = useState(undefined)
  const [minecraft_version, setMinecraftVersion] = useState(undefined)
  const [max_players, setMaxPlayers] = useState(0)
  const [eula_status, setEulaStatus] = useState(true)

  const [ram_total, setRamTotal] = useState(undefined)
  const [ram_used, setRamUsed] = useState(undefined)
  const [cpu_percent, setCpuPercent] = useState(undefined)
  
  const [uptime, setUptime] = useState("0:0:0:0")

  const [api_works, setApiWorks] = useState(false)
  const [server_works_level, setServerWorksLevel] = useState(0)
  const [players, setPlayers] = useState([])

  const [backups, setBackups] = useState([])
  const [plugins, setPlugins] = useState([])

  const [backup_creates, setBackupCreates] = useState(false)
  const [active_section, setActiveSection] = useState(1)
  
  let logs_websocket = useRef(undefined)
  const [logs, setLogs] = useState([])

  const [search_installed_plugins, setSearchInstalledPlugins] = useState("")
  const [search_backups, setSearchBackups] = useState("")


  const confirm_action_ref = useRef(undefined)
  const [confirm_dialog, setConfirmDialog] = useState({
    show: false,
    title: "",
    description: "",
    confirm_text: "",
    confirm_type: "success",
  })

  const [server_properties, setServerProperties] = useState({})
  const [edited_server_properties, setEditedServerProperties] = useState({})

  const handle_start_server = async () => {
    await startServer()
    setServerWorksLevel(1)
  }

  const handle_stop_server = async () => {
    await stopServer()
    setServerWorksLevel(3)
  }

  const handle_restart_server = async () => {
    await restartServer()
    setServerWorksLevel(3)
  }

  const check_server_info = async () => {
    const server_info = await getServerInfo()
    setServerSoftware(server_info.data.info.server_software[0].toUpperCase() + server_info.data.info.server_software.slice(1))
    setMinecraftVersion(server_info.data.info.minecraft_version)
    setMaxPlayers(server_info.data.info.max_players)
    setUptime(server_info.data.info.uptime)
  }

  const check_eula_status = async () => {
    setEulaStatus((await getEulaStatus()).data.eula)
  }

  const handle_accept_eula = async () => {
    if (api_works) {
      await setEulaStatusApi(true)
      setEulaStatus(true)
    }
  }

  const check_metrics = async () => {
    const ram_usage = await getRamUsage()
    const cpu_percent = await getCpuPercent()
    setCpuPercent(cpu_percent.data.percent)
    setRamTotal(ram_usage.data.total)
    setRamUsed(ram_usage.data.used)
  }

  const ask_confirmation = (action, title = "Вы уверены?", description = "Действие невозможно отменить.", confirm_text = "Подтвердить", confirm_type = "success") => {
    confirm_action_ref.current = action
    setConfirmDialog({show: true, title: title, description: description, confirm_text: confirm_text, confirm_type: confirm_type})
  }

  const handle_confirm = async () => {
    setConfirmDialog(prev => ({...prev, show: false}))
    if (confirm_action_ref.current) await confirm_action_ref.current()
    confirm_action_ref.current = undefined
  }

  const handle_cancel = async () => {
    confirm_action_ref.current = undefined
    setConfirmDialog(prev => ({...prev, show: false}))
  }
  
  const handle_delete_plugin_button = async (plugin_to_delete) => {
    setPlugins(prev => {
        let updated = [...prev].filter(plugin => plugin !== plugin_to_delete)
        return updated
    })
    await delete_plugin(plugin_to_delete)
  }

  const check_server_status = async () => {
    try {
      const server_info = await getServerInfo()
      setApiWorks(true)

      setPlayers(server_info.data.info.players)

      switch (server_info.data.info.status) {
        case "starting":
          setServerWorksLevel(1)
          break
        case "running":
          setServerWorksLevel(2)
          break
        case "stopping":
          setServerWorksLevel(3)
          break
        default:
          setServerWorksLevel(0)
          break
      }
    } catch {
      setApiWorks(false)
    }
  }

  const check_backups = async () => {
    setBackups((await getBackups()).data.backups)
  }

  const check_server_plugins = async () => {
    setPlugins((await getPlugins()).data.plugins)
  }

  const check_server_properties = async () => {
    const server_properties = (await getServerProperties()).data.properties
    setServerProperties(server_properties)
    setEditedServerProperties(server_properties)
  }

  const update_server_properties = async () => {
    const diff_keys = Object.keys(edited_server_properties).filter(key => edited_server_properties[key] !== server_properties[key])
    for (const key in diff_keys) {
      await updateServerProperty(diff_keys[key], edited_server_properties[diff_keys[key]])
    }
    setServerProperties(edited_server_properties)
  }


  const update_logs = (log) => {
    if (log == undefined) return undefined
    
    setLogs(prev => {
        let updated = [...prev, log]
        return updated.slice(-1000)
    })
  }

  const connect_logs_ws = () => {
    if (logs_websocket.current && logs_websocket.current.readyState !== 3) return undefined

    logs_websocket.current = new WebSocket("ws://"+API_URL.slice(5, API_URL.length)+"ws/logs")

    logs_websocket.current.onmessage = (event) => {update_logs(event.data)}
    logs_websocket.current.onclose = (event) => {setTimeout(connect_logs_ws, 3000)}
    logs_websocket.current.onerror = (error) => {logs_websocket.current.close()}
  }


  useEffect(() => {
    connect_logs_ws()
    check_server_status()
    check_backups()
    check_server_plugins()
    check_server_properties()
    check_server_info()
    check_eula_status()
    check_metrics()
    const interval = setInterval(async () => {
      check_server_status()
      check_backups()
      check_server_plugins()
      check_server_info()
      check_metrics()
    }, 1000)
    return () => {clearTimeout(interval)}
  }, [])

  const openPlayer = (player) => {
    setSearch(player)
    setActiveSection(3)
  }

  const home_panel_props = {
    active_section,
    api_works,
    server_works_level,
    onPlayerClick: openPlayer,
    setServerWorksLevel,
    logs,
    players,
    backups,
    plugins,
    server_software,
    minecraft_version,
    max_players,
    eula_status,
    ram_total,
    ram_used,
    cpu_percent,
    uptime,
    setActiveSection,
    setSearchBackups,
    setSearchInstalledPlugins,
    handle_start_server,
    handle_stop_server,
    handle_restart_server,
    handle_accept_eula,
    executeCommand
  }

  return (
    <div className="background">
      <div className="sidebar">
        <div className="logo-div">
          <img className="logo" src="logo.png" alt="logo" />
          <div className="tool-name-div">
            <h1 className="short-tool-name">MSM</h1>
            <h6 className="tool-name">Minecraft Server Manager</h6>
          </div>
        </div>
        <div className="sections-div">
          <button className={(active_section == 1) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(1)}>
            <Home className="section-button-icon"/>
            Панель управления
          </button>
          <button className={(active_section == 2) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(2)}>
            <Terminal className="section-button-icon"/>
            Консоль
          </button>
          <button className={(active_section == 3) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(3)}>
            <User className="section-button-icon"/>
            Игроки
          </button>
          <button className={(active_section == 4) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(4)}>
            <Package className="section-button-icon"/>
            Плагины
          </button>
          <button className={(active_section == 5) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(5)}>
            <File className="section-button-icon"/>
            Бэкапы
          </button>
          <button className={(active_section == 6) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(6)}>
            <Settings className="section-button-icon"/>
            Настройки
          </button>
        </div>
        <div className="sidebar-bottom-card">
          <div className="msm-api-works-header">
            <h4 style={{color: "rgb(215, 215, 215)"}}>MSM API</h4>
            <div className="circle" style={{backgroundColor: (api_works == false) ? "#de0a0a" : "#26a550", width: "10px", height: "10px", marginTop: "6px", marginLeft: "auto", transition: "background-color 0.15s ease"}}></div>
          </div>
          <h5 style={{color: (api_works == false) ? "#de0a0a" : "#26a550", marginTop: "-10px", transition: "color 0.15s ease"}}>{(api_works == false) ? "Отключено" : "Подключено"}</h5>
        </div>
      </div>
      <div className="content">
        {(active_section == 1) && <HomePanel {...home_panel_props} />}
        {(active_section == 2) && <TerminalPanel executeCommand={executeCommand} api_works={api_works} logs={logs} />}
        {(active_section == 3) && <PlayersPanel players={players} executeCommand={executeCommand} />}
        {(active_section == 4) && <PluginsPanel setSearchInstalledPlugins={setSearchInstalledPlugins} plugins={plugins} search_installed_plugins={search_installed_plugins} api_works={api_works} deletePlugin={deletePlugin} searchPlugins={searchPlugins} installPlugin={installPlugin} />}
        {(active_section == 5) && <BackupsPanel search_backups={search_backups} api_works={api_works} createBackup={createBackup} backups={backups} backup_creates={backup_creates} setBackupCreates={setBackupCreates} ask_confirmation={ask_confirmation} deleteBackup={deleteBackup} restoreBackup={restoreBackup} setSearchBackups={setSearchBackups} />}
        {(active_section == 6) && <PropertiesPanel ask_confirmation={ask_confirmation} setEditedServerProperties={setEditedServerProperties} server_properties={server_properties} edited_server_properties={edited_server_properties} api_works={api_works} update_server_properties={update_server_properties} />}

        {confirm_dialog.show && <div className="confirm-action-card-background">
          <div className="confirm-action-card">
            <h3 className="confirm-action-card-header-text">{confirm_dialog.title}</h3>
            <h5 className="confirm-action-card-header-description">{confirm_dialog.description}</h5>
            <div className="confirm-action-card-buttons-div">
              <button className={"confirm-action-card-confirm-button confirm-action-card-confirm-button-" + confirm_dialog.confirm_type} onClick={handle_confirm}>{confirm_dialog.confirm_text}</button>
              <button className="confirm-action-card-cancel-button" onClick={handle_cancel}>Отмена</button>
            </div>
          </div>
        </div>}
      </div>
    </div>
  )
}

export default App
