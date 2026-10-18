import { useEffect, useRef, useState } from "react"
import Header from "../components/Header.jsx"
import CustomSelect from "../components/CustomSelect.jsx"
import { getServers } from "../api/servers.js"
import { ChevronRight, Crown, Shield, Eye, MoreVertical, Trash } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext.jsx"
import Dropdown from "../components/Dropdown.jsx"
import ConfirmDialog from "../components/ConfirmDialog.jsx"
import { deleteServer } from "../api/servers.js"

const Servers = () => {
  const [search, setSearch] = useState("")
  const [sortBy, setSortBy] = useState("name")
  const navigate = useNavigate()
  const pointerStartedOnExcludedElement = useRef(false)

  const confirmActionRef = useRef(undefined)
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    title: "",
    description: "",
    confirmText: "",
    confirmType: "success",
  })

  const [servers, setServers] = useState([])

  const getUserServers = async () => {
    const APIServers = await getServers()
    if (!APIServers?.detail) {
      setServers(APIServers)
    }
  }

  useEffect(() => {
    getUserServers()
  }, [])

  const searchedServers = servers.filter((server) => {return server.display_name.includes(search)})

  let sortedServers = searchedServers
  
  if (sortBy == "name") {
    sortedServers = searchedServers.sort((a, b) => {
      const stringA = a?.name || ''
      const stringB = b?.name || ''
      return stringA.localeCompare(stringB)
    }
  )}

  let showNoServersFound = false
  if (searchedServers.length == 0) {
    showNoServersFound = true
  } 

  const serverItems = sortedServers.map((server, index) => {
    let roleItem = null

    if (server.role == "owner") {
      roleItem = <div className="server-role-owner">
        <Crown />
        <h3>Владелец</h3>
      </div>
    } else if (server.role == "admin") {
      roleItem = <div className="server-role-admin">
        <Shield />
        <h3>Администратор</h3>
      </div>
    } else if (server.role == "viewer") {
      roleItem = <div className="server-role-viewer">
        <Eye />
        <h3>Наблюдатель</h3>
      </div>
    }

    const dateObject = new Date(server.created_at)
    const formatter = new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })

    const formattedDate = formatter.formatToParts(dateObject)
      .map(part => part.type === 'literal' && part.value.includes('в') ? ' ' : part.value)
      .join('')
      .replace(/\s+/g, ' ')
      .trim()

    return (
      <div
        key={index}
        className="server"
        onPointerDown={(event) => {
          pointerStartedOnExcludedElement.current = Boolean(
            event.target.closest("h3, h4, .server-image, .dropdown")
          )
        }}
        onClick={(event) => {
          const shouldIgnoreClick = pointerStartedOnExcludedElement.current
          pointerStartedOnExcludedElement.current = false
          if (shouldIgnoreClick || event.target.closest("h3, h4, .server-image, .dropdown")) return
          navigate(`/servers/${server.uuid}`)
        }}
      >
        <div className="server-left">
          <img className="server-image" src="server.png" />
          <div className="column">
            <h3 className="server-name">{server.display_name}</h3>
            <h4 className="server-created-date">Создан {formattedDate}</h4>
          </div>
        </div>
        <div className="server-right">
          {roleItem}
          <Dropdown trigger={<MoreVertical />} options={[{"text": "Удалить", "icon": Trash, "styles": "red", "action": () => {showConfirm(async () => {await deleteServer(server.uuid)}, "Удалить сервер?", "Отменить действие невозможно.", "Удалить", "danger")}}]} />
          <ChevronRight />
        </div>
      </div>
    )
  })

  const handleConfirm = async () => {
    setConfirmDialog(prev => ({...prev, show: false}))
    if (confirmActionRef.current) await confirmActionRef.current()
    confirmActionRef.current = null
    getUserServers()
  }

  const handleCancel = async () => {
    confirmActionRef.current = null
    setConfirmDialog(prev => ({...prev, show: false}))
  }

  const showConfirm = (action, title = "Вы уверены?", description = "Действие невозможно отменить.", confirmText = "Подтвердить", confirmType = "success") => {
    confirmActionRef.current = action
    setConfirmDialog({show: true, title: title, description: description, confirmText: confirmText, confirmType: confirmType})
  }

  return (
    <div>
      <div className="sticky">
        <Header />
        <div className="card without-background">
          <div className="row">
            <h1>Мои серверы</h1>
            <button className="primary-button margin-left">Создать сервер</button>
          </div>
          <div className="row">
            <input className="search" value={search} onChange={(e) => {setSearch(e.target.value)}} placeholder="🔍︎ Поиск по названию..." />
            {/* <div className="row margin-left small-gap card-background">
              <button className="card-radius-button">Все</button>
              <button className="card-radius-button">Активны</button>
              <button className="card-radius-button">Остановлены</button>
            </div> */}
            <div className="sorting-container">
              <h3 className="sorting-container-text">Cортировка:</h3>
              <CustomSelect className="custom-select--text-only" value={sortBy} onChange={setSortBy} options={[{label: "По названию", value: "name"},]} />
            </div>
          </div>
        </div>
      </div>
      <div>
        <div className="card without-background servers-list">
          {serverItems}            
        </div>
        {showNoServersFound && <div className="no-servers-found">
          <h3>Серверы не найдены.</h3>
        </div>}
      </div>
      <ConfirmDialog dialog={confirmDialog} onConfirm={handleConfirm} onCancel={handleCancel} />
    </div>
  )
}

export default Servers