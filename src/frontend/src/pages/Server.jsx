import { useState, useEffect, useRef } from "react"
import "../App.css"
import { useParams } from "react-router-dom"

import { getBackups, createBackup, deleteBackup, restoreBackup } from "../api/backups.js"
import { getServerInfo, getServer, updateServer, startServer, stopServer, restartServer, executeCommand, connectServerWebsocket } from "../api/servers.js"
import { getEulaStatus, setEulaStatus as setEulaStatusApi } from "../api/eula.js"
import { getCpuPercent, getRamUsage } from "../api/metrics.js"
import { getPlugins, deletePlugin, searchPlugins, installPlugin } from "../api/plugins.js"
import { getServerProperties, updateServerProperty } from "../api/properties.js"
import Header from "../components/Header.jsx"
import HomePanel from "../panels/HomePanel.jsx"
import TerminalPanel from "../panels/TerminalPanel.jsx"
import PlayersPanel from "../panels/PlayersPanel.jsx"
import PluginsPanel from "../panels/PluginsPanel.jsx"
import BackupsPanel from "../panels/BackupsPanel.jsx"
import PropertiesPanel from "../panels/PropertiesPanel.jsx"
import ConfirmDialog from "../components/ConfirmDialog.jsx"
import Sidebar from "../components/Sidebar.jsx"


