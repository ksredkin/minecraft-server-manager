import { useState } from "react"
import Header from "../components/Header.jsx"
import AuthLayout from "../components/AuthLayout.jsx"
import { authLogin } from "../api/auth.js"
import { Eye, EyeClosed, AlertCircle } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext.jsx"

const Login = () => {
  const navigate = useNavigate()
  const { refreshAuth } = useAuth()

  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  const [error, setError] = useState(null)

  const handleSubmit = async (event) => {
    event.preventDefault()
    try {
      const result = await authLogin(login, password)

      if (result.success) {
        await refreshAuth()
        navigate("/servers")
      } else {
        setError("Неверный логин или пароль.")
      }
    } catch (error) {
      setError("Неверный логин или пароль.")
    }
  }

  return (
    <div>
      <div className="sticky-header">
        <Header />      
      </div>
      <div className="background login-background">
        <div className="card remove-header-padding centered-card">
          <AuthLayout imageSrc="login.png">
            <h1>Войти</h1>
            <form className="form" onSubmit={handleSubmit}>
              <label>
                Логин
                <input onChange={e => {setLogin(e.target.value); setError(null)}} value={login} name="login" className="form-input" type="text" placeholder="Введите логин..." />
              </label>
              <div className="password-items">
                <label>
                  Пароль
                  <input onChange={e => {setPassword(e.target.value); setError(null)}} value={password} name="password" className="form-input" type={showPassword ? "text" : "password"} placeholder="Введите пароль..." />
                </label>
                <button type="button" className="password-button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Скрыть пароль" : "Показать пароль"}>
                  {showPassword ? <Eye className="password-eye-icon" size={30} /> : <EyeClosed className="password-eye-icon" />}
                </button>
              </div>
              {error && <div className="error">
                <AlertCircle size={20} className="error-icon" />
                <h3>{error}</h3>
              </div>}
              <button className="primary-button">Войти</button>
            </form>
          </AuthLayout>
        </div>
      </div>
    </div>
  )
}

export default Login