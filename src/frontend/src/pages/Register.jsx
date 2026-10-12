import { useState } from "react"
import Header from "../components/Header.jsx"
import AuthLayout from "../components/AuthLayout.jsx"
import { authRegister } from "../api/auth.js"
import { Eye, EyeClosed } from "lucide-react"

const Register = () => {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [email, setEmail] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    const result = await authRegister(login, password, (email !== "") ? email : null)
    console.log(result)
  }

  return (
    <div className="background">
      <Header />
      <div className="card remove-header-padding">
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
              <button className="password-button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Скрыть пароль" : "Показать пароль"}>
                {showPassword ? <Eye className="password-eye-icon" size={30} /> : <EyeClosed className="password-eye-icon" />}
              </button>
            </div>
            <button className="primary-button">Зарегистрироваться</button>
          </form>
        </AuthLayout>
      </div>
    </div>
  )
}

export default Register