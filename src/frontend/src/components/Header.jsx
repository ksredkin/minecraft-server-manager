import { Sun, Moon } from "lucide-react"
import { useState, useEffect } from "react"
import { useNavigate } from 'react-router-dom'

const Header = () => {
  const navigate = useNavigate()

  const [dark, setDark] = useState(() => {
    return localStorage.getItem("theme") !== "light"
  })

  useEffect(() => {
    document.documentElement.classList.toggle("light", !dark)
    localStorage.setItem("theme", dark ? "dark" : "light")
  }, [dark])
  
  return (
  <div className="background">
    <div className="header">
      <div className="header-left">
        <a className="link-no-underline" href="/">
          <img className="header-logo" src="logo.png" alt="MSM" />
        </a>
        <h1 className="header-left-text">MSM</h1>
        <h1 className="header-left-text-divider">|</h1>
        <h1 className="header-left-long-text">Minecraft Server Manager</h1>
      </div>
      <div className="header-center">

      </div>
      <div className="header-right">
        <button className="small-padding" onClick={() => dark ? setDark(false) : setDark(true)}>{dark ? <Sun className="icon" /> : <Moon className="icon" />}</button>
        <button className="secondary-button" onClick={() => {navigate("/login")}}>Войти</button>
        <button className="primary-button" onClick={() => {navigate("/register")}}>Регистрация</button>
      </div>
    </div>
  </div>)
}


export default Header