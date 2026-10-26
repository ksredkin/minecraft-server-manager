import { Home, Terminal, User, Package, Settings, File, ChevronLeft } from "lucide-react"
import { useNavigate } from "react-router-dom"

const Sidebar = ({activeSection, setActiveSection}) => {
  const navigate = useNavigate()
  return (<div className="sidebar">
      <button onClick={() => navigate("/servers")}>
        <ChevronLeft className="section-button-icon"/>
        К списку серверов
      </button>
      <button className={(activeSection == 1) ? "secondary-button" : ""} onClick={() => setActiveSection(1)}>
        <Home className="section-button-icon"/>
        Панель управления
      </button>
      <button className={(activeSection == 2) ? "secondary-button" : ""} onClick={() => setActiveSection(2)}>
        <Terminal className="section-button-icon"/>
        Консоль
      </button>
      <button className={(activeSection == 3) ? "secondary-button" : ""} onClick={() => setActiveSection(3)}>
        <User className="section-button-icon"/>
        Игроки
      </button>
      <button className={(activeSection == 4) ? "secondary-button" : ""} onClick={() => setActiveSection(4)}>
        <Package className="section-button-icon"/>
        Плагины
      </button>
      <button className={(activeSection == 5) ? "secondary-button" : ""} onClick={() => setActiveSection(5)}>
        <File className="section-button-icon"/>
        Бэкапы
      </button>
      <button className={(activeSection == 6) ? "secondary-button" : ""} onClick={() => setActiveSection(6)}>
        <Settings className="section-button-icon"/>
        Настройки
      </button>
  </div>)
}

export default Sidebar
