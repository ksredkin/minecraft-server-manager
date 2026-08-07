import { Home, Terminal, User, Package, Settings, File } from "lucide-react"

const Sidebar = ({active_section, api_works, setActiveSection}) => {
  return (<div className="sidebar">
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
  </div>)
}

export default Sidebar
