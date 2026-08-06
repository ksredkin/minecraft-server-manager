import { useState, useEffect, useRef } from 'react'
import './App.css'
import { Home, Terminal, Clock, User, Save, Package, Settings, File, MemoryStick, Cpu, Trash, ChevronDown, FileText } from 'lucide-react'

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
  
  let logs_websocket = useRef(undefined)
  const [logs, setLogs] = useState([])
  
  const console_input = useRef(undefined)
  const logsRef = useRef(undefined)
  const big_logsRef = useRef(undefined)
  const big_console_input = useRef(undefined)

  const [search, setSearch] = useState("")
  const [search_installed_plugins, setSearchInstalledPlugins] = useState("")

  const [search_plugins_input_value, setSearchPluginsInputValue] = useState("")
  const [searched_plugins, setSearchedPlugins] = useState([])
  const [installing_plugins, setInstallingPlugins] = useState([])
  const search_plugins_timer = useRef(undefined)

  const [search_backups, setSearchBackups] = useState("")
  const [backup_creates, setBackupCreates] = useState(false)

  const confirm_action_ref = useRef(undefined)
  const [confirm_dialog, setConfirmDialog] = useState({
    show: false,
    title: "",
    description: "",
    confirm_text: "",
    confirm_type: "success",
  })

  const server_works_level_texts = {0: "Сервер выключен", 1: "Сервер запускается", 2: "Сервер работает", 3: "Сервер выключается"}
  const server_properties_select_options = {
    difficulty: [
        "peaceful",
        "easy",
        "normal",
        "hard"
    ],

    gamemode: [
        "survival",
        "creative",
        "adventure",
        "spectator"
    ],

    "level-type": [
        "minecraft:normal",
        "minecraft:flat",
        "minecraft:large_biomes",
        "minecraft:amplified"
    ]
  }

  const [search_server_properties, setSearchServerProperties] = useState("")
  const [server_properties, setServerProperties] = useState({})
  const [edited_server_properties, setEditedServerProperties] = useState({})

  const [eula_status, setEulaStatus] = useState(undefined)


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

  const delete_backup = async (backup) => {
    await fetch(API_URL + "backups/" + backup, {method: "DELETE"})
  }

  const restore_backup = async (backup) => {
    await fetch(API_URL + "restore/" + backup, {method: "POST"})
  }

  const get_server_status = async () => {
    try {
      const result = await fetch(API_URL + "info")
      const data = await result.json()
      setApiWorks(true)
      return data
    } catch (error) {
      setApiWorks(false)
    }
  }

  const get_plugins = async () => {
    const result = await fetch(API_URL + "plugins/")
    return await result.json()
  }

  const delete_plugin = async (plugin) => {
    await fetch(API_URL + "plugins/delete/" + plugin, {method: "DELETE"})
  }

  const search_plugins = async (query) => {
    const result = await fetch(API_URL + "plugins/search?query=" + query)
    return await result.json()
  }

  const install_plugin = async (project_id_or_slug) => {
    await fetch(API_URL + "plugins/install/" + project_id_or_slug, {method: "POST"})
  }

  const get_server_properties = async () => {
    const result = await fetch(API_URL + "properties/")
    return await result.json()
  }

  const get_eula_status = async () => {
    const result = await fetch(API_URL + "eula/")
    return await result.json()
  }

  const set_eula_status = async (new_eula_status) => {
    await fetch(API_URL + "eula/?accept_eula=" + String(new_eula_status), {method: "POST"})
  }

  const update_server_property = async (key, new_value) => {
    await fetch(API_URL + "properties/" + encodeURIComponent(key) + `?value=${encodeURIComponent(new_value)}`, {method: "PUT"})
  }


  const handle_create_backup = async () => {
    try {
      if (api_works == false) return undefined
      setBackupCreates(true)
      await create_backup()
    } finally {
      setBackupCreates(false)
    }
  }

  const ask_confirmation = (action, title = "Вы уверены?", description = "Действие невозможно отменить.", confirm_text = "Подтвердить", confirm_type = "success") => {
    confirm_action_ref.current = action
    setConfirmDialog({show: true, title: title, description: description, confirm_text: confirm_text, confirm_type: confirm_type})
  }

  async function handle_confirm() {
      setConfirmDialog(prev => ({...prev, show: false}))
      if (confirm_action_ref.current) await confirm_action_ref.current()
      confirm_action_ref.current = undefined
  }

  function handle_cancel() {
      confirm_action_ref.current = undefined
      setConfirmDialog(prev => ({...prev, show: false}))
  }

  const handle_install_plugin = async (slug) => {
    setInstallingPlugins(prev => [...prev, slug])

    try {
        await install_plugin(slug)
    } finally {
        setInstallingPlugins(prev => prev.filter(plugin => plugin !== slug))
    }
  }
  
  const create_smart_search_plugins_timer = async (plugin) => {
    if (search_plugins_timer.current) clearTimeout(search_plugins_timer.current)
    if (plugin == "") return setSearchedPlugins([])

    search_plugins_timer.current = setTimeout(async () => {
      const result = await search_plugins(plugin)
      setSearchedPlugins(result.data.plugins)
    }, 1000)
  }
  
  const handle_delete_plugin_button = async (plugin_to_delete) => {
    setPlugins(prev => {
        let updated = [...prev].filter(plugin => plugin !== plugin_to_delete)
        return updated
    })
    await delete_plugin(plugin_to_delete)
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

  const check_eula_status = async () => {
    const actual_eula_status = await get_eula_status()
    setEulaStatus(actual_eula_status.data.eula)
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

  const check_server_properties = async () => {
    const actual_server_properties = await get_server_properties()
    setServerProperties(actual_server_properties.data.properties)
    setEditedServerProperties(actual_server_properties.data.properties)
  }

  const update_server_properties = async () => {
    const diff_keys = Object.keys(edited_server_properties).filter(key => edited_server_properties[key] !== server_properties[key])
    for (const key in diff_keys) {
      await update_server_property(diff_keys[key], edited_server_properties[diff_keys[key]])
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
    check_server_properties()
    check_eula_status()
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
      <div className="online-player-item" key={index} onClick={() => {setActiveSection(3); setSearch(player)}}>
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
        <button className={"big-players-card-item-kick-button button-enabled-" + api_works} onClick={() => send_command("kick " + player)}>Кикнуть</button>
        <button className={"big-players-card-item-ban-button button-enabled-" + api_works} onClick={() => send_command("ban " + player)}>Бан</button>
      </div>
    )
  })

  const filtered_installed_plugins = plugins.filter(plugin => plugin.toLowerCase().includes((search_installed_plugins.toLowerCase())))
  const installed_plugins_items = filtered_installed_plugins.map((plugin, index) => {
    return (
      <div className="left-big-plugins-card-subcard-items-div-item" key={index}>
        <Package className="big-plugins-card-subcard-items-div-package-image"/>
        <h4 className="big-plugins-card-subcard-items-div-item-text">{plugin[0].toUpperCase() + plugin.slice(1)}</h4>
        <button className={"big-plugins-card-subcard-items-div-item-delete-button button-enabled-" + api_works} onClick={() => delete_plugin(plugin)}><Trash className="big-plugins-card-subcard-items-div-item-delete-button-trash-image"/></button>
      </div>
    )
  })

  const get_install_plugin_button_or_status = (plugin) => {
    if (plugins.includes(plugin.slug)) return <h4 className="big-plugins-card-subcard-items-div-item-downloaded-text">Установлен</h4>
    if (installing_plugins.includes(plugin.slug)) return <h4 className="big-plugins-card-subcard-items-div-item-downloaded-text">Устанавливается...</h4>
    return <button className={"big-plugins-card-subcard-items-div-item-download-button button-enabled-" + (api_works && eula_status)} onClick={() => handle_install_plugin(plugin.slug)}>Установить</button>
  }

  const searched_plugins_items = searched_plugins.map((plugin, index) => {
    return <div key={index} className="big-plugins-card-subcard-items-div-item">
      <img className="big-plugins-card-subcard-items-div-item-image" src={plugin.icon_url}/>
      <h3>{plugin.title}</h3>
      <h4>{plugin.description}</h4>
      <div className="big-plugins-card-subcard-items-div-item-version-downloads-download-div">
        <h4 style={{marginTop: "5px"}}>✓ {minecraft_version}</h4>
        <h4 style={{marginTop: "5px"}}>{plugin.downloads} загрузок</h4>
        {get_install_plugin_button_or_status(plugin)}
      </div>
    </div>
  })

  const logs_rows = logs.map((log, index) => {return <h5 key={index} className="log-row">{log}</h5>})

  const reversed_backups = [...backups].reverse()
  const last_backups_backup_items = reversed_backups.map((backup, index) => {
    return <div key={index} className="last-backups-backup-item"  onClick={() => {setActiveSection(5); setSearchBackups(backup)}}>
        <File className="last-backups-file-svg"/>
        <h5>{backup}</h5>
      </div>
  })

  const filtered_backups = reversed_backups.filter(backup => backup.toLowerCase().includes(search_backups.toLowerCase()))
  const backups_items = filtered_backups.map((backup, index) => {
    return <div key={index} className="backups-card-items-div-item">
      <File className="backups-card-items-div-item-image"/>
      <h5 className="backups-card-items-div-item-text">{backup}</h5>
      <button className={"backups-card-items-div-item-restore-button button-enabled-" + api_works} onClick={() => {ask_confirmation(() => {restore_backup(backup)}, "Восстановить сервер?", "Текущее состояние сервера будет заменено выбранной резервной копией.", "Восстановить", "success")}}>Восстановить</button>
      <button className={"backups-card-items-div-item-delete-button button-enabled-" + api_works} onClick={() => {ask_confirmation(() => {delete_backup(backup)}, "Удалить резервную копию?", "После удаления восстановить её будет невозможно.", "Удалить", "danger")}}>Удалить</button>
    </div>
  })

  const plugins_card_plugins_items = plugins.map((plugin, index) => {
    return <div key={index} className="plugins-card-plugin-item" onClick={() => {setActiveSection(4); setSearchInstalledPlugins(plugin)}}>
        <Package className="plugins-card-file-svg"/>
        <h5>{((plugin[0].toUpperCase() + plugin.slice(1)).length < 39) ? (plugin[0].toUpperCase() + plugin.slice(1)) : (plugin[0].toUpperCase() + plugin.slice(1)).slice(0, 35) + "..."}</h5>
      </div>
  })

  const diff_keys = Object.keys(edited_server_properties).filter(key => edited_server_properties[key] !== server_properties[key])
  const filtered_server_properties = Object.fromEntries(Object.entries(edited_server_properties).filter(([key, value]) => key.toLowerCase().includes(search_server_properties.toLowerCase())))
  const server_properties_card_items = Object.entries(filtered_server_properties).map(([key, value], index) => {
    const updateProperty = (key, value) => setEditedServerProperties(prev => ({...prev, [key]: value}))
    let element = undefined

    if (server_properties_select_options?.[key]) {
      const sub_elements = server_properties_select_options[key].map(option => <option className="settings-card-item-select-option" key={option} value={option}>{option}</option>)
      element = <div className="settings-card-item-select-div"><select className="settings-card-item-select" value={value} onChange={(e) => updateProperty(key, e.target.value)}>{sub_elements}</select><ChevronDown className="settings-card-item-select-chevron-down"/></div>
    } else {
      if (value === "true" || value === "false") {
        element = <div className={`switch ${value === "true" ? "on" : ""}`} onClick={() => updateProperty(key, value === "true" ? "false" : "true")}>
          <div className={`switch-thumb`}></div>
        </div>
      } else {
        element = <input className="settings-card-item-value" placeholder="Введите значение..." value={value} onChange={(e) => updateProperty(key, e.target.value)}/>
      }
    }

    return <div key={index} className={"settings-card-item settings-card-item-edited-" + diff_keys.includes(key)}>
      <h4 className="settings-card-item-name">{key}</h4>
      {element}
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
        {(active_section == 1) && <div className="screen-1">
          <h2>Панель управления</h2>
          <div className="blocks1-div">
            <div className="block-background">
              <div style={{display: "flex"}}>
                <div className={"circle server-works-circle-level-" + server_works_level}></div>
                <div style={{marginLeft: "5px"}}>
                  <h2 className={"server-works-status server-works-status-level-" + server_works_level}>{server_works_level_texts[server_works_level]}</h2>
                  <h5 className="software-and-version-text">{(server_software !== undefined) ? server_software : "-"} {(minecraft_version !== undefined) ? minecraft_version : "-"}</h5>
                </div>
              </div>
              {(server_works_level == 0) && <button className={"start-server-button button-enabled-" + (api_works && eula_status)} onClick={start_server}>Запустить</button>}
              {(server_works_level == 2) && <button className={"stop-server-button button-enabled-" + api_works} onClick={stop_server}>Стоп</button>}
              {(server_works_level == 2) && <button className={"restart-server-button button-enabled-" + api_works} onClick={restart_server}>Перезапуск</button>}
            </div>

            {!eula_status && <div className="eula-card">
              <div className="eula-card-header">
                <FileText className="eula-card-header-icon" />
                <h5 className="eula-card-header-text">EULA</h5>
              </div>

              <div className="eula-card-content">
                <h5 className="eula-card-content-text">Для запуска сервера необходимо принять <a className="eula-card-content-text-mojang-eula-link" href="https://aka.ms/MinecraftEULA">лицензионное соглашение Minecraft (EULA)</a>.</h5>
                <button className={"eula-card-content-accept-eula-button button-enabled-" + (api_works && eula_status)} onClick={() => {if (api_works) {set_eula_status(true); setEulaStatus(true)}}}>Принять EULA</button>
              </div>
            </div>}

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
                <button onClick={() => setActiveSection(3)} className="online-players-card-footer-button">Все игроки →</button>
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
                <button className={"logs-card-send-button button-enabled-" + api_works} onClick={handle_console_send_button}>Отправить</button>
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
                {last_backups_backup_items}
              </div>
              <div className="last-backups-card-no-backups-text-div">
                {(backups.length == 0) && <h4 className="last-backups-card-no-backups-text">Бэкапов нет</h4>}
              </div>
              <button onClick={() => setActiveSection(5)} className="last-backups-card-footer-button">Все бэкапы →</button>
            </div>

            <div className="plugins-card">
              <h3 className="plugins-card-header-text">Установленные плагины</h3>
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
              <button className={"logs-card-send-button button-enabled-" + api_works} onClick={handle_big_console_send_button}>Отправить</button>
            </div>
          </div>
        </div>}
        
        {(active_section == 3) && <div className="screen-3">
          <div className="big-players-card">
            <div className="big-players-card-header">
              <h3 className="big-players-card-header-text">Игроки</h3>
            </div>

            <div className="big-players-card-subheader">
              <input value={search} onChange={(e) => setSearch(e.target.value)} type="text" className="big-players-card-footer-input" placeholder="🔍︎ Введите ник игрока..."/>
            </div>
            
            <div className="big-players-card-items-div">
              {big_players_card_items}
            </div>
            {(players.length == 0) && <h4 className="big-players-card-no-players-text">Сервер пуст</h4>}
          </div>  
        </div>}
        
        {(active_section == 4) && <div className="screen-4">
          <div className="big-plugins-card">
            <h2>Плагины</h2>
            <div className="big-plugins-card-subcards-div">
              <div className="big-plugins-card-subcard">
                <div className="big-plugins-card-subcard-header">
                  <h3 className="big-plugins-card-subcard-header-text">Установленные</h3>
                </div>

                <div className="big-plugins-card-subcard-header">
                  <input value={search_installed_plugins} onChange={(e) => setSearchInstalledPlugins(e.target.value)} type="text" className="big-plugins-card-subcard-footer-input" placeholder="🔍︎ Введите имя плагина..."/>
                </div>

                <div className="left-big-plugins-card-subcard-items-div">
                  {installed_plugins_items}
                  {(plugins.length == 0) && <h4 className="big-plugins-card-subcard-no-plugins-text">Плагинов нет</h4>}
                </div>
              </div>

              <div className="big-plugins-card-subcard">
                <div className="big-plugins-card-subcard-header">
                  <h3 className="big-plugins-card-subcard-header-text">Найти и установить</h3>
                </div>

                <div className="big-plugins-card-subcard-header">
                  <input value={search_plugins_input_value} onChange={(e) => {setSearchPluginsInputValue(e.target.value); create_smart_search_plugins_timer(e.target.value)}} type="text" className="big-plugins-card-subcard-footer-input" placeholder="🔍︎ Введите имя плагина..."/>
                </div>

                <div className="big-plugins-card-subcard-items-div">
                  {searched_plugins_items}
                  {(searched_plugins_items.length == 0) && <h4 className="big-plugins-card-subcard-no-plugins-text">Плагинов нет</h4>}
                </div>
              </div>
            </div>
          </div>
        </div>}

        {(active_section == 5) && <div className="screen-5">
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
        </div>}

        {(active_section == 6) && <div className="screen-6">
          <div className="server-properties-card">
            <div className="server-properties-card-header">
              <h3 className="server-properties-card-header-text">Настройки</h3>
            </div>

            <div className="server-properties-card-subheader">
              <input value={search_server_properties} onChange={(e) => setSearchServerProperties(e.target.value)} type="text" className="server-properties-card-search-input" placeholder="🔍︎ Введите имя настройки..."/>
              <button className={"server-properties-card-subheader-save-button button-enabled-" + api_works} onClick={() => {ask_confirmation(async () => {await update_server_properties()}, "Сохранить изменения?", "Изменённые настройки будут записаны в server.properties.", "Сохранить", "success")}}>{diff_keys.length == 0 ? "Сохранить настройки" : `Сохранить (${diff_keys.length} изменения)`}</button>
              <button className="server-properties-card-subheader-reset-button" onClick={() => {ask_confirmation(async () => {setEditedServerProperties(server_properties)}, "Отменить изменения?", "Все несохранённые изменения будут отменены.", "Отменить", "danger")}}>Отменить изменения</button>
            </div>

            <div className="server-properties-card-items-div">
              {(server_properties_card_items.length == 0) && <h4 className="server-properties-card-items-div-no-items-text">Настроек нет</h4>}
              {server_properties_card_items}
            </div>
          </div>
        </div>}

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
