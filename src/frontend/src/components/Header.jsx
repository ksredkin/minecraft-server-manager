import { Sun, Moon } from "lucide-react"
import { useState, useEffect } from "react"
import { useNavigate } from 'react-router-dom'
import { useAuth } from "../context/AuthContext.jsx"
import { useLocation } from "react-router-dom"
import { Link } from 'react-router-dom'

const Header = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { authInfo } = useAuth()

  console.log(authInfo)

  let showLogin = false 
  let showRegiser = false

  if (!authInfo && location.pathname == "/") {
    showLogin = true
    showRegiser = true
  } else if (!authInfo && location.pathname == "/login") {
    showRegiser = true
  } else if (!authInfo && location.pathname == "/register") {
    showLogin = true
  }

  const showUser = authInfo ? true : false

  const [dark, setDark] = useState(() => {
    return localStorage.getItem("theme") !== "light"
  })

  useEffect(() => {
    document.documentElement.classList.toggle("light", !dark)
    localStorage.setItem("theme", dark ? "dark" : "light")
  }, [dark])
  
  return (
    <div className="header">
      <div className="header-left">
        <Link to="/" className="header-logo-link">
          <img className="header-logo" src="logo.png" alt="MSM" />
        </Link>
        <h1 className="header-left-text">MSM</h1>
        <h1 className="header-left-text-divider">|</h1>
        <h1 className="header-left-long-text">Minecraft Server Manager</h1>
      </div>
      <div className="header-center">

      </div>
      <div className="header-right">
        <button className="small-padding" onClick={() => dark ? setDark(false) : setDark(true)}>{dark ? <Sun className="icon" /> : <Moon className="icon" />}</button>
        {showLogin && <button className={location.pathname == "/" ? "secondary-button" : "secondary-button"} onClick={() => {navigate("/login")}}>Войти</button>}
        {showRegiser && <button className={location.pathname == "/" ? "primary-button" : "secondary-button"} onClick={() => {navigate("/register")}}>Регистрация</button>}
        {showUser && <button className="primary-button" onClick={() => {navigate("/servers")}}>Мои серверы</button>}
        {showUser && <div className="header-user-div"><img src="logo.png" className="user-icon" /></div>}
      </div>
    </div>)
}


export default Header