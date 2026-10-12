import { createContext, useContext, useState, useEffect } from "react"
import { authMe } from "../api/auth.js"

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [authInfo, setAuthInfo] = useState(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const data = await authMe()
        setAuthInfo(data.user)
      } catch (error) {
        console.error("Пользователь не авторизован:", error)
        setAuthInfo(null)
      }
    }
  
    checkAuth()
  }, [])

  const login = (userInfo) => {
    setAuthInfo(userInfo)
  }

  const logout = () => {
    setAuthInfo(null)
  }

  return (<AuthContext.Provider value={{ authInfo, login, logout }}>
    {children}
  </AuthContext.Provider>)
}

export const useAuth = () => {
  return useContext(AuthContext)
}
