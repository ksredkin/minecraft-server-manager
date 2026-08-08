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
  const [serverSoftware, setServerSoftware] = useState(undefined)
  const [minecraftVersion, setMinecraftVersion] = useState(undefined)
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
    await startServer()
    setServerWorksLevel(1)
  }

  const handleStopServer = async () => {
    await stopServer()
    setServerWorksLevel(3)
  }

  const handleRestartServer = async () => {
    await restartServer()
    setServerWorksLevel(3)
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


  useEffect(() => {
    createLogsWebSocket(updateLogs, () => {logsWebsocket.close()}, logsWebsocket)
    
    checkBackups()
    checkServerPlugins()
    checkServerInfo()
    checkMetrics()

    checkServerProperties()
    checkEulaStatus()
    const interval = setInterval(async () => {
      await checkBackups()
      await checkServerPlugins()
      await checkServerInfo()
      await checkMetrics()
    }, 1000)
    return () => {clearInterval(interval)}
  }, [])


  const backupsPanelProps = {searchBackups, apiWorks, createBackup, backups, backupCreates, setBackupCreates, showConfirm, deleteBackup, restoreBackup, setSearchBackups}
  const propertiesPanelProps = {showConfirm, setEditedServerProperties, serverProperties, editedServerProperties, apiWorks, updateServerProperties}
  const pluginsPanelProps = {setSearchInstalledPlugins, plugins, searchInstalledPlugins, apiWorks, deletePlugin, searchPlugins, installPlugin}
  const homePanelProps = {
    activeSection,
    apiWorks,
    serverWorksLevel,
    onPlayerClick: openPlayer,
    setServerWorksLevel,
    logs,
    players,
    backups,
    plugins,
    serverSoftware,
    minecraftVersion,
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
    <div className="background">
      <Sidebar apiWorks={apiWorks} activeSection={activeSection} setActiveSection={setActiveSection} />
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
  )
}


export default App
