import { useState, useEffect, useRef } from 'react'
import './App.css'
import {Home, Terminal, Clock, User} from 'lucide-react'

const API_URL = "http://127.0.0.1:8000/"

function App() {
  const [api_works, setApiWorks] = useState(false)

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

  const [server_works_level, setServerWorksLevel] = useState(0)
  const [server_software, setServerSoftware] = useState(undefined)
  const [minecraft_version, setMinecraftVersion] = useState(undefined)
  const [uptime_hours, setUptimeHours] = useState(0)
  const [uptime_minutes, setUptimeMinutes] = useState(0)
  const [uptime_seconds, setUptimeSeconds] = useState(0)

  const check_server_status = async () => {
    const data = await get_server_status()
    if (!data) {
      return
    }

    const software = data.data.info.server_software
    const status = data.data.info.status
    const version = data.data.info.minecraft_version
    const players = data.data.info.players
    const uptime = data.data.info.uptime.split(":")
    console.log("Статус сервера:", status)

    setPlayers((players == undefined) ? [] : players)

    if (status == "running") {
      setServerWorksLevel(2)
    } else if (status == "starting") {
      setServerWorksLevel(1)
    } else if (status == "stopping") {
      setServerWorksLevel(3)
    } else {
      setServerWorksLevel(0)
    }

    if (software !== undefined) {
      setServerSoftware(software[0].toUpperCase() + software.slice(1))
    }

    if (version !== undefined) {
      setMinecraftVersion(version)
    }

    setUptimeHours(uptime[0])
    setUptimeMinutes(uptime[1])
    setUptimeSeconds(uptime[2])
  }

  const [active_section, setActiveSection] = useState(1)
  const [logs, setLogs] = useState([])
  const [players, setPlayers] = useState([])
  const [max_players, setMaxPlayers] = useState(0)
  const console_input = useRef(null)

  useEffect(() => {
    const logs_websocket = new WebSocket("ws://"+API_URL.slice(5, API_URL.length)+"ws/logs")

    logs_websocket.onmessage = (event) => {
      update_logs(event.data)
    }

    logs_websocket.onclose = (event) => {}

    check_server_status()
    setInterval(async () => {check_server_status()}, 1000)

    return () => {
      logs_websocket.close();
    }
  }, [])

  const update_logs = (log) => {
    console.log(log)
    if (log == undefined) {
      return
    }
    setLogs(prev => {
        let updated = [...prev, log]
        return updated.slice(-1000)
    })
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

  const send_command = async (command) => {
      if (!command) {
        return undefined
      }
      const result = await fetch(API_URL + "command?command=" + command, {method: "POST"})
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

  const logsRef = useRef(null)

  const players_items = players.slice(0, 7).map((player, index) => {
    return (
      <div className="online-player-item" key={index}>
        <img className="online-player-item-image" src="steve.png" alt="player" width="35px" height="35px" />
        <h4 className="online-player-item-text">{player}</h4>
      </div>
    )
  })

  const logs_rows = logs.map((log, index) => {return <h5 key={index} className="log_row">{log}</h5>})

  useEffect(() => {
    const container = logsRef.current
    if (container.scrollHeight - container.scrollTop - container.clientHeight < 50) {
      container.scrollTop = container.scrollHeight      
    }
  }, [logs])

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
                  {(server_works_level == 3) && <h2 className="server-works-status" style={{color: "#208d44"}}>Сервер работает</h2>}
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
                  <h3 style={{fontSize: "30px", marginTop: "10px"}}>{uptime_hours ? uptime_hours : "-"}ч {uptime_minutes ? uptime_minutes : "-"}м {uptime_seconds ? uptime_seconds : "-"}с</h3>
                </div>
              </div>
            </div>
          </div>
          <div className="blocks2-div">
            <div className="online-players-card">
              <div className="online-players-card-header">
                <h3 className="online-players-card-header-text">Список игроков</h3>
              </div>
              {players_items}
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
            <div className=""></div>
          </div>
        </div>}
      </div>
    </div>
  )
}

export default App