const Server = () => {
  const { uuid } = useParams()

  const serverWebsocket = useRef(null)
  const [serverStatus, setServerStatus] = useState(null)
  const [displayName, setDisplayName] = useState(null)
  const [role, setRole] = useState(null)
  const [serverCreatedDate, setServerCreatedDate] = useState(null)
  const [serverSoftware, setServerSoftware] = useState(null)
  const [minecraftVersion, setMinecraftVersion] = useState(null)


  const [maxPlayers, setMaxPlayers] = useState(0)
  const [eulaStatus, setEulaStatus] = useState(true)

  const [ramTotal, setRamTotal] = useState(undefined)
  const [ramUsed, setRamUsed] = useState(undefined)
  const [cpuPercent, setCpuPercent] = useState(undefined)

  const [uptime, setUptime] = useState("0:0:0:0")
  const [apiWorks, setApiWorks] = useState(false)
  const [serverWorksLevel, setServerWorksLevel] = useState(0)

  const [players, setPlayers] = useState([])
  const [searchPlayers, setSearchPlayers] = useState("")

  const [backups, setBackups] = useState([])
  const [searchBackups, setSearchBackups] = useState("")
  const [backupCreates, setBackupCreates] = useState(false)

  const [plugins, setPlugins] = useState([])
  const [searchInstalledPlugins, setSearchInstalledPlugins] = useState("")
  
  const [activeSection, setActiveSection] = useState(1)

  let logsWebsocket = useRef(undefined)
  const [logs, setLogs] = useState([])

  const confirmActionRef = useRef(undefined)
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    title: "",
    description: "",
    confirmText: "",
    confirmType: "success",
  })

  const [serverProperties, setServerProperties] = useState({})
  const [editedServerProperties, setEditedServerProperties] = useState({})


  const handleStartServer = async () => {
    await startServer(uuid)
    setServerStatus("starting")
  }

  const handleStopServer = async () => {
    await stopServer(uuid)
    setServerStatus("stopping")
  }

  const handleRestartServer = async () => {
    await restartServer(uuid)
    setServerStatus("stopping")
  }

  const handleAcceptEula = async () => {
    if (apiWorks) {
      await setEulaStatusApi(true)
      setEulaStatus(true)
    }
  }

  const handleConfirm = async () => {
    setConfirmDialog(prev => ({...prev, show: false}))
    if (confirmActionRef.current) await confirmActionRef.current()
    confirmActionRef.current = undefined
  }

  const handleCancel = async () => {
    confirmActionRef.current = undefined
    setConfirmDialog(prev => ({...prev, show: false}))
  }
  
  const handleDeletePluginButton = async (pluginToDelete) => {
    setPlugins(prev => {
      let updated = [...prev].filter(plugin => plugin !== pluginToDelete)
      return updated
    })
    await deletePlugin(pluginToDelete)
  }


  const checkServerInfo = async () => {
    try {
      const serverInfo = await getServerInfo()
      setApiWorks(true)

      if (Array.isArray(serverInfo.data.info.players)) setPlayers(serverInfo.data.info.players)
      setServerSoftware(serverInfo.data.info.server_software[0].toUpperCase() + serverInfo.data.info.server_software.slice(1))
      setMinecraftVersion(serverInfo.data.info.minecraft_version)
      setMaxPlayers(serverInfo.data.info.max_players)
      setUptime(serverInfo.data.info.uptime)

      switch (serverInfo.data.info.status) {
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

  const checkEulaStatus = async () => {
    setEulaStatus((await getEulaStatus()).data.eula)
  }

  const checkMetrics = async () => {
    const ramUsage = await getRamUsage()
    const cpuPercent = await getCpuPercent()
    setCpuPercent(cpuPercent.data.percent)
    setRamTotal(ramUsage.data.total)
    setRamUsed(ramUsage.data.used)
  }

  const checkBackups = async () => {
    setBackups((await getBackups()).data.backups)
  }

  const checkServerPlugins = async () => {
    setPlugins((await getPlugins()).data.plugins)
  }

  const checkServerProperties = async () => {
    const serverProperties = (await getServerProperties()).data.properties
    setServerProperties(serverProperties)
    setEditedServerProperties(serverProperties)
  }


  const updateServerProperties = async () => {
    const diffKeys = Object.keys(editedServerProperties).filter(key => editedServerProperties[key] !== serverProperties[key])
    for (const key of diffKeys) {
      await updateServerProperty(key, editedServerProperties[key])
    }
    setServerProperties(editedServerProperties)
  }

  const showConfirm = (action, title = "Вы уверены?", description = "Действие невозможно отменить.", confirmText = "Подтвердить", confirmType = "success") => {
    confirmActionRef.current = action
    setConfirmDialog({show: true, title: title, description: description, confirmText: confirmText, confirmType: confirmType})
  }

  const updateLogs = (log) => {
    if (log == undefined) return
    setLogs(prev => {
      let updated = [...prev, log]
      return updated.slice(-1000)
    })
  }

  const openPlayer = (player) => {
    setSearchPlayers(player)
    setActiveSection(3)
  }

  const handleServerWebSocketMessage = (message) => {
    console.log(message)
    const status = message.status

    setServerStatus(status.status)
    setMinecraftVersion(status.minecraft_version)
    setServerSoftware(status.server_software)
  }

  const connectWebSocket = async () => {
    if (serverWebsocket.current) return

    const websocket = await connectServerWebsocket(uuid)
    websocket.onmessage = (e) => {handleServerWebSocketMessage(JSON.parse(e.data))}
    websocket.onclose = () => {serverWebsocket.current = null}

    serverWebsocket.current = websocket
  }

  const refreshServerInfo = async () => {
    const info = (await getServer(uuid))
    console.log(info)
    setDisplayName(info.display_name)
    setRole(info.role)

    const dateObject = new Date(info.created_at)
    const formatter = new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })

    const formattedDate = formatter.formatToParts(dateObject)
      .map(part => part.type === 'literal' && part.value.includes('в') ? ' ' : part.value)
      .join('')
      .replace(/\s+/g, ' ')
      .trim()
    setServerCreatedDate(formattedDate)
  }

  useEffect(() => {
    const interval = setInterval(() => {
      connectWebSocket()
      refreshServerInfo()
    }, 1000)

    refreshServerInfo()
    return () => {clearInterval(interval)}
  }, [])


  const backupsPanelProps = {searchBackups, apiWorks, createBackup, backups, backupCreates, setBackupCreates, showConfirm, deleteBackup, restoreBackup, setSearchBackups}
  const propertiesPanelProps = {showConfirm, setEditedServerProperties, serverProperties, editedServerProperties, apiWorks, updateServerProperties}
  const pluginsPanelProps = {setSearchInstalledPlugins, plugins, searchInstalledPlugins, apiWorks, deletePlugin, searchPlugins, installPlugin}
  const homePanelProps = {
    uuid,
    displayName,
    role,
    serverCreatedDate,
    updateServer,
    serverSoftware,
    minecraftVersion,
    activeSection,
    apiWorks,
    serverStatus,
    onPlayerClick: openPlayer,
    logs,
    players,
    backups,
    plugins,
    maxPlayers,
    eulaStatus,
    ramTotal,
    ramUsed,
    cpuPercent,
    uptime,
    setActiveSection,
    setSearchBackups,
    setSearchInstalledPlugins,
    handleStartServer,
    handleStopServer,
    handleRestartServer,
    handleAcceptEula,
    executeCommand
  }


  return (
    <div>
      <div className="sticky-header">
        {role ? <Header role={role} /> : <Header />}
      </div>
      <div className="wrapper">
        <div className="sticky-sidebar">
          <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
        </div>
        <div className="content">
          {(activeSection == 1) && <HomePanel {...homePanelProps} />}
          {(activeSection == 2) && <TerminalPanel executeCommand={executeCommand} apiWorks={apiWorks} logs={logs} />}
          {(activeSection == 3) && <PlayersPanel players={players} executeCommand={executeCommand} searchPlayers={searchPlayers} setSearchPlayers={setSearchPlayers} apiWorks={apiWorks} />}
          {(activeSection == 4) && <PluginsPanel {...pluginsPanelProps} />}
          {(activeSection == 5) && <BackupsPanel {...backupsPanelProps} />}
          {(activeSection == 6) && <PropertiesPanel {...propertiesPanelProps} />}
          <ConfirmDialog dialog={confirmDialog} onConfirm={handleConfirm} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  )
}


export default Server
