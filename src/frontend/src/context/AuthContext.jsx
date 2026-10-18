import { createContext, useContext, useState, useEffect } from "react"
import { authMe } from "../api/auth.js"
import { useLocation, useNavigate } from "react-router-dom"

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const [authInfo, setAuthInfo] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  const refreshAuth = async () => {
    const data = await authMe()
    setAuthInfo(data.user)
  }

  useEffect(() => {
    refreshAuth().catch((error) => {
      console.error("Не удалось проверить авторизацию:", error)
      setAuthInfo(null)
    }).finally(() => {
      setAuthLoading(false)
    })
  }, [])

  //useEffect(() => {
  //  if (!authLoading && !authInfo && location.pathname === "/servers") {
  //    navigate("/login", { replace: true })
  //  }
  //}, [authInfo, authLoading, location.pathname, navigate])

  const login = (userInfo) => {
    setAuthInfo(userInfo)
  }

  const logout = () => {
    setAuthInfo(null)
  }

  return (<AuthContext.Provider value={{ authInfo, login, logout, refreshAuth }}>
    {children}
  </AuthContext.Provider>)
}

export const useAuth = () => {
  return useContext(AuthContext)
}
