import { useState, useEffect, useRef } from "react"
import "./App.css"

import { getBackups, createBackup, deleteBackup, restoreBackup } from "./api/backups.js"
import { getServerInfo, startServer, stopServer, restartServer, executeCommand } from "./api/server.js"
import { getEulaStatus, setEulaStatus as setEulaStatusApi } from "./api/eula.js"
import { getCpuPercent, getRamUsage } from "./api/metrics.js"
import { getPlugins, deletePlugin, searchPlugins, installPlugin } from "./api/plugins.js"
import { getServerProperties, updateServerProperty } from "./api/properties.js"
import createLogsWebSocket from "./api/logs.js"

import HomePanel from "./panels/HomePanel.jsx"
import TerminalPanel from "./panels/TerminalPanel.jsx"
import PlayersPanel from "./panels/PlayersPanel.jsx"
import PluginsPanel from "./panels/PluginsPanel.jsx"
import BackupsPanel from "./panels/BackupsPanel.jsx"
import PropertiesPanel from "./panels/PropertiesPanel.jsx"
import ConfirmDialog from "./components/ConfirmDialog.jsx"
import Sidebar from "./components/Sidebar.jsx"


const App = () => {
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
  const [searchPlayers, setSearchPlayers] = useState("")

  const [backups, setBackups] = useState([])
  const [search_backups, setSearchBackups] = useState("")
  const [backup_creates, setBackupCreates] = useState(false)

  const [plugins, setPlugins] = useState([])
  const [search_installed_plugins, setSearchInstalledPlugins] = useState("")
  
  const [active_section, setActiveSection] = useState(1)

  let logs_websocket = useRef(undefined)
  const [logs, setLogs] = useState([])

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

  const handle_accept_eula = async () => {
    if (api_works) {
      await setEulaStatusApi(true)
      setEulaStatus(true)
    }
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
    await deletePlugin(plugin_to_delete)
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

  const check_metrics = async () => {
    const ram_usage = await getRamUsage()
    const cpu_percent = await getCpuPercent()
    setCpuPercent(cpu_percent.data.percent)
    setRamTotal(ram_usage.data.total)
    setRamUsed(ram_usage.data.used)
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
    for (const key of diff_keys) {
      await updateServerProperty(key, edited_server_properties[key])
    }
    setServerProperties(edited_server_properties)
  }

  const showConfirm = (action, title = "Вы уверены?", description = "Действие невозможно отменить.", confirm_text = "Подтвердить", confirm_type = "success") => {
    confirm_action_ref.current = action
    setConfirmDialog({show: true, title: title, description: description, confirm_text: confirm_text, confirm_type: confirm_type})
  }

  const update_logs = (log) => {
    if (log == undefined) return
    setLogs(prev => {
      let updated = [...prev, log]
      return updated.slice(-1000)
    })
  }

  const openPlayer = (player) => {
    setSearch(player)
    setActiveSection(3)
  }


  useEffect(() => {
    createLogsWebSocket(update_logs, () => {logs_websocket.close()}, logs_websocket)
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
    return () => {clearInterval(interval)}
  }, [])


  const backups_panel_props = {search_backups, api_works, createBackup, backups, backup_creates, setBackupCreates, showConfirm, deleteBackup, restoreBackup, setSearchBackups}
  const properties_panel_props = {showConfirm, setEditedServerProperties, server_properties, edited_server_properties, api_works, update_server_properties}
  const plugins_panel_props = {setSearchInstalledPlugins, plugins, search_installed_plugins, api_works, deletePlugin, searchPlugins, installPlugin}
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
      <Sidebar api_works={api_works} active_section={active_section} setActiveSection={setActiveSection} />
      <div className="content">
        {(active_section == 1) && <HomePanel {...home_panel_props} />}
        {(active_section == 2) && <TerminalPanel executeCommand={executeCommand} api_works={api_works} logs={logs} />}
        {(active_section == 3) && <PlayersPanel players={players} executeCommand={executeCommand} search={searchPlayers} setSearch={setSearchPlayers} />}
        {(active_section == 4) && <PluginsPanel {...plugins_panel_props} />}
        {(active_section == 5) && <BackupsPanel {...backups_panel_props} />}
        {(active_section == 6) && <PropertiesPanel {...properties_panel_props} />}
        <ConfirmDialog dialog={confirm_dialog} onConfirm={handle_confirm} onCancel={handle_cancel} />
      </div>
    </div>
  )
}


export default App
