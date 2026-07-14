import { useState, useEffect, useRef } from 'react'
import './App.css'
import {Home, Terminal, Clock, User, Save, Package, Settings, File, MemoryStick, Cpu} from 'lucide-react'

function App() {
  const API_URL = "http://127.0.0.1:8000/"

  const [api_works, setApiWorks] = useState(false)

  const [server_works_level, setServerWorksLevel] = useState(0)
  const [server_software, setServerSoftware] = useState(undefined)
  const [minecraft_version, setMinecraftVersion] = useState(undefined)
  const [players, setPlayers] = useState([])
  const [max_players, setMaxPlayers] = useState(0)
  const [backups, setBackups] = useState([])
  const [plugins, setPlugins] = useState([])
  const [uptime, setUptime] = useState("0:0:0:0")

  const [ram_total, setRamTotal] = useState(undefined)
  const [ram_used, setRamUsed] = useState(undefined)
  const [cpu_percent, setCpuPercent] = useState(undefined)

  const [active_section, setActiveSection] = useState(1)
  
  let logs_websocket = useRef(null)
  const [logs, setLogs] = useState([])
  
  const console_input = useRef(null)
  const logsRef = useRef(null)
  const big_logsRef = useRef(null)
  const big_console_input = useRef(null)

  const [search, setSearch] = useState("");


  const send_command = async (command) => {
      if (!command) return undefined
      const result = await fetch(API_URL + "command?command=" + command, {method: "POST"})
  }

  const get_ram_usage = async () => {
      const result = await fetch(API_URL + "metrics/ram")
      return result.json()
  }

  const get_cpu_percent = async () => {
      const result = await fetch(API_URL + "metrics/cpu")
      return result.json()
  }

  const start_server = async () => {
    await fetch(API_URL + "start", {method: "POST"})
    setServerWorksLevel(1)
  }

  const stop_server = async () => {
    await fetch(API_URL + "stop", {method: "POST"})
    setServerWorksLevel(3)
  }

  const restart_server = async () => {
    await fetch(API_URL + "restart", {method: "POST"})
    setServerWorksLevel(3)
  }

  const get_backups = async () => {
    const result = await fetch(API_URL + "backups/")
    return await result.json()
  }

  const create_backup = async () => {
    await fetch(API_URL + "backups/", {method: "POST"})
  }

  const get_server_status = async () => {
    try {
      const result = await fetch(API_URL + "info")
      const data = await result.json();
      setApiWorks(true)
      return data
    } catch (error) {
      console.log("Ошибка при получении статуса сервера:", error)
      setApiWorks(false)
    }
  }

  const get_plugins = async () => {
    const result = await fetch(API_URL + "plugins/")
    return await result.json()
  }


  const check_server_status = async () => {
    const data = await get_server_status()
    if (!data) return undefined

    const software = data.data.info.server_software
    const status = data.data.info.status
    const version = data.data.info.minecraft_version
    const players = data.data.info.players
    const max_players = data.data.info.max_players
    const uptime = data.data.info.uptime

    if (players !== undefined) setPlayers(players ? players : [])

    if (status == "running") setServerWorksLevel(2)
    else if (status == "starting") setServerWorksLevel(1)
    else if (status == "stopping") setServerWorksLevel(3)
    else setServerWorksLevel(0)

    if (software !== undefined) setServerSoftware(software[0].toUpperCase() + software.slice(1))

    if (version !== undefined) setMinecraftVersion(version)

    setUptime(uptime)
    setMaxPlayers(max_players)
  }

  const check_server_backups = async () => {
    const result = await get_backups()
    if (result.data !== undefined) {
      const backups_list = result.data.backups
      setBackups(backups_list)
    }
  }

  const check_ram_usage = async () => {
    const result = await get_ram_usage()
    if (result.data !== undefined) {
      setRamTotal(result.data.total)
      setRamUsed(result.data.used)
    }
  }

  const check_cpu_percent = async () => {
    const result = await get_cpu_percent()
    if (result.data !== undefined) {
      setCpuPercent(result.data.percent)
    }
  }

  const check_server_plugins = async () => {
    const result = await get_plugins()
    if (result.data !== undefined) {
      const plugins_list = result.data.plugins
      setPlugins(plugins_list)
    }
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


  const handle_console_input_key_down = async (event) => {
    if (event.key == "Enter") {
      await send_command(console_input.current.value)
      console_input.current.value = ""
    }
  }
  
  const handle_console_send_button = async () => {
    await send_command(console_input.current.value)
    console_input.current.value = ""
  }


  const handle_big_console_input_key_down = async (event) => {
    if (event.key == "Enter") {
      await send_command(big_console_input.current.value)
      big_console_input.current.value = ""
    }
  }

  const handle_big_console_send_button = async () => {
    await send_command(big_console_input.current.value)
    big_console_input.current.value = ""
  }


  useEffect(() => {
    connect_logs_ws()
    check_server_status()
    check_server_backups()
    check_server_plugins()
    check_ram_usage()
    check_cpu_percent()
    const interval = setInterval(async () => {
      check_server_status()
      check_server_backups()
      check_server_plugins()
      check_ram_usage()
      check_cpu_percent()
    }, 1000)
    return () => {clearTimeout(interval)}
  }, [])

  useEffect(() => {
    const container = big_logsRef.current
    if (!container) return undefined

    if (container.scrollHeight - container.scrollTop - container.clientHeight < 100) container.scrollTop = container.scrollHeight      
  }, [logs])

  useEffect(() => {
    const container = logsRef.current
    if (!container) return undefined

    if (container.scrollHeight - container.scrollTop - container.clientHeight < 100) container.scrollTop = container.scrollHeight      
  }, [logs])

  useEffect(() => {
    if (active_section == 1) logsRef.current.scrollTop = logsRef.current.scrollHeight
    else if (active_section == 2) big_logsRef.current.scrollTop = big_logsRef.current.scrollHeight
  }, [active_section])


  const players_items = players.map((player, index) => {
    return (
      <div className="online-player-item" key={index}>
        <img className="online-player-item-image" src="steve.png" alt="player" width="35px" height="35px" />
        <h4 className="online-player-item-text">{player}</h4>
      </div>
    )
  })

  const filtered_players_to_big_card = players.filter(player => player.toLowerCase().includes((search.toLowerCase())))
  const big_players_card_items = filtered_players_to_big_card.map((player, index) => {
    return (
      <div className="big-players-card-item" key={index}>
        <img className="big-players-card-item-image" src="steve.png" alt="player" width="35px" height="35px" />
        <h4 className="big-players-card-item-text">{player}</h4>
        <button className="big-players-card-item-kick-button" onClick={() => send_command("kick " + player)}>Кикнуть</button>
        <button className="big-players-card-item-ban-button" onClick={() => send_command("ban " + player)}>Бан</button>
      </div>
    )
  })

  const logs_rows = logs.map((log, index) => {return <h5 key={index} className="log-row">{log}</h5>})

  const reversed_backups = [...backups].reverse();
  const last_backups_backup_items = reversed_backups.map((backup, index) => {
    return <div key={index} className="last-backups-backup-item">
        <File className="last-backups-file-svg"/>
        <h5>{backup}</h5>
      </div>
  })

  const plugins_card_plugins_items = plugins.map((plugin, index) => {
    return <div key={index} className="plugins-card-plugin-item">
        <Package className="plugins-card-file-svg"/>
        <h5>{((plugin[0].toUpperCase() + plugin.slice(1)).length < 39) ? (plugin[0].toUpperCase() + plugin.slice(1)) : (plugin[0].toUpperCase() + plugin.slice(1)).slice(0, 35) + "..."}</h5>
      </div>
  })


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
            <Home className="home-svg"/>
            Панель управления
          </button>
          <button className={(active_section == 2) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(2)}>
            <Terminal className="home-svg"/>
            Консоль
          </button>
          <button className={(active_section == 3) ? "active-section-button" : "section-button"} onClick={() => setActiveSection(3)}>
            <User className="home-svg"/>
            Игроки
          </button>
        </div>
        <div className="sidebar-bottom-card">
          <div className="msm-api-works-header">
            <h4 style={{color: "rgb(215, 215, 215)"}}>MSM API</h4>
            <div className="circle" style={{background: (api_works == false) ? "#de0a0a" : "#26a550", width: "10px", height: "10px", marginTop: "6px", marginLeft: "auto"}}></div>
          </div>
          <h5 style={{color: (api_works == false) ? "#de0a0a" : "#26a550", marginTop: "-10px"}}>{(api_works == false) ? "Отключено" : "Подключено"}</h5>
        </div>
      </div>
      <div className="content">
        {(active_section == 1) && <div className="screen-1">
          <h2>Панель управления</h2>
          <div className="blocks1-div">
            <div className="block-background">
              <div style={{display: "flex"}}>
                <div className="circle" style={{background: (server_works_level == 0) ? "#de0a0a" : "#26a550"}}></div>
                <div style={{marginLeft: "5px"}}>
                  {(server_works_level == 0) && <h2 className="server-works-status" style={{color: "#de0a0a"}}>Сервер выключен</h2>}
                  {(server_works_level == 1) && <h2 className="server-works-status" style={{color: "#208d44"}}>Сервер запускается</h2>}
                  {(server_works_level == 2) && <h2 className="server-works-status" style={{color: "#26a550"}}>Сервер работает</h2>}
                  {(server_works_level == 3) && <h2 className="server-works-status" style={{color: "#208d44"}}>Сервер выключается</h2>}
                  <h5 className="software-and-version-text">{(server_software !== undefined) ? server_software : "-"} {(minecraft_version !== undefined) ? minecraft_version : "-"}</h5>
                </div>
              </div>
              {(server_works_level == 0) && <button className="start-server-button" onClick={start_server}>Запустить</button>}
              {(server_works_level == 2) && <button className="stop-server-button" onClick={stop_server}>Стоп</button>}
              {(server_works_level == 2) && <button className="restart-server-button" onClick={restart_server}>Перезапуск</button>}
            </div>
            <div className="short-block-background">
              <div className="online-card">
                <div className="online-header">
                  <User className="user-icon"/>
                  <h5 className="online-card-title">Онлайн</h5>
                </div>
                <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                  <h2 style={{fontSize: "30px", marginTop: "10px"}}>{players.length} / {(max_players > 0) ? max_players : "-"}</h2>
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
              <h2 style={{marginTop: "8px"}}>{ram_used ? ram_used : "-"}GB / {ram_total ? ram_total : "-"}GB</h2>
            </div>

            <div className="cpu-card">
              <div className="cpu-card-header-div">
                <Cpu className="cpu-card-cpu-svg"/>
                <h5>CPU</h5>
              </div>
              <h2 style={{marginTop: "8px"}}>{cpu_percent ? cpu_percent : "-"}%</h2>
            </div>
          </div>
          <div className="blocks2-div">
            <div className="online-players-card">
              <div className="online-players-card-header">
                <h3 className="online-players-card-header-text">Список игроков</h3>
              </div>
              <div className="online-players-card-items-div">
                {players_items}
              </div>
              {(players.length == 0) && <h4 className="online-players-card-no-players-text">Сервер пуст</h4>}
              <div className="online-players-card-footer">
                <button onClick={() => setActiveSection(3)} className="online-players-card-footer-button">Все игроки ({players.length}) →</button>
              </div>
            </div>
            
            <div className="logs-card">
              <div className="logs-card-header">
                <h3 className="logs-card-header-text">Логи сервера</h3>
              </div>
              
              <div className="logs-background" ref={logsRef}>
                {logs_rows}
              </div>

              <div className="logs-card-footer">
                <input className="logs-card-input" type="text" placeholder="Введите команду..." ref={console_input} onKeyDown={handle_console_input_key_down}/>
                <button className="logs-card-send-button" onClick={handle_console_send_button}>Отправить</button>
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
              <h3 style={{marginBottom: "5px"}}>Последние бэкапы</h3>
              <div className="last-backups-backups-items-div">
                {last_backups_backup_items}
              </div>
              <div className="last-backups-card-no-backups-text-div">
                {(backups.length == 0) && <h4 className="last-backups-card-no-backups-text">Бэкапов нет</h4>}
              </div>
              <button onClick={() => setActiveSection(5)} className="last-backups-card-footer-button">Все бэкапы →</button>
            </div>

            <div className="plugins-card">
              <h3 style={{marginBottom: "5px"}}>Установленные плагины</h3>
              <div className="plugins-card-items-div">
                {plugins_card_plugins_items}
              </div>
              <div className="plugins-card-no-plugins-text-div">
                {(plugins.length == 0) && <h4 className="plugins-card-no-plugins-text">Плагинов нет</h4>}
              </div>
              <button onClick={() => setActiveSection(4)} className="plugins-card-footer-button">Все плагины →</button>
            </div>
          </div>
        </div>}
        {(active_section == 2) && <div className="screen-2">
          <div className="big-logs-card">
            <div className="logs-card-header">
              <h3 className="logs-card-header-text">Консоль</h3>
            </div>
              
            <div className="big-logs-background" ref={big_logsRef}>
              {logs_rows}
            </div>

            <div className="logs-card-footer">
              <input className="logs-card-input" type="text" placeholder="Введите команду..." ref={big_console_input} onKeyDown={handle_big_console_input_key_down}/>
              <button className="logs-card-send-button" onClick={handle_big_console_send_button}>Отправить</button>
            </div>
          </div>
        </div>}
        {(active_section == 3) && <div className="screen-3">
          <div className="big-players-card">
            <div className="big-players-card-header">
              <h3 className="big-players-card-header-text">Игроки</h3>
            </div>
            <div className="big-players-card-items-div">
              {big_players_card_items}
            </div>
            {(players.length == 0) && <h4 className="big-players-cardno-players-text">Сервер пуст</h4>}
            <div className="big-players-card-footer">
              <input value={search} onChange={(e) => setSearch(e.target.value)} type="text" className="big-players-card-footer-input" placeholder="Введите ник игрока..."/>
            </div>
          </div>  
        </div>}
      </div>
    </div>
  )
}

export default App
