import { useState } from "react"
import Header from "../components/Header.jsx"
import { authLogin } from "../api/auth.js"

const Login = () => {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = async (event) => {
    event.preventDefault()
    const result = await authLogin(login, password)
    console.log(result)
  }

  return (
    <div className="background">
      <Header />
      <div className="card remove-header-padding">
        <div className="login">
          <img src="login.png" className="login-image" />
          <div className="gap">
            <h1>Войти</h1>
            <form className="form" onSubmit={handleSubmit}>
              <label>
                Логин
                <input onChange={e => setLogin(e.target.value)} value={login} name="login" className="form-input" type="text" placeholder="Введите логин..." />
              </label>
              <label>
                Пароль
                <input onChange={e => setPassword(e.target.value)} value={password} name="password" className="form-input" type="password" placeholder="Введите пароль..." />
              </label>
              <button className="primary-button">Войти</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login