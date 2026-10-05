import { BrowserRouter, Routes, Route } from "react-router-dom"
import Server from "./pages/Server.jsx"
import Home from "./pages/Home.jsx"
import Login from "./pages/Login.jsx"


const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/server" element={<Server />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  )
}


export default App
