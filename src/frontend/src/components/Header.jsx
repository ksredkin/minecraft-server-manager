import { Sun, Moon, Settings, SquareArrowRightExit, Crown, Shield, Eye } from "lucide-react"
import { useState, useEffect } from "react"
import { useNavigate } from 'react-router-dom'
import { useAuth } from "../context/AuthContext.jsx"
import { useLocation } from "react-router-dom"
import { Link } from 'react-router-dom'
import { authExit } from '../api/auth.js'
import Dropdown from "../components/Dropdown.jsx"

const Header = ({ role = null }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { authInfo, logout } = useAuth()

  const showLogin = !authInfo && location.pathname !== "/login"
  const showRegister = !authInfo && location.pathname !== "/register"
  let showMyServers = authInfo && location.pathname === "/"

  const showUser = authInfo ? true : false

  const [dark, setDark] = useState(() => {
    return localStorage.getItem("theme") !== "light"
  })

  useEffect(() => {
    document.documentElement.classList.toggle("light", !dark)
    localStorage.setItem("theme", dark ? "dark" : "light")
  }, [dark])
  
  let roleItem = null

  if (role == "owner") {
      roleItem = <div className="server-role-owner">
        <Crown />
        <h3>Владелец</h3>
      </div>
  } else if (role == "admin") {
      roleItem = <div className="server-role-admin">
        <Shield />
        <h3>Администратор</h3>
      </div>
  } else if (role == "viewer") {
      roleItem = <div className="server-role-viewer">
        <Eye />
        <h3>Наблюдатель</h3>
      </div>
  }

  return (
    <div className="header">
      <div className="header-left">
        <Link to="/" className="header-logo-link">
          <img className="header-logo" src="/logo.png" alt="MSM" />
        </Link>
        <h1 className="header-left-text">MSM</h1>
        <h1 className="header-left-text-divider">|</h1>
        <h1 className="header-left-long-text">Minecraft Server Manager</h1>
      </div>
      <div className="header-center">

      </div>
      <div className="header-right">
        {roleItem}
        <button className="small-padding" onClick={() => dark ? setDark(false) : setDark(true)}>{dark ? <Sun className="icon" /> : <Moon className="icon" />}</button>
        {showLogin && <button className={location.pathname == "/" ? "secondary-button" : "secondary-button"} onClick={() => {navigate("/login")}}>Войти</button>}
        {showRegister && <button className={location.pathname == "/" ? "primary-button" : "secondary-button"} onClick={() => {navigate("/register")}}>Регистрация</button>}
        {showMyServers && <button className="primary-button" onClick={() => {navigate("/servers")}}>Мои серверы</button>}
        {showUser && <Dropdown trigger={<img src="/logo.png" className="user-icon" />} addtitionalGap={10} options={[
          {text: "Настройки", icon: Settings, action: () => {console.log("Настройки")}},
          {text: "Выйти", icon: SquareArrowRightExit, action: () => {logout(); authExit()}, styles: "red"},
        ]} position="left" />}
      </div>
    </div>)
}


export default Header