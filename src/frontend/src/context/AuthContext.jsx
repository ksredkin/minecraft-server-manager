import { createContext, useContext, useState } from "react"

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [authInfo, setAuthInfo] = useState(null)

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
