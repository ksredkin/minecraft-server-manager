import { Clock, User, Save, Package, Settings, File, MemoryStick, Cpu, FileText } from "lucide-react"
import { useRef, useLayoutEffect } from "react"

const serverWorksLevelTexts = {0: "Сервер выключен", 1: "Сервер запускается", 2: "Сервер работает", 3: "Сервер выключается"}

const HomePanel = ({
  activeSection,
  apiWorks,
  serverWorksLevel,
  onPlayerClick,
  setServerWorksLevel,
  logs = [],
  players = [],
  backups = [],
  plugins = [],
  serverSoftware,
  minecraftVersion,
  maxPlayers,
  eulaStatus,
  setEulaStatus,
  ramTotal,
  ramUsed,
  cpuPercent,
  uptime,
  setActiveSection,
  setSearchBackups,
  setSearchInstalledPlugins,
  handleStartServer,
  handleAcceptEula,
  handleStopServer,
  handleRestartServer,
  executeCommand
}) => {
  const terminalRef = useRef(undefined)
  const terminalInputRef = useRef(undefined)
  const shouldAutoScroll = useRef(true)

  const onTerminalScroll = () => {
    const container = terminalRef.current
    shouldAutoScroll.current = container.scrollHeight - container.scrollTop - container.clientHeight < 80
  }

  useLayoutEffect(() => {
    if (!shouldAutoScroll.current) return
    const container = terminalRef.current
    container.scrollTop = container.scrollHeight
  }, [logs])

  const sendCommand = async (command) => {
    if (command) await executeCommand(command)
  }

  const handleTerminalInputKeyDown = async (event, command) => {
    if (event.key == "Enter") {
      await sendCommand(command)
    }
  }

  const handleTerminalSendButton = async (command) => {
    await sendCommand(command)
  }

  const playersItems = players.map((player, index) => {
    return (
      <div className="online-player-item" key={index} onClick={() => {onPlayerClick(player)}}>
        <img className="online-player-item-image" src="steve.png" alt="player" width="35px" height="35px" />
        <h4 className="online-player-item-text">{player}</h4>
      </div>
    )
  })

  const logsRows = logs.map((log, index) => {return <h5 key={index} className="log-row">{log}</h5>})

  const reversedBackups = [...backups].reverse()
  const lastBackupsBackupItems = reversedBackups.map((backup, index) => {
    return <div key={index} className="last-backups-backup-item" onClick={() => {setActiveSection(5); setSearchBackups(backup)}}>
        <File className="last-backups-file-svg"/>
        <h5>{backup}</h5>
      </div>
  })

  const pluginsCardPluginsItems = plugins.map((plugin, index) => {
    return <div key={index} className="plugins-card-plugin-item" onClick={() => {setActiveSection(4); setSearchInstalledPlugins(plugin)}}>
        <Package className="plugins-card-file-svg"/>
        <h5>{((plugin[0].toUpperCase() + plugin.slice(1)).length < 39) ? (plugin[0].toUpperCase() + plugin.slice(1)) : (plugin[0].toUpperCase() + plugin.slice(1)).slice(0, 35) + "..."}</h5>
      </div>
  })

  return (<div className="panel">
    <h2>Панель управления</h2>
    <div className="blocks1-div">
      <div className="block-background">
        <div style={{display: "flex"}}>
          <div className={"circle server-works-circle-level-" + serverWorksLevel}></div>
          <div style={{marginLeft: "5px"}}>
            <h2 className={"server-works-status server-works-status-level-" + serverWorksLevel}>{serverWorksLevelTexts[serverWorksLevel]}</h2>
            <h5 className="software-and-version-text">{(serverSoftware !== undefined) ? serverSoftware : "-"} {(minecraftVersion !== undefined) ? minecraftVersion : "-"}</h5>
          </div>
        </div>

        {(serverWorksLevel == 0) && <button className={"start-server-button button-enabled-" + (apiWorks && eulaStatus)} onClick={handleStartServer}>Запустить</button>}
        {(serverWorksLevel == 2) && <button className={"stop-server-button button-enabled-" + apiWorks} onClick={handleStopServer}>Стоп</button>}
        {(serverWorksLevel == 2) && <button className={"restart-server-button button-enabled-" + apiWorks} onClick={handleRestartServer}>Перезапуск</button>}
      </div>

      {!eulaStatus && <div className="eula-card">
        <div className="eula-card-header">
          <FileText className="eula-card-header-icon" />
          <h5 className="eula-card-header-text">EULA</h5>
        </div>

        <div className="eula-card-content">
          <h5 className="eula-card-content-text">Для запуска сервера необходимо принять <a className="eula-card-content-text-mojang-eula-link" href="https://aka.ms/MinecraftEULA">лицензионное соглашение Minecraft (EULA)</a>.</h5>
          <button className={"eula-card-content-accept-eula-button button-enabled-" + (apiWorks && eulaStatus)} onClick={handleAcceptEula}>Принять EULA</button>
        </div>
      </div>}

      <div className="short-block-background">
        <div className="online-card">
          <div className="online-header">
            <User className="user-icon"/>
            <h5 className="online-card-title">Онлайн</h5>
          </div>

          <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
            <h2 style={{fontSize: "30px", marginTop: "10px"}}>{players.length} / {(maxPlayers > 0) ? maxPlayers : "-"}</h2>
            <h2 style={{fontSize: "13px", marginTop: "10px", color: "rgb(215, 215, 215)"}}>игроков</h2>
          </div>
        </div>
      </div>
      <div className="short-block-background">
        <div className="uptime-card">
          <div className="uptime-card-header">
            <Clock className="clock-icon"/>
            <h5 className="uptime-card-title">Время работы</h5>
          </div>
          <div style={{display: "flex", flexDirection: "row", alignItems: "center"}}>
            <h3 style={{fontSize: "30px", marginTop: "10px"}}>{uptime && typeof uptime === 'string' ? (
              <>
                {uptime.split(":")[0] !== "0" ? uptime.split(":")[0] + "д " : ""}
                {uptime.split(":")[1] !== "0" ? uptime.split(":")[1] + "ч " : ""}
                {uptime.split(":")[2] !== "0" ? uptime.split(":")[2] + "м " : ""}
                {uptime.split(":")[3] !== "0" ? uptime.split(":")[3] + "с " : "0с"}
              </>) : "0с"}
            </h3>
          </div>
        </div>
      </div>

      <div className="ram-card">
        <div className="ram-card-header-div">
          <MemoryStick className="ram-card-memory-stick-svg" />
          <h5>RAM</h5>
        </div>
        <h2 style={{marginTop: "8px"}}>{ramUsed ? ramUsed : "-"}GB / {ramTotal ? ramTotal : "-"}GB</h2>
      </div>

      <div className="cpu-card">
        <div className="cpu-card-header-div">
          <Cpu className="cpu-card-cpu-svg"/>
          <h5>CPU</h5>
        </div>
        <h2 style={{marginTop: "8px"}}>{cpuPercent ? cpuPercent : "-"}%</h2>
      </div>
    </div>

    <div className="blocks2-div">
      <div className="online-players-card">
        <div className="online-players-card-header">
          <h3 className="online-players-card-header-text">Список игроков</h3>
        </div>
              
        <div className="online-players-card-items-div">
          {playersItems}
        </div>
        {(players.length == 0) && <h4 className="online-players-card-no-players-text">Сервер пуст</h4>}
              
        <div className="online-players-card-footer">
          <button onClick={() => setActiveSection(3)} className="online-players-card-footer-button">Все игроки →</button>
        </div>
      </div>
            
      <div className="logs-card">
        <div className="logs-card-header">
          <h3 className="logs-card-header-text">Логи сервера</h3>
        </div>
              
        <div className="logs-background" ref={terminalRef} onScroll={onTerminalScroll}>
          {logsRows}
        </div>

        <div className="logs-card-footer">
          <input className="logs-card-input" type="text" placeholder="Введите команду..." ref={terminalInputRef} onKeyDown={(event) => {
            if (event.key === "Enter") {
              handleTerminalInputKeyDown(event, terminalInputRef.current.value)
              terminalInputRef.current.value = ""
            }
          }}/>
          <button className={"logs-card-send-button button-enabled-" + apiWorks} onClick={() => {
            handleTerminalSendButton(terminalInputRef.current.value)
            terminalInputRef.current.value = ""
          }}>Отправить</button>
        </div>
      </div>
    </div>

    <div className="blocks3-div">
      <div className="fast-actions-card">
        <h3 style={{marginBottom: "8px"}}>Быстрые действия</h3>
        <button className="fast-action-button" onClick={() => {setActiveSection(5)}}><Save className="fast-action-icon"/>Создать бэкап</button>
        <button className="fast-action-button" onClick={() => {setActiveSection(6)}}><Settings className="fast-action-icon"/>Открыть server.properties</button>
        <button className="fast-action-button" onClick={() => {setActiveSection(4)}}><Package className="fast-action-icon"/>Установить плагин</button>
      </div>
            
      <div className="last-backups-card">
        <h3 className="last-backups-card-header-text">Последние бэкапы</h3>
        <div className="last-backups-backups-items-div">
          {lastBackupsBackupItems}
        </div>
        <div className="last-backups-card-no-backups-text-div">
          {(backups.length == 0) && <h4 className="last-backups-card-no-backups-text">Бэкапов нет</h4>}
        </div>
        <button onClick={() => setActiveSection(5)} className="last-backups-card-footer-button">Все бэкапы →</button>
      </div>

      <div className="plugins-card">
        <h3 className="plugins-card-header-text">Установленные плагины</h3>
        <div className="plugins-card-items-div">
          {pluginsCardPluginsItems}
        </div>
        <div className="plugins-card-no-plugins-text-div">
          {(plugins.length == 0) && <h4 className="plugins-card-no-plugins-text">Плагинов нет</h4>}
        </div>
        <button onClick={() => setActiveSection(4)} className="plugins-card-footer-button">Все плагины →</button>
      </div>
    </div>
  </div>)
}

export default HomePanel
