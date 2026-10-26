import { useState } from "react"
import Header from "../components/Header.jsx"
import AuthLayout from "../components/AuthLayout.jsx"
import { authRegister } from "../api/auth.js"
import { Eye, EyeClosed, AlertCircle } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext.jsx"

const Register = () => {
  const navigate = useNavigate()
  const { refreshAuth } = useAuth()

  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [email, setEmail] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  const [error, setError] = useState(null)
  
  const handleSubmit = async (event) => {
    event.preventDefault()
    try {
      const result = await authRegister(login, password)

      if (result.success) {
        await refreshAuth()
        navigate("/servers")
      } else {
        setError("Аккаунт уже существует.")
      }
    } catch (error) {
      setError("Аккаунт уже существует.")
    }
  }

  return (
    <div>
      <div className="sticky-header">
        <Header />      
      </div>
      <div className="background login-background">
        <div className="card remove-header-padding centered-card">
          <AuthLayout imageSrc="register.png">
            <h1>Регистрация</h1>
            <form className="form" onSubmit={handleSubmit}>
              <label>
                Логин
                <input onChange={e => setLogin(e.target.value)} value={login} name="login" className="form-input" type="text" placeholder="Введите логин..." />
              </label>
              <label>
                Почта (необязательно)
                <input onChange={e => setEmail(e.target.value)} value={email} name="email" className="form-input" type="text" placeholder="Введите почту..." />
              </label>
              <div className="password-items">
                <label>
                  Пароль
                  <input onChange={e => setPassword(e.target.value)} value={password} name="password" className="form-input" type={showPassword ? "text" : "password"} placeholder="Введите пароль..." />
                </label>
                <button type="button" className="password-button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Скрыть пароль" : "Показать пароль"}>
                  {showPassword ? <Eye className="password-eye-icon" size={30} /> : <EyeClosed className="password-eye-icon" />}
                </button>
              </div>
              {error && <div className="error">
                <AlertCircle size={20} className="error-icon" />
                <h3>{error}</h3>
              </div>}
              <button className="primary-button">Зарегистрироваться</button>
            </form>
          </AuthLayout>
        </div>
      </div>
    </div>
  )
}

export default Register