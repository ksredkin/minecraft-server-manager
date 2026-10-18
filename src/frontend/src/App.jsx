import { BrowserRouter, Routes, Route } from "react-router-dom"
import Server from "./pages/Server.jsx"
import Home from "./pages/Home.jsx"
import Login from "./pages/Login.jsx"
import Register from "./pages/Register.jsx"
import Servers from "./pages/Servers.jsx"
import { AuthProvider } from "./context/AuthContext.jsx"


const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/server" element={<Server />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/servers" element={<Servers />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}


export default App
